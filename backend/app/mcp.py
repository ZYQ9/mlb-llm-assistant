import json
import logging
from typing import Any, Dict, List

from fastapi import WebSocket, WebSocketDisconnect

from app.tools import TOOL_SCHEMAS, call_tool

logger = logging.getLogger(__name__)


async def handle_mcp(websocket: WebSocket) -> None:
    """Minimal MCP-style websocket: list tools and execute them."""
    await websocket.accept()
    await _send_tools(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await websocket.send_json({"type": "error", "error": "invalid_json"})
                continue

            msg_type = msg.get("type")
            if msg_type == "list_tools":
                await _send_tools(websocket)
            elif msg_type == "call_tool":
                name = msg.get("name")
                args = msg.get("arguments") or {}
                await _execute_tool(websocket, name, args)
            else:
                await websocket.send_json({"type": "error", "error": f"unknown_type:{msg_type}"})
    except WebSocketDisconnect:
        logger.info("MCP websocket disconnected")


async def _send_tools(websocket: WebSocket) -> None:
    tools: List[Dict[str, Any]] = [t["function"] for t in TOOL_SCHEMAS]
    await websocket.send_json({"type": "tools", "tools": tools})


async def _execute_tool(websocket: WebSocket, name: str, args: Dict[str, Any]) -> None:
    try:
        result = await call_tool(name, args)
        await websocket.send_json({"type": "tool_result", "name": name, "result": result})
    except Exception as exc:
        logger.exception("tool %s failed", name)
        await websocket.send_json({"type": "error", "error": str(exc), "name": name})

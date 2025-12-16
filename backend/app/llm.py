import json
import logging
import os
from typing import Any, Dict, List

import httpx

from app.tools import TOOL_SCHEMAS, call_tool

logger = logging.getLogger(__name__)

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3")

SYSTEM_PROMPT = (
    "You are a baseball assistant. Prefer calling tools to fetch live data from MLB StatsAPI. "
    "Be concise; cite teams/players/games you used."
)


async def run_chat(prompt: str) -> Dict[str, str]:
    messages: List[Dict[str, Any]] = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": prompt},
    ]

    for step in range(4):
        logger.info("LLM call step %s", step + 1)
        resp = await _ollama_chat(messages)
        msg = resp.get("message", {})
        tool_calls = msg.get("tool_calls")

        if not tool_calls:
            logger.info("LLM returned final response")
            return {"message": msg.get("content", "")}

        for tool_call in tool_calls:
            name = tool_call["function"]["name"]
            args_raw = tool_call["function"].get("arguments") or "{}"
            args = json.loads(args_raw)
            logger.info("executing tool %s with args %s", name, args)
            result = await call_tool(name, args)
            messages.append(msg)
            messages.append({"role": "tool", "name": name, "content": json.dumps(result)})

    logger.warning("Reached max tool resolution steps")
    return {"message": "Could not resolve with tools after several attempts."}


async def _ollama_chat(messages: List[Dict[str, Any]]) -> Dict[str, Any]:
    payload = {
        "model": MODEL,
        "messages": messages,
        "tools": TOOL_SCHEMAS,
        "stream": False,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        resp = await client.post(f"{OLLAMA_URL}/api/chat", json=payload)
    resp.raise_for_status()
    return resp.json()

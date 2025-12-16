import logging

from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.middleware.cors import CORSMiddleware

from app.llm import run_chat
from app.mcp import handle_mcp
from app.schemas import ChatRequest, ChatResponse

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
)
logger = logging.getLogger(__name__)

app = FastAPI(title="MLB LLM Assistant")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten to your UI origin in production
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest):
    try:
        result = await run_chat(req.prompt)
        return result
    except Exception as exc:
        logger.exception("chat endpoint failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.websocket("/mcp")
async def mcp(websocket: WebSocket):
    await handle_mcp(websocket)

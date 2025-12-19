## 2025-12-18

- Set up `mlb-llm-assistant` project: FastAPI backend (`/chat`), MLB StatsAPI tools, caching/logging, React/Vite UI, and MCP server (Python `mcp` SDK, stdio transport via `app.mcp_server`).
- Tools exposed: `today_games`, `team_stats`, `player_stats`, `search_player`, `linescore`; FastAPI forwards LLM tool-calls to these; MCP server wraps the same functions.
- Dependencies: `fastapi`, `uvicorn[standard]`, `httpx`, `pydantic`, `mcp>=0.1.0`; front-end via Vite/React TS template.
- Deployment plan: 3 VMs — VM1 Ollama (llama3, private port 11434), VM2 MCP+FastAPI (points to Ollama via `OLLAMA_URL`, proxy `/chat`, optional MCP kept internal), VM3 static UI (`dist/` served by nginx or similar with `VITE_API_URL` set to backend URL).
- Sizing guidance: VM1 CPU-only 8 vCPU/16–32 GB RAM (better with GPU 12–24 GB VRAM); VM2 2–4 vCPU/4–8 GB RAM (scale with load); VM3 1–2 vCPU/1–2 GB RAM.

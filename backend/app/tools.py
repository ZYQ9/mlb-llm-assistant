import asyncio
import logging
import time
from typing import Any, Dict, Optional

import httpx

logger = logging.getLogger(__name__)

BASE = "https://statsapi.mlb.com/api/v1"
CACHE_TTL_SECONDS = 60
_cache: Dict[str, tuple[float, Any]] = {}

TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "today_games",
            "description": "Get MLB games for a given date (YYYY-MM-DD).",
            "parameters": {
                "type": "object",
                "properties": {"date": {"type": "string", "format": "date"}},
                "required": ["date"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "team_stats",
            "description": "Team hitting & pitching stats for a season.",
            "parameters": {
                "type": "object",
                "properties": {
                    "teamId": {"type": "integer"},
                    "season": {"type": "string"},
                },
                "required": ["teamId", "season"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "player_stats",
            "description": "Player season stats for given personId and season.",
            "parameters": {
                "type": "object",
                "properties": {
                    "personId": {"type": "integer"},
                    "season": {"type": "string"},
                },
                "required": ["personId", "season"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_player",
            "description": "Search player by name query.",
            "parameters": {
                "type": "object",
                "properties": {"query": {"type": "string"}},
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "linescore",
            "description": "Linescore for a gamePk.",
            "parameters": {
                "type": "object",
                "properties": {"gamePk": {"type": "integer"}},
                "required": ["gamePk"],
            },
        },
    },
]


async def call_tool(name: str, args: Dict[str, Any]) -> Dict[str, Any]:
    if name == "today_games":
        return await _get(f"/schedule?sportId=1&date={args['date']}", pick="dates")
    if name == "team_stats":
        return await _get(
            f"/teams/{args['teamId']}/stats?group=hitting,pitching&season={args['season']}",
            pick="stats",
        )
    if name == "player_stats":
        return await _get(
            f"/people/{args['personId']}/stats?stats=season&season={args['season']}",
            pick="stats",
        )
    if name == "search_player":
        return await _get(f"/people/search?query={args['query']}", pick="people")
    if name == "linescore":
        return await _get(f"/game/{args['gamePk']}/linescore")
    return {"error": f"Unknown tool {name}"}


def _cache_key(path: str) -> str:
    return path


def _read_cache(key: str) -> Optional[Any]:
    now = time.monotonic()
    entry = _cache.get(key)
    if not entry:
        return None
    expires_at, data = entry
    if expires_at < now:
        _cache.pop(key, None)
        return None
    return data


def _write_cache(key: str, data: Any) -> None:
    expires_at = time.monotonic() + CACHE_TTL_SECONDS
    _cache[key] = (expires_at, data)


async def _get(path: str, pick: Optional[str] = None) -> Dict[str, Any]:
    key = _cache_key(path)
    cached = _read_cache(key)
    if cached is not None:
        logger.debug("cache hit for %s", path)
        return cached if pick is None else cached.get(pick, cached)

    url = f"{BASE}{path}"
    last_err: Optional[Exception] = None
    for attempt in range(3):
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                resp = await client.get(url)
            resp.raise_for_status()
            data = resp.json()
            _write_cache(key, data)
            if pick:
                return data.get(pick, {})
            return data
        except Exception as exc:
            last_err = exc
            wait = 0.5 * (attempt + 1)
            logger.warning("request failed (attempt %s) for %s: %s", attempt + 1, url, exc)
            await asyncio.sleep(wait)

    logger.error("all retries failed for %s: %s", url, last_err)
    raise last_err if last_err else RuntimeError("Unknown error during request")

import asyncio
import logging

from mcp.server.fastmcp import FastMCP
from mcp.server.stdio import stdio_server

from app.tools import call_tool

logger = logging.getLogger(__name__)

server = FastMCP("mlb-statsapi")


@server.tool()
async def today_games(date: str):
    return await call_tool("today_games", {"date": date})


@server.tool()
async def team_stats(teamId: int, season: str):
    return await call_tool("team_stats", {"teamId": teamId, "season": season})


@server.tool()
async def player_stats(personId: int, season: str):
    return await call_tool("player_stats", {"personId": personId, "season": season})


@server.tool()
async def search_player(query: str):
    return await call_tool("search_player", {"query": query})


@server.tool()
async def linescore(gamePk: int):
    return await call_tool("linescore", {"gamePk": gamePk})


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    )
    async with stdio_server() as (read, write):
        await server.run(read, write)


if __name__ == "__main__":
    asyncio.run(main())

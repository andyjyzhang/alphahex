from __future__ import annotations

from fastapi import FastAPI

from catan_api.routes_bots import router as bots_router
from catan_api.routes_games import router as games_router
from catan_api.routes_replays import router as replays_router

app = FastAPI(title="Catan 1v1 Bot API")
app.include_router(games_router)
app.include_router(bots_router)
app.include_router(replays_router)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

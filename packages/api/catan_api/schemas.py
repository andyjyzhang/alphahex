from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class NewGameRequest(BaseModel):
    seed: int = 0


class GameActionRequest(BaseModel):
    state: dict[str, Any]
    action: dict[str, Any]


class BotMatchRequest(BaseModel):
    bot_a: str = "random"
    bot_b: str = "greedy"
    games: int = Field(default=10, ge=1)
    seed: int = 0

from __future__ import annotations

import random

from fastapi import APIRouter

from catan_api.schemas import BotMatchRequest, GameActionRequest, NewGameRequest
from catan_bots import create_bot
from catan_engine.actions import Action
from catan_engine.observation import create_observation
from catan_engine.rules import apply_action, get_legal_actions
from catan_engine.simulator import run_many_games
from catan_engine.state import GameState, initialize_game

router = APIRouter()


@router.post("/games/new")
def new_game(request: NewGameRequest) -> dict:
    state = initialize_game(seed=request.seed)
    return _game_payload(state, player_id=0)


@router.post("/games/action")
def game_action(request: GameActionRequest) -> dict:
    state = GameState.from_dict(request.state)
    action = Action.from_dict(request.action)
    rng = random.Random(state.rng_seed + len(state.action_log))
    new_state = apply_action(state, action, rng)
    payload = _game_payload(new_state, player_id=new_state.current_player)
    payload["observations"] = [create_observation(new_state, 0), create_observation(new_state, 1)]
    payload["winner"] = new_state.winner
    return payload


@router.post("/games/bot-match")
def bot_match(request: BotMatchRequest) -> dict:
    return run_many_games(create_bot(request.bot_a), create_bot(request.bot_b), request.games, seed=request.seed)


def _game_payload(state: GameState, player_id: int) -> dict:
    return {
        "state": state.to_dict(),
        "observation": create_observation(state, player_id),
        "legal_actions": [action.to_dict() for action in get_legal_actions(state)],
        "winner": state.winner,
    }

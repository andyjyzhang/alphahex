from __future__ import annotations

import random

from catan_bots.base import Bot
from catan_engine.actions import Action, ActionType, Phase
from catan_engine.rules import apply_action, get_legal_actions
from catan_engine.scoring import total_vp
from catan_engine.state import GameState


class GreedyBot(Bot):
    name = "greedy"

    def choose_action(self, observation: dict, legal_actions: list[Action], rng: random.Random) -> Action:
        state = observation.get("_state")
        if state is None and "state" in observation:
            state = GameState.from_dict(observation["state"])
        player_id = observation["player_id"]
        if state is not None and total_vp(state, player_id) >= state.config.target_vp - 2:
            winning = _winning_action(state, player_id, legal_actions, rng)
            if winning is not None:
                return winning

        for action_type in (
            ActionType.BUILD_CITY,
            ActionType.BUILD_SETTLEMENT,
            ActionType.BUY_DEV_CARD,
            ActionType.BUILD_ROAD,
        ):
            typed = [action for action in legal_actions if action.action_type == action_type]
            if typed:
                return typed[0]

        trades = [action for action in legal_actions if action.action_type == ActionType.MARITIME_TRADE]
        if state is not None:
            useful = _useful_trades(state, trades, rng)
            if useful:
                return useful[0]

        end_turn = [action for action in legal_actions if action.action_type == ActionType.END_TURN]
        if end_turn:
            return end_turn[0]
        return rng.choice(legal_actions)


def _winning_action(state: GameState, player_id: int, legal_actions: list[Action], rng: random.Random) -> Action | None:
    for action in legal_actions:
        rng_state = rng.getstate()
        try:
            next_state = apply_action(state, action, rng)
        finally:
            rng.setstate(rng_state)
        if next_state.phase == Phase.GAME_OVER and next_state.winner == player_id:
            return action
        if total_vp(next_state, player_id) >= next_state.config.target_vp:
            return action
    return None


def _useful_trades(state: GameState, trades: list[Action], rng: random.Random) -> list[Action]:
    build_types = {
        ActionType.BUILD_CITY,
        ActionType.BUILD_SETTLEMENT,
        ActionType.BUILD_ROAD,
        ActionType.BUY_DEV_CARD,
    }
    useful: list[Action] = []
    for action in trades:
        rng_state = rng.getstate()
        try:
            next_state = apply_action(state, action, rng)
        finally:
            rng.setstate(rng_state)
        if any(legal.action_type in build_types for legal in get_legal_actions(next_state)):
            useful.append(action)
    return useful

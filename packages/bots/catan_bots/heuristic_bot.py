from __future__ import annotations

import random

from catan_bots.base import Bot
from catan_engine.actions import Action, ActionType, Phase
from catan_engine.resources import Resource
from catan_engine.rules import apply_action, can_place_settlement, maritime_trade_ratio
from catan_engine.scoring import calculate_longest_road, total_vp, visible_vp
from catan_engine.state import GameState


class HeuristicBot(Bot):
    name = "heuristic"

    def choose_action(self, observation: dict, legal_actions: list[Action], rng: random.Random) -> Action:
        state = observation.get("_state")
        if state is None and "state" in observation:
            state = GameState.from_dict(observation["state"])
        if state is None:
            return rng.choice(legal_actions)
        player_id = observation["player_id"]
        if state.phase in {Phase.ROLL, Phase.STEAL}:
            return legal_actions[0]
        if state.phase == Phase.DISCARD:
            return _least_valuable_discard(legal_actions)

        candidates = _candidate_actions(legal_actions)
        scored: list[tuple[float, Action]] = []
        baseline = evaluate_state(state, player_id)
        for action in candidates:
            rng_state = rng.getstate()
            try:
                next_state = apply_action(state, action, rng)
            finally:
                rng.setstate(rng_state)
            scored.append((evaluate_state(next_state, player_id), action))
        best_score = max(score for score, _action in scored)
        end_turn = next((action for action in legal_actions if action.action_type == ActionType.END_TURN), None)
        if end_turn is not None and best_score <= baseline + 0.05:
            return end_turn
        best = [action for score, action in scored if score == best_score]
        return rng.choice(best)


def evaluate_state(state: GameState, player_id: int) -> float:
    player = state.players[player_id]
    opponent_id = state.opponent_id(player_id)
    opponent = state.players[opponent_id]
    score = 14.0 * total_vp(state, player_id) - 10.0 * total_vp(state, opponent_id)
    score += 0.4 * player.total_resources() - 0.2 * opponent.total_resources()
    score += 1.5 * sum(1 for amount in player.resources.values() if amount > 0)
    score += _production_score(state, player_id)
    score += _port_score(state, player_id)
    score += 0.6 * _expansion_count(state, player_id)
    score += 0.8 * calculate_longest_road(state.board, state, player_id)
    score += 1.4 * player.played_knights - opponent.played_knights
    score += 0.8 * sum(player.dev_cards.values()) + 0.4 * sum(player.new_dev_cards.values())
    score -= 2.0 * max(0, visible_vp(state, opponent_id) - visible_vp(state, player_id))
    return score


def _production_score(state: GameState, player_id: int) -> float:
    weights = {2: 1, 3: 2, 4: 3, 5: 4, 6: 5, 8: 5, 9: 4, 10: 3, 11: 2, 12: 1}
    score = 0.0
    player = state.players[player_id]
    for node_id in player.settlements | player.cities:
        multiplier = 2 if node_id in player.cities else 1
        for hex_id in state.board.get_hexes_for_node(node_id):
            hex_tile = state.board.hexes[hex_id]
            if hex_tile.number_token is None:
                continue
            score += multiplier * weights.get(hex_tile.number_token, 0)
            if hex_tile.hex_type.name in {"ORE", "GRAIN"}:
                score += 1.0
    return score


def _port_score(state: GameState, player_id: int) -> float:
    score = 0.0
    for resource in Resource:
        ratio = maritime_trade_ratio(state, player_id, resource)
        if ratio == 2:
            score += 2.0
        elif ratio == 3:
            score += 0.8
    return score


def _expansion_count(state: GameState, player_id: int) -> int:
    return sum(
        1
        for node_id in state.board.nodes
        if can_place_settlement(state, node_id, setup=False, player_id=player_id)
    )


def _candidate_actions(legal_actions: list[Action]) -> list[Action]:
    for action_type in (
        ActionType.BUILD_CITY,
        ActionType.BUILD_SETTLEMENT,
        ActionType.PLAY_KNIGHT,
        ActionType.PLAY_MONOPOLY,
        ActionType.PLAY_YEAR_OF_PLENTY,
        ActionType.PLAY_ROAD_BUILDING,
        ActionType.BUY_DEV_CARD,
        ActionType.BUILD_ROAD,
        ActionType.MARITIME_TRADE,
    ):
        typed = [action for action in legal_actions if action.action_type == action_type]
        if typed:
            return typed[:30]
    return legal_actions


def _least_valuable_discard(legal_actions: list[Action]) -> Action:
    values = {"LUMBER": 0, "BRICK": 1, "WOOL": 2, "GRAIN": 3, "ORE": 4}
    return min(
        legal_actions,
        key=lambda action: sum(values[resource] * count for resource, count in action.payload["resources"].items()),
    )

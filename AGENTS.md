# Agent Guidance

## Project Scope

This repo is a standalone 1v1 Catan-style simulator and bot research backend.
Do not automate, scrape, reverse engineer, or interact with Colonist.io or any
other external multiplayer game site.

## Repository Layout

Keep the project in a single root-level layout:

- `packages/engine/`: Catan rules engine, board/state models, scoring, simulator, replay writer.
- `packages/bots/`: bot interface plus `RandomBot`, `GreedyBot`, and `HeuristicBot`.
- `packages/api/`: FastAPI app and API routes.
- `data/replays/`: runtime replay output directory.
- `README_ENGINE.md`: backend setup, architecture, and usage notes.

Do not recreate a nested project directory such as `catan-1v1-bot/`. There should
be only one `packages/` tree, at the repository root.

## Ownership Boundaries

Backend work should stay in:

- `packages/engine/`
- `packages/bots/`
- `packages/api/`
- `data/replays/`
- `README_ENGINE.md`
- `AGENTS.md`

Avoid unrelated edits to root `README.md`, frontend/training docs, deployment
files, or future web/training packages unless the user explicitly asks.

## Engine Rules

- Keep legality and state transitions in `catan_engine.rules`.
- Bots must choose from `get_legal_actions(state)`.
- `apply_action(state, action, rng=None)` must validate legality before transition.
- `GameState.clone()` must stay safe for bot search/lookahead.
- `create_observation(state, player_id)` must hide opponent exact development cards,
  hidden VP cards, and deck order.
- Replay JSON files are generated runtime artifacts; keep only `data/replays/.gitkeep`
  unless the user explicitly asks to preserve replay outputs.

## Verification

There is currently no pytest suite, per user direction. Use smoke checks instead:

```powershell
$env:PYTHONPATH='packages/engine;packages/bots;packages/api'
python -c "from catan_engine import initialize_game, get_legal_actions; s=initialize_game(seed=0); print(s.phase.name, len(get_legal_actions(s)))"
python -m catan_engine.simulator --bot-a random --bot-b random --games 1 --seed 0
python -c "from fastapi.testclient import TestClient; from catan_api.app import app; c=TestClient(app); print(c.get('/health').json())"
```

After smoke checks, remove generated `__pycache__/` directories and replay JSON
unless they are intentionally part of the requested output.

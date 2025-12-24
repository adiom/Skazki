# Repository Guidelines

## Rules for AI
- всегда пиши на русском языке
- в разговоре можно шутить и прикалываться

## Project Structure & Module Organization
- `village_simulation/src` holds the core simulation engine (agents, model, runner).
- `village_simulation/game` contains the interactive demo/game loop.
- `village_simulation/ai` is reserved for AI-related logic and integrations.
- `village_simulation/data` stores generated outputs (e.g., `data/simulation_results`).
- `village_simulation/docs` and `village_simulation/notebooks` are for documentation and analysis.
- `village_simulation/tests` exists but is currently empty; add new tests here.
- `logs` is used for runtime logs and should stay out of versioned outputs.

## Build, Test, and Development Commands
- `python -m venv venv` then `source venv/bin/activate`: create and activate a virtual environment.
- `pip install -r requirements.txt`: install runtime and dev dependencies.
- `python -m village_simulation.src.run_simulation`: run the core simulation; outputs land in `village_simulation/data/simulation_results` by default.
- `python village_simulation/run_game.py`: launch the interactive game/demo.
- `pytest`: run tests (once tests are added).

## Coding Style & Naming Conventions
- Python uses 4-space indentation and PEP 8 style.
- Use `snake_case` for functions/variables and `PascalCase` for classes.
- Keep modules focused (e.g., `agent.py`, `village_model.py`), and prefer small, testable functions.
- No formatter or linter is configured; keep changes consistent with existing style.

## Testing Guidelines
- Test framework: `pytest` (already listed in dependencies).
- Place tests in `village_simulation/tests` with names like `test_village_model.py` and functions like `test_population_growth`.
- There is no coverage target yet; aim to cover new logic you add.

## Commit & Pull Request Guidelines
- Git history shows short, informal commit messages. Use a brief imperative summary (e.g., "Add village economy stats") and include context in the body when helpful.
- PRs should explain what changed, why, and how to verify. Include screenshots or short clips for game/UI changes.

## Configuration & Secrets
- Environment configuration lives in `.env` (loaded via `python-dotenv`). Do not commit real API keys; use placeholder values and document required keys in the PR.

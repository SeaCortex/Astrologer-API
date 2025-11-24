# Repository Guidelines

## Project Structure & Module Organization
The FastAPI app lives under `app/`. `app/main.py` wires routers in `app/routers`, while shared schemas live in `app/types` and helpers in `app/utils`. Environment-specific TOML files in `app/config/` feed `settings.py`. Generated assets belong in `app/tmp/` and should stay out of version control. API documentation is tracked via `openapi.json` and `site-docs/`. Tests reside in `tests/` and follow the v5 naming pattern to mirror the external API surface.

## Build, Test, and Development Commands
Install dependencies with `uv sync --dev` (Python 3.11). Start a hot-reload server using `uv run dev`, which executes `uvicorn app.main:app --reload`. Run the focused test suite with `uv run test` for the standard `pytest -v` task or `uv run test-cov` to enforce coverage reporting. Static checks run via `uv run quality`, while formatting is fixed through `uv run format`. If your shell cannot locate a task, fall back to `uv run poe <task-name>`.

## Coding Style & Naming Conventions
Use Black’s defaults with the project line length of 200; reformat before committing. Respect 4-space indentation, descriptive snake_case for modules and functions, and PascalCase for Pydantic models under `app/types`. Prefer type annotations everywhere so `mypy` stays clean, and keep FastAPI routers grouped per endpoint family in their existing files.

## Testing Guidelines
Write new tests in `tests/`, naming files `test_<feature>.py` and functions `test_<behavior>`. Use pytest fixtures from `tests/conftest.py` to avoid duplicate setup. Maintain ≥95% coverage, matching `.coveragerc` settings. Run `uv run test-cov` before submitting, and add regression cases for any bug fixes that touch chart computation.

## Commit & Pull Request Guidelines
Follow the concise history style: imperative subjects (e.g., `routers: add v5 composite endpoint`) and optional scope prefixes. Each PR should describe the change set, note any schema or config impacts, and reference related issues. Attach evidence of testing (`uv run test` output or coverage summary) and include screenshots when altering generated SVG or docs.

## Configuration Tips
Local overrides belong in `.env` files consumed by `app/config/settings.py`; never commit secrets. Align new configuration keys with the existing TOML structure and document defaults in `site-docs/` when they affect API clients.

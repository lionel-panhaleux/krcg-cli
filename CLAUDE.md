# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`krcg-cli` is a command-line tool for Vampire: The Eternal Struggle (V:tES). It is a
thin CLI wrapper over the [`krcg`](https://github.com/lionel-panhaleux/krcg) Python
library, which holds all the domain logic and data models (cards, decks, the Tournament
Winning Deck Archive). Issues, discussions, and most non-trivial logic belong upstream in
`krcg`; this repo is primarily argument parsing and output formatting.

## Commands

The project uses [`uv`](https://docs.astral.sh/uv/) and a `justfile`:

- `just test` — runs quality checks then the test suite (this is the full validation gate)
- `just quality` — `ruff check`, `ruff format --check`, and `mypy krcg_cli`
- `uv run pytest -vvs` — run tests directly
- `uv run pytest tests/test_card.py -vvs` — run a single test file
- `uv run pytest tests/test_card.py::test_base -vvs` — run a single test
- `uv sync --dev` — install dependencies (including dev tools)
- `just build` / `just release` — build and publish to PyPI (maintainer workflow)

Ruff is configured (in `pyproject.toml`) with rules `E, D, F, W` and Google-style
docstrings; mypy runs in strict-ish mode with stubs under `stubs/`. Note the CI workflow
(`.github/workflows/validation.yml`) currently type-checks `krcg` (not `krcg_cli`) — the
`justfile` `quality` recipe checks `krcg_cli`, which is the correct target.

## Tests require a network connection

`tests/conftest.py` aborts the whole session in `pytest_sessionstart` if it cannot reach
Google and the KRCG static server. Tests exercise the real CLI end-to-end (`cli_execute([...])`)
and assert against exact captured stdout/stderr, so they depend on live card/ruling data.
The autouse `reset_krcg_state` fixture forces offline `LOCAL_CARDS=1` mode and clears the
`VTES`/`TWDA` singletons before each test to keep tests order-independent.

## Architecture

**Entry point flow:** `krcg_cli/__init__.py:main` → `parser.execute(argv)` →
dispatches to a subcommand. `pyproject.toml` maps the `krcg` console script to
`krcg_cli:main`.

**Subcommand registration pattern:** `parser.py` builds one `argparse` subparser tree and
calls `<module>.add_parser(subparsers)` for each subcommand in `krcg_cli/subcommands/`
(card, complete, search, deck, top, affinity, build, format, seating, stats, twd). Each
subcommand module follows the same contract:
- `add_parser(subparsers)` declares its arguments and calls `parser.set_defaults(func=<handler>)`
- the handler takes the parsed `args` namespace and returns an exit code

To add a subcommand: create a module with that pair, then register it in `parser.py`.

**Shared helpers — `krcg_cli/subcommands/_utils.py`:** the most important file to read.
It contains:
- `_init(...)` — lazily loads the `krcg` data singletons (`vtes.VTES`, and `twda.TWDA`
  when `with_twda=True`). Handlers call this before touching card/deck data.
- `add_card_filters` / `filter_cards` — the shared `-d/--discipline`, `-c/--clan`,
  `--set`, etc. filter options used by `search`/`top`, backed by `vtes.VTES.search`.
- `add_twda_filters` / `filter_twda` — the shared `--from/--to/--players` TWDA filters.
- `NargsChoice` subclasses (`DisciplineChoice`, `ClanChoice`, …) — custom argparse actions
  that validate `nargs="+"` choices against `vtes.VTES.search_dimensions` (working around
  a known argparse limitation). Their valid values come from the loaded dataset, so they
  trigger a data load at parser-build time.
- price lookups (`get_cards_prices` etc.) scrape `shop.cardgamegeek.com` asynchronously;
  `NAMES_MAP` patches card names whose shop slug doesn't match the generated kebab-case slug.

**Data loading / offline mode:** card and rulings data comes from `krcg`. `__init__.py`
sets `LOCAL_CARDS=1` by default so the CLI works offline from bundled data. The
`--international` flag and TWDA-backed commands disable local mode and reload from
VEKN/GitHub, requiring network access (`_init` falls back from `load_from_vekn()` to
`load()` and prints a connection-error hint on failure).

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
- `just quality` — `ruff check`, `ruff format --check`, and `ty check krcg_cli`
- `uv run pytest -vvs` — run tests directly
- `uv run pytest tests/test_card.py -vvs` — run a single test file
- `uv run pytest tests/test_card.py::test_base -vvs` — run a single test
- `uv sync --dev` — install dependencies (including dev tools)
- `just build` / `just release` — build and publish to PyPI (maintainer workflow)

Ruff is configured (in `pyproject.toml`) with rules `E, D, F, W` and Google-style
docstrings; type-checking uses [`ty`](https://github.com/astral-sh/ty) (Astral's checker),
configured under `[tool.ty.environment]` with `extra-paths = ["stubs"]` so the local stubs
under `stubs/` are resolved. Both the `justfile` `quality` recipe and CI
(`.github/workflows/validation.yml`) run `ty check krcg_cli`.

## Tests run offline against bundled data

krcg v5 ships its card, ruling, and TWDA data inside the package, so the test suite needs
no network connection. Tests exercise the real CLI end-to-end (`cli_execute([...])`) and
assert against exact captured stdout/stderr, so their expected strings are tied to the
exact krcg version installed — bumping krcg can shift counts, rankings, rulings, and the
TWD/lackey/jol formatting, and those expectations must be regenerated from actual output.
The autouse `reset_krcg_state` fixture (`tests/conftest.py`) resets the
`_utils.VTES` / `_utils.TWDA` module singletons before each test to keep them
order-independent.

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
It owns the loaded krcg v5 data and the shape-mapping helpers the subcommands depend on:
- `_init(...)` — lazily loads the data into the module-level singletons `_utils.VTES`
  (a `krcg.collections.CardDict`, via `krcg.loader.load()`) and `_utils.TWDA` (a
  `dict[str, krcg.models.Deck]`, via `krcg.twda.load()`, only when `with_twda=True`).
  Handlers reference `_utils.VTES` / `_utils.TWDA` after calling it.
- `add_card_filters` / `filter_cards` — the shared `-d/--discipline`, `-c/--clan`,
  `--set`, etc. options used by `search`/`top`, backed by `CardDict.search`. Note v5
  search defaults to `n=100`, so `filter_cards` passes `n=None` to get all matches, and
  `--text` is a union over the `name`/`card_text`/`flavor_text` dimensions.
- `add_twda_filters` / `filter_twda` — the shared `--from/--to/--players` TWDA filters
  (dates and player counts live on `deck.event` in v5).
- `NargsChoice` subclasses (`DisciplineChoice`, `ClanChoice`, …) — custom argparse actions
  that validate `nargs="+"` choices against `CardDict.search_dimensions` (working around a
  known argparse limitation) and store the canonical-cased choice, since v5 search indexes
  are case-sensitive. Their valid values come from the loaded dataset, so they trigger a
  data load at parser-build time.
- card/deck shape helpers (`card_in_deck`, `deck_date`, `deck_cards`, `is_crypt`,
  `is_library`, `card_clans`, `card_disciplines`) that bridge the v5 models (e.g. a crypt
  card's single `clan` vs a library card's `clan_requirement`, or `Deck.cards` being a
  plain list of `CardInDeck` rather than a callable).
- price lookups (`get_cards_prices` etc.) scrape `shop.cardgamegeek.com` asynchronously;
  `NAMES_MAP` patches card names whose shop slug doesn't match the generated kebab-case slug.

**Data loading / offline:** all card, ruling, and TWDA data comes bundled with krcg v5
(`>=5` in `pyproject.toml`), including translations, so the CLI and tests work offline with
no `LOCAL_CARDS` toggle. Deck (de)serialization lives in `krcg.providers`
(`serialize_twd`/`serialize_lackey`/`serialize_jol`/`serialize_json_minimal`) and decklist
parsing in `krcg.parser.deck_from_txt`; statistics/affinity/deck-building are module-level
functions in `krcg.analyzer` (`played`/`stats`/`affinity`/`build_deck`), all taking the
loaded `CardDict`. The `--international` flag now only controls whether translations are
printed, not how data loads.

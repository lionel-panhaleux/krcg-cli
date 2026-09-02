# CLAUDE.md

This file provides guidance to **all AI agents** (Claude Code and others — `AGENTS.md` is a symlink to it) working with code in this repository.

## What this is

`krcg-cli` is the command line interface of [KRCG](https://github.com/lionel-panhaleux/krcg), the Python library for VTES (Vampire: The Eternal Struggle): card texts, rulings, the Tournament Winning Deck Archive (TWDA), deck analysis, decklist formatting and tournament seating. It is published to PyPI as `krcg-cli` and installs the `krcg` command. Python >= 3.14, krcg >= 5.11.

The library lives in the sibling repository `../krcg` when it is checked out — its `README.md` documents the public API and its `CLAUDE.md` the library conventions; consult them before guessing at the krcg API. The CLI only consumes krcg: card data, rulings and the parser belong there, not here.

## Development commands

This project uses [`uv`](https://github.com/astral-sh/uv) for dependencies and [`just`](https://github.com/casey/just) for tasks. Setup: `uv sync --group dev`.

- `uv run krcg <subcommand> ...` — run the CLI from the checkout
- `just quality` — `ruff check`, `ruff format --check`, `ty check krcg_cli`
- `just test` — `quality`, then `uv run pytest -vvs`
- `just update` — upgrade dependencies (`uv sync --upgrade`)
- `just release [minor|major]` — test, bump the version in `pyproject.toml`, tag, push, build and publish to PyPI (needs `~/.pypi_token`). `pyproject.toml` always carries the *last released* version; write the next release notes under an "(unreleased)" heading in `CHANGELOG.rst`.

Run a single test: `uv run pytest tests/test_search.py::test_filters -vvs`

Lint config lives in `pyproject.toml`: ruff selects `E,D,F,W,UP` with the Google docstring convention (every module, class and function gets a one-line docstring — ruff enforces it), type-checking is `ty check krcg_cli`. Keep `just quality` green.

## Code style

Follow the krcg conventions: compact, functional code, no OO ceremony.

- Keep changes minimal and the code tight; prefer free functions and plain data to classes.
- Don't split out a function used in only one place. Reserve helpers for genuine reuse — `_utils.py` is exactly that.
- Comments are exceptional: write one only for context the code cannot express (an external constraint, a data quirk, a surprising reason). Docstrings are one line unless the helper genuinely needs more.
- Import whole modules at the top of the file and reference qualified (`from krcg import providers`, then `providers.serialize_twd`). Never import inside a function.
- The CLI's output is `print`; diagnostics go through `logging` (the `krcg` logger, `main()` configures it). Messages to the user on failure go to `sys.stderr`, and the subcommand returns a non-zero exit code.
- Modern typing: builtin generics and `X | None`. Annotate the shared helpers; subcommand functions can stay light.

## Architecture

### Command dispatch

`krcg_cli/parser.py` builds the argparse tree: it imports every module of `krcg_cli/subcommands/` and calls its `add_parser(subparsers)`. A subcommand module defines `add_parser`, which declares the arguments and sets `func=<handler>`, and the handler, which takes the parsed `args` and **returns the exit code** (`0`, or `1` after writing the reason to stderr). `execute(argv)` returns that code; `main()` in `__init__.py` passes it to `sys.exit`.

### Shared helpers: `subcommands/_utils.py`

- **Data handles.** `get_cards()` returns the krcg `CardDict`, `get_twda()` the `dict[str, Deck]` archive; both are `functools.cache`d and load the data **bundled with krcg** (`krcg.load()` / `twda.load()`), so the CLI works offline and the data only refreshes with a krcg bump. Nothing is loaded at import time except when a parser's help text needs the search dimension values. `deck_cards(deck)` resolves a deck's entries to cards, `deck_plays(deck, card)` tests membership, `deck_date(deck)` guards the optional event.
- **TWDA filters.** `add_twda_filters` / `filter_twda` implement `--from`, `--to`, `--players`.
- **Card filters.** `add_card_filters` / `filter_cards` implement the search options shared by `search` and `top`. `DimensionChoice` is the argparse action: it validates each value against `cards.search_dimensions[dimension]` and stores the **canonical** value, because krcg's set-dimension search is case-exact. Disciplines stay case-sensitive (case encodes the level: `dom` inferior, `DOM` superior), sets accept names as well as codes (`set_code`), groups accept bare numbers. `--text` searches `name`, `card_text` and `flavor_text` and unions the results. `--no-reprint` excludes `IN_PRINT_SETS`, a hand-maintained list of set names — every name must resolve in `cards.sets`, `set_code` raises otherwise.
- **Display.** `card_text` renders a card (crypt and library differ: `isinstance` on `models.CryptCard` / `models.LibraryCard`), `typical_copies` turns `analyzer.stats` into "1-3 copies". Use `card.unique_name` to display a card and `str(card)` for the `id|name` "krcg format".
- **Prices** (`top --price`). The only network feature: cards are looked up by slug on the Card Game Geek shop's public WPGraphQL endpoint, 50 per request, `NAMES_MAP` overriding slugs the kebab-case rule gets wrong. The price is the cheapest in-stock printing (sale price when set), falling back to the cheapest overall.

### krcg 5 idioms worth knowing

- `Deck.cards` is a `list[CardInDeck]` (id, count, kind, types, comment): resolve through `get_cards()` for full cards, filter by `card.kind`.
- Deck operations are free functions: `parser.deck_from_txt(lines, cards)` to parse, `providers.serialize_twd(deck, cards)` / `serialize_lackey` / `serialize_jol` to print, `msgspec.json.encode(deck)` for JSON.
- Analysis is free functions over any deck list: `analyzer.played`, `stats`, `affinity`, `build_deck` (raises `AnalysisError` on an empty sample).
- `CardDict` lookups are fuzzy (`in` too): names, ids, translations and aliases all resolve. Deck ids and player names don't collide with card names in practice, `deck` relies on it.

## Testing notes

- Tests drive the CLI through the `cli` fixture (`tests/conftest.py`), which runs `execute(argv)` and returns `(code, stdout, stderr)`. Expected outputs are files under `tests/snapshots/`, compared with the `snapshot(name, output)` fixture. To re-baseline after a krcg bump or an intended output change, run `UPDATE_SNAPSHOTS=1 uv run pytest`, then **review `git diff tests/snapshots`** before committing — the diff is the point.
- Tests whose snapshots embed live data (rulings, translations, TWDA listings and rankings) are marked `@pytest.mark.baseline`: a failure is reported as an amber `xfail` ("data drift, eyeball it"), never red. Tests of formatting and logic (help, card text, format, seating, filter semantics) are unmarked and fail red. Apply that criterion when adding a test; don't mark a test baseline to hide a regression.
- Follow the krcg test philosophy: few, dense tests exercising a whole command, no mocks, no test that restates the implementation. Nothing in the suite touches the network (`--price` is untested on purpose).
- Python 3.14's argparse colors its output when `FORCE_COLOR` is set; the conftest pins `PYTHON_COLORS=0` so snapshots stay plain.

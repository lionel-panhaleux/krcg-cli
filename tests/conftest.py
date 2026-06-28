"""Configuration for pytest."""

import pytest

from krcg.collections import CardDict

from krcg_cli.subcommands import _utils


@pytest.fixture(autouse=True)
def reset_krcg_state():
    """Clear the cards and TWDA singletons so each test starts fresh.

    krcg v5 ships its data offline, so tests need no network connection; this
    only keeps the lazily-loaded `_utils.VTES` / `_utils.TWDA` order-independent.
    """
    _utils.VTES = CardDict()
    _utils.TWDA = {}
    yield

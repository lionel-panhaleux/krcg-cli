"""Configuration for pytest."""

import pytest
import requests

from krcg import config
from krcg import cards as krcg_cards
from krcg import vtes as krcg_vtes
from krcg import twda as krcg_twda


def pytest_sessionstart(session):
    """Check for internet connection."""
    # Do not launch tests is there is no proper Internet connection.
    try:
        requests.get("http://www.google.com", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get(config.KRCG_STATIC_SERVER, timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("KRCG website not available")


@pytest.fixture(autouse=True)
def reset_krcg_state(monkeypatch):
    """Ensure a consistent krcg load mode and clear caches before each test.

    - Default to LOCAL_CARDS offline mode so tests are not order-dependent.
    - Clear VTES and TWDA singletons so each test starts fresh.
    """
    monkeypatch.setenv("LOCAL_CARDS", "1")
    krcg_cards.LOCAL_CARDS = "1"
    try:
        krcg_vtes.VTES.clear()
    except Exception:
        pass
    try:
        krcg_twda.TWDA.clear()
    except Exception:
        pass
    yield

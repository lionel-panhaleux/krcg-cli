import os
import pytest
import requests

from krcg import config
from krcg_cli.subcommands import _utils as sub_utils


def pytest_sessionstart(session):
    # Do not launch tests is there is no proper Internet connection.
    try:
        requests.get("http://www.google.com", timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("No internet connection")
    try:
        requests.get(config.KRCG_STATIC_SERVER, timeout=1)
    except requests.exceptions.RequestException:
        pytest.fail("KRCG website not available")
    # remove marshall files to start fresh
    try:
        os.remove(sub_utils.VTES_FILE)
    except FileNotFoundError:
        pass
    try:
        os.remove(sub_utils.TWDA_FILE)
    except FileNotFoundError:
        pass

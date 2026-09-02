"""Test the twd subcommand."""

import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    """Snapshot the twd output."""
    code, out, err = cli("twd", "--from", "2012", "--to", "2013")
    assert code == 0
    assert err == ""
    snapshot("twd-2012", out)

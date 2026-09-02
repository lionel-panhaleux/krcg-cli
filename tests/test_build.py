"""Test the build subcommand."""

import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    """Snapshot the build output."""
    code, out, err = cli("build", "--from", "2013", "--to", "2014", "KRCG")
    assert code == 0
    assert err == ""
    snapshot("build-krcg-2013", out)


def test_not_found(cli):
    """Check the error on an unknown argument."""
    assert cli("build", "Foobar") == (1, "", "Card not found: foobar\n")

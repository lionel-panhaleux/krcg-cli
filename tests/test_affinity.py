"""Test the affinity subcommand."""

import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    """Snapshot the affinity output."""
    code, out, err = cli("affinity", "--from", "2015", "--to", "2020", "Fame")
    assert code == 0
    assert err == ""
    snapshot("affinity-fame-2015-2020", out)


def test_not_found(cli):
    """Check the error on an unknown argument."""
    assert cli("affinity", "Foobar") == (1, "", "Card not found: foobar\n")

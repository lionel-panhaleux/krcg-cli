"""Test the search subcommand."""

import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    """Snapshot the search output."""
    for name, args in {
        "search-text-pentex": ["--text", "Pentex"],
        "search-city-chicago": ["--city", "chicago"],
        "search-title-imperator": ["--title", "imperator"],
        "search-title-primogen-ser": ["--title", "primogen", "-d", "ser"],
        "search-bonus-stealth-votes": ["--bonus", "stealth", "votes"],
        "search-bonus-stealth-votes-all": ["--bonus", "stealth", "votes", "-n", "0"],
        "search-set-black-hand": ["--set", "Black Hand", "-n", "5"],
        "search-no-reprint-master": ["--no-reprint", "-t", "master", "-n", "5"],
    }.items():
        code, out, err = cli("search", *args)
        assert code == 0, name
        assert err == "", name
        snapshot(name, out)


def test_filters(cli):
    # sets are accepted by name or code, case-insensitive
    """Check the filters semantics."""
    by_name = cli("search", "--set", "black hand", "-n", "0")
    assert by_name[0] == 0
    assert by_name == cli("search", "--set", "BH", "-n", "0")
    # groups are accepted as bare numbers
    assert cli("search", "-g", "4", "-n", "0") == cli("search", "-g", "G4", "-n", "0")
    # --no-reprint excludes cards from sets in print
    assert cli("search", "--set", "V5", "--no-reprint") == (1, "", "No match\n")
    # invalid choices are reported
    with pytest.raises(SystemExit):
        cli("search", "--clan", "foobar")

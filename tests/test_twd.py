"""Test twd subcommand."""

from krcg_cli.parser import execute as cli_execute


def test(capsys):
    """Test twd subcommand."""
    cli_execute(["twd", "--from", "2012", "--to", "2013"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    # TODO test for real when output gets stable

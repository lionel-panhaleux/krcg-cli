"""Test complete subcommand."""

from krcg_cli.parser import execute as cli_execute


def test(capsys):
    """Test complete subcommand."""
    cli_execute(["complete", "Pentex"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Pentex™ Loves You!
Pentex™ Subversion
Enzo Giovanni, Pentex Board of Directors
Enzo Giovanni, Pentex Board of Directors (ADV)
Harold Zettler, Pentex Director
"""
    )

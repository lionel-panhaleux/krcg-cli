"""Test search subcommand."""

from krcg_cli.parser import execute as cli_execute


def test(capsys):
    """Test search subcommand."""
    cli_execute(["search", "--text", "Pentex"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Enzo Giovanni, Pentex Board of Directors
Enzo Giovanni, Pentex Board of Directors (ADV)
Harold Zettler, Pentex Director
Pentex™ Loves You!
Pentex™ Subversion
"""
    )
    cli_execute(["search", "--city", "chicago"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Antón de Concepción
Crusade: Chicago
Horatio Ballard
Kevin Jackson
Lachlan, Noddist
Lodin (Olaf Holte)
Maldavis (ADV)
Maxwell
Praxis Seizure: Chicago
Sir Walter Nash
"""
    )
    cli_execute(["search", "--title", "imperator"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Camarilla's Iron Fist
Confiscation
Karsh (ADV)
National Guard Support
Persona Non Grata
Reinforcements
Rubicon
Scourge
"""
    )
    cli_execute(["search", "--title", "primogen", "-d", "ser"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == "Amenophobis\n"
    # --bonus is an intersection filter in krcg v5: cards with both stealth and votes
    cli_execute(["search", "--bonus", "stealth", "votes"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Camarilla Conclave
Loki's Gift
Perfect Paragon
"""
    )
    cli_execute(["search", "--bonus", "stealth", "votes", "-n", "15"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Camarilla Conclave
Loki's Gift
Perfect Paragon
"""
    )

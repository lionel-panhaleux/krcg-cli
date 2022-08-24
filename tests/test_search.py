from krcg_cli.parser import execute as cli_execute


def test(capsys):
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
        == """Imperator
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
    cli_execute(["search", "--bonus", "stealth", "votes"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Antonio Veradas
Bulscu (ADV)
Dark Selina
Jessica (ADV)
Joseph Cambridge
Karen Suadela
Loki's Gift
Maxwell
Natasha Volfchek
Perfect Paragon
... 3 more results, use -n 13 to display them.
"""
    )
    cli_execute(["search", "--bonus", "stealth", "votes", "-n", "13"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Antonio Veradas
Bulscu (ADV)
Dark Selina
Jessica (ADV)
Joseph Cambridge
Karen Suadela
Loki's Gift
Maxwell
Natasha Volfchek
Perfect Paragon
Sela (ADV)
Suhailah
Zayyat, The Sandstorm
"""
    )

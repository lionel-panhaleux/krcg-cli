"""Test card subcommand."""

from krcg_cli.parser import execute as cli_execute


def test_base(capsys):
    """Test base card."""
    cli_execute(["card", "krcg"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """KRCG News Radio
[Master][2P] -- (#101067)
Unique location.
You can lock this card to give a minion you control +1 intercept. You can lock this card and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.

-- Rulings
Sequencing rules apply. You must gain the impulse to be able to use the reaction, or use the effect (whichever is applicable).  Other Methuselahs must declare block attempts (or not) and pass the impulse to you as normal. [ANK 20200607]
"""  # noqa: E501
    )


def test_international(capsys):
    """Test translations."""
    cli_execute(["card", "--international", ".44 Magnum"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """.44 Magnum
  fr -- Magnum .44
  es -- Magnum .44
[Equipment][2P] -- (#100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- fr
Arme à feu.
Frapper à toute portée : 2 points de dégâts, avec 1 manœuvre optionnelle durant chaque combat.

-- es
Arma: arma de fuego.
Ataque: 2 de daño a distancia, con una maniobra opcional por combate.

-- Rulings
Provides only one maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]
"""  # noqa: E501
    )


def test_short(capsys):
    """Test short mode."""
    cli_execute(["card", "--short", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == "Alastor\n"


def test_text(capsys):
    """Test text mode."""
    cli_execute(["card", "--text", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Alastor
[Political Action] -- (#100038)
Requires a justicar or Inner Circle member.
Choose a ready Camarilla vampire. Successful referendum means you search your library for an equipment card and put this card and the equipment on the chosen vampire (ignore requirements; shuffle afterward); pay half the cost rounded down of the equipment. The attached vampire can enter combat with a vampire as a +1 stealth Ⓓ action. The attached vampire cannot commit diablerie. A vampire can have only one Alastor.
"""  # noqa: E501
    )


def test_links(capsys):
    """Test links for rulings."""
    cli_execute(["card", "--links", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Alastor
[Political Action] -- (#100038)
Requires a justicar or Inner Circle member.
Choose a ready Camarilla vampire. Successful referendum means you search your library for an equipment card and put this card and the equipment on the chosen vampire (ignore requirements; shuffle afterward); pay half the cost rounded down of the equipment. The attached vampire can enter combat with a vampire as a +1 stealth Ⓓ action. The attached vampire cannot commit diablerie. A vampire can have only one Alastor.

-- Rulings
If the weapon retrieved costs blood, that cost is paid by the vampire chosen by the terms. [LSJ 20040518]
Requirements do not apply. If a discipline is required (eg. {Inscription}) and the Alastor vampire does not have it, the inferior version is used. [ANK 20200901] [LSJ 20040518-2]
Finding equipment is optional. When no equipment is found, alastor is still attached. [LSJ 20050331-2]
Cards requiring a discipline come in play at the inferior version. [RBK equip] [RBK recruit-ally] [RBK employ-retainer]

-- Rulings references
LSJ 20040518: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/4emymfUPwAM/m/B2SCC7L6kuMJ
ANK 20200901: https://www.vekn.net/forum/rules-questions/78830-alastor-and-ankara-citadel#100653
LSJ 20040518-2: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/4emymfUPwAM/m/JF_o7OOoCbkJ
LSJ 20050331-2: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/NLFFYNok1Ns/m/n7mHhZ_oTRQJ
RBK equip: https://www.vekn.net/rulebook#equip
RBK recruit-ally: https://www.vekn.net/rulebook#recruit-ally
RBK employ-retainer: https://www.vekn.net/rulebook#employ-retainer
"""  # noqa: E501
    )


def test_id(capsys):
    """Test id argument."""
    cli_execute(["card", "-s", "100001"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == ".44 Magnum\n"


def test_multi(capsys):
    """Test multiple cards."""
    cli_execute(["card", "-t", ".44 Magnum", "Alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """.44 Magnum
[Equipment][2P] -- (#100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

Alastor
[Political Action] -- (#100038)
Requires a justicar or Inner Circle member.
Choose a ready Camarilla vampire. Successful referendum means you search your library for an equipment card and put this card and the equipment on the chosen vampire (ignore requirements; shuffle afterward); pay half the cost rounded down of the equipment. The attached vampire can enter combat with a vampire as a +1 stealth Ⓓ action. The attached vampire cannot commit diablerie. A vampire can have only one Alastor.
"""  # noqa: E501
    )

from krcg_cli.parser import execute as cli_execute


def test_base(capsys):
    cli_execute(["card", "krcg"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """KRCG News Radio
[Master][2P] -- (#101067)
Unique location.
Lock to give a minion you control +1 intercept. Lock and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.
"""  # noqa: E501
    )


def test_international(capsys):
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
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]
"""  # noqa: E501
    )


def test_short(capsys):
    cli_execute(["card", "--short", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == "Alastor\n"


def test_text(capsys):
    cli_execute(["card", "--text", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Alastor
[Political Action] -- (#100038)
Requires a justicar or Inner Circle member.
Choose a ready Camarilla vampire. If this referendum is successful, search your library for an equipment card and place this card and the equipment on the chosen vampire. Pay half the cost (round down) of the equipment. This vampire may enter combat with any vampire controlled by another Methuselah as a +1 stealth Ⓓ action. This vampire cannot commit diablerie. A vampire may have only one Alastor.
"""  # noqa: E501
    )


def test_links(capsys):
    cli_execute(["card", "--links", "alastor"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Alastor
[Political Action] -- (#100038)
Requires a justicar or Inner Circle member.
Choose a ready Camarilla vampire. If this referendum is successful, search your library for an equipment card and place this card and the equipment on the chosen vampire. Pay half the cost (round down) of the equipment. This vampire may enter combat with any vampire controlled by another Methuselah as a +1 stealth Ⓓ action. This vampire cannot commit diablerie. A vampire may have only one Alastor.

-- Rulings
If the given weapon costs blood, the target Alastor pays the cost. [LSJ 20040518]
Requirements do not apply. [ANK 20200901]
[LSJ 20040518]: https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/4emymfUPwAM/B2SCC7L6kuMJ
[ANK 20200901]: http://www.vekn.net/forum/rules-questions/78830-alastor-and-ankara-citadel#100653
"""  # noqa: E501
    )


def test_id(capsys):
    cli_execute(["card", "-s", "100001"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == ".44 Magnum\n"


def test_multi(capsys):
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
Choose a ready Camarilla vampire. If this referendum is successful, search your library for an equipment card and place this card and the equipment on the chosen vampire. Pay half the cost (round down) of the equipment. This vampire may enter combat with any vampire controlled by another Methuselah as a +1 stealth Ⓓ action. This vampire cannot commit diablerie. A vampire may have only one Alastor.
"""  # noqa: E501
    )

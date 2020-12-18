from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute(["build", "--from", "2018", "--to", "2020", "KRCG"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Created by: KRCG

Inspired by:
 - 2019bcspspdms        (No Name)
 - 2018nacd2co          Owain and His Merry Band of Assholes, 2018 Edition
 - 2018pbcthbc          !Ventrue Toolbox
Crypt (12 cards, min=18, max=31, avg=6.25)
------------------------------------------
2x Owain Evans, The Wanderer   8 AUS DOM FOR cel pre              Ventrue antitribu:3
2x Blackhorse Tanner           7 AUS DOM FOR                      Ventrue antitribu:3
1x Jesse Menks                 8 AUS DOM FOR ani      archbishop  Ventrue antitribu:3
1x Samson                      2 dom                              Ventrue antitribu:2
1x Joseph O'Grady              7 DOM FOR aus cel                  Ventrue antitribu:3
1x Charice Fontaigne           6 AUS DOM for pot                  Ventrue antitribu:3
2x Neighbor John               5 AUS dom for                      Ventrue antitribu:4
2x Jefferson Foster            6 AUS DOM for tha      bishop      Ventrue antitribu:4

Library (90 cards)
Master (19)
2x Anarch Troublemaker
1x Barrens, The
3x Blood Doll
1x Channel 10
2x Direct Intervention
2x Dreams of the Sphinx
1x Information Highway
1x KRCG News Radio
1x Misdirection
1x Pentex(TM) Subversion
1x Perfectionist
1x Powerbase: Montreal
1x Sudden Reversal
1x WMRH Talk Radio

Action (16)
1x Abbot
11x Govern the Unaligned
4x Under Siege

Equipment (3)
1x Bowl of Convergence
1x Heart of Nizchetus
1x Ivory Bow

Action Modifier (11)
5x Conditioning
2x Daring the Dawn
4x Freak Drive

Reaction (24)
8x Deflection
2x Delaying Tactics
4x Eyes of Argus
2x My Enemy's Enemy
4x On the Qui Vive
4x Telepathic Misdirection

Combat (17)
5x Hidden Strength
4x Indomitability
4x Rolling with the Punches
4x Weighted Walking Stick
"""
    )
    cli_execute(["build", "Foobar"])
    outerr = capsys.readouterr()
    assert outerr.err == "Card not found: foobar\n"
    assert outerr.out == ""

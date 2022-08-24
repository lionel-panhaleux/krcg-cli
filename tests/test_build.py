from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute(["build", "--from", "2018", "--to", "2020", "KRCG"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Created by: KRCG

Inspired by:
 - 2019ctllpdvs         (No Name)
 - 2019bcspspdms        (No Name)
 - 2019gppwp            Bored Owain (sorry, I just need to do it - Szewski)
 - 2018pbcthbc          !Ventrue Toolbox
Crypt (12 cards, min=19, max=31, avg=6.33)
------------------------------------------
2x Owain Evans, The Wanderer   8 AUS DOM FOR cel pre              Ventrue antitribu:3
2x Blackhorse Tanner           7 AUS DOM FOR                      Ventrue antitribu:3
1x Joseph O'Grady              7 DOM FOR aus cel                  Ventrue antitribu:3
1x Charice Fontaigne           6 AUS DOM for pot                  Ventrue antitribu:3
2x Jefferson Foster            6 AUS DOM for tha      bishop      Ventrue antitribu:4
1x Neighbor John               5 AUS dom for                      Ventrue antitribu:4
1x Jesse Menks                 8 AUS DOM FOR ani      archbishop  Ventrue antitribu:3
1x Jephta Hester               5 DOM FOR aus                      Ventrue antitribu:4
1x Ulrike Rothbart             3 dom for                          Ventrue antitribu:4

Library (90 cards)
Master (19; 5 trifle)
1x Anarch Troublemaker
2x Blood Doll
1x Channel 10
1x Corporate Hunting Ground
2x Dreams of the Sphinx
1x Giant's Blood
1x KRCG News Radio
1x Misdirection
1x Pentex(TM) Subversion
1x Powerbase: Barranquilla
1x Powerbase: Montreal
3x Vessel
1x Wall Street Night, Financial Newspaper
2x Wider View

Action (14)
1x Abbot
13x Govern the Unaligned

Equipment (3)
1x Bowl of Convergence
1x Heart of Nizchetus
1x Ivory Bow

Action Modifier (10)
2x Bonding
5x Conditioning
2x Daring the Dawn
1x Day Operation

Reaction (28)
6x Deflection
2x Delaying Tactics
2x Eagle's Sight
2x Enhanced Senses
5x Eyes of Argus
2x My Enemy's Enemy
5x On the Qui Vive
4x Telepathic Misdirection

Combat (16)
4x Hidden Strength
3x Indomitability
4x Rolling with the Punches
5x Weighted Walking Stick
"""
    )
    cli_execute(["build", "Foobar"])
    outerr = capsys.readouterr()
    assert outerr.err == "Card not found: foobar\n"
    assert outerr.out == ""

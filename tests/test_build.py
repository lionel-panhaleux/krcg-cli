"""Test build subcommand."""

from krcg_cli.parser import execute as cli_execute


def test(capsys):
    """Test build subcommand."""
    cli_execute(["build", "--from", "2013", "--to", "2014", "KRCG"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Created by: KRCG

Inspired by:
 - 2013fsfiiifb         !Ventrue
 - 2013bdmspb           Ventrue! Grinder
 - 2013addbspb          Ventrue! Grinder
 - 2013tnotbspb         Ventrue! Grinder
 - 2013bssbotuk         Gents on the town, twirling their canes v7 2013
 - 2013ukdcp            Owain's Grindhouse
 - 2013ecqllf           (No Name)
 - 2013fdss             Ventrue Anti Grind
Crypt (12 cards, min=16, max=30, avg=5.75)
------------------------------------------
1x Jephta Hester               5 DOM FOR aus                  Ventrue antitribu:4
1x Ulrike Rothbart             3 dom for                      Ventrue antitribu:4
2x Owain Evans, The Wanderer   8 AUS DOM FOR cel pre          Ventrue antitribu:3
2x Blackhorse Tanner           7 AUS DOM FOR                  Ventrue antitribu:3
2x Neighbor John               5 AUS dom for                  Ventrue antitribu:4
1x Lana Butcher                3 dom for                      Ventrue:3
1x Jefferson Foster            6 AUS DOM for tha      bishop  Ventrue antitribu:4
1x Joseph O'Grady              7 DOM FOR aus cel              Ventrue antitribu:3
1x Ilyana Ravidovich           5 aus dom for pre              Ventrue:3

Library (90 cards)
Master (17; 6 trifle)
1x Anarch Troublemaker
1x Channel 10
1x Corporate Hunting Ground
2x Dreams of the Sphinx
1x KRCG News Radio
1x Misdirection
1x Pentex(TM) Subversion
1x Powerbase: Montreal
4x Vessel
1x Vox Domini
1x Wall Street Night, Financial Newspaper
2x Wider View

Action (10)
10x Govern the Unaligned

Ally (1)
1x Carlton Van Wyk

Equipment (2)
1x Bowl of Convergence
1x Ivory Bow

Action Modifier (9)
2x Bonding
5x Conditioning
1x Daring the Dawn
1x Day Operation

Reaction (31)
5x Deflection
2x Delaying Tactics
2x Eagle's Sight
2x Enhanced Senses
3x Eyes of Argus
2x Forced Awakening
2x My Enemy's Enemy
4x On the Qui Vive
2x Redirection
4x Telepathic Misdirection
3x Wake with Evening's Freshness

Combat (18)
5x Hidden Strength
4x Indomitability
4x Rolling with the Punches
5x Weighted Walking Stick

Event (2)
1x Scourge of the Enochians
1x Uncoiling, The
"""
    )
    cli_execute(["build", "Foobar"])
    outerr = capsys.readouterr()
    assert outerr.err == "Card not found: foobar\n"
    assert outerr.out == ""

"""Test format subcommand."""

import json

from krcg_cli.parser import execute as cli_execute


DECKLIST = """Crypt (12 cards, min=7, max=24, avg=3.75)
-----------------------------------------
1x Gilbert Duane          7 AUS DOM OBF      prince  Malkavian:1
1x Mariel, Lady Thunder   7 DOM OBF aus tha          Malkavian:1
1x Badr al-Budur          5 OBF cel dom qui          Banu Haqim:2
1x Count Ormonde          5 OBF dom pre ser          Ministry:2
1x Didi Meyers            5 DOM aus cel obf          Malkavian:1
1x Zebulon                5 OBF aus dom pro          Malkavian:1
1x Dimple                 2 obf                      Nosferatu:1
1x Mustafa Rahman         2 dom                      Tremere:2
1x Normal                 2 obf                      Malkavian:1
1x Ohanna                 2 dom                      Malkavian:2
1x Samson                 2 dom                      Ventrue antitribu:2
1x Basil                  1 obf                      Pander:2

Library (87 cards)
Master (19; 3 trifle)
1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex
3x Sudden Reversal
3x Vessel

Ally (12)
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods

Equipment (9)
1x Deer Rifle
8x Flash Grenade

Action Modifier (19)
6x Cloak the Gathering
7x Conditioning
2x Lost in Crowds
4x Veil the Legions

Reaction (16)
7x Deflection
2x Delaying Tactics
7x On the Qui Vive

Combat (8)
8x Concealed Weapon

Event (4)
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x Unmasking, The
"""


def test(capsys, tmpdir):
    """Test format subcommand."""
    file_path = tmpdir + "test-format.txt"
    with file_path.open("w") as f:
        f.write(DECKLIST)
    cli_execute(["format", "-f", "twd", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == (
        """Crypt (12 cards, min=7, max=24, avg=3.75)
-----------------------------------------
1x Gilbert Duane (G1)    7  AUS DOM OBF      prince  Malkavian:1
1x Mariel, Lady Thunder  7  DOM OBF aus tha          Malkavian:1
1x Badr al-Budur         5  OBF cel dom qui          Banu Haqim:2
1x Count Ormonde         5  OBF dom pre ser          Ministry:2
1x Didi Meyers           5  DOM aus cel obf          Malkavian:1
1x Zebulon               5  OBF aus dom pro          Malkavian:1
1x Dimple                2  obf                      Nosferatu:1
1x Mustafa Rahman        2  dom                      Tremere:2
1x Normal                2  obf                      Malkavian:1
1x Ohanna                2  dom                      Malkavian:2
1x Samson                2  dom                      Ventrue antitribu:2
1x Basil                 1  obf                      Pander:2

Library (87 cards)
Master (19; 3 trifle)
1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex
3x Sudden Reversal
3x Vessel

Ally (12)
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods

Equipment (9)
1x Deer Rifle
8x Flash Grenade

Action Modifier (19)
6x Cloak the Gathering
7x Conditioning
2x Lost in Crowds
4x Veil the Legions

Reaction (16)
7x Deflection
2x Delaying Tactics
7x On the Qui Vive

Combat (8)
8x Concealed Weapon

Event (4)
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x Unmasking, The
"""
    )
    cli_execute(["format", "-f", "lackey", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """1\tChannel 10
2\tCharisma
1\tCreepshow Casino
1\tKRCG News Radio
2\tPerfectionist
6\tStorage Annex
3\tSudden Reversal
3\tVessel
1\tCarlton Van Wyk
1\tGregory Winter
1\tImpundulu
1\tMuddled Vampire Hunter
1\tOssian
6\tProcurer
1\tYoung Bloods
1\tDeer Rifle
8\tFlash Grenade
6\tCloak the Gathering
7\tConditioning
2\tLost in Crowds
4\tVeil the Legions
7\tDeflection
2\tDelaying Tactics
7\tOn the Qui Vive
8\tConcealed Weapon
1\tFBI Special Affairs Division
1\tHunger Moon
1\tRestricted Vitae
1\tUnmasking, The
Crypt:
1\tBadr al-Budur
1\tBasil
1\tCount Ormonde
1\tDidi Meyers
1\tDimple
1\tGilbert Duane (G1)
1\tMariel, Lady Thunder
1\tMustafa Rahman
1\tNormal
1\tOhanna
1\tSamson
1\tZebulon
"""
    )
    cli_execute(["format", "-f", "jol", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """1x Badr al-Budur
1x Basil
1x Count Ormonde
1x Didi Meyers
1x Dimple
1x Gilbert Duane (G1)
1x Mariel, Lady Thunder
1x Mustafa Rahman
1x Normal
1x Ohanna
1x Samson
1x Zebulon

1x Channel 10
2x Charisma
1x Creepshow Casino
1x KRCG News Radio
2x Perfectionist
6x Storage Annex
3x Sudden Reversal
3x Vessel
1x Carlton Van Wyk
1x Gregory Winter
1x Impundulu
1x Muddled Vampire Hunter
1x Ossian
6x Procurer
1x Young Bloods
1x Deer Rifle
8x Flash Grenade
6x Cloak the Gathering
7x Conditioning
2x Lost in Crowds
4x Veil the Legions
7x Deflection
2x Delaying Tactics
7x On the Qui Vive
8x Concealed Weapon
1x FBI Special Affairs Division
1x Hunger Moon
1x Restricted Vitae
1x Unmasking, The
"""
    )
    cli_execute(["format", "-f", "json", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    # the minimal JSON format maps card id -> count (order-independent)
    assert json.loads(outerr.out) == {
        "cards": {
            "100298": 1,
            "100327": 1,
            "100332": 2,
            "100362": 6,
            "100392": 8,
            "100401": 7,
            "100444": 1,
            "100516": 1,
            "100518": 7,
            "100519": 2,
            "100709": 1,
            "100745": 8,
            "100855": 1,
            "100944": 1,
            "100966": 1,
            "101067": 1,
            "101125": 2,
            "101250": 1,
            "101321": 7,
            "101333": 1,
            "101388": 2,
            "101491": 6,
            "101614": 1,
            "101877": 6,
            "101896": 3,
            "102079": 1,
            "102097": 4,
            "102113": 3,
            "102202": 1,
            "200161": 1,
            "200173": 1,
            "200295": 1,
            "200343": 1,
            "200346": 1,
            "200517": 1,
            "200929": 1,
            "201027": 1,
            "201065": 1,
            "201073": 1,
            "201231": 1,
            "201503": 1,
        }
    }

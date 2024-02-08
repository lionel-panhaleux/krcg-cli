import arrow
import datetime
from krcg_cli.parser import execute as cli_execute


def test(capsys, tmpdir):
    file_path = tmpdir + "test-format.txt"
    with file_path.open("w") as f:
        f.write(
            """Crypt (12 cards, min=7, max=24, avg=3.75)
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
        )
    cli_execute(["format", "-f", "twd", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == (
        f"""{arrow.get(datetime.date.today()).format("MMMM Do YYYY")}

Crypt (12 cards, min=7, max=24, avg=3.75)
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
    )
    cli_execute(["format", "-f", "lackey", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """1	Channel 10
2	Charisma
1	Creepshow Casino
1	KRCG News Radio
2	Perfectionist
6	Storage Annex
3	Sudden Reversal
3	Vessel
1	Carlton Van Wyk
1	Gregory Winter
1	Impundulu
1	Muddled Vampire Hunter
1	Ossian
6	Procurer
1	Young Bloods
1	Deer Rifle
8	Flash Grenade
6	Cloak the Gathering
7	Conditioning
2	Lost in Crowds
4	Veil the Legions
7	Deflection
2	Delaying Tactics
7	On the Qui Vive
8	Concealed Weapon
1	FBI Special Affairs Division
1	Hunger Moon
1	Restricted Vitae
1	Unmasking, The
Crypt:
1	Gilbert Duane
1	Mariel, Lady Thunder
1	Badr al-Budur
1	Count Ormonde
1	Didi Meyers
1	Zebulon
1	Dimple
1	Mustafa Rahman
1	Normal
1	Ohanna
1	Samson
1	Basil
"""
    )
    cli_execute(["format", "-f", "jol", str(file_path)])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """1x Gilbert Duane
1x Mariel, Lady Thunder
1x Badr al-Budur
1x Count Ormonde
1x Didi Meyers
1x Zebulon
1x Dimple
1x Mustafa Rahman
1x Normal
1x Ohanna
1x Samson
1x Basil

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
    assert (
        outerr.out
        == f'{{\n  "date": "{datetime.date.today().isoformat()}",\n'
        + """  "crypt": {
    "count": 12,
    "cards": [
      {
        "id": 200517,
        "count": 1,
        "name": "Gilbert Duane"
      },
      {
        "id": 200929,
        "count": 1,
        "name": "Mariel, Lady Thunder"
      },
      {
        "id": 200161,
        "count": 1,
        "name": "Badr al-Budur"
      },
      {
        "id": 200295,
        "count": 1,
        "name": "Count Ormonde"
      },
      {
        "id": 200343,
        "count": 1,
        "name": "Didi Meyers"
      },
      {
        "id": 201503,
        "count": 1,
        "name": "Zebulon"
      },
      {
        "id": 200346,
        "count": 1,
        "name": "Dimple"
      },
      {
        "id": 201027,
        "count": 1,
        "name": "Mustafa Rahman"
      },
      {
        "id": 201065,
        "count": 1,
        "name": "Normal"
      },
      {
        "id": 201073,
        "count": 1,
        "name": "Ohanna"
      },
      {
        "id": 201231,
        "count": 1,
        "name": "Samson"
      },
      {
        "id": 200173,
        "count": 1,
        "name": "Basil"
      }
    ]
  },
  "library": {
    "count": 87,
    "cards": [
      {
        "type": "Master",
        "count": 19,
        "cards": [
          {
            "id": 100327,
            "count": 1,
            "name": "Channel 10"
          },
          {
            "id": 100332,
            "count": 2,
            "name": "Charisma"
          },
          {
            "id": 100444,
            "count": 1,
            "name": "Creepshow Casino"
          },
          {
            "id": 101067,
            "count": 1,
            "name": "KRCG News Radio"
          },
          {
            "id": 101388,
            "count": 2,
            "name": "Perfectionist"
          },
          {
            "id": 101877,
            "count": 6,
            "name": "Storage Annex"
          },
          {
            "id": 101896,
            "count": 3,
            "name": "Sudden Reversal"
          },
          {
            "id": 102113,
            "count": 3,
            "name": "Vessel"
          }
        ]
      },
      {
        "type": "Ally",
        "count": 12,
        "cards": [
          {
            "id": 100298,
            "count": 1,
            "name": "Carlton Van Wyk"
          },
          {
            "id": 100855,
            "count": 1,
            "name": "Gregory Winter"
          },
          {
            "id": 100966,
            "count": 1,
            "name": "Impundulu"
          },
          {
            "id": 101250,
            "count": 1,
            "name": "Muddled Vampire Hunter"
          },
          {
            "id": 101333,
            "count": 1,
            "name": "Ossian"
          },
          {
            "id": 101491,
            "count": 6,
            "name": "Procurer"
          },
          {
            "id": 102202,
            "count": 1,
            "name": "Young Bloods"
          }
        ]
      },
      {
        "type": "Equipment",
        "count": 9,
        "cards": [
          {
            "id": 100516,
            "count": 1,
            "name": "Deer Rifle"
          },
          {
            "id": 100745,
            "count": 8,
            "name": "Flash Grenade"
          }
        ]
      },
      {
        "type": "Action Modifier",
        "count": 19,
        "cards": [
          {
            "id": 100362,
            "count": 6,
            "name": "Cloak the Gathering"
          },
          {
            "id": 100401,
            "count": 7,
            "name": "Conditioning"
          },
          {
            "id": 101125,
            "count": 2,
            "name": "Lost in Crowds"
          },
          {
            "id": 102097,
            "count": 4,
            "name": "Veil the Legions"
          }
        ]
      },
      {
        "type": "Reaction",
        "count": 16,
        "cards": [
          {
            "id": 100518,
            "count": 7,
            "name": "Deflection"
          },
          {
            "id": 100519,
            "count": 2,
            "name": "Delaying Tactics"
          },
          {
            "id": 101321,
            "count": 7,
            "name": "On the Qui Vive"
          }
        ]
      },
      {
        "type": "Combat",
        "count": 8,
        "cards": [
          {
            "id": 100392,
            "count": 8,
            "name": "Concealed Weapon"
          }
        ]
      },
      {
        "type": "Event",
        "count": 4,
        "cards": [
          {
            "id": 100709,
            "count": 1,
            "name": "FBI Special Affairs Division"
          },
          {
            "id": 100944,
            "count": 1,
            "name": "Hunger Moon"
          },
          {
            "id": 101614,
            "count": 1,
            "name": "Restricted Vitae"
          },
          {
            "id": 102079,
            "count": 1,
            "name": "The Unmasking"
          }
        ]
      }
    ]
  }
}"""
    )

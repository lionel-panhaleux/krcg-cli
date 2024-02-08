from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute(["deck", "foobar"])
    outerr = capsys.readouterr()
    assert outerr.err == '"foobar" did not match a deck #, card or author'
    assert outerr.out == ""

    cli_execute(["deck", "2010tcdbng"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """[2010tcdbng     ]===================================================
Trading Card Day
Bad Nauheim, Germany
May 8th 2010
2R+F
10 players
Rudolf Scholz

-- +4

Deck Name: The Storage Procurers

Description: Allies with Flash Grenades to keep troubles at bay.
Storage Annex for card efficiency and a structured hand. Weenies and
Midcaps with Obfuscate and/or Dominate to oust via Conditionings and
Deflections.

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
6x Storage Annex           -- great card! usually underestimated
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
8x Flash Grenade           -- brings fear to the methuselahs rather than to minions

Action Modifier (19)
6x Cloak the Gathering
7x Conditioning            -- should be more!
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
"""  # noqa: E501
    )
    cli_execute(
        [
            "deck",
            "--from",
            "2019-01-01",
            "--to",
            "2020-01-01",
            "--players",
            "25",
            "Fame",
        ]
    )
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """-- 4 decks --
[2019pncwp] Anson Ashurs
[2019ecwon2pf] None
[2019ecday2pf] Finnish Politics
[2019ptfplpp] Amiable Jacko and friends
"""
    )
    cli_execute(["deck", "--to", "2020-01-01", "Rudolf Scholz"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """-- 11 decks --
[2k8madhanau] Thank You Vlada
[2010dorkside] New Days, Old School
[2010tcdbng] The Storage Procurers
[2011pombmg] Announce your PRE
[2012dnccd] Anson will find the Danish throne
[2013dnccd] Obey the Tremere
[2013fcqf14pf] Maris et Lutz à Paris
[2015gitamv2bng] Anson reloaded
[2017gecqgitamv4bng] German ECQ 2017 (1st place): Matasuntha's unbound heart
[2018dnccd] Danish Nationals 2018 (1st Place): Supply and Demand
[2019bfbafg] Swedish Legionnaires
"""
    )
    cli_execute(
        [
            "deck",
            "--from",
            "2018",
            "--to",
            "2019",
            "--players",
            "50",
        ]
    )
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """-- 5 decks --
[2018igpadhs] None
[2018eclcqwp] Dear diary, today I feel like a wraith.. Liquidation
[2018ecday1wp] MMA.MPA (EC 2018)
[2018ecday2wp] EC 2018 win
[2018pncwp] Deadly kittens
"""
    )

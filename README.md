# KRCG CLI

[![PyPI version](https://badge.fury.io/py/krcg-cli.svg)](https://badge.fury.io/py/krcg-cli)
[![Validation](https://github.com/lionel-panhaleux/krcg-cli/actions/workflows/validation.yml/badge.svg)](https://github.com/lionel-panhaleux/krcg-cli/actions/workflows/validation.yml)
[![Python version](https://img.shields.io/badge/python-3.11-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-black-black)](https://github.com/psf/black)

CLI tool for V:tES, using
the VEKN [official card texts](http://www.vekn.net/card-lists),
the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm) and
[KRCG](https://github.com/lionel-panhaleux/krcg) rulings list.

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](dark-pack.png)

## Install

You need to have [Python 3](https://www.python.org) installed on your system.
`krcg-cli` is a standard Python package, you can install it using `pip`:

```bash
pip install krcg-cli
```

## Usage

An internet connection is required to initialize krcg with official VEKN data
(cards list and TWDA):

Use the help command for a full documentation of the tool:

```bash
krcg --help
```

And also extensive help on each sub-command:

```bash
krcg [COMMAND] --help
```

## Contribute

**Contributions are welcome !**

This CLI is an offspring of the [KRCG](https://github.com/lionel-panhaleux/krcg)
python package, so please refer to that repository for issues, discussions
and contributions guidelines.

## Examples

Get a card text (case is not relevant, some abbreviations / misspellings are understood):

```bash
$ krcg card krcg
KRCG News Radio
[Master][2P] -- (#101067)
Unique location.
Lock to give a minion you control +1 intercept.
Lock and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.
```

This provides rulings, if any:

```bash
$ krcg card ".44 magnum"
.44 Magnum
[Equipment][2P] -- (#100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]
```

Use the `-l` option to get ruling links:

```bash
$ krcg card -l ".44 magnum"
.44 Magnum
[Equipment][2P] -- (#100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only ony maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]
[LSJ 19980302-2]: https://groups.google.com/d/msg/rec.games.trading-cards.jyhad/9YVFkeiL3Js/4UZXMyicluwJ
[LSJ 20021028]: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/g0GGiVIxyis/m/35WA-O9XrroJ
```

Search for cards matching a number of criteria

```bash
$ krcg search --type reaction --trait "Black Hand"
Follow the Blood
Ministry
Truth in Ink
Watch Commander
```

Search for specific card text

```bash
$ krcg search --text "this equipment card represents a location"
Catacombs
Dartmoor, England
Inveraray, Scotland
Living Manse
Local 1111
Lyndhurst Estate, New York
Palatial Estate
Pier 13, Port of Baltimore
Ruins of Ceoris
Ruins of Villers Abbey, Belgium
...
```

Search cards by artist

```bash
$ krcg search --artist "Ron Spencer"
Antediluvian Awakening
Arcanum Investigator
Bang Nakh — Tiger's Claws
Bauble
Blessing of Durga Syn
Blood Agony
Blood Shield
Blood Tears of Kephran
Bonecraft
Brass Knuckles
...
```

Search cards by set

```bash
$ krcg search --set "Black Hand"
Abyssal Hunter
Acrobatics
Alpha Glint
Amaranth
Ambush
Ana Rita Montaña
Animal Magnetism
...
```

List TWDA decks containing a card:

```bash
$ krcg deck "Fame"
-- 572 decks --
[steveholmer] Weenies with Blazing Guns
[portoct99] None
[rtpa2] " I'll be your dog"
[rtpa2k] ' I'll be your dog !'
[valentine] None
[normbsl] Who sez guns don't win?
[kotb] Kiss of the Brujah
...
```

Display any TWDA deck:

```bash
$ krcg deck 2016gncbg
[2016gncbg      ]===================================================
German NC 2016
Bochum, Germany
December 3rd 2016
3R+F
19 players
Bram van Stappen

-- 2gw6.5 + 1.5vp in the final

Deck Name: weenie animalism minimal: "Ich bin eine von wir"

played (untested) at the German Nationals 03.12.2016, Bochum

Crypt (12 cards, min=8, max=21, avg=3.75)
-----------------------------------------
2x Stick                3 ANI                      Nosferatu antitribu:4
1x Janey Pickman        6 ANI PRO for              Gangrel antitribu:4
1x Céleste Lamontagne   5 ANI PRO for              Gangrel antitribu:4
1x Effie Lowery         5 ANI SPI obf              Ahrimane:4
1x Sahana               5 ANI pre pro spi          Ahrimane:4
1x Yuri Kerezenski      5 ANI aus for vic  bishop  Tzimisce:4
1x Beetleman            4 ANI obf                  Nosferatu:4
1x Bobby Lemon          4 ANI pro                  Gangrel:3
1x Mouse                2 ani                      Nosferatu:3
1x Zip                  2 ani                      Ravnos:3
1x Lisa Noble           1 ani                      Caitiff:3

Library (90 cards)
Master (12)
5x Blood Doll
1x Direct Intervention
1x Fame
1x KRCG News Radio
1x Pentex(TM) Subversion
2x Powerbase: Montreal
1x Rack, The

Action (14)
2x Abbot
1x Aranthebes, The Immortal
1x Army of Rats
10x Deep Song

Equipment (1)
1x Sniper Rifle

Retainer (7)
1x Mr. Winthrop
6x Raven Spy

Reaction (18)
5x Cats' Guidance
3x Delaying Tactics
4x Forced Awakening
5x On the Qui Vive
1x Wake with Evening's Freshness

Combat (38)
16x Aid from Bats
2x Canine Horde
11x Carrion Crows
1x Pack Alpha
6x Taste of Vitae
2x Terror Frenzy
```

Display all decks that won a tournament of 50 players or more in 2018:

```bash
$ krcg deck --players 50 --from 2018 --to 2019
-- 5 decks --
[2018igpadhs] None
[2018eclcqwp] Dear diary, today I feel like a wraith.. Liquidation
[2018ecday1wp] MMA.MPA (EC 2018)
[2018ecday2wp] EC 2018 win
[2018pncwp] Deadly kittens
```

Display all winning decks for a given player:

```bash
krcg deck "Ben Peal"
-- 35 decks --
[dragoncon99] None
[benrcp2k] Wonderwall
[newjerseycc] Short Leash Bleed
[aftermath] None
...
```

List cards most associated with a given card in TWD:

```bash
$ krcg affinity "Fame"
Taste of Vitae                 (in 57% of decks, typically 3-6 copies)
Delaying Tactics               (in 33% of decks, typically 1-3 copies)
Dragonbound                    (in 32% of decks, typically 1 copy)
Powerbase: Montreal            (in 31% of decks, typically 1 copy)
Immortal Grapple               (in 28% of decks, typically 6-11 copies)
Carrion Crows                  (in 28% of decks, typically 6-11 copies)
Haven Uncovered                (in 27% of decks, typically 1-4 copies)
Carlton Van Wyk                (in 27% of decks, typically 1 copy)
Bum's Rush                     (in 27% of decks, typically 1-8 copies)
```

List most played cards of a given type, clan or discipline:

```bash
$ krcg top -d ani
Carrion Crows                  (played in 346 decks, typically 5-10 copies)
Cats' Guidance                 (played in 328 decks, typically 2-6 copies)
Raven Spy                      (played in 279 decks, typically 1-6 copies)
Canine Horde                   (played in 247 decks, typically 1-3 copies)
Army of Rats                   (played in 211 decks, typically 1-2 copies)
Aid from Bats                  (played in 204 decks, typically 5-14 copies)
Deep Song                      (played in 195 decks, typically 3-10 copies)
Sense the Savage Way           (played in 171 decks, typically 2-6 copies)
Guard Dogs                     (played in 119 decks, typically 1-4 copies)
Nana Buruku                    (played in 93 decks, typically 2-4 copies)
```

Build a deck from any given cards based on TWDA:

```bash
$ krcg build "Fame" "Carrion Crows"
Created by: KRCG

Inspired by:
 - 2020mdmlf            Nanarch Buruku
 - 2019r6vh             Aksinya+Nana+Anarch+Ani 4.0
 - 2019bncfb            Resistência Anarch
...

Crypt (12 cards, min=4, max=29, avg=4.08)
-----------------------------------------
1x Stick                3 ANI            Nosferatu antitribu:4
1x Beetleman            4 ANI obf        Nosferatu:4
1x Bobby Lemon          4 ANI pro        Gangrel:3
3x Nana Buruku          8 ANI POT PRE    Guruhi:4
1x Céleste Lamontagne   5 ANI PRO for    Gangrel antitribu:4
1x Petra                5 ANI OBF aus    Nosferatu:4
4x Anarch Convert       1 -none-         Caitiff:ANY

Library (90 cards)
Master (30; 4 trifle)
7x Anarch Revolt
1x Archon Investigation
8x Ashur Tablets
1x Direct Intervention
2x Dreams of the Sphinx
1x Fame
2x Haven Uncovered
3x Liquidation
1x Pentex(TM) Subversion
3x Vessel
1x Wider View

Action (11)
1x Army of Rats
10x Deep Song

Retainer (4)
4x Raven Spy

Reaction (9)
4x Cats' Guidance
2x Delaying Tactics
3x On the Qui Vive

Combat (36)
13x Aid from Bats
2x Canine Horde
10x Carrion Crows
4x Target Vitals
4x Taste of Vitae
3x Terror Frenzy
```

Format a decklist into another format - also note that krcg commands can be piped.

```bash
krcg deck 2016gncbg | krcg format -f lackey > 2016gncbg.txt
```

Compute an optimal tournament seating

```bash
$ krcg seating -v 16
8,2,12,15,7,14,9,13,6,16,1,3,10,4,5,11
15,6,10,14,11,7,8,1,4,13,16,2,12,9,3,5
2,5,7,6,14,3,4,8,16,15,11,9,1,10,13,12
--------------------------------- details ---------------------------------
Round 1: [[8, 2, 12, 15], [7, 14, 9, 13], [6, 16, 1, 3], [10, 4, 5, 11]]
Round 2: [[15, 6, 10, 14], [11, 7, 8, 1], [4, 13, 16, 2], [12, 9, 3, 5]]
Round 3: [[2, 5, 7, 6], [14, 3, 4, 8], [16, 15, 11, 9], [1, 10, 13, 12]]
R1   0.00  OK (predator-prey)
R2   0.00  OK (opponent thrice)
R3   0.00  OK (available vps)
R4   0.00  OK (opponent twice)
R5   0.00  OK (fifth seat)
R6   0.00  OK (position)
R7   0.00  OK (same seat)
R8   1.12 NOK (starting transfers): mean is 7.50, [4, 7, 10, 16] have 6, [3, 5, 9, 13] have 9
R9   0.00  OK (position group)
```

You can also compute a modified seating if players leave early or arrive late.
For example, to remove player 6 and 9 and add player 18 in round 2, just list round 1
as played and add and remove players as needed.

```bash
$ krcg seating -p 8,2,12,15,7,14,9,13,6,16,1,3,10,4,5,11 --remove 6 9 --add 18 -v
8,2,12,15,7,14,9,13,6,16,1,3,10,4,5,11
11,1,15,7,12,5,18,13,16,2,14,3,4,8,10
15,11,16,5,14,2,13,8,1,4,18,12,3,10,7
--------------------------------- details ---------------------------------
Round 1: [[8, 2, 12, 15], [7, 14, 9, 13], [6, 16, 1, 3], [10, 4, 5, 11]]
Round 2: [[11, 1, 15, 7, 12], [5, 18, 13, 16, 2], [14, 3, 4, 8, 10]]
Round 3: [[15, 11, 16, 5, 14], [2, 13, 8, 1, 4], [18, 12, 3, 10, 7]]
R1   0.00  OK (predator-prey)
R2   0.00  OK (opponent thrice)
R3   0.00  OK (available vps)
R4  10.00 NOK (opponent twice): 2-8, 2-13, 3-10, 4-8, 4-10, 5-11, 5-16, 7-12, 11-15, 12-15
R5   0.00  OK (fifth seat)
R6   0.00  OK (position)
R7   0.00  OK (same seat)
R8   0.81 NOK (starting transfers): mean is 8.36, [2, 11, 14] have 7, [1, 3, 4, 7, 10, 12, 13, 16] have 9
R9   0.00  OK (position group)
```

Note that removed and added players are not considered in vps and transfers rules (R3, R8)

# KRCG CLI

[![PyPI version](https://badge.fury.io/py/krcg-cli.svg)](https://badge.fury.io/py/krcg-cli)
[![Validation](https://github.com/lionel-panhaleux/krcg-cli/actions/workflows/validation.yml/badge.svg)](https://github.com/lionel-panhaleux/krcg-cli/actions/workflows/validation.yml)
[![Python version](https://img.shields.io/badge/python-3.14-blue)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/License-MIT-blue)](https://opensource.org/licenses/MIT)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-black)](https://github.com/astral-sh/ruff)

CLI tool for V:tES, using
the VEKN [official card texts](http://www.vekn.net/card-lists),
the [Tournament Winning Deck Archive (TWDA)](http://www.vekn.fr/decks/twd.htm) and
[KRCG](https://github.com/lionel-panhaleux/krcg) rulings list.

Portions of the materials are the copyrights and trademarks of Paradox Interactive AB,
and are used with permission. All rights reserved.
For more information please visit [white-wolf.com](http://www.white-wolf.com).

![Dark Pack](dark-pack.png)

## Install

You need to have [Python 3.14+](https://www.python.org) installed on your system.
`krcg-cli` is a standard Python package, you can install it using `pip`
or, better, [uv](https://github.com/astral-sh/uv):

```bash
uv tool install krcg-cli
```

## Usage

The official VEKN data (cards list, rulings and TWDA) ships with the tool,
so it works offline: upgrade to get fresher data. Only the `--price` option
of the `card` and `top` commands needs an internet connection.

Use the help command for a full documentation of the tool:

```bash
krcg --help
```

And also extensive help on each sub-command:

```bash
krcg [COMMAND] --help
```

Available subcommands:

- `card`: show cards
- `complete`: card name completion
- `search`: search card
- `deck`: show TWDA decks
- `top`: display top cards (most played)
- `affinity`: display cards affinity (most played together)
- `build`: build a deck around given card(s), based on the TWDA
- `format`: format a decklist
- `seating`: compute optimal seating
- `stats`: compute stats on a deck archive
- `twd`: display TWD statistics

Common filters and options:

- TWDA filters (`deck`, `top`, `affinity`, `build`, `stats`, `twd`):
  - `--from YYYY[-MM[-DD]]`: only consider decks from that date
  - `--to YYYY[-MM[-DD]]`: only consider decks up to that date
  - `--players N`: only consider tournaments with at least N players
- Card filters (`search`, `top`):
  - `-d/--discipline`, `-c/--clan`, `-t/--type`, `-g/--group`,
    `-x/--exclude-set`, `-e/--exclude-type`, `-b/--bonus`, `--text ...`,
    `--trait`, `--capacity`, `--set`, `--sect`, `--title`, `--city`,
    `--rarity`, `--precon`, `--artist`, `--no-reprint`
  - sets are given by name or code (`--set "Black Hand"` or `--set BH`),
    `--no-reprint` filters out the cards currently in print
- Output options:
  - `card`: `--international`, `--short`, `--text`, `--links`, `--krcg`, `--price`
  - `top`: `-n/--number`, `--output [human|full|csv]`, `--price`
  - `deck`: `-f/--full` to always display the full decklists
  - `format`: `-f/--format [jol|twd|lackey|json]` (reads stdin if no file is given)
  - `seating`: `--archon` (tab-separated, Archon-compatible), `-o FILE`,
    `-r/--rounds`, `-i/--iterations`, `-v/--verbose`

## Contribute

**Contributions are welcome !**

This CLI is an offspring of the [KRCG](https://github.com/lionel-panhaleux/krcg)
python package, so please refer to that repository for issues, discussions
and contributions guidelines.

Development uses [uv](https://github.com/astral-sh/uv) and
[just](https://github.com/casey/just): `uv sync --group dev`, then `just test`.
See [CLAUDE.md](CLAUDE.md) for the code layout and conventions.

## Examples

Get a card text (case is not relevant, some abbreviations / misspellings are understood):

```bash
$ krcg card krcg
KRCG News Radio
[Master][2P] -- (#101067)
Unique location.
You can lock this card to give a minion you control +1 intercept. You can lock this card and burn 1 pool to give a minion controlled by another Methuselah +1 intercept.

-- Rulings
Sequencing rules apply. You must gain the impulse to be able to use the reaction, or use the effect (whichever is applicable).  Other Methuselahs must declare block attempts (or not) and pass the impulse to you as normal. [ANK 20200607]
```

This provides rulings, if any:

```bash
$ krcg card ".44 magnum"
.44 Magnum
[Equipment][2P] -- (#100001)
Weapon: gun.
Strike: 2R damage, with 1 optional maneuver each combat.

-- Rulings
Provides only one maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
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
Provides only one maneuver each combat, even if the bearer changes. [LSJ 19980302-2]
The optional maneuver cannot be used if the strike cannot be used (eg. {Hidden Lurker}). [LSJ 20021028]

-- Rulings references
LSJ 19980302-2: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/9YVFkeiL3Js/m/4UZXMyicluwJ
LSJ 20021028: https://groups.google.com/g/rec.games.trading-cards.jyhad/c/g0GGiVIxyis/m/35WA-O9XrroJ
```

Other useful flags for cards:

```bash
# Translations alongside the English text
$ krcg card --international ".44 Magnum"

# Only the card name (useful when piping)
$ krcg card --short Alastor

# Only the card rules text, without rulings
$ krcg card --text Alastor

# KRCG export format (id|name)
$ krcg card --krcg Alastor
```

The `--price` option adds the price on the secondary market
(cheapest printing in stock on [Card Game Geek](https://shop.cardgamegeek.com)):

```bash
$ krcg card --price Alastor
€ 9.00 Alastor
[Political Action] -- (#100038)
...
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
Local 1111
Lyndhurst Estate, New York
Palatial Estate
Pier 13, Port of Baltimore
Ruins of Ceoris
Ruins of Villers Abbey, Belgium
Sacré-Cœur Cathedral, France
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
Apportation
...
```

Tip: use `-n/--number` to control how many results are printed, and
`--no-reprint`, `--exclude-type`, or `--exclude-set` to refine the pool.

Autocomplete a card name

```bash
$ krcg complete Pentex
Pentex™ Subversion
Pentex™ Loves You!
Enzo Giovanni, Pentex Board of Directors
Enzo Giovanni, Pentex Board of Directors (ADV)
Harold Zettler, Pentex Director
```

List TWDA decks containing a card:

```bash
$ krcg deck "Fame"
-- 834 decks --
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
Bram Van Stappen
https://www.vekn.net/event-calendar/event/8345

-- 2GW6.5+1.5!

Deck Name: weenie Animalism minimal: "Ich bin eine von wir"

played (untested) at the German Nationals 03.12.2016, Bochum

Crypt (12 cards, min=8, max=21, avg=3.75)
-----------------------------------------
2x Stick               3  ANI                      Nosferatu antitribu:4
1x Janey Pickman       6  ANI PRO for              Gangrel antitribu:4
1x Céleste Lamontagne  5  ANI PRO for              Gangrel antitribu:4
1x Effie Lowery        5  ANI SPI obf              Ahrimane:4
1x Sahana              5  ANI pre pro spi          Ahrimane:4
1x Yuri Kerezenski     5  ANI aus for vic  bishop  Tzimisce:4
1x Beetleman           4  ANI obf                  Nosferatu:4
1x Bobby Lemon         4  ANI pro                  Gangrel:3
1x Mouse               2  ani                      Nosferatu:3
1x Zip                 2  ani                      Ravnos:3
1x Lisa Noble          1  ani                      Caitiff:3

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
$ krcg deck "Ben Peal"
-- 37 decks --
[dragoncon99] None
[benrcp2k] Wonderwall
[newjerseycc] Short Leash Bleed
[aftermath] None
...
```

List cards most associated with a given card in TWD:

```bash
$ krcg affinity "Fame"
Taste of Vitae                 (in 59% of decks, typically 3-6 copies)
Powerbase: Montreal            (in 35% of decks, typically 1 copy)
Dragonbound                    (in 31% of decks, typically 1 copy)
Immortal Grapple               (in 30% of decks, typically 6-10 copies)
Carrion Crows                  (in 26% of decks, typically 5-11 copies)
Wider View                     (in 26% of decks, typically 1-2 copies)
Bum's Rush                     (in 25% of decks, typically 1-7 copies)
Haven Uncovered                (in 25% of decks, typically 1-4 copies)
```

List most played cards of a given type, clan or discipline:

```bash
$ krcg top -d ani
Carrion Crows                  (played in 443 decks, typically 5-10 copies)
Raven Spy                      (played in 432 decks, typically 1-5 copies)
Cats' Guidance                 (played in 404 decks, typically 2-6 copies)
Deep Song                      (played in 309 decks, typically 3-10 copies)
Army of Rats                   (played in 308 decks, typically 1-2 copies)
Canine Horde                   (played in 298 decks, typically 1-3 copies)
Aid from Bats                  (played in 248 decks, typically 5-14 copies)
Sense the Savage Way           (played in 239 decks, typically 2-7 copies)
Deep Ecology                   (played in 187 decks, typically 2-7 copies)
Kuyén                          (played in 181 decks, typically 1-2 copies)
```

Add the price on the secondary market, filter out cards currently in print:

```bash
$ krcg top --no-reprint --price -n 5
€ 0.80 Anthelios, The Red Star        (played in 322 decks, typically 1-2 copies)
€ 0.20 Bum's Rush                     (played in 320 decks, typically 1-7 copies)
€ 0.30 Canine Horde                   (played in 298 decks, typically 1-3 copies)
€45.00 Ossian                         (played in 295 decks, typically 1 copy)
€ 0.70 Effective Management           (played in 282 decks, typically 1-5 copies)
```

Build a deck from any given cards based on TWDA:

```bash
$ krcg build "Fame" "Carrion Crows"
Created by: KRCG

Inspired by:
 - 10491                O verdadeiro Anarch (Vitória para o Bruninho)
 - 2010arargs           Girls will find AIDS
 - 2010badiajune        CrewCuervos
 - 2010bfw              Nana and friends
 - 2010espoomq          (No Name)
 - 2010hungarianecq     Nana Buruku
 - 2010treatmentboston  Nana's Box of Firecrackers
 - 2011ccpdms           Me hago bicho bola
 - 2011fsmoscow         Been there, done that
 - 2011hncrkn           N.W.A
 - 2011pvpbs            Nana Buruku with ani weenies
 - 2011rog              Nana Buruku
 - 2012cbpf             (No Name)
 - 2012fsssh            N.W.A v1.1
 - 2012ncrkh            N.W.A v1.2
 - 2012qcfmf            So, it's a Girl, a bat and a crow...
 - 2013sacpgesb         Zoólogico 2013
 - 2013tsiems           Trolls Converters
 - 2014cfhspb           Zoologico 3 a Missão
 - 2014cnccb            Resistência Anarch
 - 2014dnccd            Sons of Anarchy
 - 2014gncmg            Welcome To The Jungle
 - 2014lfb              Resistência Anarch
 - 2015ce03fb           (No Name)
 - 2015fssiimb          Resistência Anarch
 - 2015pncap            Nana anarch, low crypt, Portuguese version
 - 2015saclcqfb         Cidade em Chamas
 - 2016ecqmmf           Weenie Animalism v1.2
 - 2016ncqmmf           New Nana (27)
 - 2016sncss            Vampire-SM 2016. Field Training Bats v.3
 - 2016wueiiisb         Bruninho (Crow)
 - 2017gracjf           Stolen Field Training Bats
 - 2018csmno            Nana superstar
 - 2018fnclf            Nana Toolbox
 - 2018lkpf             Crows and Bats
 - 2018ovaof            Nanarch Animalism
 - 2019bncfb            Resistência Anarch
 - 2019r6vh             Aksinya+Nana+Anarch+Ani 4.0
 - 2020bldfaca          Mono animalismo
 - 2020mdmlf            Nanarch Buruku
 - 2021zdco             “Subterfúgios” anarquistas mode on
 - 2k9blackplanet       Vår nya integrationsminister
 - 9115                 Nana ANI tablets
 - 9952                 Nanarch Buruku
Crypt (12 cards, min=4, max=29, avg=4.08)
-----------------------------------------
4x Anarch Convert      1  -none-       Caitiff:ANY
3x Nana Buruku         8  ANI POT PRE  Guruhi:4
1x Céleste Lamontagne  5  ANI PRO for  Gangrel antitribu:4
1x Petra               5  ANI OBF aus  Nosferatu:4
1x Beetleman           4  ANI obf      Nosferatu:4
1x Bobby Lemon         4  ANI pro      Gangrel:3
1x Stick               3  ANI          Nosferatu antitribu:4

Library (90 cards)
Master (29; 4 trifle)
7x Anarch Revolt
1x Archon Investigation
8x Ashur Tablets
1x Direct Intervention
2x Dreams of the Sphinx
1x Fame
2x Haven Uncovered
2x Liquidation
1x Pentex(TM) Subversion
3x Vessel
1x Wider View

Action (10)
10x Deep Song

Retainer (4)
4x Raven Spy

Reaction (9)
4x Cats' Guidance
2x Delaying Tactics
3x On the Qui Vive

Combat (38)
13x Aid from Bats
2x Canine Horde
10x Carrion Crows
2x Groundfighting
4x Target Vitals
4x Taste of Vitae
3x Terror Frenzy
```

Format a decklist into another format - also note that krcg commands can be piped.

```bash
krcg deck 2016gncbg | krcg format -f lackey > 2016gncbg.txt
# Supported formats: jol, twd, lackey, json
```

Compute an optimal tournament seating

```bash
$ krcg seating -v 16
1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16
2,16,5,9,3,15,10,6,7,12,1,14,8,11,4,13
14,8,2,10,6,9,13,1,15,4,12,5,11,7,16,3

------------------- details (16 players) -------------------
Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
Round 2: [[2, 16, 5, 9], [3, 15, 10, 6], [7, 12, 1, 14], [8, 11, 4, 13]]
Round 3: [[14, 8, 2, 10], [6, 9, 13, 1], [15, 4, 12, 5], [11, 7, 16, 3]]
R1   0.00  OK (predator-prey)
R2   0.00  OK (opponent thrice)
R3   0.00  OK (available vps)
R4   0.00  OK (opponent twice)
R5   0.00  OK (fifth seat)
R6   0.00  OK (position)
R7   0.00  OK (same seat)
R8   0.37 NOK (starting transfers): mean is 2.50, [2, 7, 11, 15] have 2.0, [4, 10, 12, 16] have 3.0
R9   0.00  OK (position group)
```

You can also compute a modified seating if players leave early or arrive late.
For example, to remove player 6 and 9 and add player 18 in round 2, just list round 1
as played and add and remove players as needed.

```bash
$ krcg seating -p 1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16 --remove 6 9 --add 18 -v
```

Note that removed and added players are not considered in vps and transfers rules (R3, R8).

For tournament management:

- Use `--archon` to output tab-separated, Archon-compatible seating (empty 5th seat in 4-player tables).
- Use `-o FILE` to append results to a file.

Display TWD statistics, a per-year breakdown of clans and disciplines:

```bash
$ krcg twd --from 2012 --to 2013

============================================================= 2012
------------------------------------------------ clans
Tremere	20/220 (9.1%)
Malkavian	19/220 (8.6%)
Tremere antitribu	16/220 (7.3%)
Giovanni	15/220 (6.8%)
Ventrue	15/220 (6.8%)
Toreador	15/220 (6.8%)
Baali	13/220 (5.9%)
Lasombra	12/220 (5.5%)
Gangrel antitribu	12/220 (5.5%)
```

Compute statistics on a deck archive, the TWDA or a local folder of decklists:

```bash
$ krcg stats --from 2024

AVERAGE METASCORE: 4.09

  Format: <rank>. <trend> <played> <score> (<norm>) [<diff>] <card name>
     - norm: vps / decks_having_it                  # use to compare cards
     - diff: (vps - average_vps) * decks_having_it  # how far from average

=============== Rankings ===============

------------ Played ------------
1. = 574 342GW2403.5 (4.19) [54.55] Villein 
2. = 461 274GW2000.0 (4.34) [112.96] Dreams of the Sphinx 
3. = 404 207GW1540.5 (3.81) [-115.12] On the Qui Vive 
4. = 351 232GW1619.5 (4.61) [180.78] Giant's Blood 
```

```bash
# On a local folder of .txt decklists
$ krcg stats -f ./my-decks
```

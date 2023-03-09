import collections
import functools
import pathlib
import re
from typing import Iterable

from krcg import analyzer
from krcg import deck

from . import _utils


def add_parser(parser):
    parser = parser.add_parser("stats", help="compute stats on a deck archive")
    parser.add_argument(
        "-f",
        "--folder",
        type=pathlib.Path,
        help="(Opt.) Folder containing the archive. If not set, use the TWDA",
    )
    _utils.add_twda_filters(parser)
    parser.set_defaults(func=stats)


FILTERS = {
    "Library": lambda c: c.library,
    "Crypt": lambda c: c.crypt,
    "Action": lambda c: "Action" in c.types,
    "Action Modifier": lambda c: "Action Modifier" in c.types,
    "Ally": lambda c: "Ally" in c.types,
    "Combat": lambda c: "Combat" in c.types,
    "Equipment": lambda c: "Equipment" in c.types,
    "Event": lambda c: "Event" in c.types,
    "Master": lambda c: "Master" in c.types,
    "Political Action": lambda c: "Political Action" in c.types,
    "Reaction": lambda c: "Reaction" in c.types,
    "Retainer": lambda c: "Retainer" in c.types,
}
DISCIPLINES = {
    "Abombwe": lambda c: c.library and {"abo", "ABO"} & set(c.disciplines),
    "Animalism": lambda c: c.library and {"ani", "ANI"} & set(c.disciplines),
    "Auspex": lambda c: c.library and {"aus", "AUS"} & set(c.disciplines),
    "Blood Sorcery": lambda c: c.library and {"tha", "THA"} & set(c.disciplines),
    "Celerity": lambda c: c.library and {"cel", "CEL"} & set(c.disciplines),
    "Chimerstry": lambda c: c.library and {"chi", "CHI"} & set(c.disciplines),
    "Daimonon": lambda c: c.library and {"dai", "DAI"} & set(c.disciplines),
    "Dementation": lambda c: c.library and {"dem", "DEM"} & set(c.disciplines),
    "Dominate": lambda c: c.library and {"dom", "DOM"} & set(c.disciplines),
    "Fortitude": lambda c: c.library and {"for", "FOR"} & set(c.disciplines),
    "Melpominee": lambda c: c.library and {"mel", "MEL"} & set(c.disciplines),
    "Mytherceria": lambda c: c.library and {"myt", "MYT"} & set(c.disciplines),
    "Necromancy": lambda c: c.library and {"nec", "NEC"} & set(c.disciplines),
    "Obeah": lambda c: c.library and {"obe", "OBE"} & set(c.disciplines),
    "Obfuscate": lambda c: c.library and {"obf", "OBF"} & set(c.disciplines),
    "Obtenebration": lambda c: c.library and {"obt", "OBT"} & set(c.disciplines),
    "Potence": lambda c: c.library and {"pot", "POT"} & set(c.disciplines),
    "Presence": lambda c: c.library and {"pre", "PRE"} & set(c.disciplines),
    "Protean": lambda c: c.library and {"pro", "PRO"} & set(c.disciplines),
    "Quietus": lambda c: c.library and {"qui", "QUI"} & set(c.disciplines),
    "Sanguinus": lambda c: c.library and {"san", "SAN"} & set(c.disciplines),
    "Serpentis": lambda c: c.library and {"ser", "SER"} & set(c.disciplines),
    "Spiritus": lambda c: c.library and {"spi", "SPI"} & set(c.disciplines),
    "Temporis": lambda c: c.library and {"tem", "TEM"} & set(c.disciplines),
    "Thanatosis": lambda c: c.library and {"thn", "THN"} & set(c.disciplines),
    "Valeren": lambda c: c.library and {"val", "VAL"} & set(c.disciplines),
    "Vicissitude": lambda c: c.library and {"vic", "VIC"} & set(c.disciplines),
    "Visceratika": lambda c: c.library and {"vis", "VIS"} & set(c.disciplines),
}
CLANS = {
    "Abomination": lambda c: "Abomination" in c.clans,
    "Ahrimane": lambda c: "Ahrimane" in c.clans,
    "Akunanse": lambda c: "Akunanse" in c.clans,
    "Avenger": lambda c: "Avenger" in c.clans,
    "Baali": lambda c: "Baali" in c.clans,
    "Banu Haqim": lambda c: "Banu Haqim" in c.clans,
    "Blood Brother": lambda c: "Blood Brother" in c.clans,
    "Brujah": lambda c: "Brujah" in c.clans,
    "Brujah antitribu": lambda c: "Brujah antitribu" in c.clans,
    "Caitiff": lambda c: "Caitiff" in c.clans,
    "Daughter of Cacophony": lambda c: "Daughter of Cacophony" in c.clans,
    "Gangrel": lambda c: "Gangrel" in c.clans,
    "Gangrel antitribu": lambda c: "Gangrel antitribu" in c.clans,
    "Gargoyle": lambda c: "Gargoyle" in c.clans,
    "Giovanni": lambda c: "Giovanni" in c.clans,
    "Guruhi": lambda c: "Guruhi" in c.clans,
    "Harbinger of Skulls": lambda c: "Harbinger of Skulls" in c.clans,
    "Ishtarri": lambda c: "Ishtarri" in c.clans,
    "Kiasyd": lambda c: "Kiasyd" in c.clans,
    "Lasombra": lambda c: "Lasombra" in c.clans,
    "Malkavian": lambda c: "Malkavian" in c.clans,
    "Malkavian antitribu": lambda c: "Malkavian antitribu" in c.clans,
    "Ministry": lambda c: "Ministry" in c.clans,
    "Nagaraja": lambda c: "Nagaraja" in c.clans,
    "Nosferatu": lambda c: "Nosferatu" in c.clans,
    "Nosferatu antitribu": lambda c: "Nosferatu antitribu" in c.clans,
    "Osebo": lambda c: "Osebo" in c.clans,
    "Pander": lambda c: "Pander" in c.clans,
    "Ravnos": lambda c: "Ravnos" in c.clans,
    "Salubri": lambda c: "Salubri" in c.clans,
    "Salubri antitribu": lambda c: "Salubri antitribu" in c.clans,
    "Samedi": lambda c: "Samedi" in c.clans,
    "Toreador": lambda c: "Toreador" in c.clans,
    "Toreador antitribu": lambda c: "Toreador antitribu" in c.clans,
    "Tremere": lambda c: "Tremere" in c.clans,
    "Tremere antitribu": lambda c: "Tremere antitribu" in c.clans,
    "True Brujah": lambda c: "True Brujah" in c.clans,
    "Tzimisce": lambda c: "Tzimisce" in c.clans,
    "Ventrue": lambda c: "Ventrue" in c.clans,
    "Ventrue antitribu": lambda c: "Ventrue antitribu" in c.clans,
}
FILTERS.update(DISCIPLINES)
FILTERS.update(CLANS)


@functools.total_ordering
class Score:
    def __init__(self, **kwargs):
        self.gw: int = int(kwargs.get("gw", 0))
        self.vp: float = float(kwargs.get("vp", 0))

    def __eq__(self, rhs):
        return (self.gw, self.vp) == (rhs.gw, rhs.vp)

    def __lt__(self, rhs):
        return (self.gw, self.vp) < (rhs.gw, rhs.vp)

    def __str__(self):
        return f"{self.gw}GW{self.vp}"

    def __add__(self, rhs):
        return self.__class__(gw=self.gw + rhs.gw, vp=self.vp + rhs.vp)

    def __iadd__(self, rhs):
        self.gw += rhs.gw
        self.vp += rhs.vp
        return self


def ranking(it: Iterable):
    rank, last_score = 0, None
    for i, (c, score) in enumerate(it, 1):
        if not last_score or score < last_score:
            rank = i
            last_score = score
        yield rank, c, score


def trend(upheaval_score):
    if upheaval_score > 20:
        return "↑"
    if upheaval_score < -60:
        return "↓"
    return "="


def stats(args):
    if args.folder:
        _utils._init(with_twda=False)
        decks = [deck.Deck.from_txt(f.open()) for f in args.folder.glob("*.txt")]
    else:
        _utils._init(with_twda=True)
        decks = _utils.filter_twda(args)
    A = analyzer.Analyzer(decks, spoilers=False)
    A.refresh()
    most_common = A.played.most_common()
    for dek in decks:
        match = re.search(
            r"(?P<gw>\d)\s*GW\s*(?P<vp>\d+)((\.|,)(?P<vp_frac>\d))?",
            dek.comments or "" if args.folder else "",
            re.MULTILINE,
        )
        if match:
            dek.score = Score(
                gw=int(match.group("gw")),
                vp=int(match.group("vp")) + int(match.group("vp_frac") or 0) / 10,
            )
        else:
            dek.score = Score()
    cards_score = collections.defaultdict(Score)
    for dek in decks:
        for card, _ in dek.cards():
            cards_score[card] += dek.score

    cards_score_list = sorted(cards_score.items(), key=lambda a: a[1], reverse=True)
    cards_norm_score_list = sorted(
        [
            (card, round(score.vp / A.played[card], 2))
            for card, score in cards_score.items()
        ],
        key=lambda a: a[1],
        reverse=True,
    )
    played_rank = {c: r for r, c, count in ranking(most_common) if count > 2}
    score_rank = {c: r for r, c, _score in ranking(cards_score_list)}
    cards_norm_score = dict(cards_norm_score_list)
    upheaval = {k: v - score_rank[k] for k, v in played_rank.items()}
    average_score = sum(d.score.vp for d in decks) / len(decks)
    cards_diff_score = {
        card: round((score - average_score) * A.played[card], 2)
        for card, score in cards_norm_score.items()
    }
    print()
    print(f"AVERAGE METASCORE: {round(average_score, 2)}")
    print()
    print("=============== Rankings ===============")
    print()
    print("------------ Played ------------")
    for r, c, count in ranking(most_common):
        print(
            f"{r}. {trend(upheaval.get(c, 0))} {count:0>2} {cards_score[c]} "
            f"({cards_norm_score[c]}) [{cards_diff_score[c]}] {c} "
        )
    print()
    print()
    print("------------ Score ------------")
    for r, c, score in ranking(cards_norm_score_list):
        if A.played[c] < 3:
            continue
        print(
            f"{r}. {trend(upheaval.get(c, 0))} {A.played[c]:0>2} {cards_score[c]} "
            f"({cards_norm_score[c]}) [{cards_diff_score[c]}] {c} "
        )
    print()
    if args.folder:
        print()
        print("=============== Upheaval ===============")
        print()
        upheaval_list = sorted(
            upheaval.items(),
            key=lambda a: a[1],
            reverse=True,
        )
        print("------------ Overperforming ------------")
        for i, (card, dif) in enumerate(upheaval_list):
            if dif < 20:
                break
            print(
                f"{i}. {card} has {dif} ranks more ({A.played[card]}: "
                f"{cards_norm_score[card]}) [{cards_diff_score[card]}]"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -60:
                break
            print(
                f"{i}. {card} has {-dif} ranks less ({A.played[card]}: "
                f"{cards_norm_score[card]}) [{cards_diff_score[card]}]"
            )
        print()
        print("=============== Diff to AVG ===============")
        print()
        upheaval_list = sorted(
            cards_diff_score.items(),
            key=lambda a: a[1],
            reverse=True,
        )
        print("------------ Overperforming ------------")
        for i, (card, dif) in enumerate(upheaval_list):
            if dif < 6:
                break
            print(
                f"{i}. {card} got {dif} more VPs than average ({A.played[card]}: "
                f"{cards_norm_score[card]})"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -5:
                break
            print(
                f"{i}. {card} has {-dif} less VPs than average ({A.played[card]}: "
                f"{cards_norm_score[card]})"
            )

    print()
    print("=============== Cards Statistics ===============")
    print()
    for name, condition in FILTERS.items():
        top = [c for c in most_common if condition(c[0])][:10]
        if len(top) < 3:
            continue
        if top[0][1] < 2:
            continue
        print(f"------------ {name} ------------")
        for rank, (card, count) in enumerate(top, 1):
            if count < 2:
                break
            print(
                f"{rank}. {card} – played in {count} decks, "
                f"{_utils.typical_copies(A, card)} – {cards_score[card]} "
                f"({cards_norm_score[card]}) [{cards_diff_score[card]}] "
                f"{trend(upheaval.get(card, 0))}"
            )
        print()

    print()
    print("=============== Collection Statistics ===============")
    print()
    print("------------ Disciplines ------------")
    proportions = sorted(
        [
            (
                len([d for d in decks if len(list(d.cards(condition))) > 5])
                / len(decks),
                name,
            )
            for name, condition in DISCIPLINES.items()
        ],
        reverse=True,
    )
    for p, name in proportions:
        if p < 0.005:
            break
        print(f"- {round(p*100)}% {name}")
    print()
    print("------------ Clans ------------")
    proportions = sorted(
        [
            (
                len([d for d in decks if len(list(d.cards(condition))) > 5])
                / len(decks),
                name,
            )
            for name, condition in CLANS.items()
        ],
        reverse=True,
    )
    for p, name in proportions:
        if p < 0.005:
            break
        print(f"- {round(p*100)}% {name}")
    print()

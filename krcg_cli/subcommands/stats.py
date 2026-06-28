"""Compute stats on a deck archive."""

import collections
import functools
import pathlib
import re
import sys
from typing import Iterable, TypeVar

from krcg import analyzer
from krcg import parser as krcg_parser
from krcg.models import Card

from . import _utils


def add_parser(parser):
    """Add parser for stats subcommand."""
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
    "Library": _utils.is_library,
    "Crypt": _utils.is_crypt,
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
#: Discipline display name -> level-agnostic trigram (as indexed on library cards).
_DISCIPLINE_TRIGRAMS = {
    "Abombwe": "abo",
    "Animalism": "ani",
    "Auspex": "aus",
    "Blood Sorcery": "tha",
    "Celerity": "cel",
    "Chimerstry": "chi",
    "Daimonon": "dai",
    "Dementation": "dem",
    "Dominate": "dom",
    "Fortitude": "for",
    "Melpominee": "mel",
    "Mytherceria": "myt",
    "Necromancy": "nec",
    "Obeah": "obe",
    "Obfuscate": "obf",
    "Obtenebration": "obt",
    "Potence": "pot",
    "Presence": "pre",
    "Protean": "pro",
    "Quietus": "qui",
    "Sanguinus": "san",
    "Serpentis": "ser",
    "Spiritus": "spi",
    "Temporis": "tem",
    "Thanatosis": "thn",
    "Valeren": "val",
    "Vicissitude": "vic",
    "Visceratika": "vis",
}
_CLANS = [
    "Abomination",
    "Ahrimane",
    "Akunanse",
    "Avenger",
    "Baali",
    "Banu Haqim",
    "Blood Brother",
    "Brujah",
    "Brujah antitribu",
    "Caitiff",
    "Daughter of Cacophony",
    "Gangrel",
    "Gangrel antitribu",
    "Gargoyle",
    "Giovanni",
    "Guruhi",
    "Harbinger of Skulls",
    "Ishtarri",
    "Kiasyd",
    "Lasombra",
    "Malkavian",
    "Malkavian antitribu",
    "Ministry",
    "Nagaraja",
    "Nosferatu",
    "Nosferatu antitribu",
    "Osebo",
    "Pander",
    "Ravnos",
    "Salubri",
    "Salubri antitribu",
    "Samedi",
    "Toreador",
    "Toreador antitribu",
    "Tremere",
    "Tremere antitribu",
    "True Brujah",
    "Tzimisce",
    "Ventrue",
    "Ventrue antitribu",
]


def _has_discipline(trigram):
    """Build a condition: a library card providing the given discipline."""
    return lambda c: _utils.is_library(c) and trigram in _utils.card_disciplines(c)


def _has_clan(clan):
    """Build a condition: a card of the given clan."""
    return lambda c: clan in _utils.card_clans(c)


DISCIPLINES = {
    name: _has_discipline(trigram) for name, trigram in _DISCIPLINE_TRIGRAMS.items()
}
CLANS = {name: _has_clan(name) for name in _CLANS}
FILTERS.update(DISCIPLINES)
FILTERS.update(CLANS)


@functools.total_ordering
class Score:
    """Score."""

    def __init__(self, **kwargs):
        """Initialize score."""
        self.gw: int = int(kwargs.get("gw", 0))
        self.vp: float = float(kwargs.get("vp", 0))

    def __eq__(self, rhs):
        """Compare scores."""
        return (self.gw, self.vp) == (rhs.gw, rhs.vp)

    def __lt__(self, rhs):
        """Compare scores."""
        return (self.gw, self.vp) < (rhs.gw, rhs.vp)

    def __str__(self):
        """String representation."""
        return f"{self.gw}GW{self.vp}"

    def __add__(self, rhs):
        """Add scores."""
        return self.__class__(gw=self.gw + rhs.gw, vp=self.vp + rhs.vp)

    def __iadd__(self, rhs):
        """Add scores."""
        self.gw += rhs.gw
        self.vp += rhs.vp
        return self


T = TypeVar("T", bound=int | float | Score)


def ranking(
    it: Iterable[tuple[Card, T]],
) -> Iterable[tuple[int, Card, T]]:
    """Ranking."""
    rank: int = 0
    last_score: T | None = None
    for i, (c, score) in enumerate(it, 1):
        if not last_score or score < last_score:
            rank = i
            last_score = score
        yield rank, c, score


def trend(upheaval_score: int) -> str:
    """Trend for the card score."""
    if upheaval_score > 20:
        return "↑"
    if upheaval_score < -60:
        return "↓"
    return "="


def _deck_score(deck, from_comment: bool) -> Score:
    """Resolve a deck's tournament Score (from its result or its comment)."""
    if deck.score:
        return Score(
            gw=int(deck.score.round_gw or 0),
            vp=float(deck.score.round_vp or 0) + float(deck.score.finals_vp or 0),
        )
    match = re.search(
        r"(?P<gw>\d)\s*GW\s*(?P<vp>\d+)((\.|,)(?P<vp_frac>\d))?",
        deck.comment or "" if from_comment else "",
        re.MULTILINE,
    )
    if match:
        return Score(
            gw=int(match.group("gw")),
            vp=int(match.group("vp")) + int(match.group("vp_frac") or 0) / 10,
        )
    return Score()


def stats(args):
    """Compute stats on a deck archive."""
    if args.folder:
        _utils._init(with_twda=False)
        decks = [
            krcg_parser.deck_from_txt(f.open(), _utils.VTES)
            for f in args.folder.glob("*.txt")
        ]
    else:
        _utils._init(with_twda=True)
        decks = _utils.filter_twda(args)
    if not decks:
        print("No deck in the archive matches the given filters", file=sys.stderr)
        return 1
    played = analyzer.played(decks, _utils.VTES)
    deck_stats = analyzer.stats(decks, _utils.VTES)
    most_common = played.most_common()
    scores = [_deck_score(dek, bool(args.folder)) for dek in decks]
    cards_score: dict[Card, Score] = collections.defaultdict(Score)
    for dek, score in zip(decks, scores):
        for card, _ in _utils.deck_cards(dek):
            cards_score[card] += score

    cards_score_list = sorted(cards_score.items(), key=lambda a: a[1], reverse=True)
    cards_norm_score_list = sorted(
        [
            (card, round(score.vp / played[card], 2))
            for card, score in cards_score.items()
        ],
        key=lambda a: a[1],
        reverse=True,
    )
    played_rank = {c: r for r, c, count in ranking(most_common) if count > 2}
    score_rank = {c: r for r, c, _score in ranking(cards_score_list)}
    cards_norm_score = dict(cards_norm_score_list)
    upheaval = {k: v - score_rank[k] for k, v in played_rank.items()}
    average_score = sum(s.vp for s in scores) / len(decks)
    cards_diff_score = {
        card: round((score - average_score) * played[card], 2)
        for card, score in cards_norm_score.items()
    }
    print()
    print(f"AVERAGE METASCORE: {round(average_score, 2)}")
    print()
    print("  Format: <rank>. <trend> <played> <score> (<norm>) [<diff>] <card name>")
    print("     - norm: vps / decks_having_it                  # use to compare cards")
    print("     - diff: (vps - average_vps) * decks_having_it  # how far from average")
    print()
    print("=============== Rankings ===============")
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
        if played[c] < 3:
            continue
        print(
            f"{r}. {trend(upheaval.get(c, 0))} {played[c]:0>2} {cards_score[c]} "
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
                f"{i}. {card} has {dif} ranks more ({played[card]}: "
                f"{cards_norm_score[card]}) [{cards_diff_score[card]}]"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -60:
                break
            print(
                f"{i}. {card} has {-dif} ranks less ({played[card]}: "
                f"{cards_norm_score[card]}) [{cards_diff_score[card]}]"
            )
        print()
        print("=============== Diff to AVG ===============")
        print()
        diff_upheaval_list = sorted(
            cards_diff_score.items(),
            key=lambda a: a[1],
            reverse=True,
        )
        print("------------ Overperforming ------------")
        for i, (card, dif_float) in enumerate(diff_upheaval_list):
            if dif_float < 6:
                break
            print(
                f"{i}. {card} got {dif_float} more VPs than average ({played[card]}: "
                f"{cards_norm_score[card]})"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -5:
                break
            print(
                f"{i}. {card} has {-dif} less VPs than average ({played[card]}: "
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
                f"{_utils.typical_copies(deck_stats, card)} – {cards_score[card]} "
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
                len(
                    [d for d in decks if len(list(_utils.deck_cards(d, condition))) > 5]
                )
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
        print(f"- {round(p * 100)}% {name}")
    print()
    print("------------ Clans ------------")
    proportions = sorted(
        [
            (
                len(
                    [d for d in decks if len(list(_utils.deck_cards(d, condition))) > 5]
                )
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
        print(f"- {round(p * 100)}% {name}")
    print()

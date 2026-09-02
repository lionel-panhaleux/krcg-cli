import collections
import functools
import pathlib
import re
from collections.abc import Iterable

from krcg import analyzer
from krcg import models
from krcg import parser as krcg_parser

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


def _is_library(card: models.Card) -> bool:
    return card.kind == models.Card.Kind.LIBRARY


def _has_discipline(card: models.Card, trigram: str) -> bool:
    return (
        isinstance(card, models.LibraryCard)
        and card.discipline_requirement is not None
        and trigram in card.discipline_requirement.disciplines
    )


def _clans(card: models.Card) -> list[str]:
    if isinstance(card, models.CryptCard):
        return [card.clan] if card.clan else []
    if isinstance(card, models.LibraryCard):
        return card.clan_requirement
    return []


FILTERS = {
    "Library": _is_library,
    "Crypt": lambda c: c.kind == models.Card.Kind.CRYPT,
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
    "Abombwe": functools.partial(_has_discipline, trigram="abo"),
    "Animalism": functools.partial(_has_discipline, trigram="ani"),
    "Auspex": functools.partial(_has_discipline, trigram="aus"),
    "Blood Sorcery": functools.partial(_has_discipline, trigram="tha"),
    "Celerity": functools.partial(_has_discipline, trigram="cel"),
    "Chimerstry": functools.partial(_has_discipline, trigram="chi"),
    "Daimonon": functools.partial(_has_discipline, trigram="dai"),
    "Dementation": functools.partial(_has_discipline, trigram="dem"),
    "Dominate": functools.partial(_has_discipline, trigram="dom"),
    "Fortitude": functools.partial(_has_discipline, trigram="for"),
    "Melpominee": functools.partial(_has_discipline, trigram="mel"),
    "Mytherceria": functools.partial(_has_discipline, trigram="myt"),
    "Necromancy": functools.partial(_has_discipline, trigram="nec"),
    "Obeah": functools.partial(_has_discipline, trigram="obe"),
    "Obfuscate": functools.partial(_has_discipline, trigram="obf"),
    "Obtenebration": functools.partial(_has_discipline, trigram="obt"),
    "Potence": functools.partial(_has_discipline, trigram="pot"),
    "Presence": functools.partial(_has_discipline, trigram="pre"),
    "Protean": functools.partial(_has_discipline, trigram="pro"),
    "Quietus": functools.partial(_has_discipline, trigram="qui"),
    "Sanguinus": functools.partial(_has_discipline, trigram="san"),
    "Serpentis": functools.partial(_has_discipline, trigram="ser"),
    "Spiritus": functools.partial(_has_discipline, trigram="spi"),
    "Temporis": functools.partial(_has_discipline, trigram="tem"),
    "Thanatosis": functools.partial(_has_discipline, trigram="thn"),
    "Valeren": functools.partial(_has_discipline, trigram="val"),
    "Vicissitude": functools.partial(_has_discipline, trigram="vic"),
    "Visceratika": functools.partial(_has_discipline, trigram="vis"),
}
CLANS = {
    "Abomination": lambda c, clan="Abomination": clan in _clans(c),
    "Ahrimane": lambda c, clan="Ahrimane": clan in _clans(c),
    "Akunanse": lambda c, clan="Akunanse": clan in _clans(c),
    "Avenger": lambda c, clan="Avenger": clan in _clans(c),
    "Baali": lambda c, clan="Baali": clan in _clans(c),
    "Banu Haqim": lambda c, clan="Banu Haqim": clan in _clans(c),
    "Blood Brother": lambda c, clan="Blood Brother": clan in _clans(c),
    "Brujah": lambda c, clan="Brujah": clan in _clans(c),
    "Brujah antitribu": lambda c, clan="Brujah antitribu": clan in _clans(c),
    "Caitiff": lambda c, clan="Caitiff": clan in _clans(c),
    "Daughter of Cacophony": lambda c, clan="Daughter of Cacophony": clan in _clans(c),
    "Gangrel": lambda c, clan="Gangrel": clan in _clans(c),
    "Gangrel antitribu": lambda c, clan="Gangrel antitribu": clan in _clans(c),
    "Gargoyle": lambda c, clan="Gargoyle": clan in _clans(c),
    "Giovanni": lambda c, clan="Giovanni": clan in _clans(c),
    "Guruhi": lambda c, clan="Guruhi": clan in _clans(c),
    "Harbinger of Skulls": lambda c, clan="Harbinger of Skulls": clan in _clans(c),
    "Ishtarri": lambda c, clan="Ishtarri": clan in _clans(c),
    "Kiasyd": lambda c, clan="Kiasyd": clan in _clans(c),
    "Lasombra": lambda c, clan="Lasombra": clan in _clans(c),
    "Malkavian": lambda c, clan="Malkavian": clan in _clans(c),
    "Malkavian antitribu": lambda c, clan="Malkavian antitribu": clan in _clans(c),
    "Ministry": lambda c, clan="Ministry": clan in _clans(c),
    "Nagaraja": lambda c, clan="Nagaraja": clan in _clans(c),
    "Nosferatu": lambda c, clan="Nosferatu": clan in _clans(c),
    "Nosferatu antitribu": lambda c, clan="Nosferatu antitribu": clan in _clans(c),
    "Osebo": lambda c, clan="Osebo": clan in _clans(c),
    "Pander": lambda c, clan="Pander": clan in _clans(c),
    "Ravnos": lambda c, clan="Ravnos": clan in _clans(c),
    "Salubri": lambda c, clan="Salubri": clan in _clans(c),
    "Salubri antitribu": lambda c, clan="Salubri antitribu": clan in _clans(c),
    "Samedi": lambda c, clan="Samedi": clan in _clans(c),
    "Toreador": lambda c, clan="Toreador": clan in _clans(c),
    "Toreador antitribu": lambda c, clan="Toreador antitribu": clan in _clans(c),
    "Tremere": lambda c, clan="Tremere": clan in _clans(c),
    "Tremere antitribu": lambda c, clan="Tremere antitribu": clan in _clans(c),
    "True Brujah": lambda c, clan="True Brujah": clan in _clans(c),
    "Tzimisce": lambda c, clan="Tzimisce": clan in _clans(c),
    "Ventrue": lambda c, clan="Ventrue": clan in _clans(c),
    "Ventrue antitribu": lambda c, clan="Ventrue antitribu": clan in _clans(c),
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


def _matching(deck: models.Deck, condition) -> int:
    """Number of distinct cards of the deck matching the condition."""
    return sum(1 for card, _ in _utils.deck_cards(deck) if condition(card))


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
    cards_db = _utils.get_cards()
    if args.folder:
        decks = [
            krcg_parser.deck_from_txt(f.open(), cards_db)
            for f in sorted(args.folder.glob("*.txt"))
        ]
    else:
        decks = _utils.filter_twda(args)
    played = analyzer.played(decks, cards_db)
    card_stats = analyzer.stats(decks, cards_db)
    most_common = played.most_common()
    scores: dict[int, Score] = {}
    for index, dek in enumerate(decks):
        if dek.score:
            scores[index] = Score(
                gw=dek.score.round_gw, vp=dek.score.round_vp + dek.score.finals_vp
            )
            continue
        match = re.search(
            r"(?P<gw>\d)\s*GW\s*(?P<vp>\d+)((\.|,)(?P<vp_frac>\d))?",
            dek.comment if args.folder else "",
            re.MULTILINE,
        )
        if match:
            scores[index] = Score(
                gw=int(match.group("gw")),
                vp=int(match.group("vp")) + int(match.group("vp_frac") or 0) / 10,
            )
        else:
            scores[index] = Score()
    cards_score = collections.defaultdict(Score)
    for index, dek in enumerate(decks):
        for card, _ in _utils.deck_cards(dek):
            cards_score[card] += scores[index]

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
    average_score = sum(s.vp for s in scores.values()) / len(decks)
    cards_diff_score = {
        card: round((score - average_score) * played[card], 2)
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
            f"({cards_norm_score[c]}) [{cards_diff_score[c]}] "
            f"{c.unique_name} "
        )
    print()
    print()
    print("------------ Score ------------")
    for r, c, score in ranking(cards_norm_score_list):
        if played[c] < 3:
            continue
        print(
            f"{r}. {trend(upheaval.get(c, 0))} {played[c]:0>2} {cards_score[c]} "
            f"({cards_norm_score[c]}) [{cards_diff_score[c]}] "
            f"{c.unique_name} "
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
                f"{i}. {card.unique_name} has {dif} ranks more ({played[card]}: "
                f"{cards_norm_score[card]}) [{cards_diff_score[card]}]"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -60:
                break
            print(
                f"{i}. {card.unique_name} has {-dif} ranks less ({played[card]}: "
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
                f"{i}. {card.unique_name} got {dif} more VPs than average "
                f"({played[card]}: {cards_norm_score[card]})"
            )

        print("------------ Underperforming ------------")
        for i, (card, dif) in enumerate(reversed(upheaval_list)):
            if dif > -5:
                break
            print(
                f"{i}. {card.unique_name} has {-dif} less VPs than average "
                f"({played[card]}: {cards_norm_score[card]})"
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
                f"{rank}. {card.unique_name} – played in {count} decks, "
                f"{_utils.typical_copies(card_stats, card)} – {cards_score[card]} "
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
                len([d for d in decks if _matching(d, condition) > 5]) / len(decks),
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
                len([d for d in decks if _matching(d, condition) > 5]) / len(decks),
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

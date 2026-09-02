import collections
import itertools

from krcg import models

from . import _utils


def add_parser(parser):
    parser = parser.add_parser("twd", help="display TWD statistics")
    _utils.add_twda_filters(parser)
    parser.set_defaults(func=twd)


ANARCH_CONVERT = 200076


def twd(args):
    decks = _utils.filter_twda(args)
    decks_by_year = collections.defaultdict(set)
    decks_clans = collections.defaultdict(set)
    decks_disciplines = collections.defaultdict(set)
    for deck in decks:
        date = _utils.deck_date(deck)
        if not date:
            continue
        decks_by_year[date.year].add(deck.id)
        cards = list(_utils.deck_cards(deck))
        decks_clans[deck.id] = [
            clan
            for clan, count in collections.Counter(
                itertools.chain.from_iterable(
                    [c.clan] * count
                    for c, count in cards
                    if isinstance(c, models.CryptCard)
                    and c.clan
                    and c.id != ANARCH_CONVERT
                )
            ).most_common()
            if count > 3
        ]
        decks_disciplines[deck.id] = [
            discipline
            for discipline, count in collections.Counter(
                itertools.chain.from_iterable(
                    c.discipline_requirement.disciplines * count
                    for c, count in cards
                    if isinstance(c, models.LibraryCard) and c.discipline_requirement
                )
            ).most_common()
            if count > 5
        ]
    for year, ids in sorted(decks_by_year.items()):
        total = len(ids)
        print(f"\n============================================================= {year}")
        print("------------------------------------------------ clans")
        for clan, count in collections.Counter(
            itertools.chain.from_iterable(decks_clans[i] for i in sorted(ids))
        ).most_common():
            print(f"{clan}\t{count}/{total} ({count / total:.1%})")
        print("\n------------------------------------------ disciplines")
        for discipline, count in collections.Counter(
            itertools.chain.from_iterable(decks_disciplines[i] for i in sorted(ids))
        ).most_common():
            print(f"{discipline}\t{count}/{total} ({count / total:.1%})")
    return 0

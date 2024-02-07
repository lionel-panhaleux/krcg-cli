import collections
import itertools

from . import _utils


def add_parser(parser):
    _utils._init()
    parser = parser.add_parser("twd", help="display TWD statistics")
    _utils.add_twda_filters(parser)
    parser.set_defaults(func=twd)


def twd(args):
    decks = _utils.filter_twda(args)
    decks_by_year = collections.defaultdict(set)
    decks_clans = collections.defaultdict(set)
    decks_disciplines = collections.defaultdict(set)
    for deck in decks:
        decks_by_year[deck.date.year].add(deck.id)
        decks_clans[deck.id] = [
            clan
            for clan, count in collections.Counter(
                itertools.chain.from_iterable(
                    c.clans * count
                    for c, count in deck.cards(lambda c: c.crypt and c.id != 200076)
                )
            ).most_common()
            if count > 3
        ]
        decks_disciplines[deck.id] = [
            discipline
            for discipline, count in collections.Counter(
                itertools.chain.from_iterable(
                    c.disciplines * count
                    for c, count in deck.cards(lambda c: c.library)
                )
            ).most_common()
            if count > 5
        ]
    for year, ids in decks_by_year.items():
        total = len(ids)
        print(f"\n============================================================= {year}")
        print("------------------------------------------------ clans")
        for clan, count in collections.Counter(
            itertools.chain.from_iterable(decks_clans[i] for i in ids)
        ).most_common():
            print(f"{clan}\t{count}/{total} ({count/total:.1%})")
        print("\n------------------------------------------ disciplines")
        for discipline, count in collections.Counter(
            itertools.chain.from_iterable(decks_disciplines[i] for i in ids)
        ).most_common():
            print(f"{discipline}\t{count}/{total} ({count/total:.1%})")

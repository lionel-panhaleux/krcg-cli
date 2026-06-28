"""Display TWD statistics."""

import collections
import itertools
import sys

from . import _utils


def add_parser(parser):
    """Add parser for twd subcommand."""
    parser = parser.add_parser("twd", help="display TWD statistics")
    _utils.add_twda_filters(parser)
    parser.set_defaults(func=twd)


def twd(args):
    """Display TWD statistics."""
    _utils._init(with_twda=True)
    decks = _utils.filter_twda(args)
    decks_by_year: dict[int, set[str]] = collections.defaultdict(set)
    decks_clans: dict[str, set[str]] = collections.defaultdict(set)
    decks_disciplines: dict[str, set[str]] = collections.defaultdict(set)
    for deck in decks:
        if not deck.id:
            print(f"Deck {deck.name} has no id", file=sys.stderr)
            continue
        date = _utils.deck_date(deck)
        if date:
            decks_by_year[date.year].add(deck.id)
        decks_clans[deck.id] = set(
            clan
            for clan, count in collections.Counter(
                itertools.chain.from_iterable(
                    _utils.card_clans(c) * count
                    for c, count in _utils.deck_cards(
                        deck, lambda c: _utils.is_crypt(c) and c.id != 200076
                    )
                )
            ).most_common()
            if count > 3
        )
        decks_disciplines[deck.id] = set(
            discipline
            for discipline, count in collections.Counter(
                itertools.chain.from_iterable(
                    _utils.card_disciplines(c) * count
                    for c, count in _utils.deck_cards(deck, _utils.is_library)
                )
            ).most_common()
            if count > 5
        )
    for year, ids in decks_by_year.items():
        total = len(ids)
        print(f"\n============================================================= {year}")
        print("------------------------------------------------ clans")
        for clan, count in collections.Counter(
            itertools.chain.from_iterable(decks_clans[i] for i in ids)
        ).most_common():
            print(f"{clan}\t{count}/{total} ({count / total:.1%})")
        print("\n------------------------------------------ disciplines")
        for discipline, count in collections.Counter(
            itertools.chain.from_iterable(decks_disciplines[i] for i in ids)
        ).most_common():
            print(f"{discipline}\t{count}/{total} ({count / total:.1%})")

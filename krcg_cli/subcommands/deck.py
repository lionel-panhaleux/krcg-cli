"""Show TWDA decks."""

import datetime
import sys

from krcg import providers
from krcg import utils as krcg_utils

from . import _utils


def add_parser(parser):
    """Add the deck subparser."""
    parser = parser.add_parser("deck", help="show TWDA decks")
    _utils.add_twda_filters(parser)
    parser.add_argument(
        "-f", "--full", action="store_true", help="display each deck content"
    )
    parser.add_argument(
        "filter",
        metavar="TXT",
        nargs="*",
        help="list of TWDA decks IDs, author names or card names",
    )
    parser.set_defaults(func=deck)


def deck(args):
    """List or display TWDA decks by id, card or player."""
    cards_db = _utils.get_cards()
    archive = _utils.get_twda()
    known_authors = {
        krcg_utils.normalize(name)
        for d in archive.values()
        for name in (d.player, d.author)
        if name
    }
    filters = set(args.filter)
    joined_args = krcg_utils.normalize(" ".join(args.filter))
    deck_ids = [i for i in args.filter if i in archive]
    filters -= set(deck_ids)
    cards = [cards_db[c] for c in args.filter if c in cards_db]
    filters -= {c for c in args.filter if c in cards_db}
    if joined_args in cards_db:
        cards.append(cards_db[joined_args])
        filters.clear()
    authors = [krcg_utils.normalize(a) for a in args.filter]
    authors = [a for a in authors if a in known_authors]
    filters -= set(authors)
    if joined_args in known_authors:
        authors.append(joined_args)
        filters.clear()
    if filters:
        sys.stderr.write(
            f'"{" ".join(filters)}" did not match a deck #, card or author'
        )
        return 1
    decks = _utils.filter_twda(args)
    if deck_ids or cards or authors:
        decks = [
            d
            for d in decks
            if d.id in deck_ids
            or (cards and all(_utils.deck_plays(d, c) for c in cards))
            or krcg_utils.normalize(d.player) in authors
            or krcg_utils.normalize(d.author) in authors
        ]
    if len(decks) == 1:
        args.full = True
    if not args.full:
        print(f"-- {len(decks)} decks --")
    decks.sort(key=lambda d: _utils.deck_date(d) or datetime.date.min)
    for d in decks:
        if args.full:
            print(f"[{d.id:<15}]===================================================")
            print(providers.serialize_twd(d, cards_db))
        else:
            print(f"[{d.id}] {d.name or None}")
    return 0

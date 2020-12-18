import sys

from krcg import twda
from krcg import utils as krcg_utils
from krcg import vtes

from . import _utils


def add_parser(parser):
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
    _utils._init(with_twda=True)
    filters = set(args.filter)
    joined_args = krcg_utils.normalize(" ".join(args.filter))
    deck_ids = [i for i in args.filter if i in twda.TWDA]
    filters -= set(deck_ids)
    cards = [vtes.VTES[c] for c in args.filter if c in vtes.VTES]
    filters -= set(cards)
    if joined_args in vtes.VTES:
        cards.append(vtes.VTES[joined_args])
        filters.clear()
    authors = [krcg_utils.normalize(a) for a in args.filter]
    authors = [a for a in authors if a in twda.TWDA.by_author]
    filters -= set(authors)
    if joined_args in twda.TWDA.by_author:
        authors.append(joined_args)
        filters.clear()
    if filters:
        sys.stderr.write(
            f"\"{' '.join(filters)}\" did not match a deck #, card or author"
        )
        return 1
    decks = _utils.filter_twda(args)
    if deck_ids or cards or authors:
        decks = [
            d
            for d in decks
            if d.id in deck_ids
            or (cards and all(c in d for c in cards))
            or krcg_utils.normalize(d.player) in authors
            or krcg_utils.normalize(d.author) in authors
        ]
    if len(decks) == 1:
        args.full = True
    if not args.full:
        print(f"-- {len(decks)} decks --")

    for d in sorted(decks, key=lambda a: a.date):
        if args.full:
            print(f"[{d.id:<15}]===================================================")
            print(d.to_txt())
        else:
            print(f"[{d.id}] {d.name}")
    return 0

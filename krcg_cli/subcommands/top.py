import sys

from krcg import analyzer

from . import _utils


def add_parser(parser):
    _utils._init()
    parser = parser.add_parser("top", help="display top cards (most played)")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of cards to print (default 10)",
    )
    _utils.add_card_filters(parser)
    _utils.add_twda_filters(parser)
    parser.set_defaults(func=top)


def top(args):
    candidates = _utils.filter_cards(args)
    if not candidates:
        sys.stderr.write("No card match\n")
        return 1
    decks = _utils.filter_twda(args)
    A = analyzer.Analyzer(decks)
    A.refresh(condition=lambda c: c in candidates)
    for card, count in A.played.most_common()[: args.number]:
        print(
            f"{card.name:<30} (played in {count} decks, typically "
            f"{_utils.typical_copies(A, card)})"
        )
    return 0

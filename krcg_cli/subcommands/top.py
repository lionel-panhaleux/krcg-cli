"""Display top cards."""

import collections
import sys

from krcg import analyzer

from . import _utils


def add_parser(parser):
    """Add parser for top subcommand."""
    _utils._init()
    parser = parser.add_parser("top", help="display top cards (most played)")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of cards to print (default 10)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        default="human",
        choices=["human", "csv"],
        help="Output format (default human)",
    )
    _utils.add_card_filters(parser)
    _utils.add_twda_filters(parser)
    _utils.add_price_option(parser)
    parser.set_defaults(func=top)


def top(args):
    """Display top cards."""
    candidates = _utils.filter_cards(args)
    if not candidates:
        sys.stderr.write("No card match\n")
        return 1
    decks = _utils.filter_twda(args)
    played = analyzer.played(decks, _utils.VTES)
    played = collections.Counter({c: n for c, n in played.items() if c in candidates})
    stats = analyzer.stats(decks, _utils.VTES)
    if args.output == "csv":
        print(",".join(("Card name", "# decks", "# copies")))
    cards = list(played.most_common()[: args.number])
    if args.price:
        prices = _utils.get_cards_prices([c for c, _n in cards])
    for card, count in cards:
        if args.output == "human":
            s = (
                f"{card.unique_name:<30} (played in {count} decks, typically "
                f"{_utils.typical_copies(stats, card)})"
            )
        elif args.output == "csv":
            s = ",".join(
                (
                    f'"{card.unique_name}"',
                    str(count),
                    _utils.typical_copies(stats, card, naked=True),
                )
            )
        if args.price:
            if prices.get(card):
                s = f"€{prices[card]:>5.2f} " + s
            else:
                s = "  N/A  " + s
        print(s)
    return 0

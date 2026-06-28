"""Build a deck around given card(s), based on the TWDA."""

import sys

from krcg import analyzer
from krcg import providers

from . import _utils


def add_parser(parser):
    """Add parser for build subcommand."""
    parser = parser.add_parser(
        "build", help="build a deck around given card(s), based on the TWDA"
    )
    _utils.add_twda_filters(parser)
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=build)


def build(args):
    """Build a deck around given card(s), based on the TWDA."""
    decks = _utils.filter_twda(args)
    try:
        cards = [_utils.VTES[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    deck = analyzer.build_deck(decks, _utils.VTES, *cards)
    print(providers.serialize_twd(deck, _utils.VTES))
    return 0

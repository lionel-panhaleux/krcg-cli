import sys

from krcg import analyzer
from krcg import providers

from . import _utils


def add_parser(parser):
    parser = parser.add_parser(
        "build", help="build a deck around given card(s), based on the TWDA"
    )
    _utils.add_twda_filters(parser)
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=build)


def build(args):
    decks = _utils.filter_twda(args)
    cards_db = _utils.get_cards()
    try:
        cards = [cards_db[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    try:
        deck = analyzer.build_deck(decks, cards_db, *cards)
    except analyzer.AnalysisError as e:
        sys.stderr.write(f"Cannot build a deck: {e}\n")
        return 1
    print(providers.serialize_twd(deck, cards_db))
    return 0

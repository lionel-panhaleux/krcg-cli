import sys

from krcg import analyzer
from krcg import vtes

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
    try:
        cards = [vtes.VTES[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    print(analyzer.Analyzer(decks).build_deck(*cards).to_txt())
    return 0

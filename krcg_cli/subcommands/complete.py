"""Card name completion."""

import sys

from . import _utils


def add_parser(parser):
    """Add the complete subparser."""
    parser = parser.add_parser("complete", help="card name completion")
    parser.add_argument("-f", "--full", action="store_true", help="display cards text")
    parser.add_argument("name", metavar="NAME", help="parts of the name")
    parser.set_defaults(func=complete)


def complete(args):
    """Print the cards whose name matches the given text."""
    completions = _utils.get_cards().complete(args.name)
    if not completions:
        sys.stderr.write("No match\n")
        return 1
    for card in completions:
        print(card.unique_name)
        if args.full:
            print(_utils.card_text(card, False))
            print()
    return 0

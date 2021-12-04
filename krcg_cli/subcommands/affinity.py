import sys

from krcg import analyzer
from krcg import vtes

from . import _utils


def add_parser(parser):
    _utils._init()
    parser = parser.add_parser(
        "affinity", help="display cards affinity (most played together)"
    )
    parser.add_argument(
        "--min",
        type=int,
        default=25,
        help="Minimum affinity score to display (0 to 100, default 25)",
    )
    _utils.add_twda_filters(parser)
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=affinity)


def affinity(args):
    decks = _utils.filter_twda(args)
    try:
        cards = [vtes.VTES[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    A = analyzer.Analyzer(decks)
    A.refresh(*cards, similarity=1)
    if len(A.examples) < 4:
        print("Too few example in TWDA.")
        if len(A.examples) > 0:
            print(
                "To see them:\n\tkrcg deck "
                + " ".join('"' + card.usual_name + '"' for card in cards)
            )
        return 0
    # do not include spoilers if affinity is within 50% of natural occurence
    candidates = A.candidates(*cards, spoiler_multiplier=1.5)
    for card, score in candidates:
        score = round(score * 100 / len(cards))
        if args.min > score:
            break
        print(
            f"{card.usual_name:<30} (in {score:.0f}% of decks, typically "
            f"{_utils.typical_copies(A, card)})"
        )
    return 0

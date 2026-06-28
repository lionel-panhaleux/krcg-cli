"""Display cards affinity (most played together)."""

import sys

from krcg import analyzer

from . import _utils


def add_parser(parser):
    """Add parser for affinity subcommand."""
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
    """Display cards affinity (most played together)."""
    decks = _utils.filter_twda(args)
    try:
        cards = [_utils.VTES[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    # decks playing all the reference cards (similarity=1)
    examples = [d for d in decks if all(_utils.card_in_deck(c, d) for c in cards)]
    if len(examples) < 4:
        print("Too few example in TWDA.")
        if len(examples) > 0:
            print(
                "To see them:\n\tkrcg deck "
                + " ".join('"' + card.unique_name + '"' for card in cards)
            )
        return 0
    stats = analyzer.stats(examples, _utils.VTES)
    candidates = analyzer.affinity(decks, _utils.VTES, *cards, similarity=1.0)
    for card, score in candidates:
        score = round(score * 100 / len(cards))
        if args.min > score:
            break
        print(
            f"{card.unique_name:<30} (in {score:.0f}% of decks, typically "
            f"{_utils.typical_copies(stats, card)})"
        )
    return 0

import sys

from krcg import analyzer

from . import _utils


def add_parser(parser):
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
    cards_db = _utils.get_cards()
    try:
        cards = [cards_db[name] for name in args.cards]
    except KeyError as e:
        sys.stderr.write(f"Card not found: {e.args[0]}\n")
        return 1
    examples = [d for d in decks if all(_utils.deck_plays(d, c) for c in cards)]
    if len(examples) < 4:
        print("Too few example in TWDA.")
        if len(examples) > 0:
            print(
                "To see them:\n\tkrcg deck "
                + " ".join('"' + card.unique_name + '"' for card in cards)
            )
        return 0
    stats = analyzer.stats(examples, cards_db)
    # do not include spoilers if affinity is within 50% of natural occurence
    played = analyzer.played(decks, cards_db)
    spoilers = {c: n / len(decks) for c, n in played.items() if n > len(decks) / 4}
    for card, score in analyzer.affinity(decks, cards_db, *cards, similarity=1):
        score = score / len(cards)
        if card in spoilers and score < spoilers[card] * 1.5:
            continue
        score = round(score * 100)
        if args.min > score:
            break
        print(
            f"{card.unique_name:<30} (in {score:.0f}% of decks, typically "
            f"{_utils.typical_copies(stats, card)})"
        )
    return 0

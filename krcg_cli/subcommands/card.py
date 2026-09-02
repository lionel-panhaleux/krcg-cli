import sys

from krcg import models

from . import _utils


def add_parser(parser):
    parser = parser.add_parser("card", help="show cards")
    parser.add_argument(
        "-i", "--international", action="store_true", help="display translations"
    )
    parser.add_argument(
        "-s", "--short", action="store_true", help="display only card name"
    )
    parser.add_argument(
        "-t", "--text", action="store_true", help="display card text only (no rulings)"
    )
    parser.add_argument(
        "-l", "--links", action="store_true", help="display ruling links"
    )
    parser.add_argument("-k", "--krcg", action="store_true", help="display KRCG format")
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=card)


def card(args):
    """Display cards, their text and rulings"""
    index = 0
    cards = args.cards
    if not cards and not sys.stdin.isatty():
        cards = sys.stdin.read().splitlines()
    try:
        for name in cards:
            _display_card(args, name, index)
            index += 1
        return 0
    except KeyError:
        if index == 0:
            try:
                _display_card(args, " ".join(cards))
                return 0
            except KeyError:
                pass
    sys.stderr.write("Card not found\n")
    return 1


def _display_card(args, name: str, index: int = 0) -> None:
    if not args.short and index > 0:
        print()
    key: int | str = int(name) if name.isdigit() else name
    card = _utils.get_cards()[key]
    if args.krcg:
        print(str(card))
    else:
        print(card.unique_name)
    translations = sorted(card.i18n.items())
    if args.international:
        for lang, translation in translations:
            print(f"  {lang} -- {translation.name}")
    if args.short:
        return
    print(_utils.card_text(card, args.krcg))
    if args.international:
        for lang, translation in translations:
            print(f"\n-- {lang}\n{translation.text}")
    if args.text or not card.rulings:
        return
    print(_card_rulings(args, card))


def _card_rulings(args, card: models.Card) -> str:
    """Text of a card's rulings"""
    text = "\n-- Rulings\n"
    for ruling in card.rulings:
        text += ruling.text + "\n"
        if args.links:
            for reference in ruling.references:
                text += f"{reference.label}: {reference.url}\n"
            text += "\n"
    return text[:-1]

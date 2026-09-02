"""Show cards: text, rulings, translations and price."""

import sys

from krcg import models

from . import _utils


def add_parser(parser):
    """Add the card subparser."""
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
    _utils.add_price_option(parser)
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=card)


def card(args):
    """Display cards, their text, price and rulings."""
    cards_db = _utils.get_cards()
    names = args.cards
    if not names and not sys.stdin.isatty():
        names = sys.stdin.read().splitlines()
    # a name given as separate words: "krcg card Govern the Unaligned"
    if len(names) > 1 and " ".join(names) in cards_db:
        names = [" ".join(names)]
    cards = []
    for name in names:
        key: int | str = int(name) if name.isdigit() else name
        try:
            cards.append(cards_db[key])
        except KeyError:
            sys.stderr.write(f"Card not found: {name}\n")
            return 1
    prices = _utils.get_cards_prices(cards) if args.price else {}
    for index, card in enumerate(cards):
        if index > 0 and not args.short:
            print()
        _display_card(args, card, prices.get(card.id))
    return 0


def _display_card(args, card: models.Card, price: float | None) -> None:
    name = str(card) if args.krcg else card.unique_name
    if args.price:
        name = (f"€{price:>5.2f} " if price else "  N/A  ") + name
    print(name)
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
    text = "\n-- Rulings\n"
    for ruling in card.rulings:
        text += ruling.text + "\n"
    if args.links:
        references = {
            reference.label: reference.url
            for ruling in card.rulings
            for reference in ruling.references
        }
        text += "\n-- Rulings references\n"
        for label, url in references.items():
            text += f"{label}: {url}\n"
    return text[:-1]

"""Show cards, their text, price on the secondary market, and rulings."""

import argparse
import sys

from krcg.cards import Card
from krcg import vtes

from . import _utils


def add_parser(parser):
    """Add parser for card subcommand."""
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
    """Display cards, their text, price on the secondary market, and rulings."""
    _utils._init(international=args.international)
    card_names = args.cards
    if not card_names and not sys.stdin.isatty():
        card_names = sys.stdin.read().splitlines()
    cards: list[Card] = []
    for index, name in enumerate(card_names):
        try:
            name = int(name)
        except ValueError:
            pass
        try:
            cards.append(vtes.VTES[name])
        except KeyError:
            if index == 0:
                try:
                    cards.append(vtes.VTES[" ".join(card_names)])
                    break
                except KeyError:
                    sys.stderr.write(f"Card not found: {name}")
                    return 1
    prices = None
    if args.price:
        print("Fetching prices... (it takes a minute)")
        prices = _utils.get_cards_prices(cards)
    for i, card in enumerate(cards):
        if i > 0:
            print()
        _display_card(args, card, prices)


def _display_card(
    args: argparse.Namespace, card: Card, prices: dict[Card, int] | None = None
) -> None:
    """Print helper."""
    if args.krcg:
        name_line = f"{card.id}|{card.name}"
    else:
        name_line = card.usual_name
    if args.price:
        prices = prices or _utils.get_cards_prices([card])
        if prices.get(card):
            name_line = f"€{prices[card]:>5.2f} " + name_line
        else:
            name_line = "  N/A  " + name_line
    print(name_line)
    if args.international:
        for lang, translation in card.i18n_variants("name"):
            print(f"  {lang[:2]} -- {translation}")
    if args.short:
        return
    print(_card_text(args, card))
    if args.international:
        for lang, translation in card.i18n_variants("card_text"):
            print(f"\n-- {lang[:2]}\n{translation}")
    if args.text or not card.rulings:
        return
    print(_card_rulings(args, card))


def _card_text(args: argparse.Namespace, card: Card) -> str:
    """Full text of a card (id, title, traits, costs, ...) for display purposes."""
    text = "[{}]".format("/".join(card.types))
    if card.clans:
        text += "[{}]".format("/".join(card.clans))
    if card.pool_cost:
        text += "[{}P]".format(card.pool_cost)
    if card.blood_cost:
        text += "[{}B]".format(card.blood_cost)
    if card.conviction_cost:
        text += "[{}C]".format(card.conviction_cost)
    if card.capacity:
        text += "[{}]".format(card.capacity)
    if not args.krcg and card.group:
        text += "(g.{})".format(card.group)
    if card.burn_option:
        text += "(Burn Option)"
    if card.banned:
        text += " -- BANNED on " + card.banned
    if not args.krcg:
        text += " -- (#{})".format(card.id)
    if card.crypt and card.disciplines:
        text += "\n{}".format(" ".join(card.disciplines) or "-- No discipline")
    text += "\n{}".format(card.card_text)
    return text


def _card_rulings(args: argparse.Namespace, card: Card) -> str:
    """Text of a card's rulings."""
    text = "\n-- Rulings\n"
    for ruling in card.rulings:
        text += ruling["text"] + "\n"
    if args.links:
        seen = set()
        text += "\n-- Rulings references\n"
        for ruling in card.rulings:
            for ref in ruling["references"]:
                if ref["label"] in seen:
                    continue
                seen.add(ref["label"])
                text += f"{ref['label']}: {ref['url']}\n"
    return text[:-1]

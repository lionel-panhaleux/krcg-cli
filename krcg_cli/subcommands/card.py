"""Show cards, their text, price on the secondary market, and rulings."""

import argparse
import sys

from krcg import models
from krcg.models import Card, CryptCard, LibraryCard

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
            cards.append(_utils.VTES[name])
        except KeyError:
            if index == 0:
                try:
                    cards.append(_utils.VTES[" ".join(card_names)])
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
        name_line = f"{card.id}|{card.unique_name}"
    else:
        name_line = card.unique_name
    if args.price:
        prices = prices or _utils.get_cards_prices([card])
        if prices.get(card):
            name_line = f"€{prices[card]:>5.2f} " + name_line
        else:
            name_line = "  N/A  " + name_line
    print(name_line)
    if args.international:
        for lang in models.Lang:
            if lang != models.Lang.EN and lang in card.i18n:
                print(f"  {lang.value[:2]} -- {card.i18n[lang].name}")
    if args.short:
        return
    print(_card_text(args, card))
    if args.international:
        for lang in models.Lang:
            if lang != models.Lang.EN and lang in card.i18n:
                print(f"\n-- {lang.value[:2]}\n{card.i18n[lang].text}")
    if args.text or not card.rulings:
        return
    print(_card_rulings(args, card))


_COST_SUFFIX = {
    models.Cost.Type.POOL: "P",
    models.Cost.Type.BLOOD: "B",
    models.Cost.Type.CONVICTION: "C",
}


def _card_text(args: argparse.Namespace, card: Card) -> str:
    """Full text of a card (id, title, traits, costs, ...) for display purposes."""
    text = "[{}]".format("/".join(t.value for t in card.types))
    if isinstance(card, CryptCard):
        clans = [card.clan] if card.clan else []
    elif isinstance(card, LibraryCard):
        clans = card.clan_requirement
    else:
        clans = []
    if clans:
        text += "[{}]".format("/".join(clans))
    if isinstance(card, LibraryCard) and card.cost:
        text += "[{}{}]".format(card.cost.value, _COST_SUFFIX[card.cost.type])
    if isinstance(card, CryptCard) and card.capacity:
        text += "[{}]".format(card.capacity)
    if not args.krcg and isinstance(card, CryptCard) and card.group:
        text += "(g.{})".format(card.group.value[1:])
    if isinstance(card, LibraryCard) and card.burn_option:
        text += "(Burn Option)"
    if card.banned:
        text += " -- BANNED on " + str(card.banned)
    if not args.krcg:
        text += " -- (#{})".format(card.id)
    if isinstance(card, CryptCard) and card.disciplines:
        text += "\n{}".format(" ".join(card.disciplines) or "-- No discipline")
    text += "\n{}".format(card.text)
    return text


def _card_rulings(args: argparse.Namespace, card: Card) -> str:
    """Text of a card's rulings."""
    text = "\n-- Rulings\n"
    for ruling in card.rulings:
        text += ruling.text + "\n"
    if args.links:
        seen = set()
        text += "\n-- Rulings references\n"
        for ruling in card.rulings:
            for ref in ruling.references:
                if ref.label in seen:
                    continue
                seen.add(ref.label)
                text += f"{ref.label}: {ref.url}\n"
    return text[:-1]

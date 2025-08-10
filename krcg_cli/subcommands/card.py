import sys

from krcg import cards
from krcg import vtes

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
    _utils.add_price_option(parser)
    parser.add_argument("cards", metavar="CARD", nargs="*", help="card names or IDs")
    parser.set_defaults(func=card)


def card(args):
    """Display cards, their text and rulings"""
    _utils._init()
    card_names = args.cards
    if not card_names and not sys.stdin.isatty():
        cards = sys.stdin.read().splitlines()
    cards = []
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
    for card in cards:
        _display_card(args, card, prices)
        print()


def _display_card(args, card: cards.Card, prices: dict[int, str] | None = None) -> None:
    if args.krcg:
        name_line = f"{card.id}|{card.name}"
    else:
        name_line = card.usual_name
    if args.price:
        prices = prices or _utils.get_cards_prices([card])
        if prices.get(card.id):
            name_line = f"€{prices[card.id]:>5.2f} " + name_line
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
    if args.text or not card.rulings.get("text"):
        return
    print(_card_rulings(args, card))


def _card_text(args, card) -> str:
    """Full text of a card (id, title, traits, costs, ...) for display purposes"""
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
        text += " -- BANNED in " + card["Banned"]
    if not args.krcg:
        text += " -- (#{})".format(card.id)
    if card.crypt and card.disciplines:
        text += "\n{}".format(" ".join(card.disciplines) or "-- No discipline")
    text += "\n{}".format(card.card_text)
    return text


def _card_rulings(args, card):
    """Text of a card's rulings"""
    text = "\n-- Rulings\n"
    for ruling in card.rulings["text"]:
        text += ruling + "\n"
    if args.links:
        for ref, link in card.rulings["links"].items():
            text += f"{ref}: {link}\n"
    return text[:-1]

"""Shared helpers: data handles, argparse filters, display, and card prices."""

from collections.abc import Iterator
import argparse
import asyncio
import datetime
import functools
import itertools
import json
import logging
import math
import os

import aiohttp
import arrow
import caseconverter
import unidecode

import krcg
from krcg import loader
from krcg import models
from krcg import twda

logger = logging.getLogger("krcg")


@functools.cache
def get_cards() -> krcg.CardDict:
    """The cards library, loaded once (bundled data, version cache when present)."""
    if os.path.exists(loader.PICKLE_FILE):
        return krcg.load()
    return krcg.load_local()


@functools.cache
def get_twda() -> twda.DecksArchive:
    """The TWDA, loaded once from the bundled snapshot."""
    return twda.load()


def deck_date(deck: models.Deck) -> datetime.date | None:
    return deck.event.date if deck.event else None


def deck_cards(deck: models.Deck) -> Iterator[tuple[models.Card, int]]:
    """Yield (card, count) for each deck entry, resolved in the cards library."""
    cards = get_cards()
    for entry in deck.cards:
        card = cards.get(entry.id)
        if card:
            yield card, entry.count


def deck_plays(deck: models.Deck, card: models.Card) -> bool:
    return any(entry.id == card.id for entry in deck.cards)


# ---------------------------------------------------------------------- TWDA filters


def add_twda_filters(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--from",
        type=lambda s: arrow.get(s).date(),
        dest="date_from",
        help="only consider decks from that date on",
    )
    parser.add_argument(
        "--to",
        type=lambda s: arrow.get(s).date(),
        dest="date_to",
        help="only consider decks up to that date",
    )
    parser.add_argument(
        "--players",
        type=int,
        default=0,
        help="only consider decks that won against at least that many players",
    )


def filter_twda(args: argparse.Namespace) -> list[models.Deck]:
    decks = list(get_twda().values())
    if args.date_from:
        decks = [
            d for d in decks if (deck_date(d) or datetime.date.min) >= args.date_from
        ]
    if args.date_to:
        decks = [d for d in decks if (deck_date(d) or datetime.date.max) < args.date_to]
    if args.players:
        decks = [d for d in decks if d.event and d.event.players_count >= args.players]
    return decks


# ---------------------------------------------------------------------- card filters

#: sets currently in print, excluded by --no-reprint
IN_PRINT_SETS = [
    "Anthology",
    "Anthology I",
    "Echoes of Gehenna",
    "Fall of London",
    "Fifth Edition",
    "Fifth Edition (Anarch)",
    "Fifth Edition (Companion)",
    "First Blood",
    "Heirs to the Blood Reprint",
    "Keepers of Tradition Reprint",
    "Lost Kindred",
    "New Blood",
    "New Blood II",
    "New Blood III",
    "Print on Demand",
    "Sabbat Preconstructed",
    "Sabbat V5",
    "Shadows of Berlin",
    "Thirtieth Anniversary",
    "Twenty-Fifth Anniversary",
]


def set_code(name: str) -> str:
    """The code of a set given by code or name (case-insensitive)."""
    lookup = {
        key.lower(): expansion.code
        for expansion in get_cards().sets.values()
        for key in (expansion.code, expansion.name)
    }
    return lookup[name.lower()]


def choices(dimension: str) -> list[str]:
    """The values a search dimension can take (None excluded)."""
    return [v for v in get_cards().search_dimensions[dimension] if v]


class DimensionChoice(argparse.Action):
    """Choices with nargs +/*, resolved to the dimension's canonical values.

    argparse cannot combine `choices` with `nargs`, cf. bugs.python.org/issue9625.
    Matching ignores case except for disciplines (case encodes the level).
    Sets accept names as well as codes, groups accept bare numbers.
    """

    def __init__(self, dimension: str, **kwargs) -> None:
        super().__init__(**kwargs)
        self.dimension = dimension

    def canonical(self, value: str) -> str:
        if self.dimension == "set":
            return set_code(value)
        if self.dimension == "group" and value.isdigit():
            value = "G" + value
        values = choices(self.dimension)
        if self.dimension == "discipline":
            lookup = {v: v for v in values}
            return lookup[value]
        lookup = {v.lower(): v for v in values}
        return lookup[value.lower()]

    def __call__(self, parser, namespace, values, option_string=None):
        result = []
        for value in values:
            try:
                result.append(self.canonical(value))
            except KeyError:
                raise argparse.ArgumentError(
                    self,
                    f"invalid choice: {value} (choose from: "
                    f"{', '.join(choices(self.dimension))})",
                )
        setattr(namespace, self.dest, result)


def add_card_filters(parser: argparse.ArgumentParser) -> None:
    def add(*flags: str, dimension: str, help: str, listed: bool = True, **kwargs):
        if listed:
            help += f" ({', '.join(choices(dimension))})"
        parser.add_argument(
            *flags,
            action=DimensionChoice,
            dimension=dimension,
            metavar=dimension.upper(),
            nargs="+",
            help=help,
            **kwargs,
        )

    add("-d", "--discipline", dimension="discipline", help="Filter by discipline")
    add("-c", "--clan", dimension="clan", help="Filter by clan")
    add("-t", "--type", dimension="type", help="Filter by type")
    add("-g", "--group", dimension="group", help="Filter by group")
    add(
        "-x",
        "--exclude-set",
        dimension="set",
        dest="exclude_set",
        help="Exclude given sets",
    )
    add(
        "-e",
        "--exclude-type",
        dimension="type",
        dest="exclude_type",
        help="Exclude given types",
    )
    add("-b", "--bonus", dimension="bonus", help="Filter by bonus")
    parser.add_argument(
        "--text",
        metavar="TEXT",
        nargs="+",
        help="Filter by text (including name and flavor text)",
    )
    add("--trait", dimension="trait", help="Filter by trait")
    add("--capacity", dimension="capacity", help="Filter by capacity")
    add("--set", dimension="set", help="Filter by set (name or code)")
    add("--sect", dimension="sect", help="Filter by sect")
    add("--title", dimension="title", help="Filter by title")
    add("--city", dimension="city", help="Filter by city", listed=False)
    add("--rarity", dimension="rarity", help="Filter by rarity")
    add(
        "--precon",
        dimension="precon",
        help="Filter by preconstructed starter (SET:BUNDLE)",
        listed=False,
    )
    add("--artist", dimension="artist", help="Filter by artist", listed=False)
    parser.add_argument(
        "--no-reprint",
        action="store_true",
        help="Filter out cards that are currently in print",
    )


SEARCH_DIMENSIONS = [
    "discipline",
    "clan",
    "type",
    "group",
    "bonus",
    "trait",
    "capacity",
    "set",
    "sect",
    "title",
    "city",
    "rarity",
    "precon",
    "artist",
]


def filter_cards(args: argparse.Namespace) -> set[models.Card]:
    """The cards matching the card filters (all cards if there are none)."""
    cards = get_cards()
    criteria = {
        dimension: getattr(args, dimension)
        for dimension in SEARCH_DIMENSIONS
        if getattr(args, dimension, None)
    }
    text = " ".join(args.text or [])
    if text:
        result = set[models.Card]()
        for dimension in ("name", "card_text", "flavor_text"):
            result |= set(cards.search(n=None, **criteria, **{dimension: [text]}))
    elif criteria:
        result = set(cards.search(n=None, **criteria))
    else:
        result = set(cards.cards())
    exclude_set = set(args.exclude_set or [])
    if args.no_reprint:
        exclude_set |= {set_code(name) for name in IN_PRINT_SETS}
    for type_ in args.exclude_type or []:
        result -= set(cards.search(n=None, type=[type_]))
    for code in exclude_set:
        result -= set(cards.search(n=None, set=[code]))
    return result


# ---------------------------------------------------------------------- display


def typical_copies(
    stats: dict[models.Card, tuple[float, float]], card: models.Card, naked=False
) -> str:
    """Typical count played, from the analyzer stats: "1-3 copies"."""
    average, variance = stats[card]
    deviation = math.sqrt(variance)
    min_copies = max(1, round(average - deviation))
    max_copies = max(1, round(average + deviation))
    if min_copies == max_copies:
        ret = f"{min_copies}"
    else:
        ret = f"{min_copies}-{max_copies}"
    if naked:
        return ret
    if max_copies > 1:
        ret += " copies"
    else:
        ret += " copy"
    return ret


def card_text(card: models.Card, krcg_format: bool) -> str:
    """Full text of a card (types, traits, costs, ...) for display purposes."""
    text = "[{}]".format("/".join(card.types))
    if isinstance(card, models.CryptCard):
        if card.clan:
            text += f"[{card.clan}]"
        if card.capacity:
            text += f"[{card.capacity}]"
        if not krcg_format and card.group:
            text += f"(g.{card.group.value[1:]})"
    if isinstance(card, models.LibraryCard):
        if card.clan_requirement:
            text += "[{}]".format("/".join(card.clan_requirement))
        if card.cost:
            text += f"[{card.cost.value}{card.cost.type.value[0]}]"
        if card.burn_option:
            text += "(Burn Option)"
    if card.banned:
        text += f" -- BANNED in {card.banned.year}"
    if not krcg_format:
        text += f" -- (#{card.id})"
    if isinstance(card, models.CryptCard):
        text += "\n{}".format(" ".join(card.disciplines) or "-- No discipline")
    text += f"\n{card.text}"
    return text


# ---------------------------------------------------------------------- prices

# The CGC shop is a WooCommerce site exposing a public WPGraphQL endpoint.
# Products are looked up by slug; a variable product has one variation per
# printing, with its own price and stock status.
CGC_GRAPHQL_URL = "https://shop.cardgamegeek.com/wp/graphql"
CGC_QUERY = """
fragment P on Product {
  ... on SimpleProduct { price salePrice stockStatus }
  ... on VariableProduct {
    price
    salePrice
    variations(first: 100) { nodes { price salePrice stockStatus } }
  }
}
query {%s}
"""


def cgc_product_price(product: dict | None) -> float | None:
    """Price of a CGC product: sale price if any, else regular price.

    Simple products carry their price directly. Variable products (one variation
    per printing) do not: use the cheapest variation, preferring those in stock.
    """
    if not product:
        return None
    offers = [product] + ((product.get("variations") or {}).get("nodes") or [])
    prices = {}  # price -> in stock
    for offer in offers:
        price = offer.get("salePrice") or offer.get("price")
        if price:
            in_stock = offer.get("stockStatus") == "IN_STOCK"
            prices[price] = prices.get(price, False) or in_stock
    if not prices:
        return None
    in_stock = [price for price, available in prices.items() if available]
    return min(in_stock or prices)


NAMES_MAP = {
    "47th Street Royals": "47th-street-royal",
    "Abraham DuSable": "abraham-dusable",
    "Akhenaten, The Sun Pharaoh": "akhenaten-the-sun-pharaoh-mummy",
    "Amam the Devourer": "amam-the-devourer-bane-mummy",
    "Ambrosius, The Ferryman": "ambrosius-the-ferryman-wraith",
    "Anarch Manifesto, An": "an-anarch-manifesto",
    "Andre LeRoux": "andre-leroux",
    "Antoinette DuChamp": "antoinette-duchamp",
    "Brigitte Gebauer": "brigitte-gebauer-wraith",
    "C.J.": "c-j",
    "Carlton Van Wyk": "carlton-van-wyk-hunter",
    "Chester DuBois": "chester-dubois",
    "CrimethInc.": "crimethinc",
    "Crusade: Washington, D.C.": "crusade-washington-d-c",
    "Dauntain Black Magician": "dauntain-black-magician-changeling",
    "DeSalle": "desalle",
    "Doris McMillon": "doris-mcmillon",
    "Draeven Softfoot": "draeven-softfoot-changeling",
    "Evan Klein (G6)": "evan-klein-2",
    "Gerald FitzGerald": "gerald-fitzgerald",
    "Gilbert Duane (G6)": "gilbert-duane-2",
    "Hesha Ruhadze (G6)": "hesha-ruhadze-2",
    "Jake Washington": "jake-washington-hunter",
    "Kalinda (G6)": "kalinda-2",
    "Kherebutu": "kherebutu-bane-mummy",
    "KoKo": "koko",
    "Kpist m/45": "kpist-m-45",
    "Kuyén": "kuyen-promo",
    "MacAlister Marshall": "macalister-marshall",
    "Maila": "maila-promo",
    "Masquer": "masquer-wraith",
    "Meditative Grove": "mediative-grove",
    "Mehemet of the Ahl-i-Batin": "mehemet-of-the-ahl-i-batin-mage",
    "Michael diCarlo": "michael-dicarlo",
    "Mylan Horseed": "mylan-horseed-goblin",
    "Navar McClaren": "navar-mcclaren",
    "Neighborhood Watch Commander": "neighborhood-watch-commander-hunter",
    "Nephandus": "nephandus-mage",
    "Paul DiCarlo, The Alpha": "paul-dicarlo-the-alpha",
    "Pentex™ Subversion": "pentex-subversion",
    "Powerbase: Washington, D.C.": "powerbase-washington-d-c",
    "Praxis Seizure: Washington, D.C.": "praxis-seizure-washington-d-c",
    "Qetu the Evil Doer": "qetu-the-evil-doer-bane-mummy",
    "Ramiel DuPre": "ramiel-dupre",
    "Redbone McCray": "redbone-mccray",
    "Rego Motum": "rego-motus",
    "Ruth McGinley": "ruth-mcginley",
    "Sacré-Cœur Cathedral, France": "sacre-cour-cathedral-france",
    "SchreckNET": "schrecknet",
    "Shadow Court Satyr": "shadow-court-satyr-changeling",
    "Sébastien Goulet (ADV)": "sebastian-goulet-adv",
    "Sébastien Goulet": "sebastian-goulet",
    "T.J.": "t-j",
    "Thadius Zho": "thadius-zho-mage",
    "The Crimson Sentinel": "crimson-sentinel",
    "The Dracon": "the-dracon-humble-bundle",
    "The Khabar: Community": "khabar-the-community",
    "The Meddling of Semsith": "meddling-of-semsith",
    "Theo Bell (G6)": "theo-bell-2",
    "Tutu the Doubly Evil One": "tutu-the-doubly-evil-one-bane-mummy",
    "Tyler McGill": "tyler-mcgill",
    "Veneficti": "veneficti-mage",
    "Wendell Delburton": "wendell-delburton-hunter",
    'Anna "Dictatrix11" Suljic': "anna-dictatrixll-suljic",
    'Felix "Fix" Hessian': "felix-fix-hessian-wraith",
    'Xian "DziDzat155" Quan': "xian-dzidzat155-quan",
}


def batched(iterable, n):
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


def cgc_slug(card_name: str) -> str:
    return NAMES_MAP.get(
        card_name, caseconverter.kebabcase(unidecode.unidecode(card_name))
    )


async def get_cards_price_CGC(
    session: aiohttp.ClientSession, card_names: list[str]
) -> list[float | None]:
    """Fetch the prices of a batch of cards in a single GraphQL query."""
    query = CGC_QUERY % "".join(
        f"p{i}: product(id: {json.dumps(cgc_slug(name))}, idType: SLUG) {{ ...P }}"
        for i, name in enumerate(card_names)
    )
    async with session.post(
        CGC_GRAPHQL_URL, json={"query": query}, timeout=aiohttp.ClientTimeout(total=60)
    ) as response:
        response.raise_for_status()
        result = await response.json()
    for error in result.get("errors") or []:
        # per-product errors (unknown slug) have a path, query errors do not
        level = logging.DEBUG if "path" in error else logging.WARNING
        logger.log(level, "CGC price lookup: %s", error.get("message"))
    data = result.get("data") or {}
    return [cgc_product_price(data.get(f"p{i}")) for i in range(len(card_names))]


async def get_all_cards_price_CGC(card_names: list[str]) -> list[float | None]:
    prices = []
    async with aiohttp.ClientSession() as session:
        for batch in batched(card_names, n=50):
            try:
                prices.extend(await get_cards_price_CGC(session, batch))
            except (aiohttp.ClientError, TimeoutError, ValueError) as e:
                logger.warning("CGC price lookup failed: %r", e)
                prices.extend([None] * len(batch))
    return prices


def add_price_option(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--price",
        action="store_true",
        help="Display cards prices on the secondary market",
    )


def get_cards_prices(cards: list[models.Card]) -> dict[int, float]:
    prices = asyncio.run(get_all_cards_price_CGC([c.unique_name for c in cards]))
    return {c.id: p for c, p in zip(cards, prices) if p}

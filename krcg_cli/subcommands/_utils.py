import aiohttp
import argparse
import asyncio
import arrow
import itertools
import json
import logging
import math
import sys

import caseconverter
import unidecode

import krcg.cards
from krcg import deck
from krcg import twda
from krcg import vtes


def _init(with_twda=False):
    try:
        if not vtes.VTES:
            vtes.VTES.load()
            if with_twda:
                # if TWDA existed but VTES was not loaded, load TWDA anew
                twda.TWDA.load()
        if with_twda and not twda.TWDA:
            twda.TWDA.load()
    except:  # noqa: E722
        sys.stderr.write("Fail to initialize - check your Internet connection.\n")
        raise


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
    "Carlton Van Wyk": "carlton-van-wyk-hunter",
    "Jake Washington": "jake-washington-hunter",
    "Pentex™ Subversion": "pentex-subversion",
    "Kuyén": "kuyen-promo",
    "CrimethInc.": "crimethinc",
    "Mylan Horseed": "mylan-horseed-goblin",
    "Rego Motum": "rego-motus",
    "Nephandus": "nephandus-mage",
    "Veneficti": "veneficti-mage",
    "Wendell Delburton": "wendell-delburton-hunter",
    "Neighborhood Watch Commander": "neighborhood-watch-commander-hunter",
    "Ambrosius, The Ferryman": "ambrosius-the-ferryman-wraith",
    "Draeven Softfoot": "draeven-softfoot-changeling",
    "Shadow Court Satyr": "shadow-court-satyr-changeling",
    "Thadius Zho": "thadius-zho-mage",
    "Amam the Devourer": "amam-the-devourer-bane-mummy",
    "Akhenaten, The Sun Pharaoh": "akhenaten-the-sun-pharaoh-mummy",
    "Brigitte Gebauer": "brigitte-gebauer-wraith",
    "Masquer": "masquer-wraith",
    "Kherebutu": "kherebutu-bane-mummy",
    "Mehemet of the Ahl-i-Batin": "mehemet-of-the-ahl-i-batin-mage",
    "Dauntain Black Magician": "dauntain-black-magician-changeling",
    "The Meddling of Semsith": "meddling-of-semsith",
    "The Khabar: Community": "khabar-the-community",
    "SchreckNET": "schrecknet",
    "Praxis Seizure: Washington, D.C.": "praxis-seizure-washington-d-c",
    "Crusade: Washington, D.C.": "crusade-washington-d-c",
    "Powerbase: Washington, D.C.": "powerbase-washington-d-c",
    "Sacré-Cœur Cathedral, France": "sacre-cour-cathedral-france",
    "The Crimson Sentinel": "crimson-sentinel",
    "47th Street Royals": "47th-street-royal",
    "Kpist m/45": "kpist-m-45",
    "Antoinette DuChamp": "antoinette-duchamp",
    "Andre LeRoux": "andre-leroux",
    "Paul DiCarlo, The Alpha": "paul-dicarlo-the-alpha",
    "Tyler McGill": "tyler-mcgill",
    'Felix "Fix" Hessian': "felix-fix-hessian-wraith",
    "KoKo": "koko",
    "Ramiel DuPre": "ramiel-dupre",
    "T.J.": "t-j",
    'Xian "DziDzat155" Quan': "xian-dzidzat155-quan",
    "Navar McClaren": "navar-mcclaren",
    "Gilbert Duane (G6)": "gilbert-duane-2",
    "Kalinda (G6)": "kalinda-2",
    "Ruth McGinley": "ruth-mcginley",
    "Theo Bell (G6)": "theo-bell-2",
    "Michael diCarlo": "michael-dicarlo",
    "Sébastien Goulet": "sebastian-goulet",
    "Sébastien Goulet (ADV)": "sebastian-goulet-adv",
    "Evan Klein (G6)": "evan-klein-2",
    "The Dracon": "the-dracon-humble-bundle",
    "Tutu the Doubly Evil One": "tutu-the-doubly-evil-one-bane-mummy",
    "Maila": "maila-promo",
    "Hesha Ruhadze (G6)": "hesha-ruhadze-2",
    "Anarch Manifesto, An": "an-anarch-manifesto",
    "Redbone McCray": "redbone-mccray",
    "Abraham DuSable": "abraham-dusable",
    "Qetu the Evil Doer": "qetu-the-evil-doer-bane-mummy",
    "Meditative Grove": "mediative-grove",
    "Doris McMillon": "doris-mcmillon",
    "MacAlister Marshall": "macalister-marshall",
    'Anna "Dictatrix11" Suljic': "anna-dictatrixll-suljic",
    "Chester DuBois": "chester-dubois",
    "DeSalle": "desalle",
    "C.J.": "c-j",
    "Gerald FitzGerald": "gerald-fitzgerald",
}


def batched(iterable, n):
    # py 3.12 function
    # batched('ABCDEFG', 3) --> ABC DEF G
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
        CGC_GRAPHQL_URL, json={"query": query}, timeout=60
    ) as response:
        response.raise_for_status()
        result = await response.json()
    for error in result.get("errors") or []:
        # per-product errors (unknown slug) have a path, query errors do not
        level = logging.DEBUG if "path" in error else logging.WARNING
        logging.getLogger().log(level, "CGC price lookup: %s", error.get("message"))
    data = result.get("data") or {}
    return [cgc_product_price(data.get(f"p{i}")) for i in range(len(card_names))]


async def get_all_cards_price_CGC(card_names: list[str]) -> list[float | None]:
    prices = []
    async with aiohttp.ClientSession() as session:
        for batch in batched(card_names, n=50):
            try:
                prices.extend(await get_cards_price_CGC(session, batch))
            except (aiohttp.ClientError, TimeoutError, ValueError) as e:
                logging.getLogger().warning("CGC price lookup failed: %r", e)
                prices.extend([None] * len(batch))
    return prices


def add_price_option(parser):
    parser.add_argument(
        "--price",
        action="store_true",
        help="Display cards prices on the secondary market",
    )


def get_cards_prices(cards):
    prices = asyncio.run(get_all_cards_price_CGC([c.usual_name for c in cards]))
    return {c.id: p for c, p in zip(cards, prices) if p}


class NargsChoice(argparse.Action):
    """Choices with nargs +/*: this is a known issue for argparse
    cf. https://bugs.python.org/issue9625
    """

    CASE_SENSITIVE = False

    def get_choices(self): ...

    def __call__(self, parser, namespace, values, option_string=None):
        choices = self.get_choices()
        if not self.CASE_SENSITIVE:
            values = [v.lower() for v in values]
            choices = {c.lower() for c in choices}
        if values:
            for value in values:
                if value not in choices:
                    raise argparse.ArgumentError(
                        self,
                        f"invalid choice: {value} (choose from: "
                        f"{', '.join(self.get_choices())})",
                    )
        setattr(namespace, self.dest, values)


def add_twda_filters(parser):
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


def filter_twda(args) -> list[deck.Deck]:
    _init(with_twda=True)
    decks = list(twda.TWDA.values())
    if args.date_from:
        decks = [d for d in decks if d.date >= args.date_from]
    if args.date_to:
        decks = [d for d in decks if d.date < args.date_to]
    if args.players:
        decks = [d for d in decks if (d.players_count or 0) >= args.players]
    return decks


class DisciplineChoice(NargsChoice):
    CASE_SENSITIVE = True

    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["discipline"]


class ClanChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["clan"]

    # ALIASES = config.CLANS_AKA


class TypeChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["type"]


class TraitChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["trait"]


class GroupChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["group"]


class BonusChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["bonus"]


class CapacityChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["capacity"]


class SectChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["sect"]


class TitleChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["title"]


class CityChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["city"]


class SetChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["set"]


class RarityChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["rarity"]


class PreconChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["precon"]


class ArtistChoice(NargsChoice):
    @staticmethod
    def get_choices():
        return vtes.VTES.search_dimensions["artist"]


def add_card_filters(parser):
    parser.add_argument(
        "-d",
        "--discipline",
        action=DisciplineChoice,
        metavar="DISCIPLINE",
        nargs="+",
        help="Filter by discipline ({})".format(
            ", ".join(DisciplineChoice.get_choices())
        ),
    )
    parser.add_argument(
        "-c",
        "--clan",
        action=ClanChoice,
        metavar="CLAN",
        nargs="+",
        help="Filter by clan ({})".format(", ".join(ClanChoice.get_choices())),
    )
    parser.add_argument(
        "-t",
        "--type",
        action=TypeChoice,
        metavar="TYPE",
        nargs="+",
        help="Filter by type ({})".format(", ".join(TypeChoice.get_choices())),
    )
    parser.add_argument(
        "-g",
        "--group",
        action=GroupChoice,
        metavar="GROUP",
        nargs="+",
        help="Filter by group ({})".format(
            ", ".join(map(str, GroupChoice.get_choices()))
        ),
    )
    parser.add_argument(
        "-x",
        "--exclude-set",
        action=SetChoice,
        metavar="SET",
        nargs="+",
        help="Exclude given types ({})".format(", ".join(SetChoice.get_choices())),
    )
    parser.add_argument(
        "-e",
        "--exclude-type",
        action=TypeChoice,
        metavar="TYPE",
        nargs="+",
        help="Exclude given types ({})".format(", ".join(TypeChoice.get_choices())),
    )
    parser.add_argument(
        "-b",
        "--bonus",
        action=BonusChoice,
        metavar="BONUS",
        nargs="+",
        help="Filter by bonus ({})".format(", ".join(BonusChoice.get_choices())),
    )
    parser.add_argument(
        "--text",
        metavar="TEXT",
        nargs="+",
        help="Filter by text (including name and flavor text)",
    )
    parser.add_argument(
        "--trait",
        action=TraitChoice,
        metavar="TRAIT",
        nargs="+",
        help="Filter by trait ({})".format(", ".join(TraitChoice.get_choices())),
    )
    parser.add_argument(
        "--capacity",
        type=int,
        action=CapacityChoice,
        metavar="CAPACITY",
        nargs="+",
        help="Filter by capacity ({})".format(
            ", ".join(map(str, CapacityChoice.get_choices()))
        ),
    )
    parser.add_argument(
        "--set",
        action=SetChoice,
        metavar="SET",
        nargs="+",
        help="Filter by set",
    )
    parser.add_argument(
        "--sect",
        action=SectChoice,
        metavar="SECT",
        nargs="+",
        help="Filter by sect ({})".format(", ".join(SectChoice.get_choices())),
    )
    parser.add_argument(
        "--title",
        action=TitleChoice,
        metavar="TITLE",
        nargs="+",
        help="Filter by title ({})".format(", ".join(TitleChoice.get_choices())),
    )
    parser.add_argument(
        "--city",
        action=CityChoice,
        metavar="CITY",
        nargs="+",
        help="Filter by city",
    )
    parser.add_argument(
        "--rarity",
        action=RarityChoice,
        metavar="RARITY",
        nargs="+",
        help="Filter by rarity ({})".format(", ".join(RarityChoice.get_choices())),
    )
    parser.add_argument(
        "--precon",
        action=PreconChoice,
        metavar="PRECON",
        nargs="+",
        help="Filter by preconstructed starter",
    )
    parser.add_argument(
        "--artist",
        action=ArtistChoice,
        metavar="ARTIST",
        nargs="+",
        help="Filter by artist",
    )
    parser.add_argument(
        "--no-reprint",
        action="store_true",
        help="Filter our cards that are currently in print",
    )


def filter_cards(args):
    _init()
    args = {
        k: v
        for k, v in vars(args).items()
        if k
        in {
            "discipline",
            "clan",
            "type",
            "group",
            "exclude_set",
            "exclude_type",
            "no_reprint",
            "bonus",
            "text",
            "trait",
            "capacity",
            "set",
            "sect",
            "title",
            "city",
            "rarity",
            "precon",
            "artist",
        }
    }
    exclude_set = set(args.pop("exclude_set", None) or [])
    exclude_type = set(args.pop("exclude_type", None) or [])
    if args.pop("no_reprint", None):
        exclude_set |= {
            "Anthology",
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
            "Print on Demand",
            "Sabbat Preconstructed",
            "Shadows of Berlin",
            "Twenty-Fifth Anniversary",
        }
    args["text"] = " ".join(args.pop("text") or [])
    args = {k: v for k, v in args.items() if v}
    ret = set(vtes.VTES.search(**args))
    for exclude in exclude_type:
        ret -= set(vtes.VTES.search(type=[exclude]))
    for exclude in exclude_set:
        ret -= set(vtes.VTES.search(set=[exclude]))
    return ret


def typical_copies(A, card, naked=False):
    deviation = math.sqrt(A.variance[card])
    min_copies = max(1, round(A.average[card] - deviation))
    max_copies = max(1, round(A.average[card] + deviation))
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


def card_text(card: krcg.cards.Card, krcg_format: bool) -> str:
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
    if not krcg_format and card.group:
        text += "(g.{})".format(card.group)
    if card.burn_option:
        text += "(Burn Option)"
    if card.banned:
        text += " -- BANNED in " + card["Banned"]
    if not krcg_format:
        text += " -- (#{})".format(card.id)
    if card.crypt and card.disciplines:
        text += "\n{}".format(" ".join(card.disciplines) or "-- No discipline")
    text += "\n{}".format(card.card_text)
    return text

import aiohttp
import argparse
import asyncio
import arrow
import html.parser
import json
import logging
import math
import sys

import caseconverter
import unidecode

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


class CGCParser(html.parser.HTMLParser):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price = None
        self.in_price = False

    def handle_starttag(self, tag, attrs):
        if self.in_price:
            return
        if tag != "script":
            return
        id_ = dict(attrs).get("id")
        if id_ == "__NEXT_DATA__":
            self.in_price = True

    def handle_endtag(self, tag):
        if not self.in_price:
            return
        if tag != "script":
            return
        self.in_price = False

    def handle_data(self, data):
        if not self.in_price:
            return
        try:
            data = json.loads(data)
            main_price = data["props"]["pageProps"]["product"]["price"]
            if main_price:
                self.price = main_price
                return
            for node in data["props"]["pageProps"]["product"]["variations"]["nodes"]:
                if not self.price:
                    self.price = node["price"]
                else:
                    self.price = min(self.price, node["price"])
        except KeyError:
            logging.getLogger().exception("failed to parse: %s", data)


NAMES_MAP = {
    "Carlton Van Wyk": "carlton-van-wyk-hunter",
    "Jake Washington": "jake-washington-hunter",
    "Pentex™ Subversion": "pentex-subversion",
}


async def get_cards_price_CGC(card_names, result):
    async with aiohttp.ClientSession() as session:
        result.extend(
            await asyncio.gather(
                *(
                    get_card_price_CGC(
                        session,
                        "https://shop.cardgamegeek.com/shop/product/"
                        + NAMES_MAP.get(
                            name, caseconverter.kebabcase(unidecode.unidecode(name))
                        ),
                    )
                    for name in card_names
                ),
                return_exceptions=True,
            )
        )


async def get_card_price_CGC(session: aiohttp.ClientSession, url):
    async with session.get(url, timeout=30) as response:
        parser = CGCParser()
        index = await response.text()
        parser.feed(index)
        return parser.price


def add_price_option(parser):
    parser.add_argument(
        "--price",
        action="store_true",
        help="Display cards prices on the secondary market",
    )


def get_cards_prices(cards):
    prices = []
    asyncio.run(get_cards_price_CGC([c.usual_name for c in cards], prices))
    return {c.id: p for c, p in zip(cards, prices) if not isinstance(p, Exception)}


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

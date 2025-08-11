import aiohttp
import argparse
import asyncio
import arrow
import html.parser
import itertools
import json
import logging
import math
from typing import Iterable, Generator, TypeVar
import sys

import caseconverter
import unidecode

from krcg import cards
from krcg import deck
from krcg import twda
from krcg import vtes


def _init(with_twda: bool = False, international: bool = False) -> None:
    """Load krcg data.

    Args:
        with_twda: Also load TWDA dataset.
        international: Force loading translations (disable LOCAL_CARDS) and
            reload cards from VEKN/GitHub sources.
    """
    try:
        # If international view is requested, disable LOCAL_CARDS and force reload
        if international or with_twda:
            # Disable local mode and ensure a fresh load with translations
            # cards.LOCAL_CARDS is defined in krcg.cards
            cards.LOCAL_CARDS = None
            vtes.VTES.clear()

        if not vtes.VTES:
            # Prefer local CSV (offline) if available via LOCAL_CARDS=1
            try:
                vtes.VTES.load_from_vekn()
            except Exception:
                # Fallback to network static if local data is not bundled
                vtes.VTES.load()
        if with_twda:
            # Always reload TWDA to ensure consistent state across calls
            twda.TWDA.load()
    except:  # noqa: E722
        sys.stderr.write("Fail to initialize - check your Internet connection.\n")
        raise


class CGCParser(html.parser.HTMLParser):
    """Parse cards prices from https://shop.cardgamegeek.com pages."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.price: int | None = None
        self.in_price: bool = False

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
            print(main_price, type(main_price))
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
    "47th Street Royals": "47th-street-royal",
    "Akhenaten, The Sun Pharaoh": "akhenaten-the-sun-pharaoh-mummy",
    "Amam the Devourer": "amam-the-devourer-bane-mummy",
    "Ambrosius, The Ferryman": "ambrosius-the-ferryman-wraith",
    "Brigitte Gebauer": "brigitte-gebauer-wraith",
    "Carlton Van Wyk": "carlton-van-wyk-hunter",
    "CrimethInc.": "crimethinc",
    "Crusade: Washington, D.C.": "crusade-washington-d-c",
    "Dauntain Black Magician": "dauntain-black-magician-changeling",
    "Draeven Softfoot": "draeven-softfoot-changeling",
    "Jake Washington": "jake-washington-hunter",
    "Kherebutu": "kherebutu-bane-mummy",
    "Kpist m/45": "kpist-m-45",
    "Kuyén": "kuyen-promo",
    "Masquer": "masquer-wraith",
    "Mehemet of the Ahl-i-Batin": "mehemet-of-the-ahl-i-batin-mage",
    "Mylan Horseed": "mylan-horseed-goblin",
    "Neighborhood Watch Commander": "neighborhood-watch-commander-hunter",
    "Nephandus": "nephandus-mage",
    "Pentex™ Subversion": "pentex-subversion",
    "Powerbase: Washington, D.C.": "powerbase-washington-d-c",
    "Praxis Seizure: Washington, D.C.": "praxis-seizure-washington-d-c",
    "Rego Motum": "rego-motus",
    "Sacré-Cœur Cathedral, France": "sacre-cour-cathedral-france",
    "SchreckNET": "schrecknet",
    "Shadow Court Satyr": "shadow-court-satyr-changeling",
    "Thadius Zho": "thadius-zho-mage",
    "The Crimson Sentinel": "crimson-sentinel",
    "The Khabar: Community": "khabar-the-community",
    "The Meddling of Semsith": "meddling-of-semsith",
    "Veneficti": "veneficti-mage",
    "Wendell Delburton": "wendell-delburton-hunter",
}

T = TypeVar("T")


def batched(iterable: Iterable[T], n: int) -> Generator[Iterable[T], None, None]:
    """Batch iterable into chunks of size n.

    batched('ABCDEFG', 3) -> 'ABC', 'DEF', 'G'
    """
    it = iter(iterable)
    while batch := tuple(itertools.islice(it, n)):
        yield batch


async def get_cards_price_CGC(cards: Iterable[cards.Card]) -> dict[cards.Card, int]:
    """Get cards prices from shop.cardgamegeek.com."""
    result = []
    card_names = [
        NAMES_MAP.get(
            c.usual_name, caseconverter.kebabcase(unidecode.unidecode(c.usual_name))
        )
        for c in cards
    ]
    async with aiohttp.ClientSession() as session:
        for batch in batched(card_names, n=50):
            result.extend(
                await asyncio.gather(
                    *(
                        get_card_price_CGC(
                            session,
                            f"https://shop.cardgamegeek.com/shop/product/{name}",
                        )
                        for name in batch
                    ),
                    return_exceptions=True,
                )
            )
    return {
        c: p for c, p in zip(cards, result) if p and not isinstance(p, BaseException)
    }


async def get_card_price_CGC(
    session: aiohttp.ClientSession, url: str
) -> int | None | BaseException:
    """Get one card price from shop.cardgamegeek.com."""
    async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
        parser = CGCParser()
        index = await response.text()
        parser.feed(index)
        return parser.price


def add_price_option(parser: argparse.ArgumentParser) -> None:
    """Add --price option to parser."""
    parser.add_argument(
        "--price",
        action="store_true",
        help="Display cards prices on the secondary market",
    )


def get_cards_prices(cards: Iterable[cards.Card]) -> dict[cards.Card, int]:
    """Get cards prices from shop.cardgamegeek.com."""
    return asyncio.run(get_cards_price_CGC(cards))


def _get_dimension_choices(dimension: str) -> list[str]:
    """Return available values for a given search dimension.

    Ensures the VTES dataset is loaded before accessing dimensions.
    """
    if not vtes.VTES:
        _init()
    return vtes.VTES.search_dimensions.get(dimension, [])


class NargsChoice(argparse.Action):
    """Choices with nargs +/*: this is a known issue for argparse.

    cf. https://github.com/python/cpython/issues/53834 - to be fixed in 3.14
    """

    CASE_SENSITIVE = False

    def get_choices(self): ...

    def __call__(self, parser, namespace, values, option_string=None):
        """Call the action."""
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
    """Add --from, --to and --players options to parser."""
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


def filter_twda(args: argparse.Namespace) -> list[deck.Deck]:
    """Filter TWDA decks."""
    if not twda.TWDA:
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
    """Filter by discipline."""

    CASE_SENSITIVE = True

    @staticmethod
    def get_choices():
        return _get_dimension_choices("discipline")


class ClanChoice(NargsChoice):
    """Filter by clan."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("clan")


class TypeChoice(NargsChoice):
    """Filter by type."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("type")


class TraitChoice(NargsChoice):
    """Filter by trait."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("trait")


class GroupChoice(NargsChoice):
    """Filter by group."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("group")


class BonusChoice(NargsChoice):
    """Filter by bonus."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("bonus")


class CapacityChoice(NargsChoice):
    """Filter by capacity."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("capacity")


class SectChoice(NargsChoice):
    """Filter by sect."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("sect")


class TitleChoice(NargsChoice):
    """Filter by title."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("title")


class CityChoice(NargsChoice):
    """Filter by city."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("city")


class SetChoice(NargsChoice):
    """Filter by set."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("set")


class RarityChoice(NargsChoice):
    """Filter by rarity."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("rarity")


class PreconChoice(NargsChoice):
    """Filter by preconstructed starter."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("precon")


class ArtistChoice(NargsChoice):
    """Filter by artist."""

    @staticmethod
    def get_choices():
        return _get_dimension_choices("artist")


def add_card_filters(parser):
    """Add card filters to parser."""
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
    """Filter cards."""
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
    """Get typical number of copies of a card in a deck."""
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

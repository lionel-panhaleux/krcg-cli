import argparse
import arrow
import marshal
import math
import tempfile
import os
import sys

from krcg import twda
from krcg import vtes

VTES_FILE = os.path.join(tempfile.gettempdir(), "krcg-vtes.pyc")
TWDA_FILE = os.path.join(tempfile.gettempdir(), "krcg-twda.pyc")


def _init(with_twda=False):
    try:
        if not vtes.VTES:
            vtes.VTES.from_json(marshal.load(open(VTES_FILE, "rb")))
        if with_twda and not twda.TWDA:
            twda.TWDA.from_json(marshal.load(open(TWDA_FILE, "rb")))
    except FileNotFoundError:
        try:
            if not vtes.VTES:
                vtes.VTES.load()
            marshal.dump(vtes.VTES.to_json(), open(VTES_FILE, "wb"))
            if with_twda:
                # if TWDA existed but VTES was not loaded, load TWDA anew
                twda.TWDA.load()
                marshal.dump(twda.TWDA.to_json(), open(TWDA_FILE, "wb"))
        except:  # noqa: E722
            sys.stderr.write("Fail to initialize - check your Internet connection.\n")
            raise


class NargsChoice(argparse.Action):
    """Choices with nargs +/*: this is a known issue for argparse
    cf. https://bugs.python.org/issue9625
    """

    CASE_SENSITIVE = False

    def get_choices(self):
        ...

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


def filter_twda(args):
    _init(with_twda=True)
    decks = list(twda.TWDA.values())
    if args.date_from:
        decks = [d for d in decks if d.date >= args.date_from]
    if args.date_to:
        decks = [d for d in decks if d.date < args.date_to]
    if args.players:
        decks = [d for d in decks if d.players_count >= args.players]
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
            "exclude-type",
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
    exclude_type = args.pop("exclude_type", None)
    if exclude_type:
        args["type"] = list(
            args.get("type", set())
            | (set(TypeChoice.get_choices()) - set(exclude_type))
        )
    args["text"] = " ".join(args.pop("text") or [])
    args = {k: v for k, v in args.items() if v}
    return vtes.VTES.search(**args)


def typical_copies(A, card):
    deviation = math.sqrt(A.variance[card])
    min_copies = max(1, round(A.average[card] - deviation))
    max_copies = max(1, round(A.average[card] + deviation))
    if min_copies == max_copies:
        ret = f"{min_copies}"
    else:
        ret = f"{min_copies}-{max_copies}"
    if max_copies > 1:
        ret += " copies"
    else:
        ret += " copy"
    return ret

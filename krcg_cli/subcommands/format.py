"""Format a decklist."""

import contextlib
import pathlib
import sys

import msgspec

from krcg import parser as krcg_parser
from krcg import providers
from krcg import utils as krcg_utils

from . import _utils


def add_parser(parser):
    """Add the format subparser."""
    parser = parser.add_parser("format", help="format a decklist")
    parser.add_argument(
        "-f",
        "--format",
        help="Format",
        required=True,
        type=str.lower,
        choices=["jol", "twd", "lackey", "json"],
    )
    parser.add_argument(
        "infile",
        nargs="?",
        type=pathlib.Path,
        help="Input file. If not provided, read from standard input (stdin)",
    )
    parser.set_defaults(func=format)


def format(args):
    """Parse a decklist and print it in the requested format."""
    cards_db = _utils.get_cards()
    try:
        with contextlib.ExitStack() as stack:
            source = (
                stack.enter_context(args.infile.open()) if args.infile else sys.stdin
            )
            deck = krcg_parser.deck_from_txt(source, cards_db)
    except Exception as e:
        sys.stderr.write(f"Failed to parse decklist: {e}\n")
        return 1
    krcg_utils.sort_cards(deck)
    match args.format:
        case "json":
            print(msgspec.json.format(msgspec.json.encode(deck), indent=2).decode())
        case "twd":
            print(providers.serialize_twd(deck, cards_db))
        case "lackey":
            print(providers.serialize_lackey(deck))
        case "jol":
            print(providers.serialize_jol(deck))
    return 0

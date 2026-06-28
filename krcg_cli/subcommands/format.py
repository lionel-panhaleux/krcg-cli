"""Format a decklist."""

import json
import sys

from krcg import parser as krcg_parser
from krcg import providers

from . import _utils


def add_parser(parser):
    """Add parser for format subcommand."""
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
        metavar="FILE",
        help="Input file. If not provided, read from standard input (stdin)",
    )
    parser.set_defaults(func=format)


def format(args):
    """Format a decklist."""
    _utils._init()
    d = None
    try:
        if args.infile:
            with open(args.infile) as infile:
                d = krcg_parser.deck_from_txt(infile, _utils.VTES)
        else:
            d = krcg_parser.deck_from_txt(sys.stdin, _utils.VTES)
    except OSError as e:
        print(f"Failed to open decklist: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Failed to parse decklist: {e}", file=sys.stderr)
        return 1
    if not d or not d.cards:
        print("Empty or incorrect decklist", file=sys.stderr)
        return 1
    if args.format == "json":
        json.dump(
            providers.serialize_json_minimal(d),
            sys.stdout,
            ensure_ascii=False,
            indent=2,
        )
    elif args.format == "twd":
        print(providers.serialize_twd(d, _utils.VTES))
    elif args.format == "lackey":
        print(providers.serialize_lackey(d))
    elif args.format == "jol":
        print(providers.serialize_jol(d))
    return 0

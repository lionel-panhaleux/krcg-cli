import argparse
import json
import sys

from krcg import deck


def add_parser(parser):
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
        type=argparse.FileType("r"),
        default=sys.stdin,
        help="Input file. If not provided, read from standard input (stdin)",
    )
    parser.set_defaults(func=format)


def format(args):
    d = None
    try:
        d = deck.Deck.from_txt(args.infile)
    except Exception as e:
        sys.stderr.write(f"Failed to parse decklist: {e}")
    if args.format == "json":
        json.dump(d.to_json(), sys.stdout, ensure_ascii=False, indent=2)
    else:
        print(d.to_txt(format=args.format))

import argparse

from .subcommands import affinity
from .subcommands import build
from .subcommands import card
from .subcommands import complete
from .subcommands import deck
from .subcommands import format
from .subcommands import search
from .subcommands import seating
from .subcommands import stats
from .subcommands import top
from .subcommands import twd


parser = argparse.ArgumentParser(prog="krcg", description="VTES tool")
subparsers = parser.add_subparsers(metavar="", title="subcommands", dest="subcommand")
card.add_parser(subparsers)
complete.add_parser(subparsers)
search.add_parser(subparsers)
deck.add_parser(subparsers)
top.add_parser(subparsers)
affinity.add_parser(subparsers)
build.add_parser(subparsers)
format.add_parser(subparsers)
seating.add_parser(subparsers)
stats.add_parser(subparsers)
twd.add_parser(subparsers)


def execute(args):
    args = parser.parse_args(args)
    if not args.subcommand:
        parser.print_help()
        return 0
    return args.func(args)

import sys

from krcg import vtes

from . import _utils


def add_parser(parser):
    parser = parser.add_parser("complete", help="card name completion")
    parser.add_argument("-f", "--full", action="store_true", help="display cards text")
    parser.add_argument("name", metavar="NAME", help="parts of the name")
    parser.set_defaults(func=complete)


def complete(args):
    _utils._init()
    completions = vtes.VTES.complete(args.name)
    if not completions:
        sys.stderr.write("No match\n")
        return 1
    print("\n".join(completions))
    return 0

import sys


from . import _utils


def add_parser(parser):
    _utils._init()
    parser = parser.add_parser("search", help="search card")
    parser.add_argument(
        "-n",
        "--number",
        type=int,
        default=10,
        help="Number of cards to print (default 10)",
    )
    _utils.add_card_filters(parser)
    parser.set_defaults(func=search)


def search(args):
    results = _utils.filter_cards(args)
    if not results:
        sys.stderr.write("No match\n")
        return 1
    results = sorted(c.usual_name for c in results)
    if args.number and args.number < len(results):
        full = len(results)
        results = results[: args.number]
        results.append(
            f"... {full - args.number} more results, use -n {full} to display them."
        )
    print("\n".join(results))
    return 0

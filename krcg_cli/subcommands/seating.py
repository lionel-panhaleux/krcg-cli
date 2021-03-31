import collections
import functools
import itertools
import multiprocessing
import sys

from krcg import seating


def add_parser(parser):
    parser = parser.add_parser("seating", help="compute optimal seating")
    parser.add_argument(
        "players",
        type=int,
        metavar="PLAYERS",
        help=("Number of players."),
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=3,
        help=(
            "Number of rounds, "
            "if this argument is used the [players] argument can only appear once"
        ),
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=80000,
        help="Number of iterations to use (less is faster but may yield worse results)",
    )
    parser.add_argument(
        "--remove",
        type=lambda s: tuple((int(x) for x in s.split(":"))),
        nargs="*",
        metavar="ROUND:PLAYER",
        help=(
            "Remove given player, starting from given round. "
            "Format is '[round]:[player]'"
        ),
    )
    parser.add_argument(
        "--add",
        type=int,
        nargs="*",
        metavar="ROUND",
        help="Add a player, starting from given round.",
    )
    parser.set_defaults(func=seat)


POSITIONS = {
    1: "prey",
    2: "grand-prey",
    3: "grand-predator",
    4: "predator",
    5: "cross-table",
}

GROUPS = {
    1: "adjacent",
    2: "non-adjacent",
}


def progression(iterations, step):
    print(f"\t{step / iterations * 100:.0f}%", file=sys.stderr, end="\r")


def seat(args):
    players = args.players
    if args.rounds:
        permutations = seating.permutations(players, args.rounds)
    else:
        permutations = [list(range(1, p + 1)) for p in players]

    # addition/removal is a bit tricy
    # we add/remove all players at once: 10<->11 is difficult, but 10<->12 works
    # we use seating.permutations: seating 6, 7 or 11 players
    # might still be doable by adding more rounds, if there are enough rounds left.
    # if you began interlaced rounds for 6, 7 or 11 players,
    # additions and removals are not doable.
    if args.players in [6, 7, 11] and args.add:
        print(f"cannot add players to {args.players} players", file=sys.stderr)
        return 1
    additions = collections.Counter(args.add or [])
    for round_, count in sorted(additions.items()):
        players += count
        permutations = permutations[: round_ - 1] + seating.permutations(
            players, args.rounds - round_ + 1
        )
    if args.players in [6, 7, 11] and args.remove:
        print(f"cannot remove players from {args.players} players", file=sys.stderr)
        return 1

    # removal
    removals = collections.defaultdict(set)
    for round_, player in args.remove or []:
        removals[round_].add(player)
    removed_players = []
    for round_, removed in sorted(removals.items()):
        # make sure we are removing players that were playing
        absent = removed - set(
            p for p in itertools.chain.from_iterable(permutations[round_ - 1 :])
        )
        if absent:
            print(
                f"trying to remove {absent} starting from round {round_}, "
                "but they're absent",
                file=sys.stderr,
            )
            return 1
        players -= len(removed)
        removed_players.extend(removed)
        try:
            permutations = permutations[: round_ - 1] + seating.permutations(
                players, args.rounds - round_ + 1
            )
        except RuntimeError:
            print(
                f"removal in round {round_} " "yields an invalid number of players.",
                file=sys.stderr,
            ),
            return 1
        # since seating.permutations assigns a "normal" range of player numbers
        # we need to replace the removed numbers by the right ones
        for i, player in enumerate(removed_players):
            for permutation in permutations[round_ - 1 :]:
                try:
                    # careful, this has to be stable: removed_players list is in round order
                    permutation[permutation.index(player)] = (
                        players + len(removed_players) - i
                    )
                except ValueError:
                    pass

    try:
        cpus = multiprocessing.cpu_count()
    except NotImplementedError:
        cpus = 1
    with multiprocessing.Pool(processes=cpus) as pool:
        results = [
            pool.apply_async(
                seating.optimise,
                (
                    permutations,
                    args.iterations,
                    functools.partial(progression, args.iterations),
                ),
            )
            for _ in range(cpus)
        ]
        rounds, score = min((r.get() for r in results), key=lambda x: x[1].total)

    for i, round_ in enumerate(rounds, 1):
        print(f"Round {i}: {round_}")
    print(f"Total score: {score.total:.2f}")
    for index, (code, label, _) in enumerate(seating.RULES):
        s = f"{code} {score.rules[index]:6.2f} "
        if score.rules[index]:
            s += f"NOK ({label}): {format_anomalies(score, code)}"
        else:
            s += f" OK ({label})"
        print(s)
    return 0


def format_anomalies(score, code):
    anomalies = getattr(score, code)
    if code in ["R1", "R2", "R4"]:
        return ", ".join(f"{a}-{b}" for a, b in anomalies)
    if code == "R3":
        return partition(score.vps, score.mean_vps)
    if code == "R5":
        return ", ".join(f"{player} twice" for player in anomalies)
    if code == "R6":
        return ", ".join(
            f"{p2} is {p1} {POSITIONS[p]} twice" for p1, p2, p in anomalies
        )
    if code == "R7":
        return ", ".join(f"{player} seats {seat} twice" for player, seat in anomalies)
    if code == "R8":
        return partition(score.transfers, score.mean_transfers)
    if code == "R9":
        return ", ".join(f"{p1} is {p2} {GROUPS[g]} twice" for p1, p2, g in anomalies)
    raise RuntimeError(f"unknown rule {code}")


def partition(anomalies, mean):
    partitions = collections.defaultdict(list)
    for player, value in anomalies:
        partitions[value].append(player)
    return f"mean is {mean:.2f}, " + ", ".join(
        f"{players} {'has' if len(players) < 2 else 'have'} {value}"
        for value, players in sorted(partitions.items())
    )

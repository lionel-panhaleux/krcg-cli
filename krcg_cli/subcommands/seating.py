import argparse
import collections
import multiprocessing
import multiprocessing.shared_memory
import sys

from krcg import seating


def add_parser(parser):
    parser = parser.add_parser(
        "seating",
        help="compute optimal seating",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            """Optimal seating is useful for tournament play.
An optimal seating follows the rules established by the Rules Director, see
https://groups.google.com/g/rec.games.trading-cards.jyhad/c/4YivYLDVYQc/m/CCH-ZBU5UiUJ

The output is a normalised comma-separated list of players, one line per round
Tables of 5 are first, tables of 4, if any, are last.
For example, 1,2,3,4,5,6,7,8,9,10,11,12,13 unambiguously means:
[1, 2, 3, 4, 5], [6, 7, 8, 9], [10, 11, 12, 13]

Use the -v option to display the table structure for each round.
The comma-separated normal form can be used as input of the command
to indicate rounds that have already been played.
This allows for players list modifications during a tournament. For example:

$ krcg seating --played 1,2,3,4,5,6,7,8,9 --remove 4

will output a new seating with the played round left untouched,
and the next 2 rounds without player 4.

Seating for 6, 7 or 11 players required multiple intertwined rounds.
For example, for 6 players to play 2 rounds each, 3 rounds are required
with some players sitting out on each of them:

$ krcg seating --rounds 2 6
2,6,1,4
4,1,5,3
3,5,6,2

This can also be the case when you remove players and come down to 6, 7, or 11 players.
The command will accomodate if they are enough rounds left for intertwined rounds:

$ krcg seating --played 1,2,3,4,5,6,7,8,9 --remove 4 5

Note that when you began to play such intertwined rounds, you cannot modify
the players list in the middle of them. Trying to use the command in this case will
yield unusable seatings listing only the players of the last round.
"""
        ),
    )
    parser.add_argument(
        "players",
        type=int,
        nargs="?",
        metavar="PLAYERS",
        help=("Number of players."),
    )
    parser.add_argument(
        "-r",
        "--rounds",
        type=int,
        default=3,
        help=("Number of rounds"),
    )
    parser.add_argument(
        "-i",
        "--iterations",
        type=int,
        default=80000,
        help="Number of iterations to use (less is faster but may yield worse results)",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=argparse.FileType("a"),
        default=sys.stdout,
        help="File to append the result to",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Display seating tables and statistics",
    )
    parser.add_argument(
        "--archon",
        action="store_true",
        help="Display Archon-compatible seating lines (empty cell for empty 5th seat)",
    )
    parser.add_argument(
        "-p",
        "--played",
        type=lambda s: seating.Round.from_players([int(x) for x in s.split(",") if x]),
        nargs="*",
        metavar="ROUND",
        help="Rounds that have already been played",
    )
    parser.add_argument(
        "--remove",
        type=int,
        nargs="*",
        metavar="PLAYER",
        help="Remove given players",
    )
    parser.add_argument(
        "--add",
        type=int,
        nargs="*",
        metavar="PLAYER",
        help="Add given players",
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


class Progression:
    def __init__(self, iterations: int):
        self.iterations = iterations

    def callback(self, step, **kwargs):
        print(f"\t{step / self.iterations * 100:.0f}%", file=sys.stderr, end="\r")


def seat(options):
    if options.players and options.played:
        print(
            "the [played] and [players] arguments cannot be used both", file=sys.stderr
        )
        return 1
    if not options.players and not options.played:
        print("one of [played] or [players] arguments must be used", file=sys.stderr)
        return 1

    if options.players:
        players = set(range(1, options.players + 1))
        rounds_count = options.rounds
    else:
        players = set(options.played[-1].iter_players())
        rounds_count = options.rounds - len(options.played)

    for player in options.add or []:
        if player in players:
            print(
                f"trying to add {player} but they are already in",
                file=sys.stderr,
            )
        players.add(player)
    for player in options.remove or []:
        if player not in players:
            print(
                f"trying to remove {player} but they are absent",
                file=sys.stderr,
            )
        players.remove(player)

    try:
        rounds = seating.get_rounds(list(players), rounds_count)
    except RuntimeError:
        print(
            "seating cannot be arranged - more rounds or players required",
            file=sys.stderr,
        )
        return 1

    if options.played:
        rounds = options.played + rounds

    if rounds_count > 0:
        progression = Progression(options.iterations)
        try:
            cpus = min(4, multiprocessing.cpu_count())
        except NotImplementedError:
            cpus = 1
        with multiprocessing.Pool(processes=cpus) as pool:
            results = [
                pool.apply_async(
                    seating.optimise,
                    kwds=dict(
                        rounds=rounds,
                        iterations=options.iterations,
                        fixed=max(1, len(options.played or [])),
                        callback=progression.callback,
                    ),
                )
                for _ in range(cpus)
            ]
            rounds, score = min((r.get() for r in results), key=lambda x: x[1].total)
            print("", file=sys.stderr, end="")
    else:
        score = seating.Score(rounds)
    if options.archon:
        print(f"{len(players)}\tPlayers", file=options.output)
    for i, round_ in enumerate(rounds, 1):
        delimiter = ","
        if options.archon:
            delimiter = "\t"
            for table in round_:
                if len(table) == 4:
                    table.append("")
            print(f"\tRound {i}", file=options.output, end="\t")
        print(
            delimiter.join(str(p) for p in round_.iter_players()),
            file=options.output,
        )

    if not options.verbose:
        return 0
    print(
        f"\n------------------- details ({len(players)} players) -------------------",
        file=options.output,
    )
    for i, round_ in enumerate(rounds, 1):
        print(f"Round {i}: {round_}", file=options.output)
    for index, (code, label, _) in enumerate(seating.RULES):
        s = f"{code} {score.rules[index]:6.2f} "
        if score.rules[index]:
            s += f"NOK ({label}): {format_anomalies(score, code)}"
        else:
            s += f" OK ({label})"
        print(s, file=options.output)
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

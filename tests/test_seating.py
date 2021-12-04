from krcg_cli.parser import execute as cli_execute


def test_base(capsys):
    #
    # Base usage, defaults to 3 rounds
    #
    cli_execute("seating -i 1 12".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    assert set(int(i) for i in outerr.out.split()[0].split(",")) == set(range(1, 13))
    assert set(int(i) for i in outerr.out.split()[1].split(",")) == set(range(1, 13))
    assert set(int(i) for i in outerr.out.split()[2].split(",")) == set(range(1, 13))
    #
    # Two rounds
    #
    cli_execute("seating -i 1 -r 2 12".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    assert set(int(i) for i in outerr.out.split()[0].split(",")) == set(range(1, 13))
    assert set(int(i) for i in outerr.out.split()[1].split(",")) == set(range(1, 13))
    #
    # Two rounds for six players results in three intertwined rounds with sit outs
    #
    cli_execute("seating -i 1 -r 2 6".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    players = set(range(1, 7))
    assert set(int(i) for i in outerr.out.split()[0].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[1].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[2].split(",")).issubset(players)


def test_add_remove(capsys):
    #
    # Adding and removing players after first round have been played
    #
    cli_execute(
        "seating -i 1 -p 1,2,3,4,5,6,7,8,9,10,11,12 --add 13 14 --remove 5".split()
    )
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    # played round is left untouched
    assert outerr.out.split()[0] == "1,2,3,4,5,6,7,8,9,10,11,12"
    # other rounds have new players
    players = (set(range(1, 13)) - {5}) | {13, 14}
    assert set(int(i) for i in outerr.out.split()[1].split(",")) == players
    assert set(int(i) for i in outerr.out.split()[2].split(",")) == players
    #
    # Down to 11 players with 2 rounds left is doable, it adds a round
    #
    cli_execute("seating -i 1 -p 1,2,3,4,5,6,7,8,9,10,11,12 --remove 5".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    assert outerr.out.split()[0] == "1,2,3,4,5,6,7,8,9,10,11,12"
    players = set(range(1, 13)) - {5}
    assert set(int(i) for i in outerr.out.split()[1].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[2].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[3].split(",")).issubset(players)
    #
    # Down to 7 players with 2 rounds left is doable too
    #
    cli_execute("seating -i 1 -p 1,2,3,4,5,6,7,8,9 --remove 4 5".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    assert outerr.out.split()[0] == "1,2,3,4,5,6,7,8,9"
    players = set(range(1, 10)) - {4, 5}
    assert set(int(i) for i in outerr.out.split()[1].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[2].split(",")).issubset(players)
    assert set(int(i) for i in outerr.out.split()[3].split(",")).issubset(players)
    #
    # down to 11 players with a single round left to play is impossible
    #
    cli_execute(
        (
            "seating -i 1 -p 1,2,3,4,5,6,7,8,9,10,11,12 "
            "12,11,10,9,8,7,6,5,4,3,2,1 --remove 5"
        ).split()
    )
    outerr = capsys.readouterr()
    assert (
        outerr.err == "seating cannot be arranged - more rounds or players required\n"
    )
    assert outerr.out == ""
    #
    # but 10 players with a single round is OK
    #
    cli_execute(
        (
            "seating -i 1 -p 1,2,3,4,5,6,7,8,9,10,11,12 "
            "12,11,10,9,8,7,6,5,4,3,2,1 --remove 5 6"
        ).split()
    )
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out
    assert outerr.out.split()[0] == "1,2,3,4,5,6,7,8,9,10,11,12"
    assert outerr.out.split()[1] == "12,11,10,9,8,7,6,5,4,3,2,1"
    players = set(range(1, 13)) - {5, 6}
    assert set(int(i) for i in outerr.out.split()[2].split(",")) == players


def test_simple_scoring(capsys):
    cli_execute(
        (
            "seating -vi 0 -p " "1,2,3,4,5,6,7,8,9 2,5,7,1,8,9,4,6,3 4,1,9,7,2,8,3,5,6"
        ).split()
    )
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out == (
        "1,2,3,4,5,6,7,8,9\n"
        "2,5,7,1,8,9,4,6,3\n"
        "4,1,9,7,2,8,3,5,6\n"
        "--------------------------------- details ---------------------------------\n"
        "Round 1: [[1, 2, 3, 4, 5], [6, 7, 8, 9]]\n"
        "Round 2: [[2, 5, 7, 1, 8], [9, 4, 6, 3]]\n"
        "Round 3: [[4, 1, 9, 7, 2], [8, 3, 5, 6]]\n"
        "R1   0.00  OK (predator-prey)\n"
        "R2   1.00 NOK (opponent thrice): 1-2\n"
        "R3   0.31 NOK (available vps): mean is 4.56, [6] has 4.0, [1, 2] have 5.0\n"
        "R4  16.00 NOK (opponent twice): 1-2, 1-4, 1-5, 1-7, 2-4, 2-5, 2-7, "
        "3-4, 3-5, 3-6, 4-9, 5-8, 6-8, 6-9, 7-8, 7-9\n"
        "R5   0.00  OK (fifth seat)\n"
        "R6   0.00  OK (position)\n"
        "R7   0.00  OK (same seat)\n"
        "R8   0.27 NOK (starting transfers): mean is 2.67, [3, 5, 7] have 3.0\n"
        "R9   2.00 NOK (position group): 1 is 2 non-adjacent twice, "
        "5 is 8 non-adjacent twice\n"
    )

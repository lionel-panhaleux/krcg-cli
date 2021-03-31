from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute("seating -i 1 12".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out[:55] == "Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\n"
    cli_execute("seating -i 1 -r 2 12".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out[:55] == "Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\n"
    cli_execute("seating -i 1 -r 3 12 --add 2 2 3".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out[:55] == "Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\n"
    cli_execute("seating -i 1 -r 3 12 --remove 2:4 2:7".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out[:55] == "Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\n"
    cli_execute("seating -i 1 -r 3 12 --remove 2:4".split())
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert outerr.out[:55] == "Round 1: [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]\n"
    cli_execute("seating -i 1 -r 3 12 --remove 3:4".split())
    outerr = capsys.readouterr()
    assert outerr.err == "removal in round 3 yields an invalid number of players.\n"
    assert outerr.out[:55] == ""

import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    code, out, err = cli("deck", "2010tcdbng")
    assert code == 0
    assert err == ""
    snapshot("deck-2010tcdbng", out)
    for name, args in {
        "deck-fame-2019-25-players": [
            "--from",
            "2019-01-01",
            "--to",
            "2020-01-01",
            "--players",
            "25",
            "Fame",
        ],
        "deck-rudolf-scholz": ["--to", "2020-01-01", "Rudolf Scholz"],
        "deck-2018-50-players": ["--from", "2018", "--to", "2019", "--players", "50"],
    }.items():
        code, out, err = cli("deck", *args)
        assert code == 0, name
        assert err == "", name
        snapshot(name, out)


def test_not_found(cli):
    assert cli("deck", "foobar") == (
        1,
        "",
        '"foobar" did not match a deck #, card or author',
    )

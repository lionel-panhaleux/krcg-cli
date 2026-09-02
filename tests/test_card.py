import pytest


def test_base(cli, snapshot):
    code, out, err = cli("card", "krcg")
    assert code == 0
    assert err == ""
    snapshot("card-krcg", out)


@pytest.mark.baseline
def test_international(cli, snapshot):
    code, out, err = cli("card", "--international", ".44 Magnum")
    assert code == 0
    assert err == ""
    snapshot("card-international-44-magnum", out)


def test_short(cli):
    assert cli("card", "--short", "alastor") == (0, "Alastor\n", "")
    assert cli("card", "-s", "100001") == (0, ".44 Magnum\n", "")
    assert cli("card", "-k", "-s", "100001") == (0, "100001|.44 Magnum\n", "")


def test_text(cli, snapshot):
    code, out, err = cli("card", "--text", "alastor")
    assert code == 0
    assert err == ""
    snapshot("card-text-alastor", out)
    code, out, err = cli("card", "-t", ".44 Magnum", "Alastor")
    assert code == 0
    assert err == ""
    snapshot("card-text-multi", out)


@pytest.mark.baseline
def test_links(cli, snapshot):
    code, out, err = cli("card", "--links", "alastor")
    assert code == 0
    assert err == ""
    snapshot("card-links-alastor", out)


def test_not_found(cli):
    assert cli("card", "foobar") == (1, "", "Card not found\n")

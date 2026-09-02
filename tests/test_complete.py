import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    code, out, err = cli("complete", "Pentex")
    assert code == 0
    assert err == ""
    snapshot("complete-pentex", out)


def test_no_match(cli):
    assert cli("complete", "xyzzyfoo") == (1, "", "No match\n")

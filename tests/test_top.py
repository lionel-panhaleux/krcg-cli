import pytest


@pytest.mark.baseline
def test(cli, snapshot):
    code, out, err = cli("top", "--from", "2015", "--to", "2020", "-d", "ani")
    assert code == 0
    assert err == ""
    snapshot("top-ani-2015-2020", out)
    code, out, err = cli(
        "top", "-n", "3", "-o", "csv", "--from", "2020", "-c", "brujah"
    )
    assert code == 0
    assert err == ""
    snapshot("top-csv-brujah-2020", out)

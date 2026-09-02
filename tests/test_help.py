"""Test the top-level help."""


def test(cli, snapshot):
    """Snapshot the help output."""
    code, out, err = cli()
    assert code == 0
    assert err == ""
    snapshot("help", out)

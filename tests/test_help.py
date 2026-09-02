def test(cli, snapshot):
    code, out, err = cli()
    assert code == 0
    assert err == ""
    snapshot("help", out)

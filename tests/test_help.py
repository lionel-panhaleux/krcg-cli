from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute([])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """usage: krcg [-h]  ...

VTES tool

optional arguments:
  -h, --help  show this help message and exit

subcommands:
  
    card      show cards
    complete  card name completion
    search    search card
    deck      show TWDA decks
    top       display top cards (most played)
    affinity  display cards affinity (most played together)
    build     build a deck around given card(s), based on the TWDA
    format    format a decklist
    seating   compute optimal seating
    stats     compute stats on a deck archive
"""  # noqa: W293
    )

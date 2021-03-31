from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute(["top", "--from", "2015", "--to", "2020", "-d", "ani"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Carrion Crows                  (played in 71 decks, typically 5-10 copies)
Cats' Guidance                 (played in 69 decks, typically 2-6 copies)
Deep Song                      (played in 57 decks, typically 3-10 copies)
Sense the Savage Way           (played in 55 decks, typically 2-7 copies)
Canine Horde                   (played in 53 decks, typically 1-2 copies)
Raven Spy                      (played in 47 decks, typically 1-5 copies)
Aid from Bats                  (played in 43 decks, typically 6-14 copies)
Army of Rats                   (played in 39 decks, typically 1-2 copies)
Guard Dogs                     (played in 30 decks, typically 1-4 copies)
Beetleman                      (played in 29 decks, typically 1 copy)
"""
    )

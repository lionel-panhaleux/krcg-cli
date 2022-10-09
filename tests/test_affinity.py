from krcg_cli.parser import execute as cli_execute


def test(capsys):
    cli_execute(["affinity", "--from", "2015", "--to", "2020", "Fame"])
    outerr = capsys.readouterr()
    assert outerr.err == ""
    assert (
        outerr.out
        == """Taste of Vitae                 (in 61% of decks, typically 3-5 copies)
Powerbase: Montreal            (in 44% of decks, typically 1 copy)
Haven Uncovered                (in 37% of decks, typically 1-4 copies)
Target Vitals                  (in 37% of decks, typically 2-5 copies)
Anarch Convert                 (in 36% of decks, typically 3-5 copies)
Cats' Guidance                 (in 36% of decks, typically 2-5 copies)
Ashur Tablets                  (in 35% of decks, typically 6-11 copies)
Carrion Crows                  (in 35% of decks, typically 7-11 copies)
Archon Investigation           (in 33% of decks, typically 1 copy)
Deep Song                      (in 32% of decks, typically 5-11 copies)
The Parthenon                  (in 31% of decks, typically 1-4 copies)
Canine Horde                   (in 30% of decks, typically 1-3 copies)
Anarch Revolt                  (in 28% of decks, typically 3-9 copies)
Aid from Bats                  (in 28% of decks, typically 9-15 copies)
Stick                          (in 26% of decks, typically 1 copy)
The Rack                       (in 25% of decks, typically 1 copy)
Dragonbound                    (in 25% of decks, typically 1 copy)
Beetleman                      (in 25% of decks, typically 1 copy)
The Unmasking                  (in 25% of decks, typically 1-2 copies)
"""
    )
    cli_execute(["affinity", "Foobar"])
    outerr = capsys.readouterr()
    assert outerr.err == "Card not found: foobar\n"
    assert outerr.out == ""

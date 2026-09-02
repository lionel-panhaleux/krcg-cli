3.0 (unreleased)
----------------

- Migrate to krcg 5 (Python 3.14+). Cards, rulings and the TWDA ship with krcg:
  the CLI works offline, only the `--price` option needs an Internet connection.
- Fix the `--price` option of the `top` command (CGC shop GraphQL API)
- Add `--output full` to the `top` command (cards text)
- Add the `--price` option to the `card` command
- `card --links` lists the rulings references once, after the rulings
- Set filters (`--set`, `--exclude-set`) accept set names or codes
- Group filter (`--group`) accepts bare numbers
- `format --format json` outputs the krcg deck JSON
- Packaging: uv, just and ruff replace pip, make and black


2.8 (2024-02-08)
----------------

- Fixed minor issues with the `seating` command


2.7 (2024-02-08)
----------------

- Fix card filtering commands
- Add `stats` command
- Add `seating` command
- Add `twd` command
- Add --price option to the `top` command
- Packaging: PEP 517 toml Packaging

2.6 (2022-08-24)
----------------

- Additional options for technical interfaces (csv, krcg format)


2.5 (2021-12-04)
----------------

- Slight changes (retro-compatible) to handle V5 Anarch
- Adapted to seating algorithm changes


2.4 (2021-07-09)
----------------

- Improve logging


2.3 (2021-07-09)
----------------

- Improve logging
- Seating command: option to output an archon file compatible structure


2.2 (2021-04-02)
----------------

- New seating subcommand


2.1 (2020-12-20)
----------------

- Register on PyPI


2.0 (2020-12-20)
----------------

#!/usr/bin/env python3
"""VTES tool."""

import logging
import os
import sys

# Prefer offline local CSV/rulings from the `cards` package by default.
# Users can override by exporting LOCAL_CARDS="0".
os.environ.setdefault("LOCAL_CARDS", "1")

from . import parser


def main():
    """Entry point for the CLI."""
    logging.basicConfig(level=logging.INFO, format="[%(levelname)7s] %(message)s")
    exit(parser.execute(sys.argv[1:]))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import logging
import sys

from . import parser


def main():
    logging.basicConfig(level=logging.INFO, format="[%(levelname)7s] %(message)s")
    exit(parser.execute(sys.argv[1:]))


if __name__ == "__main__":
    main()

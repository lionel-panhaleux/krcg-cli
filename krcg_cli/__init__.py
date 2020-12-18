#!/usr/bin/env python3
import sys

from . import parser


def main():
    exit(parser.execute(sys.argv[1:]))


if __name__ == "__main__":
    main()

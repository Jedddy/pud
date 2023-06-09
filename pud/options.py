import argparse
from typing import Sequence


def get_args(argv: Sequence[str]):
    parser = argparse.ArgumentParser(
        prog="pud",
        allow_abbrev=False
    )

    parser.add_argument(
        "--cursor",
        default="=>",
        help="The cursor to use."
    )

    parser.add_argument(
        "--no-keep-state",
        default=False,
        help="Whether not to keep the cursor state after entering/leaving a directory.",
        action="store_true"
    )

    return parser.parse_known_args(argv)

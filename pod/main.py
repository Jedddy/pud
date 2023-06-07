import argparse
import curses

from .app import App


def main():
    parser = argparse.ArgumentParser(
        prog="pod",
        allow_abbrev=False
    )

    parser.add_argument(
        "--cursor",
        default="=>",
        help="The cursor to use."
    )

    args = parser.parse_args()
    print(args)
    app = App(cursor=args.cursor)
    curses.wrapper(app)


if __name__ == "__main__":
    main()

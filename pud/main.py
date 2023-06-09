import curses
import sys

from .app import App
from .options import get_args


def main():
    args, _ = get_args(sys.argv[1:])

    app = App(cursor=args.cursor, keep_cursor_state=not args.no_keep_state)
    curses.wrapper(app)


if __name__ == "__main__":
    main()

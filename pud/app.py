from __future__ import annotations

import curses
from pathlib import Path

from .entity import Entity
from .handlers import DirectoryExplorer


KEY_UP = (curses.KEY_UP, 450, ord('w'))
KEY_DOWN = (curses.KEY_DOWN, 456, ord('s'))
ENTER = (curses.KEY_ENTER, curses.KEY_RIGHT, 454, ord('\n'), ord('\r'), ord('d'))
SCROLL_UP = (65536,)
SCROLL_DOWN = (2097152,)
QUIT = (27, ord('q'))
GO_BACK = (curses.KEY_LEFT, 452, 260, ord('b'), ord('a'))


class App:
    """The main application for displaying folders and selecting directories.

    Attributes
    ----------
    cursor:
        The cursor to use to point to a currently selected folder or file.

    keep_cursor_state:
        Whether to keep the cursor state when entering/leaving a directory.

    idx:
        The index of the cursor on the list of entities.

    offset:
        The offset of the display screen from the top of the file.

    screen_idx:
        The index of the cursor on the screen.

    explorer:
        The directory handler.

    cursor_stack:
        The cursor stack used to 'remember' the past cursor placement before
        entering a new directory. It is a tuple of 3 items.
        (offset, index, screen_index)

        `offset` is the offset of the display screen from the top of the file list.
        `index` is the index of the cursor.
        `screen_index` is the index of the cursor on the screen.

    screen:
        A curses window.

    coords:
        The coords of current file entries on the screen.
    """

    screen: "curses._CursesWindow"
    coords: list[tuple[str, range, int]]

    def __init__(self, cursor: str, keep_cursor_state: bool):
        self.cursor = cursor.strip()
        self.keep_cursor_state = keep_cursor_state
        self.idx = 0
        self.offset = 0
        self.screen_idx = 0
        self.explorer = DirectoryExplorer(Path().cwd())
        self.cursor_stack = [(0, 0, 0) for _ in self.explorer.cwd.parts]

    def __call__(self, screen: "curses._CursesWindow"):
        curses.curs_set(0)
        curses.mousemask(-1)
        curses.start_color()
        curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
        screen.keypad(True)
        self.screen = screen

        try:
            self._run()
        except KeyboardInterrupt:
            return

    def reset_state(self) -> None:
        """Resets the states."""

        self.idx = 0
        self.offset = 0
        self.screen_idx = 0

    def get_files(self) -> tuple[tuple[int, Entity], ...]:
        """Gets all the files from the current working directory and stores it in a list."""

        files = self.explorer.list_files()

        if files is None:
            files = []
            message = "Permission Denied."
            maxy, maxx = self.screen.getmaxyx()
            self.screen.addstr(maxy // 2, (maxx // 2) - (len(message) // 2), message)

        elif len(files) == 0:
            message = "Directory Empty."
            self.maxy, maxx = self.screen.getmaxyx()
            self.screen.addstr(self.maxy // 2, (maxx // 2) - (len(message) // 2), message)

        ret = sorted(files, key=lambda f: f.is_file)
        return tuple(enumerate(ret))

    def show_help(self):
        """Shows the help window."""

        maxy, maxx = self.screen.getmaxyx()
        size_y, size_x = maxy // 2, maxx // 2
        win = curses.newwin(size_y, size_x, maxy // 4 , maxx // 4)
        win.bkgd(" ", curses.color_pair(1))
        win.box()

        win_maxy, win_maxx = win.getmaxyx()

        win.addstr(0, (win_maxx // 2) - 2, "Help")
        action_col = win_maxx // 2

        y = 1
        win.addstr(y, 1, "KEY")
        win.addstr(y, action_col, "ACTION")
        y += 1

        help_comb = [
            ("up, w", "Move up"),
            ("down, s", "Move down"),
            ("enter, right, a", "Enter directory"),
            ("b, left, d", "Go to parent directory"),
            ("esc, q", "Exit")
        ]

        for y, (key, action) in zip(range(1, win_maxy - 1), help_comb):
            win.addstr(y, 1, key)
            win.addstr(y, action_col, action)

        while True:
            key = win.getch()

            if key in (27, ord('q')):
                curses.endwin()
                break

    def draw_screen(self) -> None:
        """Draws all the folders/files into the screen."""

        self.screen.clear()

        y = 0
        self.maxy, maxx = self.screen.getmaxyx()
        self.maxy -= 4
        files = self.get_files()

        self.screen.addstr(y, 1, "Press ? to show help window. Esc or q to exit.")
        y += 1

        self.screen.addstr(y, 1, f"Current Directory: {self.explorer.cwd}", curses.A_STANDOUT)
        y += 2

        self.screen.addstr(y, 4, "File Name")
        self.screen.addstr(y, maxx // 3, "File Size")
        self.screen.addstr(y, maxx // 2, "Last Modified")

        files = files[self.offset:(self.maxy + self.offset) - 2]
        coords = []

        for idx, file in files:
            y += 1

            if len(file.name) > 29:
                file.name = f"{file.name[:29]}..."

            if self.idx == idx:
                file_display = f"{self.cursor} {file}"
            else:
                file_display = f"{' ' * len(self.cursor)} {file}"

            self.screen.addnstr(y, 1, file_display, maxx - 2)
            self.screen.addnstr(y, maxx // 3, file.size, maxx - 2)
            self.screen.addnstr(y, maxx // 2, file.last_modified, maxx - 2)
            coords.append((file.name, range(1, len(file_display)), y))

        self.coords = coords
        self.screen.refresh()

    def get_key(self) -> int:
        """Returns a pressed key."""

        return self.screen.getch()

    def move_up(self) -> None:
        """Adjusts the indexes and offset if possible.

        This makes the cursor go up.
        """

        if self.idx > 0:
            self.idx -= 1

        if self.idx < self.offset and self.idx >= 0:
            self.offset -= 1

        if self.screen_idx > 0:
            self.screen_idx -= 1

    def move_down(self) -> None:
        """Adjusts the indexes and offsets if possible.

        This makes the cursor go down.
        """

        if self.idx < len(self.get_files()) - 1:
            self.idx += 1

            if self.screen_idx >= self.maxy - 3:
                self.offset += 1

            if self.screen_idx < self.maxy - 3:
                self.screen_idx += 1

    def pop_cursor_stack(self):
        """Pops the cursor stack and returns it."""

        if len(self.cursor_stack) > 1:
            return self.cursor_stack.pop()

        return self.cursor_stack[0]

    def execute_by_key(self, key: int) -> None:
        """Executes an action based on the key.

        key:
            The key returned by `get_key`.
        """

        if key in QUIT:  # Esc key or 'q'
            raise SystemExit()

        if key in (ord('?'),):
            self.show_help()

        if key in GO_BACK:
            self.explorer.go_back()

            if self.keep_cursor_state:
                offset, index, screen_index = self.pop_cursor_stack()

                self.offset = offset
                self.idx = index
                self.screen_idx = screen_index

        if key in KEY_UP:
            self.move_up()

        if key in KEY_DOWN:
            self.move_down()

        if key in ENTER:
            files = self.get_files()

            if not files:
                return

            selected = files[self.idx][1].name

            entered = self.explorer.enter(selected)

            if not entered:
                return

            state = (0, 0, 0)

            if self.keep_cursor_state:
                state = (
                    self.offset,
                    self.idx,
                    self.screen_idx
                )

            self.cursor_stack.append(state)
            self.reset_state()

    def handle_mouse_event(self) -> None:
        """Handles a mouse event."""

        _, x, y, _, bstate = curses.getmouse()

        is_double_click = bstate & curses.BUTTON1_DOUBLE_CLICKED

        if is_double_click:
            for name, c_x, c_y in self.coords:
                # Check if the coordinates clicked
                # matches any of the folder coordinates on
                # the screen.
                if not (x in c_x and y == c_y):
                    continue

                if name == "Back":
                    self.explorer.go_back()
                    break

                self.explorer.enter(name)
                self.reset_state()

        if bstate in SCROLL_UP:
            self.move_up()

        if bstate in SCROLL_DOWN:
            self.move_down()

    def _run(self):
        """Starts the loop to run the app."""

        while True:
            self.draw_screen()
            key = self.get_key()
            print(key)
            if key == curses.KEY_MOUSE:
                self.handle_mouse_event()
                continue

            self.execute_by_key(key)

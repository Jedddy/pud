from __future__ import annotations

import os
import curses
from pathlib import Path

from .entity import Entity, GoBack


KEY_UP = (curses.KEY_UP, 450, ord('w'))
KEY_DOWN = (curses.KEY_DOWN, 456, ord('s'))
ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))
SCROLL_UP = (65536,)
SCROLL_DOWN = (2097152,)


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

    cwd:
        The current working directory.

    cursor_stack:
        The cursor stack used to 'remember' the past cursor placement before
        entering a new directory. It is a tuple of 4 items.
        (offset, index, screen_index)

        `offset` is the offset of the display screen from the top of the file list.
        `index` is the index of the cursor.
        `screen_index` is the index of the cursor on the screen.

    files:
        The list of files on the current working directory.

    screen:
        A curses window.

    coords:
        The coords of current file entries on the screen.
    """

    screen: "curses._CursesWindow"
    coords: list[tuple[str, int, int]]

    def __init__(self, cursor: str, keep_cursor_state: bool):
        self.cursor = cursor.strip()
        self.keep_cursor_state = keep_cursor_state
        self.idx = 0
        self.offset = 0
        self.screen_idx = 0
        self.cwd = Path().cwd()
        self.cursor_stack = [(0, 0, 0) for part in self.cwd.parts]
        self.files = self.get_files()

    def __call__(self, screen: "curses._CursesWindow"):
        curses.curs_set(0)
        curses.mousemask(-1)
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

    def get_files(self) -> tuple[tuple[int, GoBack | Entity], ...]:
        """Gets all the files from the current working directory and stores it in a list."""

        back = [GoBack()]
        ret = []

        try:
            files = list(self.cwd.iterdir())
        except PermissionError:
            message = "Permission Denied."
            maxy, maxx = self.screen.getmaxyx()
            files = []

            self.screen.addstr(maxy // 2, (maxx // 2) - (len(message) // 2), message)

        for file in files:
            ret.append(Entity(file.name, is_file=file.is_file()))

        ret = sorted(ret, key=lambda f: f.is_file)
        return tuple(enumerate(back + ret))

    def draw_screen(self) -> None:
        """Draws all the folders/files into the screen."""

        self.screen.clear()

        y = 0
        self.maxy, maxx = self.screen.getmaxyx()
        self.maxy -= 4
        files = self.get_files()

        self.screen.addstr(y, 1, f"Current Directory: {self.cwd}")
        y += 1
        self.screen.addstr(y, 1, "Press CTRL + C or Esc or q to exit.")
        y += 1

        files = files[self.offset:self.maxy + self.offset]
        coords = []

        for idx, file in files:
            y += 1

            if self.idx == idx:
                file_display = f"{self.cursor} {file}"
            else:
                file_display = f"{' ' * len(self.cursor)} {file}"

            self.screen.addnstr(y, 1, file_display, maxx - 2)
            coords.append((file.name, range(1, len(file_display)), y))

        self.coords = coords
        self.screen.refresh()

    def get_key(self) -> str | int:
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

        if self.idx < len(self.files) - 1:
            self.idx += 1

            if self.screen_idx >= self.maxy - 1:
                self.offset += 1

            if self.screen_idx < self.maxy - 1:
                self.screen_idx += 1

    def pop_cursor_stack(self):
        """Pops the cursor stack and returns it."""

        if len(self.cursor_stack) > 1:
            return self.cursor_stack.pop()

        return self.cursor_stack[0]

    def refresh_cwd(self):
        """Refreshes the current working directory."""

        self.cwd = Path().cwd()
        self.files = self.get_files()

    def execute_by_key(self, key: int) -> None:
        """Executes an action based on the key.

        key:
            The key returned by `get_key`.
        """

        if key in (27, ord('q')):  # Esc key or 'q'
            raise SystemExit()

        if key in KEY_UP:
            self.move_up()

        if key in KEY_DOWN:
            self.move_down()

        if key in ENTER:
            if self.idx == 0:
                selected = self.cwd.parent

                os.chdir(selected)

                if self.keep_cursor_state:
                    offset, index, screen_index = self.pop_cursor_stack()

                    self.offset = offset
                    self.idx = index
                    self.screen_idx = screen_index

            else:
                selected = self.cwd / str(self.files[self.idx][1].name)

                if selected.is_file():
                    return

                state = (0, 0, 0)

                if self.keep_cursor_state:
                    state = (
                        self.offset,
                        self.idx,
                        self.screen_idx
                    )

                self.cursor_stack.append(state)

                os.chdir(selected)

                self.reset_state()

        self.refresh_cwd()

    def handle_mouse_event(self) -> None:
        """Handles a mouse event."""

        clicked = None
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
                    clicked = self.cwd.parent
                    break

                clicked = self.cwd / name

                if clicked.is_file():
                    return

                self.reset_state()

            if clicked:
                os.chdir(clicked)
                self.refresh_cwd()

        if bstate in SCROLL_UP:
            self.move_up()

        if bstate in SCROLL_DOWN:
            self.move_down()

    def _run(self):
        """Starts the loop to run the app."""

        while True:
            self.draw_screen()
            key = self.get_key()

            if key == curses.KEY_MOUSE:
                self.handle_mouse_event()
                continue

            self.execute_by_key(key)

import os
import curses
from pathlib import Path

from .file import Back, Entity


KEY_UP = (curses.KEY_UP, 450)
KEY_DOWN = (curses.KEY_DOWN, 456)
ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))


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
        (part, offset, index, screen_index)

        `part` is the folder name.
        `offset` is the offset of the display screen from the top of the file list.
        `index` is the index of the cursor.
        `screen index` is the index of the cursor on the screen

    files:
        The list of files on the current working directory.
    """

    screen: "curses._CursesWindow"

    def __init__(self, cursor: str, keep_cursor_state: bool):
        self.cursor = cursor.strip()
        self.keep_cursor_state = keep_cursor_state
        self.idx = 0
        self.offset = 0
        self.screen_idx = 0
        self.cwd = Path(os.getcwd())
        self.cursor_stack = [(part, 0, 0, 0) for part in self.cwd.parts]
        self.files = self.get_files()

    def __call__(self, screen: "curses._CursesWindow"):
        curses.curs_set(0)
        screen.keypad(True)
        self.screen = screen

        try:
            self._run()
        except KeyboardInterrupt:
            self.screen.clear()
            self.screen.addstr(1, 1, "Press any key to exit.")
            self.screen.refresh()
            self.screen.getch()

    def reset_state(self) -> None:
        self.idx = 0
        self.offset = 0
        self.screen_idx = 0

    def get_files(self) -> tuple[tuple[int, Back | Path], ...]:
        back = [Back()]
        ret = []

        try:
            files = list(self.cwd.iterdir())
        except PermissionError:
            files = []

        for file in files:
            ret.append(Entity(file.name, is_file=file.is_file()))

        ret = sorted(ret, key=lambda f: f.is_file)
        return tuple(enumerate(back + ret))

    def draw_screen(self) -> None:
        self.screen.clear()

        y = 0
        self.maxy, maxx = self.screen.getmaxyx()
        self.maxy -= 4
        files = self.get_files()

        self.screen.addnstr(y, 1, f"Current Directory: {self.cwd}", maxx - 2)
        y += 1

        files = files[self.offset:self.maxy + self.offset]

        for idx, file in files:
            y += 1

            if self.idx == idx:
                file_display = f"{self.cursor} {file}"
            else:
                file_display = f"{' ' * len(self.cursor)} {file}"

            self.screen.addnstr(y, 1, file_display, maxx - 2)

        self.screen.refresh()

    def get_key(self) -> str | int:
        return self.screen.getch()

    def move_up(self) -> None:
        if self.idx > 0:
            self.idx -= 1

        if self.idx < self.offset and self.idx >= 0:
            self.offset -= 1

        if self.screen_idx > 0:
            self.screen_idx -= 1

    def move_down(self) -> None:
        if self.idx < len(self.files) - 1:
            self.idx += 1

            if self.screen_idx >= self.maxy - 1:
                self.offset += 1

            if self.screen_idx < self.maxy - 1:
                self.screen_idx += 1

    def pop_cursor_stack(self):
        if len(self.cursor_stack) > 1:
            return self.cursor_stack.pop()
        return self.cursor_stack[0]

    def _run(self):
        while True:
            self.draw_screen()

            key = self.screen.getch()

            if key in KEY_UP:
                self.move_up()

            if key in KEY_DOWN:
                self.move_down()

            if key in ENTER:
                if self.idx == 0:
                    selected = self.cwd.parent

                    os.chdir(selected)

                    if self.keep_cursor_state:
                        _, offset, index, screen_index = self.pop_cursor_stack()

                        self.offset = offset
                        self.idx = index
                        self.screen_idx = screen_index

                else:
                    selected = self.cwd / str(self.files[self.idx][1].name)

                    if selected.is_file():
                        continue

                    if self.keep_cursor_state:
                        state = (
                            self.cwd.name,
                            self.offset,
                            self.idx,
                            self.screen_idx
                        )

                        self.cursor_stack.append(state)

                    os.chdir(selected)

                    self.reset_state()

                self.cwd = Path(os.getcwd())
                self.files = self.get_files()

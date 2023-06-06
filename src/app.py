import os
import curses
from pathlib import Path


KEY_UP = (curses.KEY_UP, 450)
KEY_DOWN = (curses.KEY_DOWN, 456)
ENTER = (curses.KEY_ENTER, ord('\n'), ord('\r'))


class App:
    selected: str
    screen: "curses._CursesWindow"

    def __init__(self, cursor: str = "=>"):
        self.cursor = cursor
        self.idx = 0
        self.offset = 0
        self.screen_idx = 0
        self.cwd = Path(os.getcwd())

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

    def get_files(self) -> tuple[tuple[int, str]]:
        files = ["< Go Back"] + os.listdir(self.cwd)
        return tuple(enumerate(files))

    def draw_screen(self) -> None:
        self.screen.clear()

        y = 0
        self.maxy, maxx = self.screen.getmaxyx()
        self.maxy -= 4
        files = self.get_files()

        self.screen.addnstr(y, 1, f"Current Directory: {str(self.cwd)}", maxx - 2)
        y += 1

        files = files[self.offset:self.maxy + self.offset]

        for idx, file in files:
            y += 1

            if self.idx == idx:
                self.selected = file
                file = f"{self.cursor} {file}"
            else:
                file = f"{' ' * len(self.cursor)} {file}"

            self.screen.addnstr(y, 1, file, maxx - 2)

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
        if self.idx < len(self.get_files()) - 1:
            self.idx += 1

            if self.screen_idx < self.maxy:
                self.screen_idx += 1

            if self.screen_idx > self.maxy - 1:
                self.offset += 1

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
                    os.chdir(self.cwd.parent)
                else:
                    selected = Path(self.cwd, self.selected)

                    if selected.is_file():
                        continue

                    os.chdir(selected)
                self.cwd = Path(os.getcwd())
                self.idx = 0
                self.offset = 0
                self.screen_idx = 0

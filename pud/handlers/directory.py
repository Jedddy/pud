from __future__ import annotations

import os
from datetime import datetime
from pathlib import Path

from ..entity import Entity


class DirectoryExplorer:
    """The directory handler responsible for entering and leaving directories.

    Attributes
    ----------
    cwd:
        The current working directory.
    """
    def __init__(self, cwd: Path) -> None:
        self.cwd = cwd

    def enter(self, name: str) -> bool:
        """Enters a folder or a file.

        Paremeters
        ----------
        name:
            The name of the folder or file to enter.

        Returns
        ----------
        bool:
            If the entry was successful or not.
        """

        directory = self.cwd / name

        if directory.is_file():
            return False  # TODO: Make a file viewer

        try:
            os.chdir(name)
            self.refresh_cwd()
        except PermissionError:
            return False

        return True

    def go_back(self) -> None:
        """Goes back to the parent directory."""

        self.enter(self.cwd.parent)
        self.refresh_cwd()

    def list_files(self) -> list[Entity] | None:
        """Lists all the files in the current directory."""

        try:
            files = []

            for entity in self.cwd.iterdir():
                stats = entity.stat()
                last_modified = datetime.fromtimestamp(stats.st_mtime)
                files.append(
                    Entity(
                        entity.name,
                        stats.st_size,
                        entity.is_file(),
                        last_modified.strftime("%x %I:%M:%S")
                    )
                )

        except PermissionError:
            files = None

        return files

    def refresh_cwd(self):
        """Refreshes the current directory."""

        self.cwd = Path.cwd()

"""Represent a person's frame."""

import tkinter as tk
import typing as t

from . import config
from .cell import Cell

if t.TYPE_CHECKING:
    from .battleship import Battleship
else:
    Battleship = t.Any


class Frame:
    """A frame."""

    __slots__ = (
        "master",
        "frame",
        "player",
        "boats",
        "grid",
    )

    def __init__(self, master: Battleship, player: bool) -> None:
        """Initialize the frame."""
        self.master = master

        self.player = player  # Player-controlled

        self.frame = tk.Frame(master.main, config.FRAME_CONFIG)

        self.boats: list[tuple[int, int]] = []

        self.grid = [
            [Cell(self, (i, j)) for j in range(config.GRID_SIZE)]
            for i in range(config.GRID_SIZE)
        ]

    def hit(self, coords: tuple[int, int]) -> None:
        """Act upon a cell being hit."""
        self.boats.remove(coords)

        if not self.boats:
            self.master.ending(not self.player)

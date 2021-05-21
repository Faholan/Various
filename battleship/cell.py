"""Battleship cell."""

import typing as t

import tkinter as tk

from . import config
from .drawer import draw
from .enums import Status


class Cell:
    """Implementation of a battleship cell."""

    __slots__ = (
        "master",
        "canvas",
        "coords",
        "fired",
        "isboat",
        "drawer_args",
    )

    def __init__(
        self,
        master,
        coords: t.Tuple[int, int],
    ) -> None:
        """Initialize the cell."""
        self.master = master

        self.canvas = tk.Canvas(
            master.frame,
            config.CELL_DEFAULT,
            width=config.CELL_SIZE,
            height=config.CELL_SIZE,
        )

        self.coords = coords

        self.fired = False
        self.isboat = False

        self.drawer_args: t.Dict[str, t.Any] = {}

        self.canvas.grid(row=coords[0], column=coords[1])

        self.canvas.bind("<Button-1>", self.left)

    def left(self, _) -> None:
        """Implement left click."""
        if self.master.player:
            self.place()
        else:
            try:
                self.fire()
            except ValueError:
                return

    def place(self) -> None:
        """Place a boat.

        This implements left click for players
        """
        if not self.master.master.placing:
            return

        self.master.master.candidate_place(self.coords)

    def fire(self) -> bool:
        """Fire upon a cell."""
        if not self.master.master.process_hits:
            return False  # Should ignore the hit
        if self.fired:
            raise ValueError("Cell already hit")
            # If this error appears in logs, then the AI has an issue

        self.fired = True
        if self.isboat:
            if self.master.player:
                self.canvas.delete("all")
                draw(self.canvas, status=Status.HIT, **self.drawer_args)
            else:
                self.canvas.config(config.CELL_HIT)
            self.master.hit(self.coords)
        elif self.master.player or config.SHOW_AI_MISSED:
            self.canvas.config(config.CELL_MISSED)

        if not self.master.player:
            self.master.master.ai_turn()

        return self.isboat  # In order to allow the AI to process

import tkinter as tk

from . import config


class Cell:
    """Implement one cell."""

    __slots__ = (
        "master",
        "size",
        "canvas",
        "coords",
        "value",
        "ismine",
        "flagged",
        "clicked",
    )

    colours = (
        "gray4",
        "blue",
        "green",
        "red",
        "purple4",
        "brown4",
        "dark green",
        "black",
        "white",
    )

    def __init__(self, master, i, j):
        """Initialize the cell."""
        self.master = master
        self.size = self.master.cell_size
        self.canvas = tk.Canvas(
            master.frame, width=self.size, height=self.size, **config.CELL_ARGS
        )
        self.coords = (i, j)
        self.value = 0
        self.canvas.bind("<Button-1>", self.left)
        self.canvas.bind("<Button-3>", self.flag)
        self.ismine = False
        self.flagged = False
        self.clicked = False
        self.canvas.grid(row=i, column=j)

    @property
    def colour(self) -> str:
        """Get the colour associated to the value."""
        return self.colours[self.value]

    def left(self, _=None) -> None:
        """Implement left clicking."""
        if self.flagged or not self.master.enabled:
            return

        if self.master.blank:
            self.master.first_click(*self.coords)

        if self.clicked:
            self.master.second_click(*self.coords)
            return

        if self.ismine:
            self.canvas.config(bg=config.MINE_COLOR)
            self.master.enabled = False
            self.master.lose(*self.coords)
            return

        self.click()

        if not self.value:
            self.master.zero(*self.coords)

        if self.master.completed():
            self.master.enabled = False
            self.master.win()

    def flag(self, _=None) -> None:
        """Flag thyself."""
        if self.clicked or not self.master.enabled:
            return

        if self.flagged:
            self.canvas.delete(tk.ALL)
            self.master.cur_mines += 1
        else:
            self.canvas.create_line(
                17 * self.size / 48,
                3 * self.size / 16,
                17 * self.size / 48,
                71 * self.size / 80,
                fill=config.FLAG_COLOR,
                width=2,
            )
            self.canvas.create_polygon(
                17 * self.size / 48,
                3 * self.size / 16,
                19 * self.size / 24,
                63 * self.size / 160,
                17 * self.size / 48,
                3 * self.size / 5,
                outline="",
                fill=config.FLAG_COLOR,
            )
            self.master.cur_mines -= 1

        self.master.remaining.config(text=str(self.master.cur_mines))
        self.flagged = not self.flagged

    def click(self) -> None:
        """Fill the cell with color."""
        if self.flagged:
            self.flag()

        self.clicked = True

        if self.value:
            self.canvas.config(bg=config.CELL_CLICKED)
            self.canvas.create_text(
                self.size / 2,
                self.size / 2,
                text=str(self.value),
                fill=self.colour,
                font=config.CELL_FONT,
            )
        else:
            self.canvas.config(bg=config.CELL_ZERO)

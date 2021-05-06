"""MIT License.

Copyright (c) 2021 Faholan

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

import tkinter as tk
import typing as t
from random import choice


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
        "clicked"
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
        self.size = self.master.size
        self.canvas = tk.Canvas(
            master.main,
            width=master.size,
            height=master.size,
            bg="gray80",
            highlightbackground="gray4",
        )
        self.coords = (i, j)
        self.value = 0
        self.canvas.bind("<Button-1>", self.left)
        self.canvas.bind("<Button-3>", self.flag)
        self.ismine = False
        self.flagged = False
        self.clicked = False
        self.canvas.grid(row=i, column=j)

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
            self.canvas.config(bg="red3")
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
                fill="red",
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
                fill="red",
            )
            self.master.cur_mines -= 1
        self.master.remaining.config(text=f"Mines: {self.master.cur_mines}")
        self.flagged = not self.flagged

    @property
    def colour(self) -> str:
        """Get the colour associated to the value."""
        return self.colours[self.value]

    def click(self) -> None:
        """Fill the cell with color."""
        if self.flagged:
            self.flag()
        self.clicked = True
        if self.value:
            self.canvas.config(bg="gray30")
            self.canvas.create_text(
                self.size / 2,
                self.size / 2,
                text=str(self.value),
                fill=self.colour,
                font="arial 20",
            )
        else:
            self.canvas.config(bg="gray4")


class Minesweeper:
    """Main class, actually implement the game."""

    __slots__ = (
        "main",
        "grid",
        "size",
        "mines",
        "cur_mines",
        "rows",
        "columns",
        "difficulties",
        "remaining",
        "blank",
        "enabled",
    )

    def __init__(self) -> None:
        """Initialize the minesweeper."""
        self.main: tk.Tk = None
        self.grid: t.List[t.List[Cell]] = []
        self.size = 0
        self.mines = 0
        self.cur_mines = 0
        self.rows = 0
        self.columns = 0
        self.difficulties = (
            {
                "text": "Easy",
                "bg": "green",
                "command": self.gen_game(60, 10, 8, 8),
            },
            {
                "text": "Medium",
                "bg": "midnight blue",
                "command": self.gen_game(35, 40, 16, 16),
            },
            {"text": "Hard", "bg": "red3",
                "command": self.gen_game(30, 99, 16, 32)},
        )
        self.remaining: tk.Label = None
        self.blank = True  # Not clicked yet
        self.enabled = True  # Lock the grid after the game is finished

    def gen_game(self, size, mines, rows, columns) -> t.Callable:
        """Generate callables for the different difficulties."""

        def predictate() -> None:
            self.size = size
            self.mines = mines
            self.cur_mines = mines
            self.rows = rows
            self.columns = columns
            self.blank = True
            self.enabled = True
            self.main.destroy()
            self.game()

        return predictate

    def start(self) -> None:
        """First screen."""
        self.main = tk.Tk()
        self.main.title("Minesweeper")
        text = tk.Label(
            self.main,
            bg="gray30",
            fg="white",
            font="arial 20",
            text="Choose the difficulty",
            justify=tk.CENTER,
        )
        text.grid(column=0, row=0)

        for i, args in enumerate(self.difficulties):
            button = tk.Button(self.main, fg="white", font="arial 20", **args)
            button.grid(column=0, row=i + 1, sticky=tk.NSEW)
        self.main.resizable(False, False)
        self.main.mainloop()

    def completed(self) -> bool:
        """Check if all non-mined tiles have been clicked."""
        for row in self.grid:
            for cell in row:
                if not cell.ismine and not cell.clicked:
                    return False
        return True

    def game(self) -> None:
        """Actual game."""
        self.main = tk.Tk()
        self.main.title("Minesweeper")
        self.main.config(bg="gray30")
        self.remaining = tk.Label(
            self.main,
            bg="gray30",
            fg="white",
            font="arial 20",
            relief="flat",
            text=f"Mines: {self.cur_mines}",
            justify=tk.CENTER,
        )
        self.remaining.grid(
            row=self.rows, column=0, columnspan=self.columns, sticky=tk.EW
        )

        self.grid = [
            [Cell(self, i, j) for j in range(self.columns)] for i in range(self.rows)
        ]
        self.main.resizable(False, False)

    def neighbours(self, i: int, j: int) -> t.List[Cell]:
        """Get the neighbours."""
        final = []
        if i != 0:
            final.append(self.grid[i - 1][j])
        if i != self.rows - 1:
            final.append(self.grid[i + 1][j])
        if j != 0:
            final.append(self.grid[i][j - 1])
        if j != self.columns - 1:
            final.append(self.grid[i][j + 1])
        if 0 not in {i, j}:
            final.append(self.grid[i - 1][j - 1])
        if i != self.rows - 1 and j != self.columns - 1:
            final.append(self.grid[i + 1][j + 1])
        if i != 0 and j != self.columns - 1:
            final.append(self.grid[i - 1][j + 1])
        if i != self.rows - 1 and j != 0:
            final.append(self.grid[i + 1][j - 1])
        return final

    def first_click(self, i: int, j: int) -> None:
        """Plant the mines."""
        self.blank = False
        for _ in range(self.mines):
            x, y = i, j
            cell = self.grid[i][j]
            while (abs(x - i) <= 1 and abs(y - j) <= 1) or cell.ismine:
                cell = choice(choice(self.grid))
                x, y = cell.coords
            cell.ismine = True

            for cell in self.neighbours(x, y):
                if not cell.ismine:
                    cell.value += 1

    def zero(self, i: int, j: int) -> None:
        """When you click a zero."""
        for cell in self.neighbours(i, j):
            if cell.clicked:
                continue
            cell.click()
            if cell.value == 0:
                self.zero(*cell.coords)

    def second_click(self, i: int, j: int) -> None:
        """When you click for the second time."""
        neighb = self.neighbours(i, j)
        if sum(1 if cell.flagged else 0 for cell in neighb) == self.grid[i][j].value:
            for cell in neighb:
                if not cell.clicked:
                    cell.left()

    def lose(self, i: int, j: int) -> None:
        """Lose the game."""
        for row in self.grid:
            for cell in row:
                if cell.flagged and not cell.ismine:
                    cell.canvas.config(bg="dark turquoise")
                elif cell.coords != (i, j) and cell.ismine:
                    cell.canvas.config(bg="purple4")
        self.endscreen("You lost", "It's a loss !", "red3")

    def win(self) -> None:
        """Win the game."""
        self.endscreen("You won", "It's a victory !", "green3")

    def endscreen(self, title, content, bg):
        """Draw the endscreen."""
        screen = tk.Tk()
        screen.title(title)
        screen.config(bg=bg)
        text = tk.Label(
            screen,
            bg=bg,
            fg="white",
            font="arial 20",
            text=content,
            justify=tk.CENTER,
        )
        text.grid(row=0, column=0, sticky=tk.EW)

        def stop():
            self.main.destroy()
            screen.destroy()

        def restart():
            self.main.destroy()
            screen.destroy()
            self.start()

        restart_btn = tk.Button(
            screen,
            text="Start a new game",
            bg="green3",
            fg="white",
            font="arial 20",
            command=restart,
        )
        quit_btn = tk.Button(
            screen,
            text="Quit the game",
            bg="red3",
            fg="white",
            font="arial 20",
            command=stop,
        )

        restart_btn.grid(row=1, column=0, sticky=tk.EW)
        quit_btn.grid(row=2, column=0, sticky=tk.EW)
        screen.resizable(False, False)
        screen.mainloop()


def main():
    """Start the game."""
    Minesweeper().start()


if __name__ == "__main__":
    main()

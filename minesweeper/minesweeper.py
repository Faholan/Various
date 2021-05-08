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

import sqlite3
import tkinter as tk
import typing as t
from random import choice
from tkinter import messagebox

import config


class Database:
    """Class for managing all SQL-related things."""

    __slots__ = ("con",)

    def __init__(self) -> None:
        """Initialize the connection."""
        self.con = sqlite3.connect("minesweeper.db")
        self.initialize()

    def initialize(self) -> None:
        """Table creation."""
        cur = self.con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS highscores (
                difficulty INTEGER NOT NULL,
                time INTEGER NOT NULL,
                name TEXT NOT NULL,
                rowid INTEGER PRIMARY KEY
            )
            """
        )
        self.con.commit()

    def highscores(self, difficulty: int) -> t.List[t.Tuple[int, str]]:
        """Fetch the highscores."""
        cur = self.con.cursor()
        return cur.execute(
            "SELECT time, name FROM highscores WHERE difficulty=? ORDER BY time ASC",
            (difficulty,),
        ).fetchall()

    def is_highscore(
        self, difficulty: int, time: int
    ) -> t.Tuple[bool, t.Optional[int]]:
        """Test if a score is in the leaderboard.

        Also returns the lowest highscore for increased performance, or None if there are less than ten of them
        """
        cur = self.con.cursor()
        high_list = cur.execute(
            "SELECT time FROM highscores WHERE difficulty=? ORDER BY time ASC",
            (difficulty,),
        ).fetchall()
        if len(high_list) < 10:
            return True, None
        lowest = high_list[-1][0]
        return time < lowest, lowest

    def insert_highscore(
        self,
        difficulty: int,
        time: int,
        name: str,
        lowest: t.Optional[int],
    ) -> None:
        """Insert a new highscore, deleting the lowest one."""
        cur = self.con.cursor()

        if lowest is not None:
            cur.execute(
                "DELETE FROM highscores WHERE rowid IN (SELECT rowid FROM highscores WHERE difficulty=? AND time=? LIMIT 1)",
                (difficulty, lowest),
            )
        cur.execute(
            "INSERT INTO highscores VALUES(?, ?, ?)",
            (difficulty, time, name),
        )
        self.con.commit()


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
            master.main, width=self.size, height=self.size, **config.CELL_ARGS
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


class Minesweeper:
    """Main class, actually implement the game."""

    __slots__ = (
        "main",
        "grid",
        "cell_size",
        "mines",
        "cur_mines",
        "rows",
        "columns",
        "remaining",
        "blank",
        "enabled",
        "database",
        "time",
        "time_display",
        "game_num",
        "difficulty",
    )

    def __init__(self) -> None:
        """Initialize the minesweeper."""
        self.main: tk.Tk = None
        self.grid: t.List[t.List[Cell]] = []
        self.cell_size = 0
        self.mines = 0
        self.cur_mines = 0
        self.rows = 0
        self.columns = 0
        self.remaining: tk.Label = None
        self.blank = True  # Not clicked yet
        self.enabled = True  # Lock the grid after the game is finished
        self.database = Database()
        self.time = 0
        self.time_display: tk.Label = None
        self.game_num = 0
        self.difficulty = 0
        # Solve potential issue with incr_time running multiple times

    def incr_time(self, game_num: int) -> None:
        """Increment the time and time display."""
        if self.game_num == game_num and self.enabled:
            self.time += 1
            try:
                self.time_display.config(text=str(self.time))
            except tk.TclError:
                return  # window killed
            self.main.after(1000, self.incr_time, game_num)

    def gen_game(self, difficulty: int, args) -> t.Callable:
        """Generate callables for the different difficulties."""

        def predictate() -> None:
            self.difficulty = difficulty
            self.cell_size = args["cell_size"]
            self.mines = self.cur_mines = args["mines"]
            self.rows = args["rows"]
            self.columns = args["columns"]
            self.blank = True
            self.enabled = True
            self.main.destroy()
            self.game()

        return predictate

    def completed(self) -> bool:
        """Check if all non-mined tiles have been clicked."""
        for row in self.grid:
            for cell in row:
                if not cell.ismine and not cell.clicked:
                    return False
        return True

    def neighbours(self, i: int, j: int) -> t.List[Cell]:
        """Get the neighbours of a cell."""
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

    def start(self) -> None:
        """First screen."""
        self.game_num += 1
        self.time = 0

        self.main = tk.Tk()
        self.main.title(config.SELECT_TITLE)
        text = tk.Label(self.main, **config.SELECT_TEXT)
        text.grid(column=0, row=0)

        for diff, args in enumerate(config.DIFFICULTIES):
            button = tk.Button(
                self.main,
                command=self.gen_game(diff + 1, args),
                text=args["name"],
                bg=args["button_color"],
                **config.DIFFICULTY_BUTTON,
            )
            button.grid(column=0, row=diff + 1, sticky=tk.NSEW)
        self.main.resizable(False, False)
        self.main.focus_force()
        self.main.mainloop()

    def game(self) -> None:
        """Actual game."""
        self.main = tk.Tk()
        self.main.title(config.GAME_TITLE)
        self.main.config(bg=config.GAME_BG)
        self.remaining = tk.Label(
            self.main, text=str(self.cur_mines), **config.REMAINING_MINES
        )
        self.time_display = tk.Label(
            self.main,
            text="0",
            **config.TIME_DISPLAY,
        )

        self.remaining.grid(row=self.rows, column=0,
                            columnspan=4, sticky=tk.EW)
        self.time_display.grid(
            row=self.rows, column=self.columns - 5, columnspan=4, sticky=tk.EW
        )

        self.grid = [
            [Cell(self, i, j) for j in range(self.columns)] for i in range(self.rows)
        ]
        self.main.resizable(False, False)
        self.main.focus_force()

    def first_click(self, i: int, j: int) -> None:
        """Plant the mines."""
        self.main.after(1000, self.incr_time, self.game_num)
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
        """When you click a cell for the second time."""
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
                    cell.canvas.config(bg=config.WRONG_FLAG)
                elif cell.coords != (i, j) and cell.ismine:
                    cell.canvas.config(bg=config.DISPLAY_MINES)
        self.endscreen(config.LOSE_END)

    def win(self) -> None:
        """Win the game."""
        test, lowest = self.database.is_highscore(self.difficulty, self.time)
        if test:
            self.new_highscore(lowest)
            return
        self.endscreen(config.WIN_END)

    def new_highscore(self, lowest) -> None:
        """Add a new highscore."""
        screen = tk.Tk()
        screen.title("New highscore !")
        text = tk.Label(screen, config.HIGHSCORE_TEXT)
        text.grid(row=0, column=0, sticky=tk.EW)
        entry = tk.Entry(screen, **config.HIGHSCORE_ENTRY)
        entry.grid(row=1, column=0)

        def submit():
            if not entry.get().strip():
                messagebox.showerror(
                    "Invalid operation",
                    "Your name cannot be blank. Enter a name.",
                )
                return

            self.database.insert_highscore(
                self.difficulty, self.time, entry.get().strip(), lowest
            )
            screen.destroy()
            self.endscreen(config.WIN_END)

        button = tk.Button(screen, command=submit, **config.HIGHSCORE_BUTTON)
        button.grid(row=2, column=0)
        screen.focus_force()

    def endscreen(self, args):
        """Draw the endscreen."""
        screen = tk.Tk()
        screen.title(args["title"])
        screen.config(bg=args["bg"])
        text = tk.Label(screen, **args["text"])
        text.grid(row=0, column=0, sticky=tk.EW)

        def stop():
            self.main.destroy()
            screen.destroy()

        def restart():
            self.main.destroy()
            screen.destroy()
            self.start()

        restart_btn = tk.Button(screen, command=restart, **config.RESTART_BTN)
        quit_btn = tk.Button(screen, command=stop, **config.QUIT_BTN)

        restart_btn.grid(row=1, column=0, sticky=tk.NSEW)
        quit_btn.grid(row=2, column=0, sticky=tk.NSEW)

        highscores = tk.Listbox(screen, **config.HIGHSCORE_LIST)

        for time, name in self.database.highscores(self.difficulty):
            highscores.insert(tk.END, f"{time} s - {name}")

        highscores.grid(row=0, column=1, rowspan=3, sticky=tk.NS)

        screen.resizable(False, False)
        screen.focus_force()
        screen.mainloop()


def main():
    """Start the game."""
    Minesweeper().start()


if __name__ == "__main__":
    main()

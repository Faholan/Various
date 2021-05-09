import tkinter as tk
import typing as t
from random import choice
from tkinter import messagebox

from . import config
from .cell import Cell
from .database import Database


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
        "frame",
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
        self.frame: tk.Frame = None
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

        def predicate() -> None:
            self.difficulty = difficulty
            self.cell_size = args["cell_size"]
            self.mines = self.cur_mines = args["mines"]
            self.rows = args["rows"]
            self.columns = args["columns"]
            self.blank = True
            self.enabled = True
            self.main.destroy()
            self.game()

        return predicate

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

        self.frame = tk.Frame(self.main, **config.FRAME)

        self.remaining = tk.Label(
            self.main, text=str(self.cur_mines), **config.REMAINING_MINES
        )

        self.time_display = tk.Label(
            self.main, text="0", **config.TIME_DISPLAY)

        self.grid = [
            [Cell(self, i, j) for j in range(self.columns)] for i in range(self.rows)
        ]

        self.frame.grid(**config.FRAME_GRID)

        self.remaining.grid(**config.REMAINING_GRID)
        self.time_display.grid(**config.TIME_GRID)

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
        screen.title("New highscore!")
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
            self.database.con.close()

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

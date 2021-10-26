"""Minesweeper game."""

import getpass
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
        "frame",
        "remaining",
        "time_display",
        "time",
        "cell_size",
        "grid",
        "rows",
        "columns",
        "mines",
        "cur_mines",
        "database",
        "blank",
        "enabled",
        "game_num",
        "difficulty",
        "highscore_screen",
    )

    def __init__(self) -> None:
        """Initialize the minesweeper."""
        self.main: tk.Tk = None  # type: ignore
        self.frame: tk.Frame = None  # type: ignore
        self.remaining: tk.Label = None  # type: ignore
        self.time_display: tk.Label = None  # type: ignore
        self.time = 0

        self.cell_size = 0

        self.grid: list[list[Cell]] = []

        self.rows = 0
        self.columns = 0

        self.mines = 0
        self.cur_mines = 0

        self.database = Database()

        self.blank = True  # Not clicked yet
        self.enabled = True  # Lock the grid after the game is finished

        self.game_num = 0
        self.difficulty = 0
        # Solve potential issue with incr_time running multiple times

        self.highscore_screen: t.Optional[tk.Tk] = None

    def incr_time(self, game_num: int) -> None:
        """Increment the time and time display."""
        if self.game_num == game_num and self.enabled:
            self.time += 1
            try:
                self.time_display.config(text=str(self.time))
            except tk.TclError:
                return  # window killed

            self.main.after(1000, self.incr_time, game_num)

    def gen_game(
        self, difficulty: int, args: dict[str, t.Any]
    ) -> t.Callable[[], None]:
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

    def neighbours(self, i: int, j: int) -> list[Cell]:
        """Get the neighbours of a cell."""
        final: list[Cell] = []
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
        text = tk.Label(self.main, config.SELECT_TEXT)

        text.grid(column=0, row=0)

        for diff, args in enumerate(config.DIFFICULTIES):
            button = tk.Button(
                self.main,
                config.DIFFICULTY_BUTTON,
                command=self.gen_game(diff + 1, args),
                text=args["name"],  # type: ignore
                bg=args["button_color"],  # type: ignore
            )
            button.grid(column=0, row=diff + 1, sticky=tk.NSEW)

        highscores_button = tk.Button(
            self.main,
            config.HIGHSCORES_BUTTON,
            command=self.display_highscores,
        )

        highscores_button.grid(config.START_HIGHSCORES_GRID)

        self.main.resizable(False, False)
        self.main.focus_force()
        self.main.mainloop()

    def game(self) -> None:
        """Actual game."""
        self.main = tk.Tk()
        self.main.title(config.GAME_TITLE)
        self.main.config(config.GAME_CONFIG)

        self.frame = tk.Frame(self.main, **config.FRAME)

        self.remaining = tk.Label(
            self.main,
            config.REMAINING_MINES,
            text=str(self.cur_mines),
        )

        self.time_display = tk.Label(
            self.main,
            config.TIME_DISPLAY,
            text="0",
        )

        self.grid = [
            [Cell(self, i, j) for j in range(self.columns)] for i in range(self.rows)
        ]

        self.frame.grid(**config.FRAME_GRID)  # type: ignore
        self.remaining.grid(**config.REMAINING_GRID)  # type: ignore
        self.time_display.grid(**config.TIME_GRID)  # type: ignore

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

    def new_highscore(self, lowest: t.Optional[int]) -> None:
        """Add a new highscore."""
        screen = tk.Tk()
        screen.title("New highscore!")
        screen.config(config.HIGHSCORE_CONFIG)

        text = tk.Label(
            screen,
            config.HIGHSCORE_LABEL,
            text=config.HIGHSCORE_TEXT.format(time=self.time),
        )

        entry = tk.Entry(screen, config.HIGHSCORE_ENTRY)

        try:
            entry.insert(tk.END, getpass.getuser())
        except Exception:
            # getpass.getuser may raise an exception, but the docs don't
            # specify what exception may be raised.
            # For example, under Windows, it may be an ImportError
            pass

        def submit() -> None:
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

        button = tk.Button(
            screen,
            config.HIGHSCORE_BUTTON,
            command=submit,
        )

        text.grid(config.HIGHSCORE_LABEL_GRID)
        entry.grid(config.HIGHSCORE_ENTRY_GRID)
        button.grid(config.HIGHSCORE_BUTTON_GRID)

        screen.resizable(False, False)
        screen.focus_force()

    def endscreen(self, args: dict[str, t.Any]) -> None:
        """Draw the endscreen."""
        screen = tk.Tk()
        screen.title(args["title"])
        screen.config(bg=args["bg"])
        text = tk.Label(screen, **args["text"])

        def stop() -> None:
            try:
                self.main.destroy()
            except tk.TclError:
                # Main already closed
                pass
            if self.highscore_screen is not None:
                try:
                    self.highscore_screen.destroy()
                except tk.TclError:
                    pass
            screen.destroy()
            self.database.con.close()

        def restart() -> None:
            try:
                self.main.destroy()
            except tk.TclError:
                # main already closed
                pass
            screen.destroy()
            self.start()

        restart_btn = tk.Button(screen, command=restart, **config.RESTART_BTN)
        quit_btn = tk.Button(screen, command=stop, **config.QUIT_BTN)

        highscores = tk.Listbox(screen, config.END_HIGHSCORE_LIST)

        for time, name in self.database.highscores(self.difficulty):
            highscores.insert(tk.END, f"{time} s - {name}")

        highscores_button = tk.Button(
            screen,
            config.HIGHSCORES_BUTTON,
            command=self.display_highscores,
        )

        text.grid(**config.END_TEXT_GRID)
        restart_btn.grid(**config.RESTART_GRID)
        quit_btn.grid(**config.QUIT_GRID)
        highscores.grid(**config.HIGHSCORE_GRID)
        highscores_button.grid(**config.END_HIGHSCORES_GRID)

        screen.resizable(False, False)
        screen.focus_force()
        screen.mainloop()

    def display_highscores(self) -> None:
        """Display the various highscores."""
        if self.highscore_screen is not None:
            try:
                self.highscore_screen.focus_force()
            except tk.TclError:
                self.draw_highscores()
        else:
            self.draw_highscores()

    def draw_highscores(self) -> None:
        """Draw a window to display the various highscores."""
        self.highscore_screen = tk.Tk()

        self.highscore_screen.title(config.HIGHSCORES_TITLE)
        self.highscore_screen.config(config.HIGHSCORES_CONFIG)

        for diff in range(3):
            tk.Label(
                self.highscore_screen,
                config.HIGHSCORES_LABELS,
                text=config.HIGHSCORES_TITLES[diff],
            ).grid(row=0, column=diff)
            highscores = tk.Listbox(
                self.highscore_screen,
                config.HIGHSCORES_LISTS,
            )

            for time, name in self.database.highscores(diff + 1):
                highscores.insert(tk.END, f"{time} s - {name}")

            highscores.grid(row=1, column=diff, sticky="nsew")

        self.highscore_screen.resizable(False, False)
        self.highscore_screen.focus_force()

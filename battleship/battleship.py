"""Battleship game."""

import tkinter as tk
import typing as t
from random import choice, randint

from . import config
from .drawer import draw
from .enums import Orientation, Status
from .frame import Frame

OPPOSITES = {
    Orientation.NORTH: Orientation.SOUTH,
    Orientation.SOUTH: Orientation.NORTH,
    Orientation.EAST: Orientation.WEST,
    Orientation.WEST: Orientation.EAST,
}


class Battleship:
    """Main battleship class."""

    __slots__ = (
        "main",
        "player_frame",
        "enemy_frame",
        "candidate",
        "boat_candidate",
        "orientation",
        "cur_boat",
        "placing",
        "playing",
        "continue_playing",
        # AI
        "impossible",
        "must_fire",
        "fire_grid",
        "not_destroyed",
        "hit_boat",
        "dist",
    )

    def __init__(self) -> None:
        """Initialize Battleship."""
        self.main = tk.Tk()

        self.main.title(config.TITLE)

        self.main.config(**config.MAIN_CONFIG)

        self.player_frame = Frame(self, True)
        self.enemy_frame = Frame(self, False)

        # The cell clicked for placing a boat
        self.candidate: t.Optional[t.Tuple[int, int]] = None

        # The boat that may be pressed
        self.boat_candidate: t.Optional[t.List[t.Tuple[int, int]]] = None

        # Currently selected orientation
        self.orientation = Orientation.EAST

        # N° of the boat being placed
        self.cur_boat = 0

        # State variables
        self.placing = True
        self.playing = True

        # Whether or not to start a new game after this one is finished
        self.continue_playing = False

        # Tkinter configuration
        self.main.bind("<Return>", self.place_boat)
        self.main.bind("<space>", self.place_boat)

        self.player_frame.frame.grid(config.PLAYER_GRID)
        self.enemy_frame.frame.grid(config.ENEMY_GRID)

        for key, orientation in (
            ("<Down>", Orientation.SOUTH),
            ("<Up>", Orientation.NORTH),
            ("<Right>", Orientation.EAST),
            ("<Left>", Orientation.WEST),
        ):
            self.main.bind(key, self._rotator(orientation))

        self.main.resizable(False, False)
        self.main.focus_force()

        # AI

        # Cells that cannot contain boats
        self.impossible: t.List[t.Tuple[int, int]] = []

        # Cells that most probably contain a boat cell
        self.must_fire: t.List[t.Tuple[t.Tuple[int, int], Orientation]] = []

        # Remember the remaining enemy boats
        self.not_destroyed = list(config.SIZES)

        # Boat being currently hit
        self.hit_boat: t.List[t.Tuple[int, int]] = []

        # Step for the fire grid
        self.dist = 2
        self.fire_grid = self._get_fire_grid()

    def mainloop(self) -> bool:
        """Start the tkinter mainloop.

        Returns True if the user wishes to continue playing.
        """
        self.main.mainloop()

        return self.continue_playing

    @property
    def process_hits(self) -> bool:
        """Whether or not to process clicks."""
        return (not self.placing) and self.playing

    def candidate_place(self, coords) -> None:
        """Place a candidate."""
        if self.candidate:
            i, j = self.candidate
            self.player_frame.grid[i][j].canvas.config(**config.CELL_DEFAULT)
        self.candidate = coords
        self.turn_boat()

    def _rotator(self, orientation):
        """Generate a caller to rotate the boat.

        This is called by the Up, Down, Left and Right keys
        """

        def predictate(_) -> None:
            self.orientation = orientation
            self.turn_boat()

        return predictate

    @staticmethod
    def _neighbours(coords):
        """Yield all neighbours of a couple of coordinates."""
        for i in {-1, 0, 1}:
            for j in {-1, 0, 1}:
                yield coords[0] + i, coords[1] + j

    @staticmethod
    def _boat_cells(
        candidate: t.Tuple[int, int],
        orientation: Orientation,
        cur_boat: int,
    ) -> t.List[t.Tuple[int, int]]:
        """Get the cells the boat considered shall be in."""
        if not candidate:
            return [(-1, -1)]
        x, y = candidate
        if orientation == Orientation.SOUTH:
            return [(x + i, y) for i in range(config.SIZES[cur_boat])]
        if orientation == Orientation.NORTH:
            return [(x - i, y) for i in range(config.SIZES[cur_boat])]
        if orientation == Orientation.EAST:
            return [(x, y + i) for i in range(config.SIZES[cur_boat])]

        # west
        return [(x, y - i) for i in range(config.SIZES[cur_boat])]

    def _is_valid(self, boat: t.List[t.Tuple[int, int]], frame: Frame) -> bool:
        """Check if a boat can be placed in a frame."""
        if any(
            i < 0 or j < 0 or i >= config.GRID_SIZE or (j >= config.GRID_SIZE)
            for (i, j) in boat
        ):
            return False

        if any(
            any(
                0 <= i < config.GRID_SIZE
                and 0 <= j < config.GRID_SIZE
                and (frame.grid[i][j].isboat)
                for i, j in self._neighbours(coords)
            )
            for coords in boat
        ):
            return False
        return True

    def turn_boat(self) -> None:
        """Turn the boat toward a direction."""
        if not self.candidate:
            return
        try:
            if self.boat_candidate:
                for i, j in self.boat_candidate:
                    self.player_frame.grid[i][j].canvas.delete(tk.ALL)
                    self.player_frame.grid[i][j].canvas.config(
                        **config.CELL_DEFAULT)
        except tk.TclError:
            return

        i, j = self.candidate

        self.player_frame.grid[i][j].canvas.config(**config.CELL_DEFAULT)

        boat = self._boat_cells(
            self.candidate,
            self.orientation,
            self.cur_boat,
        )

        if not self._is_valid(boat, self.player_frame):
            self.player_frame.grid[i][j].canvas.config(**config.CELL_BLINKING)
            return
        self.boat_candidate = boat  # valid placement
        for k, (i, j) in enumerate(boat):
            draw(
                self.player_frame.grid[i][j].canvas,
                self.cur_boat,
                k,
                self.orientation,
                Status.BLINKING,
            )

    def place_boat(self, _) -> None:
        """Place the boat.

        This is called by the Enter and space keys
        """
        if not self.boat_candidate or not self.placing:
            return  # No boat to place.

        self.candidate = None

        for k, (i, j) in enumerate(self.boat_candidate):
            self.player_frame.grid[i][j].isboat = True
            self.player_frame.grid[i][j].canvas.delete(tk.ALL)

            self.player_frame.grid[i][j].drawer_args = {
                "cur_boat": self.cur_boat,
                "num": k,
                "orientation": self.orientation,
            }
            draw(
                self.player_frame.grid[i][j].canvas,
                self.cur_boat,
                k,
                self.orientation,
                Status.PLACING,
            )

            self.player_frame.boats.append((i, j))

        self.boat_candidate = None

        self.cur_boat += 1

        if self.cur_boat == len(config.SIZES):
            self.placing = False
            self.place_ai_boats()
            # TODO: update display for firing

    def ending(self, won: bool) -> None:
        """Implement win or loss."""
        self.playing = False
        screen = tk.Toplevel()

        conf = config.CONF_WIN if won else config.CONF_LOSS

        screen.title(conf["title"])
        screen.config(bg=conf["bg"])  # type: ignore

        text = tk.Label(screen, **conf["text"])  # type: ignore

        def stop():
            try:
                self.main.destroy()
            except tk.TclError:
                pass

        def restart():
            self.continue_playing = True
            stop()

        restart_btn = tk.Button(screen, config.RESTART_BTN, command=restart)
        quit_btn = tk.Button(screen, config.QUIT_BTN, command=stop)

        text.grid(config.END_TEXT_GRID)
        restart_btn.grid(config.RESTART_GRID)
        quit_btn.grid(config.QUIT_GRID)

        screen.resizable(False, False)
        screen.focus_force()
        screen.mainloop()

    # AI part

    def place_ai_boats(self) -> None:
        """Place the AI's boats."""
        cur_boat = 0

        while cur_boat < len(config.SIZES):
            candidate = randint(0, config.GRID_SIZE - 1), randint(
                0, config.GRID_SIZE - 1
            )
            orientation = choice((Orientation.NORTH, Orientation.EAST))
            # Only two orientations need to be considered

            boat = self._boat_cells(candidate, orientation, cur_boat)
            if not self._is_valid(boat, self.enemy_frame):
                continue

            cur_boat += 1

            for i, j in boat:
                self.enemy_frame.grid[i][j].isboat = True
                self.enemy_frame.boats.append((i, j))

    def _get_fire_grid(self) -> t.List[t.Tuple[int, int]]:
        """Get the grid for the AI's fire."""
        final = []
        for i in range(10):
            final += [
                (i, self.dist * j + i % self.dist)
                for j in range(10 // self.dist)
                if (i, self.dist * j + i % self.dist) not in self.impossible
            ]

        return final

    def ai_turn(self) -> None:
        """Implement the AI's turn."""
        if not self.playing:
            return

        target = self.player_frame.grid

        if self.must_fire:
            # The AI knows which cells are likely to hold boats

            (i, j), orientation = choice(self.must_fire)
            self.impossible.append((i, j))
            self.must_fire.remove(((i, j), orientation))

            # We don't know the enemy boat's orientation
            no_direction = len(self.hit_boat) == 1
            if not target[i][j].fire():
                # A miss
                if not self.must_fire:
                    # No remaining cell -> boat destroyed
                    self.not_destroyed.remove(len(self.hit_boat))
                    if min(self.not_destroyed) > self.dist:
                        # We can increase dist
                        self.dist = min(self.not_destroyed)
                        self.fire_grid = self._get_fire_grid()
                    for coords in self.hit_boat:
                        # No neighbouring cells contain boats
                        self.impossible += self._neighbours(coords)
                    self.hit_boat = []
            else:
                # We have hit a boat
                self.hit_boat.append((i, j))
                if no_direction:
                    # We now know the orientation
                    for coords, orient in self.must_fire:
                        if orient != OPPOSITES[orientation]:
                            self.must_fire.remove((coords, orient))

                if orientation == Orientation.NORTH:
                    i2, j2 = i - 1, j
                elif orientation == Orientation.SOUTH:
                    i2, j2 = i + 1, j
                elif orientation == Orientation.EAST:
                    i2, j2 = i, j + 1
                else:
                    i2, j2 = i, j - 1

                if 0 <= i2 < config.GRID_SIZE and 0 <= j2 < config.GRID_SIZE:
                    # Can we continue firing in that direction ?
                    self.must_fire.append(((i2, j2), orientation))

                if len(self.hit_boat) == max(self.not_destroyed):
                    # We must have destroyed a boat
                    self.not_destroyed.remove(len(self.hit_boat))
                    for coords in self.hit_boat:
                        self.impossible += self._neighbours(coords)
                    self.must_fire = []
                    self.hit_boat = []
        else:
            # Choose a random possible cell from the grid
            (i, j) = choice(self.fire_grid)
            while (i, j) in self.impossible:
                (i, j) = choice(self.fire_grid)

            self.fire_grid.remove((i, j))
            self.impossible.append((i, j))

            if target[i][j].fire():
                # We have hit something
                self.hit_boat = [(i, j)]
                if i != 0:
                    self.must_fire.append(((i - 1, j), Orientation.NORTH))
                if i != config.GRID_SIZE - 1:
                    self.must_fire.append(((i + 1, j), Orientation.SOUTH))
                if j != 0:
                    self.must_fire.append(((i, j - 1), Orientation.WEST))
                if j != config.GRID_SIZE - 1:
                    self.must_fire.append(((i, j + 1), Orientation.EAST))

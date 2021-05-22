"""Draw the battleships."""

from . import config
from .enums import Orientation, Status


def draw(canvas, cur_boat, num, orientation, status) -> None:
    """Draw a boat part in a canvas."""
    if status == Status.PLACING:
        conf = config.DRAW_PLACING
    elif status == Status.BLINKING:
        conf = config.DRAW_BLINKING
    else:
        conf = config.DRAW_HIT
    if (
        num == 0
        and orientation == Orientation.NORTH
        or (num == config.SIZES[cur_boat] - 1 and orientation == Orientation.SOUTH)
    ):
        # Bottom drawing
        canvas.create_arc(
            0,
            -config.CELL_SIZE * 3 / 4,
            config.CELL_SIZE * 21 / 20,
            config.CELL_SIZE * 3 / 4,
            extent=180,
            start=180,
            **conf["draw"]
        )
    elif (
        num == 0
        and orientation == Orientation.WEST
        or (num == config.SIZES[cur_boat] - 1 and orientation == Orientation.EAST)
    ):
        # Right drawing
        canvas.create_arc(
            -config.CELL_SIZE * 3 / 4,
            0,
            config.CELL_SIZE * 3 / 4,
            config.CELL_SIZE * 21 / 20,
            extent=180,
            start=-90,
            **conf["draw"]
        )
    elif (
        num == 0
        and orientation == Orientation.SOUTH
        or (num == config.SIZES[cur_boat] - 1 and orientation == Orientation.NORTH)
    ):
        # Top drawing
        canvas.create_arc(
            0,
            config.CELL_SIZE / 4,
            config.CELL_SIZE * 21 / 20,
            config.CELL_SIZE * 2,
            extent=180,
            **conf["draw"]
        )
    elif (
        num == 0
        and orientation == Orientation.EAST
        or (num == config.SIZES[cur_boat] - 1 and orientation == Orientation.WEST)
    ):
        # Left drawing
        canvas.create_arc(
            config.CELL_SIZE * 1 / 4,
            0,
            config.CELL_SIZE * 2,
            config.CELL_SIZE * 21 / 20,
            extent=180,
            start=90,
            **conf["draw"]
        )
    else:
        canvas.config(**conf["static"])

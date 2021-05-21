"""Enumaration types."""

from enum import Enum


class Orientation(Enum):
    """Orientation."""

    NORTH = "north"
    SOUTH = "south"
    EAST = "east"
    WEST = "west"


class Status(Enum):
    """Status for drawing."""

    PLACING = "placing"
    BLINKING = "blinking"
    HIT = "hit"

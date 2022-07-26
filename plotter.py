"""Plot a pie graph nicely. For Discord bots later."""

import typing as t

from matplotlib import pyplot as plt

DATA = {
    "DnD": 3,
    "Online": 4,
    "Offline": 8,
}


def do_pie(data: t.Dict[str, int]) -> None:
    """Plot a pie graph."""

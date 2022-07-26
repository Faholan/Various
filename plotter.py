"""Plot a pie graph nicely. For Discord bots later."""

from matplotlib import pyplot as plt

import typing as t


DATA = {
    "DnD": 3,
    "Online": 4,
    "Offline": 8,
}


def do_pie(data: t.Dict[str, int]) -> None:
    """Plot a pie graph."""

"""Battleship configuration."""

# Battleship configuration
GRID_SIZE = 10

CELL_SIZE = 50

SIZES = (5, 4, 3, 3, 2)

SHOW_AI_MISSED = True  # Show the hits missed by the AI

TITLE = "Battleship"

MAIN_CONFIG = {"bg": "gray30"}

FRAME_CONFIG = {"borderwidth": 5}

PLAYER_GRID = {"row": 0, "column": 0}
ENEMY_GRID = {"row": 0, "column": 1}

DRAW_PLACING = {
    "bg": "green",
    "border": "green4",
}

DRAW_BLINKING = {
    "bg": "yellow",
    "border": "yellow4",
}

DRAW_HIT = {
    "bg": "red",
    "border": "red4",
}

# Cell configuration
CELL_DEFAULT = {
    "bg": "gray30",
}

CELL_HIT = {
    "bg": "red",
}

CELL_MISSED = {
    "bg": "white",
}

CELL_BOAT = {
    "bg": "green",
}

CELL_BLINKING = {
    "bg": "yellow",
}

CONF_WIN = {
    "title": "You won!",
    "bg": "green3",
    "text": {
        "bg": "green3",
        "fg": "white",
        "text": "You won",
        "justify": "center",
        "font": "arial 20",
    },
}

CONF_LOSS = {
    "title": "You lost!",
    "bg": "red3",
    "text": {
        "bg": "red3",
        "fg": "white",
        "text": "You lost",
        "justify": "center",
        "font": "arial 20",
    },
}

RESTART_BTN = {
    "text": "RESTART",
    "bg": "green3",
    "fg": "white",
    "font": "arial 20",
}

QUIT_BTN = {
    "text": "QUIT",
    "bg": "red3",
    "fg": "white",
    "font": "arial 20",
}

END_TEXT_GRID = {
    "row": 0,
    "column": 0,
    "sticky": "ew",
}

RESTART_GRID = {
    "row": 1,
    "column": 0,
    "sticky": "nsew",
}

QUIT_GRID = {
    "row": 3,
    "column": 0,
    "sticky": "nsew",
}

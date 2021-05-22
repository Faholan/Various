"""Battleship configuration."""

# Battleship configuration
GRID_SIZE = 10  # Number of rows and columns in the grid

CELL_SIZE = 50  # Size (in pixel) of each square

SIZES = (5, 4, 3, 3, 2)  # Boat sizes

SHOW_AI_MISSED = False  # Show the hits missed by the AI

TITLE = "Battleship"

MAIN_CONFIG = {"bg": "gray30"}

FRAME_CONFIG = {"borderwidth": 5}

PLAYER_GRID = {"row": 0, "column": 0}
ENEMY_GRID = {"row": 0, "column": 1}

# Drawing

CELL_DEFAULT = {
    "bg": "gray30",
}

CELL_MISSED = {
    "bg": "white",
}

DRAW_PLACING = {
    "draw": {  # curved parts
        "fill": "green",
        "outline": "green4",
    },
    "static": {  # square parts (+ enemy)
        "bg": "green",
    },
}

DRAW_BLINKING = {
    "draw": {  # curved parts
        "fill": "yellow",
        "outline": "yellow4",
    },
    "static": {  # square parts (+ enemy)
        "bg": "yellow",
    },
}

DRAW_HIT = {
    "draw": {  # curved parts
        "fill": "red",
        "outline": "red4",
    },
    "static": {  # square parts (+ enemy)
        "bg": "red",
    },
}

# Endgame

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

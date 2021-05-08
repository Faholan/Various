CELL_ARGS = {
    "bg": "gray80",
    "highlightbackground": "gray4",
}
CELL_CLICKED = "gray30"
CELL_ZERO = "gray4"
CELL_FONT = "arial 20"

MINE_COLOR = "red3"
FLAG_COLOR = "red"

# Selection screen
SELECT_TITLE = "Minesweeper"
SELECT_TEXT = {
    "bg": "gray30",
    "fg": "white",
    "font": "arial 20",
    "text": "Choose the difficulty",
    "justify": "center",
}
DIFFICULTIES = (
    {
        "name": "Easy",
        "mines": 10,
        "rows": 8,
        "columns": 8,
        "cell_size": 60,
        "button_color": "green",
    },
    {
        "name": "Medium",
        "mines": 40,
        "rows": 16,
        "columns": 16,
        "cell_size": 35,
        "button_color": "midnight blue",
    },
    {
        "name": "Hard",
        "mines": 99,
        "rows": 16,
        "columns": 32,
        "cell_size": 30,
        "button_color": "red3",
    },
)

DIFFICULTY_BUTTON = {
    "fg": "white",
    "font": "arial 20"
}

# Game
GAME_TITLE = "Minesweeper"
GAME_BG = "gray30"

REMAINING_MINES = {
    "bg": "gray30",
    "fg": "white",
    "font": "arial 20",
    "relief": "flat",
    "justify": "left",
}

TIME_DISPLAY = {
    "bg": "gray30",
    "fg": "white",
    "font": "arial 20",
    "relief": "flat",
    "justify": "right"
}

# Losing
WRONG_FLAG = "dark turquoise"  # color of a wrongly placed flag
DISPLAY_MINES = "purple4"  # Color in which the mines are displayed at the end

# Highscore
HIGHSCORE_TEXT = {
    "font": "arial 20",
    "text": "New highscore ! Please enter your name",
    "justify": "center",
}

HIGHSCORE_ENTRY = {}

HIGHSCORE_BUTTON = {
    "text": "Submit",
}

# End screen
WIN_END = {
    "title": "You won",
    "bg": "green3",
    "text": {
        "bg": "green3",
        "fg": "white",
        "text": "It's a victory !",
        "justify": "center",
        "font": "arial 20"
    },
}

LOSE_END = {
    "title": "You lost",
    "bg": "red3",
    "text": {
        "bg": "red3",
        "fg": "white",
        "text": "It's a loss !",
        "justify": "center",
        "font": "arial 20"
    },
}

RESTART_BTN = {
    "text": "Start a new game",
    "bg": "green3",
    "fg": "white",
    "font": "arial 20",
}

QUIT_BTN = {
    "text": "Quit the game",
    "bg": "red3",
    "fg": "white",
    "font": "arial 20",
}

HIGHSCORE_LIST = {
    "selectmode": "single",
    "width": 30,
}

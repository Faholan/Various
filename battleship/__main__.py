"""Start the battleship game."""
from .battleship import Battleship

if __name__ == "__main__":
    PLAYING = True
    while PLAYING:
        PLAYING = Battleship().mainloop()

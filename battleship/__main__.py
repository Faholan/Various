"""Start the battleship game."""
from .battleship import Battleship

if __name__ == "__main__":
    playing = True
    while playing:
        playing = Battleship().mainloop()

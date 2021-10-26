"""Connection to the database for highscores."""

import sqlite3
import typing as t


class Database:
    """Class for managing all SQL-related things."""

    __slots__ = ("con",)

    def __init__(self) -> None:
        """Initialize the connection."""
        self.con = sqlite3.connect("minesweeper.db")
        self.initialize()

    def initialize(self) -> None:
        """Table creation."""
        cur = self.con.cursor()
        cur.execute(
            """CREATE TABLE IF NOT EXISTS highscores (
                difficulty INTEGER NOT NULL,
                time INTEGER NOT NULL,
                name TEXT NOT NULL,
                rowid INTEGER PRIMARY KEY
            )
            """
        )
        self.con.commit()

    def highscores(self, difficulty: int) -> list[tuple[int, str]]:
        """Fetch the highscores."""
        cur = self.con.cursor()
        return cur.execute(
            "SELECT time, name FROM highscores WHERE difficulty=? ORDER BY time ASC",
            (difficulty,),
        ).fetchall()

    def is_highscore(self, difficulty: int, time: int) -> tuple[bool, t.Optional[int]]:
        """
        Test if a score is in the leaderboard.

        Also returns the lowest highscore for increased performance, or None if there are less than ten of them
        """
        cur = self.con.cursor()
        high_list = cur.execute(
            "SELECT time FROM highscores WHERE difficulty=? ORDER BY time ASC",
            (difficulty,),
        ).fetchall()

        if len(high_list) < 10:
            return True, None

        lowest = high_list[-1][0]
        return time < lowest, lowest

    def insert_highscore(
        self,
        difficulty: int,
        time: int,
        name: str,
        lowest: t.Optional[int],
    ) -> None:
        """Insert a new highscore, deleting the lowest one."""
        cur = self.con.cursor()

        if lowest is not None:
            cur.execute(
                "DELETE FROM highscores WHERE rowid IN (SELECT rowid FROM highscores WHERE difficulty=? AND time=? LIMIT 1)",
                (difficulty, lowest),
            )

        cur.execute(
            "INSERT INTO highscores VALUES(?, ?, ?, NULL)",
            (difficulty, time, name),
        )
        self.con.commit()

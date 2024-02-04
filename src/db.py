# pylint: disable=missing-module-docstring
import sqlite3

class UGCDB:
    """A class to interact with the database ugc.db"""

    def __init__(self, db_path: str = ":memory:"):
        """Constructor for the UGCDB class
            Initializes the connection to the database and creates the tables if they don't exist

        Args:
            db_path (str): The path to the database file
        """
        self.con = sqlite3.connect(db_path)
        self.cur = self.con.cursor()

        with open("db/schema.sql", "r", encoding="utf-8") as f:
            self.cur.executescript(f.read())

        self.con.commit()

    def insert_movie(
        self, cinema_id: int, movie_id: int, movie_name: str, movie_img: str
    ) -> int:
        """Insert a movie into the database ugc

        Args:
            cinema_id (str): The cinema id of the cinema to get the movies from
            movie_id (str): The id of the movie
            movie_name (str): The name of the movie
            movie_img (str): The image url of the movie

        Returns:
            int: 1 if the movie is new, 0 if it already exists
        """
        formatted_name = movie_name.strip().capitalize()
        self.cur.execute(
            "INSERT OR IGNORE INTO movies (id, name, img_url) VALUES (?, ?, ?)",
            (movie_id, formatted_name, movie_img),
        )
        is_new_movie = self.cur.rowcount
        self.cur.execute(
            "INSERT OR IGNORE INTO screenings (movie_id, theater_id) VALUES (?, ?)",
            (movie_id, cinema_id),
        )
        self.con.commit()

        return is_new_movie

    def reset_screenings(self):
        """Reset the screenings table

        Returns:
            list: A list of the old data
        """
        self.cur.execute("DELETE FROM screenings")
        self.con.commit()

    def get_all_screenings(self) -> list:
        """Get the current screenings with movie name and theater name and image

        Returns:
            list: A list of the current screenings
        """
        self.cur.execute(
            """--begin-sql 
            SELECT m.name, t.name, m.img_url, m.id
            FROM movies m
            JOIN screenings s ON m.id = s.movie_id
            JOIN theaters t ON s.theater_id = t.id;
            """
        )
        screenings = self.cur.fetchall()
        grouped_screenings = {}
        for movie, theater, img_url, movie_id in screenings:
            if movie not in grouped_screenings:
                grouped_screenings[movie] = {
                    "theaters": [],
                    "img_url": img_url,
                    "id": movie_id,
                }
            grouped_screenings[movie]["theaters"].append(theater)

        return grouped_screenings

    def get_all_theaters(self) -> list:
        """Get all theaters in the database

        Returns:
            list: A list of all theaters
        """
        self.cur.execute("SELECT * FROM theaters")
        theaters = self.cur.fetchall()
        
        return theaters

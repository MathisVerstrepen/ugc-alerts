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
            
        self.is_first_run = self.cur.execute("SELECT * FROM movies").fetchone() is None
        print(f"First run: {self.is_first_run}")

        self.con.commit()
    
    def insert_movies(self, cinema_id: int, movies: list, movies_latest_screening: dict) -> int:
        """Insert a list of movies into the database ugc

        Args:
            cinema_id (str): The cinema id of the cinema to get the movies from
            movies (list): A list of movies to insert into the database
            movies_latest_screening (dict): A dictionary of the latest screening of each movie

        Returns:
            int: The number of new movies inserted
        """
        new_movies =  []
        for movie in movies:
            movie_name = movie["title"]
            movie_img = movie["img_url"]
            movie_id = movie["movie_id"]
            latest_screening = movies_latest_screening[movie_id]
            
            formatted_name = movie_name.strip().capitalize()
            
            # Check if this movie is new (no movie with the same id or latest_screening difference over 10 days)
            self.cur.execute(
                """--begin-sql 
                SELECT m.id
                FROM movies m
                WHERE m.id = ? AND julianday(?) - julianday(m.latest_screening) < 10;
                """,
                (movie_id, latest_screening),
            )
            
            # If it's new, insert it in movies and screenings tables
            if not self.cur.fetchone():
                new_movies.append(movie_id)
                self.cur.execute(
                    """--begin-sql 
                    INSERT OR IGNORE INTO movies (id, name, img_url, latest_screening) VALUES (?, ?, ?, ?);
                    """,
                    (movie_id, formatted_name, movie_img, latest_screening),
                )
                affected_rows = self.cur.rowcount
                
                if affected_rows == 0:
                    # If the movie was already in the database, update the latest_screening
                    self.cur.execute(
                        """--begin-sql 
                        UPDATE movies
                        SET latest_screening = ?
                        WHERE id = ?;
                        """,
                        (latest_screening, movie_id),
                    )
            
            # Else update the latest_screening and insert the screening
            else:
                self.cur.execute(
                    """--begin-sql 
                    UPDATE movies
                    SET latest_screening = ?
                    WHERE id = ? AND julianday(?) - julianday(latest_screening) > 0;
                    """,
                    (latest_screening, movie_id, latest_screening),
                )
                
            self.cur.execute(
                """--begin-sql 
                INSERT OR IGNORE INTO screenings (movie_id, theater_id) VALUES (?, ?);
                """,
                (movie_id, cinema_id),
            )
            
        self.con.commit()

        return new_movies

    def get_all_theaters(self) -> list:
        """Get all theaters in the database

        Returns:
            list: A list of all theaters
        """
        self.cur.execute("SELECT * FROM theaters")
        theaters = self.cur.fetchall()
        
        return theaters

    def get_movie_data(self, movie_id: int) -> dict:
        """Get the data of a movie from the database

        Args:
            movie_id (int): The id of the movie to get the data from

        Returns:
            dict: The data of the movie
        """
        self.cur.execute(
            """--begin-sql 
            SELECT m.id, m.name, m.img_url, GROUP_CONCAT(t.name, '\n') AS theaters
            FROM movies m
            JOIN screenings s ON m.id = s.movie_id
            JOIN theaters t ON s.theater_id = t.id
            WHERE m.id = ?;
            """,
            (movie_id,),
        )
        movie_data = self.cur.fetchone()

        return {
            "id": movie_data[0],
            "name": movie_data[1],
            "img_url": movie_data[2],
            "theaters": movie_data[3],
        }
        
    def debug(self):
        """Set a random movie latest_screening to 10 days ago"""
        
        self.cur.execute(
            """--begin-sql 
            UPDATE movies
            SET latest_screening = date('now', '-20 days')
            WHERE id = (SELECT id FROM movies ORDER BY RANDOM() LIMIT 1);
            """
        )
        
        self.con.commit()
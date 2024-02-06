# pylint: disable=missing-module-docstring
import os
import pathlib
from dotenv import load_dotenv

from src.ugc import get_current_screened_movies, get_movie_latest_screening
from src.db import UGCDB
from src.discord_bot import DiscordBot

if pathlib.Path("/.dockerenv").exists():
    print("Running in Docker")
    os.chdir("/app")
    load_dotenv("/app/.env")
else:
    print("Running locally")
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    load_dotenv(".env")

if __name__ == "__main__":
    ugc_db = UGCDB("db/ugc.db")
    discord_bot = DiscordBot()

    # For each cinema, get currently screened movies
    theater_data = {}
    for theater_id, theater_name in ugc_db.get_all_theaters():
        print(f"Getting movies for {theater_name}")
        theater_data[theater_id] = get_current_screened_movies(theater_id)

    # For each movie, get the latest screening
    movies_latest_screening = {}
    print("Getting latest screenings")
    for cinema_id, cinema_movies in theater_data.items():
        for movie in cinema_movies:
            movie_id = movie["movie_id"]
            if movie_id  in movies_latest_screening:
                continue
            
            movies_latest_screening[movie_id] = get_movie_latest_screening(movie_id)

    # ugc_db.debug()

    new_movies_ids = []
    print("Inserting new movies")
    for cinema_id, cinema_movies in theater_data.items():
        new_movies_ids += ugc_db.insert_movies(cinema_id, cinema_movies, movies_latest_screening)
        
    if ugc_db.is_first_run:
        print("First run, skipping Discord post")
        exit(0)
        
    # Post the new screenings in the Discord channel
    for movie_id in new_movies_ids:
        movie_data = ugc_db.get_movie_data(movie_id)

        discord_bot.post_message(
            movie_id = movie_data["id"],
            title = movie_data["name"],
            description = movie_data["theaters"],
            img_url = movie_data["img_url"],
        )

# pylint: disable=missing-module-docstring
import os
import pathlib
from dotenv import load_dotenv

from src.ugc import get_current_screened_movies
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

    # Save the current screenings and reset the screenings table
    previous_screenings = ugc_db.get_all_screenings()
    ugc_db.reset_screenings()

    # Insert the new screenings into the database
    for cinema_id, cinema_movies in theater_data.items():
        for movie in cinema_movies:
            ugc_db.insert_movie(
                cinema_id, movie["movie_id"], movie["title"], movie["img_url"]
            )

    # Post the new screenings in the Discord channel
    for movie_name, movie_data in ugc_db.get_all_screenings().items():
        if movie_name in previous_screenings:
            if movie_data == previous_screenings[movie_name]:
                continue

        theaters = movie_data["theaters"]
        discord_bot.post_message(
            title=movie_name,
            description="\n".join([f" * {theater}" for theater in theaters]),
            img_url=movie_data["img_url"],
            movie_id=movie_data["id"],
        )

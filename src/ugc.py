# pylint: disable=missing-module-docstring, wrong-import-position
import datetime
import requests
from bs4 import BeautifulSoup

from src.exceptions import RequestFailedException

headers = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/115.0",
}


def get_current_screened_movies(cinema_id: int) -> list:
    """Get all current movies screened in a cinema from UGC website

    Args:
        cinema_id (int): The cinema id of the cinema to get the movies from

    Returns:
        list: A list of all current movies screened in the cinema
    """
    url = f"https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action?filter=stillOnDisplay&cinemaId={cinema_id}&reset=false"

    req = requests.get(url, timeout=10, headers=headers)

    if req.status_code != 200:
        raise RequestFailedException(
            f"Request failed with status code {req.status_code}"
        )

    req_html = req.text

    soup = BeautifulSoup(req_html, "html.parser")
    movies_box = soup.find_all("div", class_="component--film-tile")

    data = []
    for movie_box in movies_box:
        movie_html_link = (
            movie_box.find("a", class_="cta--pink").get("href").split("=")[-1]
        )
        movie_id = movie_html_link.split(".")[0].split("_")[-1]
        title = movie_box.find("a", class_="color--dark-blue").text
        img_url = movie_box.find("img").get("data-src")

        data.append(
            {
                "movie_html_link": movie_html_link,
                "title": title,
                "img_url": img_url,
                "movie_id": movie_id,
            }
        )

    return data


def get_movie_latest_screening(move_id: int, movie_html_link: str) -> dict:
    """Get the latest screening of a movie from UGC website

    Args:
        move_id (int): The id of the movie to get the latest screening from

    Returns:
        dict: The latest screening of the movie
    """
    url = "https://www.ugc.fr/showingsFilmAjaxAction!getDaysByFilm.action"

    querystring = {
        "reloadShowingsTopic": "reloadShowingsMob",
        "dayForm": "dayFormMobile",
        "filmId": move_id,
        "day": "",
    }

    c_headers = {
        **headers,
        "Referer": f"https://www.ugc.fr/{movie_html_link}?mtm_kwd=POLE_POSITION_RUBRIQUE_CINEMAS",
    }

    req = requests.post(url, params=querystring, timeout=10, headers=c_headers)

    if req.status_code != 200:
        raise RequestFailedException(
            f"Request failed with status code {req.status_code}"
        )

    soup = BeautifulSoup(req.text, "html.parser")
    dates = soup.find_all("div", class_="slider-item")

    screenings_dates = []
    for date in dates:
        datestr = date["id"].split("_")[-1]
        screenings_dates.append(datetime.datetime.strptime(datestr, "%Y-%m-%d").date())

    if not screenings_dates:
        return None

    # Sort and get the latest screening
    screenings_dates.sort()

    return screenings_dates[-1]

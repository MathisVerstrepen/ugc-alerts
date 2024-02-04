# pylint: disable=missing-module-docstring
import requests
from bs4 import BeautifulSoup


def get_current_screened_movies(cinema_id: int) -> list:
    """Get all current movies screened in a cinema from UGC website

    Args:
        cinema_id (int): The cinema id of the cinema to get the movies from

    Returns:
        list: A list of all current movies screened in the cinema
    """
    url = f"https://www.ugc.fr/filmsAjaxAction!getFilmsAndFilters.action?filter=stillOnDisplay&cinemaId={cinema_id}&reset=false"

    req = requests.get(url, timeout=5)
    req_html = req.text

    soup = BeautifulSoup(req_html, "html.parser")
    movies_box = soup.find_all("div", class_="component--film-tile")

    data = []
    for movie_box in movies_box:
        movie_id = movie_box.find("a", class_="cta--pink").get("href").split("=")[-1]
        title = movie_box.find("a", class_="color--dark-blue").text
        img_url = movie_box.find("img").get("data-src")

        data.append({"movie_id": movie_id, "title": title, "img_url": img_url})

    return data

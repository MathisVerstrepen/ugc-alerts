# pylint: disable=missing-module-docstring, wrong-import-position
import datetime
import itertools
import pathlib
import re
import urllib.parse

import requests
from bs4 import BeautifulSoup

from src.exceptions import RequestFailedException

PROXY_FILE = pathlib.Path(__file__).resolve().parent.parent / "proxies.txt"
UGC_BASE_URL = "https://www.ugc.fr/"


def _extract_movie_id(movie_url: str) -> int:
    parsed_url = urllib.parse.urlparse(movie_url)
    query_id = urllib.parse.parse_qs(parsed_url.query).get("id")
    if query_id and query_id[0].isdigit():
        return int(query_id[0])

    path_id = re.search(r"_(\d+)\.html$", parsed_url.path)
    if path_id:
        return int(path_id.group(1))

    raise ValueError(f"Unable to extract movie id from URL: {movie_url}")


def _load_proxies() -> list:
    proxies = []

    try:
        proxy_lines = PROXY_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError as exc:
        raise RuntimeError(f"Proxy file not found: {PROXY_FILE}") from exc

    for line_number, proxy_line in enumerate(proxy_lines, start=1):
        if not proxy_line.strip():
            continue

        proxy_parts = proxy_line.strip().split(":", maxsplit=3)
        if len(proxy_parts) != 4 or not all(proxy_parts):
            raise ValueError(
                f"Invalid proxy on line {line_number}; expected host:port:user:password"
            )

        host, port, username, password = proxy_parts
        proxy_url = "socks5://{}:{}@{}:{}".format(
            urllib.parse.quote(username, safe=""),
            urllib.parse.quote(password, safe=""),
            host,
            port,
        )
        proxies.append({"http": proxy_url, "https": proxy_url})

    if not proxies:
        raise ValueError(f"No proxies found in {PROXY_FILE}")

    return proxies


PROXIES = itertools.cycle(_load_proxies())

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

    req = requests.get(url, timeout=10, proxies=next(PROXIES), headers=headers)

    if req.status_code != 200:
        raise RequestFailedException(
            f"Request failed with status code {req.status_code}"
        )

    req_html = req.text

    soup = BeautifulSoup(req_html, "html.parser")
    movies_box = soup.find_all("div", class_="component--film-tile")

    data = []
    for movie_box in movies_box:
        movie_html_link = urllib.parse.urljoin(
            UGC_BASE_URL, movie_box.find("a", class_="cta--pink").get("href")
        )
        movie_id = _extract_movie_id(movie_html_link)
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

    movie_url = urllib.parse.urljoin(UGC_BASE_URL, movie_html_link)
    query_separator = "&" if urllib.parse.urlparse(movie_url).query else "?"
    c_headers = {
        **headers,
        "Referer": f"{movie_url}{query_separator}mtm_kwd=POLE_POSITION_RUBRIQUE_CINEMAS",
    }

    req = requests.post(
        url,
        params=querystring,
        timeout=10,
        proxies=next(PROXIES),
        headers=c_headers,
    )

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

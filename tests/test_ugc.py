import unittest

from src.ugc import _extract_movie_id


class ExtractMovieIdTests(unittest.TestCase):
    def test_extracts_id_from_absolute_slug_url(self):
        self.assertEqual(
            _extract_movie_id("https://www.ugc.fr/film_dans_l_ombre_18512.html"),
            18512,
        )

    def test_extracts_id_from_relative_slug_url(self):
        self.assertEqual(_extract_movie_id("film_dans_l_ombre_18512.html"), 18512)

    def test_extracts_id_from_legacy_query_url(self):
        self.assertEqual(_extract_movie_id("film.html?id=18512"), 18512)

    def test_rejects_url_without_numeric_id(self):
        with self.assertRaisesRegex(ValueError, "Unable to extract movie id"):
            _extract_movie_id("https://www.ugc.fr/films.html")


if __name__ == "__main__":
    unittest.main()

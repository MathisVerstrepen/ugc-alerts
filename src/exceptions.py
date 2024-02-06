# pylint: disable=missing-module-docstring
class RequestFailedException(Exception):
    """
    Exception raised when a request to the Letterboxd fails
    """

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

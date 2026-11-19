import logging
import sys

class OneError(Exception):
    """Base class for exceptions in the One application."""

    code: str = "ONE_ERROR"
    user_message: str = "An unexpected error occurred"

    def __init__(self, message: str | None = None,):
        self.message = message or self.user_message
        super().__init__(self.message)

def setup_logging() -> None:
    logging.basicConfig(
        level=logging.DEBUG,
        format=(
            "%(asctime)s | " 
            "%(name)s | "
            "%(levelname)s-8s | "
            "%(message)s"
        ),
        handlers=[
            logging.StreamHandler(sys.stderr)
        ]
    )
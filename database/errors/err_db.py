from src.exceptions.base_err import OneError

class DatabaseError(OneError):
    """Raised when there is an error related to the database."""

    code: str = "DATABASE_ERROR"
    user_message: str = "An unexpected error occurred while interacting with the database."

class TimeoutError(OneError):
    code: str = "DB_TIMEOUT"
    user_message: str = "Database operation timed out"
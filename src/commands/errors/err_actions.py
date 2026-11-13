from src.exceptions.base_err import OneError

class StatusError(OneError):
    """Raised when the status of a task is invalid."""

    code: str = "INVALID_STATUS"
    user_message: str = "The status provided is not valid. Please use 'pending', 'finished', or 'in progress'."

class AppNotFound(OneError):
    """Raised when there is an error related to the application."""

    code: str = "APP_NOT_FOUND"
    user_message: str = "Application could not be found."

class UrlError(OneError):
    """Raised when there is an error related to a URL."""

    code: str = "URL_ERROR"
    user_message: str = "The provided URL could not be opened. Please try again."

class SpotifyError(OneError):
    """Raised when there is an error related to Spotify."""

    code: str = "SPOTIFY_ERROR"
    user_message: str = "There was an issue with Spotify."

class TaskNotFoundError(OneError):
    """Raised when a task is not found in the database."""

    code: str = "TASK_NOT_FOUND"
    user_message: str = "The specified task could not be found."

class HistoryQueryError(OneError):
    """Raised when the history query fails."""

    code: str = "HISTORY_QUERY_ERROR"
    user_message: str = "Error in querying the history. Verify if not empty"
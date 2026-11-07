from src.exceptions.base_err import OneError

class StatusError(OneError):
    """Raised when the status of a task is invalid."""

    code: str = "INVALID_STATUS"
    user_message: str = "The status provided is not valid. Please use 'pending', 'finished', or 'in progress'."

class AppNotFound(OneError):
    """Raised when there is an error related to the application."""

    code: str = "APP_NOT_FOUND"
    user_message: str = "Application could not be found. Please ensure it is installed and try again."


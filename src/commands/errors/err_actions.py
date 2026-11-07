from src.exceptions.base_err import OneError

class StatusError(OneError):
    """Raised when the status of a task is invalid."""

    code: str = "INVALID_STATUS"
    user_message: str = "The status provided is not valid. Please use 'pending', 'finished', or 'in progress'."

    


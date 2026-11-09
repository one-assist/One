from src.exceptions.base_err import OneError

class ListenerError(OneError):
    """Raised when there is an error related to the listener."""

    code: str = "LISTENER_ERROR"
    user_message: str = "An unexpected error occurred while audio processing pipeline."
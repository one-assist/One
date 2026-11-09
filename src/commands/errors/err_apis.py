from src.exceptions.base_err import OneError

class GeminiError(OneError):
    """Raised when there is an error related to Gemini."""

    code: str = "GEMINI_ERROR"
    user_message: str = "A unexpected error occurred while interacting with Gemini."
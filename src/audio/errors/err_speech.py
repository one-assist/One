from src.exceptions.base_err import OneError

class SpeechError(OneError):
    """Raised when there is an error related in speech function."""

    code: str = "SPEECH_ERROR"
    user_message: str = "Unable to synthesize or play speech"
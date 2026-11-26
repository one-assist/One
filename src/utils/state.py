"""Shared mutable runtime state for audio capture and transcription."""

import queue


class AppState:
    def __init__(self) -> None:
        self.q: queue.Queue[object] = queue.Queue()
        self.is_processing: bool = False
        self.is_sleeping: bool = False


state = AppState()

"""Shared mutable runtime state for audio capture, speech, and session UI."""

import queue
import threading


class AppState:
    def __init__(self) -> None:
        self.q: queue.Queue[object] = queue.Queue()
        self.is_processing: bool = False
        self.is_sleeping: bool = False
        self.is_speaking: bool = False
        self._panel_lock: threading.Lock = threading.Lock()
        self.panel_open: bool = False
        self.panel_title: str = "Session"
        self.panel_content: str = "No session results yet."

    def show_panel(self, title: str, content: str) -> None:
        """Publish content for the session panel and reveal it."""
        with self._panel_lock:
            self.panel_title = title
            self.panel_content = content
            self.panel_open = True

    def toggle_panel(self) -> None:
        """Show or hide the session panel without discarding its content."""
        with self._panel_lock:
            self.panel_open = not self.panel_open

    def panel_snapshot(self) -> tuple[bool, str, str]:
        """Return a consistent session-panel state for the UI thread."""
        with self._panel_lock:
            return self.panel_open, self.panel_title, self.panel_content


state = AppState()

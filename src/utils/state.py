"""Shared mutable runtime state for audio capture, speech, and session UI."""

import queue
import threading


class AppState:
    def __init__(self) -> None:
        self.q: queue.Queue[object] = queue.Queue()
        self.is_processing: bool = False
        self.is_sleeping: bool = False
        self.is_speaking: bool = False
        self._ui_lock: threading.Lock = threading.Lock()
        self.status_message: str = "Loading speech recognition..."
        self.panel_open: bool = False
        self.panel_title: str = "Session results"
        self.panel_content: str = ""

    def set_status(self, message: str) -> None:
        with self._ui_lock:
            self.status_message = message

    def get_status(self) -> str:
        with self._ui_lock:
            return self.status_message

    def show_panel(self, title: str, content: str) -> None:
        """Append one visually separated result and reveal the session panel."""
        entry = f"╭─ {title}\n{content}\n╰────────────────────────"
        with self._ui_lock:
            if self.panel_content:
                self.panel_content = f"{self.panel_content}\n\n{entry}"
            else:
                self.panel_content = entry
            self.panel_open = True

    def toggle_panel(self) -> None:
        """Show or hide the session panel without discarding its content."""
        with self._ui_lock:
            self.panel_open = not self.panel_open

    def ui_snapshot(self) -> tuple[str, bool, str, str]:
        """Return consistent status and panel values for the UI thread."""
        with self._ui_lock:
            return (
                self.status_message,
                self.panel_open,
                self.panel_title,
                self.panel_content,
            )


state = AppState()

"""Tests for transient session-panel state."""

import unittest

from src.utils.state import AppState


class TestAppState(unittest.TestCase):
    def test_panel_content_survives_closing(self) -> None:
        app_state = AppState()

        app_state.show_panel("Tasks", "#1  Write documentation")
        self.assertEqual(
            app_state.panel_snapshot(),
            (True, "Tasks", "#1  Write documentation"),
        )

        app_state.toggle_panel()
        self.assertEqual(
            app_state.panel_snapshot(),
            (False, "Tasks", "#1  Write documentation"),
        )


if __name__ == "__main__":
    unittest.main()

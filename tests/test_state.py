"""Tests for transient session-panel state."""

import unittest

from src.utils.state import AppState


class TestAppState(unittest.TestCase):
    def test_panel_content_survives_closing(self) -> None:
        app_state = AppState()

        app_state.show_panel("Tasks", "#1  Write documentation")
        app_state.show_panel("History", "#2  VIEW_TASKS")

        status, is_open, title, content = app_state.ui_snapshot()
        self.assertEqual(status, "Loading speech recognition...")
        self.assertTrue(is_open)
        self.assertEqual(title, "Session results")
        self.assertIn("╭─ Tasks", content)
        self.assertIn("╭─ History", content)

        app_state.toggle_panel()
        _, is_open, _, content_after_close = app_state.ui_snapshot()
        self.assertFalse(is_open)
        self.assertEqual(content_after_close, content)


if __name__ == "__main__":
    unittest.main()

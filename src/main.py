# This is where the connection between `start_listening()` and the interface is made.

import logging
import os
import queue
import threading
from datetime import timedelta

import slint

from src.audio.listener import start_listerning
from src.audio.speech import model_is_ready, model_load_finished, preload_model
from src.exceptions.base_err import setup_logging
from src.utils.state import state
from src.utils.timing import measure

logger = logging.getLogger(__name__)


def main():
    setup_logging()

    with measure("Slint setup"):
        path = os.path.dirname(os.path.abspath(__file__))
        slint_path = os.path.join(path, "..", "frontend", "app-window.slint")
        ui = slint.load_file(slint_path)
        app = ui.MainWindow()

    event_status = threading.Event()
    app.assistant_listening = False
    app.assistant_ready = False
    app.assistant_speaking = False
    status_message, panel_open, panel_title, panel_content = state.ui_snapshot()
    app.assistant_status = status_message
    app.panel_open = panel_open
    app.panel_title = panel_title
    app.panel_content = panel_content

    def switch():
        """Keep the listener Event and the Slint indicator in the same state."""
        if not model_is_ready():
            logger.info("Listener remains disabled while the speech model is loading")
            return

        if event_status.is_set():
            event_status.clear()
            while True:
                try:
                    state.q.get_nowait()
                except queue.Empty:
                    break
            logger.debug("Discarded pending audio after disabling listener")
        else:
            event_status.set()

        is_listening = event_status.is_set()
        app.assistant_listening = is_listening
        logger.info("Listener enabled: %s", is_listening)

    def update_model_status():
        if not model_load_finished():
            return

        readiness_timer.stop()
        if model_is_ready():
            app.assistant_ready = True
            state.set_status("ONE is ready")
            logger.info("ONE is ready to receive commands")
        else:
            state.set_status("Speech recognition failed to load")
            logger.error("ONE cannot receive commands because Whisper did not load")

    def update_speaking_state():
        app.assistant_speaking = state.is_speaking
        status_message, panel_open, panel_title, panel_content = state.ui_snapshot()
        app.assistant_status = status_message
        app.panel_open = panel_open
        app.panel_title = panel_title
        app.panel_content = panel_content

    def toggle_panel():
        state.toggle_panel()

    app.start_program = switch
    app.toggle_panel = toggle_panel

    model_loader = threading.Thread(
        target=preload_model,
        name="whisper-preload",
        daemon=True,
    )
    model_loader.start()

    listener = threading.Thread(
        target=start_listerning,
        args=(event_status,),
        name="audio-listener",
        daemon=True,
    )
    listener.start()

    readiness_timer = slint.Timer()
    readiness_timer.start(
        slint.TimerMode.Repeated,
        timedelta(milliseconds=100),
        update_model_status,
    )

    speaking_timer = slint.Timer()
    speaking_timer.start(
        slint.TimerMode.Repeated,
        timedelta(milliseconds=50),
        update_speaking_state,
    )
    app.run()


if __name__ == "__main__":
    main()

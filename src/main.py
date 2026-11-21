# This is where the connection between `start_listening()` and the interface is made.

import logging
import os
import threading

import slint

from src.audio.listener import *
from src.exceptions.base_err import setup_logging

logger = logging.getLogger(__name__)

started = time.perf_counter()

def main():
    setup_logging()
    
    path = os.path.dirname(os.path.abspath(__file__))
    slint_path = os.path.join(path, '..', 'frontend', 'app-window.slint')

    #load the ui
    ui = slint.load_file(slint_path)
    app = ui.MainWindow()

    event_status = threading.Event()
    event_status.clear()
    app.assistant_listening = False

    def switch():
        """Keep the listener Event and the Slint indicator in the same state."""
        if event_status.is_set():
            event_status.clear()
        else:
            event_status.set()

        is_listening = event_status.is_set()
        app.assistant_listening = is_listening
        logger.info("Listener enabled: %s", is_listening)

    app.start_program = switch

    listener = threading.Thread(target=start_listerning, args=(event_status,))
    listener.daemon = True
    listener.start()

    app.run()

    logger.info("Application time %.2fs", time.perf_counter() - started)

if __name__ == "__main__":
    main()

# This is where the connection between `start_listening()` and the interface is made.

from src.audio.listener import *
import slint
import os
import threading


def main():
    path = os.path.dirname(os.path.abspath(__file__))
    slint_path = os.path.join(path, '..', 'frontend', 'app-window.slint')

    #load the ui
    ui = slint.load_file(slint_path)
    app = ui.MainWindow()

    event_status = threading.Event()
    event_status.clear()

    def switch():
        #Is called when the user toggles the program on/off
        # If event_status is true, the clear() reverts to the default value (false)
        if event_status.is_set():
            event_status.clear()
        else:
            event_status.set()

    app.start_program = switch

    listener = threading.Thread(target=start_listerning, args=(event_status,))
    listener.daemon = True
    listener.start()

    app.run()


if __name__ == "__main__":
    main()

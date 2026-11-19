# Audio Listener & Processing Pipeline

This document explains the core audio capture, primarily handled in `listener.py` and orchestrated by `main.py`.

## High-Level Architecture

The listener module operates as a background daemon thread that continuously captures audio from the user's microphone. It uses a Voice Activity Detection (VAD) system to segment speech from silence. Once a valid speech segment is recorded, it is sent to a transcription model, and the resulting text is passed through a custom NLP pipeline (Classifier, Lexer/Scanner, Parser, and AST Checker) to execute commands.

The connection between the user interface and the audio listener is managed via a `threading.Event`. This allows the UI to easily pause or resume the listener.

## Integration with the UI 

The application entry point initializes the Slint user interface and, upon clicking the Voice-orb, starts the background audio listener. Additionally, there is a thread control event (`event_status`), a thread-safe boolean flag, that determines whether the listener should be actively recording or ignoring microphone input. 

The UI has a toggle switch that triggers the `switch()` function. If `event_status` is set, it clears it (pausing the listener); if cleared, it sets it (resuming the listener).
* **Daemon Thread**: `start_listerning` runs on a dedicated daemon thread, meaning it runs continuously in the background without blocking the UI and will automatically terminate when the main UI application is closed.

## The Audio Capture System 

The audio pipeline is initialized using the `sounddevice.InputStream` with a sample rate of 16,000 Hz and a frame duration of 30 milliseconds.

### The `callback` Function

The `callback` function is the most critical part of the real-time audio capture. It is invoked automatically by the audio stream every time a new frame of audio (30ms chunk) is available.

Here is how the logic flows inside the callback:

- **State Verification**: Before processing audio, it checks `event_status.is_set()` and `state.is_processing`. If the program is toggled off from the UI, or if the system is currently processing a previous command, the callback immediately clears the audio buffer, resets the tracking variables, and ignores the input. This prevents audio overlap and ensures the system only listens when ready.
- **Audio Conversion**: The raw audio (`float32`) is isolated and converted to 16-bit PCM bytes (`np.int16`), which is the format required by the `webrtcvad` engine.
- **Voice Activity Detection (VAD)**: The `vad.is_speech()` method evaluates the audio chunk. 
    * **If speech is detected**: `is_recording` is set to `True`, the silence counter (`offtime`) is reset to 0, and the frame is appended to the `buffer` list.
    * **If silence is detected**: If the system was already in the middle of recording (`is_recording == True`), it continues to append the silent frame to the buffer (to maintain natural pauses) and increments the `offtime` counter.
- **End of Speech Detection**: If the silence `offtime` exceeds 15 frames (approx. 450ms), the system assumes the user has finished speaking. 
    * It then checks whether the overall `buffer` has at least `MIN_AUDIO_FRAMES` frames (currently 20), filtering out very brief accidental noises while allowing short answers such as task states.
    * If valid, all frames in the buffer are concatenated into a single audio array and pushed to the thread-safe queue (`state.q`).
    * Finally, the buffer is cleared, and recording states are reset.

### The Main Processing Loop

While the `callback` handles the real-time audio gathering, the main loop in `start_listerning` handles the processing:

- **Wait State**: The loop blocks at `event_status.wait()`, consuming zero CPU cycles until the user turns the application on via the UI.
- **Fetching Audio**: It continuously tries to pull a complete audio chunk from `state.q`.
- **Processing Lock**: Once an audio chunk is retrieved, `state.is_processing` is set to `True`. This acts as a lock, signaling the `callback` to drop incoming audio while the current command is being executed.
- **Transcription**: The audio chunk is passed to `transcribe_audio(audio_chunk)`, which converts the bytes into English text.
- **State Management (Sleep/Wake)**: 
    * If the transcribed text is exactly `"sleep"`, the assistant enters a dormant state where it stops processing normal commands.
    * If the text is `"wake"`, it becomes active again.
- **Command Execution Pipeline**: If the system is awake and valid text is received, it goes through the custom NLP pipeline:
    * **Classifier**: Determines the high-level intent behind the text (`intent_object.intent`).
    * **Lexer/Scanner**: Tokenizes the raw string into semantic tokens.
    * **Parser**: Takes the tokens and the intent to build an Abstract Syntax Tree (AST).
    * **AST Checker**: Evaluates and executes the instructions defined in the AST root.
- **Error recovery**: Unexpected errors in transcription, classification, parsing, or AST execution are recorded with a traceback and ONE provides a short spoken failure message. This prevents one failed command from terminating the processing loop.
- **Cleanup**: In the `finally` block, the system aggressively clears any pending audio chunks that might have accumulated in `state.q` during execution. This ensures the assistant does not process stale or delayed audio, then it releases the lock (`state.is_processing = False`), allowing the callback to record again even after a processing error.
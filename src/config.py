# Configuration constants for audio capture and processing

SAMPLERATE = 16000
FRAMEDURATION = 30  # ms
FRAME_SIZE = int(SAMPLERATE * FRAMEDURATION / 1000)
VAD_AGGRESSIVENESS = 2

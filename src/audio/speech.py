

import contextlib
import logging
import os
import queue
import subprocess
import threading
import time

from faster_whisper import WhisperModel
from gtts import gTTS

from src.audio.errors.err_speech import *
from src.utils.state import state
from src.utils.timing import measure

logger = logging.getLogger(__name__)
model: WhisperModel | None = None
_model_lock = threading.Lock()
_model_loaded = threading.Event()
_model_loading = False


def preload_model() -> None:
    """Load Whisper once without blocking the UI thread."""
    global model, _model_loading

    with _model_lock:
        if _model_loading or _model_loaded.is_set():
            return
        _model_loading = True

    try:
        with measure("Whisper model preload"):
            model = WhisperModel("base.en", device="cpu", compute_type="int8")
        logger.info("Whisper model is ready")
    except Exception:
        logger.exception("Unable to load the Whisper model")
    finally:
        _model_loaded.set()


def model_load_finished() -> bool:
    """Return whether the preload attempt has completed."""
    return _model_loaded.is_set()


def model_is_ready() -> bool:
    """Return whether Whisper loaded successfully."""
    return model is not None


def get_model() -> WhisperModel:
    """Wait for the shared Whisper model, loading it on demand if needed."""
    if not _model_loaded.is_set():
        preload_model()
        _model_loaded.wait()

    if model is None:
        raise RuntimeError("Whisper model is unavailable")

    return model

#Função para voz de resposta a comandos
def speech(text: str):
    filename = "speech.mp3"

    try:
        tts = gTTS(text=text, lang="en")
        tts.save(filename)

        result = subprocess.run(
            ["ffplay", "-nodisp", "-autoexit", filename],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            logger.error(
                "ffplay failed with exit code %s: %s",
                result.returncode,
                result.stderr.strip(),
            )
    except Exception:
        logger.exception("Unable to synthesize or play speech")
        
    finally:
        if os.path.exists(filename):
            os.remove(filename)

    time.sleep(0.4)

def clean_text(text: str) -> str:
    cleaned = text.strip()\
        .replace(".", "")\
        .replace(",", "")\
        .replace("!", "")\
        .replace("?", "")\
        .replace(";", "")\
        .lower()
    return cleaned

def transcribe_audio(audio):
    prompts = "close, search, start, gemini, up, down, task, create, view"
    segments, _ = get_model().transcribe(
        audio, 
        language="en",
        condition_on_previous_text=False, 
        no_speech_threshold=0.6,         
        vad_filter=True, 
        beam_size=5, 
        temperature=[0.0, 0.2, 0.4, 0.6], 
        compression_ratio_threshold=2.4,  
        log_prob_threshold=-1.0,
        initial_prompt=prompts,
       )
    text_cleaned = None
    
    for segment in segments:
        text_cleaned = clean_text(segment.text)

    return text_cleaned
    
@contextlib.contextmanager
def limited_hear():
    #clear the queue
    while not state.q.empty():
        try:    
            state.q.get_nowait()
        except queue.Empty:
            pass
    
    # Set is_processing to False to indicate that the listener is not processing
    state.is_processing = False
    try:
        yield
    finally:
        state.is_processing = True

def ask_user(ask: str) -> str:
    speech(ask)

    with limited_hear():
        while True:
            try:
                audio_chunk = state.q.get(timeout=0.5)
            except queue.Empty:
                continue

            text = transcribe_audio(audio_chunk)
            if text:
                 return text

import contextlib
import logging
import os
import queue
import subprocess
import time

from faster_whisper import WhisperModel
from gtts import gTTS
from src.state import state
from src.audio.errors.err_speech import *

logger = logging.getLogger(__name__)
model = WhisperModel("base.en", device= "cpu", compute_type= "int8")

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
            logging.getLogger(__name__).error(
                "ffplay failed with exit code %s: %s",
                result.returncode,
                result.stderr.strip(),
            )
    except SpeechError as error:
        logger.error("[%s] %s", error.code, error.user_message)
        
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
    segments, _ = model.transcribe(
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

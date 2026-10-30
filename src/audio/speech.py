from gtts import gTTS
import os
import subprocess
from faster_whisper import WhisperModel
import queue
import contextlib
from src.state import state
import time

model = WhisperModel("base.en", device= "cpu", compute_type= "int8")

#Função para voz de resposta a comandos
def speech(text: str):
    tts = gTTS(text = text, lang ='en')
    tts.save("speech.mp3")

    _ = subprocess.run(
        ["ffplay", "-nodisp", "-autoexit", "speech.mp3"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check = False
    )
        
    if os.path.exists("speech.mp3"):
        os.remove("speech.mp3")

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
        print(text_cleaned)

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

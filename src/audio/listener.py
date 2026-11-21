"""
This is the core part of the code: speech is captured, 
and the resulting bytes are stored in a list (q). 
The data then passes through a transcription function that converts it into text (in English). 
Once converted, the text is processed by a Lexer/Parser/AST structure;
within the AST, it undergoes a conditional check to determine whether it constitutes a valid command.
"""

import logging
import queue
import threading
import webrtcvad
import sounddevice as sd
import numpy as np

from src.commands.actions import *
from src.lexer.scanner import *
from src.parser.parser import *
from src.ast.checker import ast_checker
from src.audio.speech import speech, transcribe_audio
from src.utils.state import state
from src.classifier.model import *
from src.audio.errors.err_listener import *
from src.utils.config import (
    END_SILENCE_FRAMES,
    FRAME_SIZE,
    MIN_AUDIO_FRAMES,
    SAMPLERATE,
    VAD_AGGRESSIVENESS,
)
from src.utils.timing import measure


logger = logging.getLogger(__name__)
                         
#By default, the event is false
def start_listerning(event_status: threading.Event):
    vad = webrtcvad.Vad(VAD_AGGRESSIVENESS)
    logger.info("Starting audio listener (device=%s, sample_rate=%s)", sd.default.device, SAMPLERATE)
    speech("Welcome to One. How can I help you?")
    state.is_sleeping = False
    buffer = []
    is_recording = False
    offtime = 0
    
    #the callback function, called by the inputStream
    def callback(indata, frames, time, status):
        nonlocal is_recording, offtime
       
        if status:
            logger.warning("Audio input status: %s", status)

        #if the event is false, clear the buffer and return
        if not event_status.is_set() or state.is_processing:
            if len(buffer) > 0:
                buffer.clear()
                is_recording = False
                offtime = 0
            return
        
        clear_indata = indata[:, 0]
        # sounddevice usually provides samples in [-1.0, 1.0], but clipping
        # prevents an out-of-range sample from overflowing when converted to int16.
        clear_bytes = (np.clip(clear_indata, -1.0, 1.0) * 32767).astype(np.int16).tobytes()
    
        if vad.is_speech(clear_bytes, SAMPLERATE):
            if not is_recording:
                logger.info("Speech detected; recording audio")
            is_recording = True
            offtime = 0
            buffer.append(clear_indata.copy())
            
        else:
            if is_recording:
                buffer.append(clear_indata.copy())
                offtime += 1
                
                if offtime > END_SILENCE_FRAMES:
                    if len(buffer) >= MIN_AUDIO_FRAMES:
                        final_audio = np.concatenate(buffer)
                        state.q.put(final_audio)
                        logger.info("Audio queued for transcription (%s frames)", len(buffer))
                    else:
                        logger.debug("Discarded short audio recording (%s frames)", len(buffer))

                    buffer.clear()
                    is_recording = False
                    offtime = 0

    
    try:
        with sd.InputStream(
            samplerate=SAMPLERATE,
            channels=1,
            dtype="float32",
            callback=callback,
            blocksize=FRAME_SIZE,
        ):
            logger.info("Audio input stream opened; waiting for the UI to enable listening")
            while True:
                event_status.wait() #Blocks thread execution until event() is true

                try:
                    audio_chunk = state.q.get(timeout = 0.5)
                except queue.Empty:
                    continue


                state.is_processing = True
                
                try:
                    with measure("Transcription"):
                        #the transcribe audio function
                        text = transcribe_audio(audio_chunk)
                    
                    # execution time info
                    logger.info("Transcription result: %r", text)
        
                    if text:
                        if text == "sleep":
                            state.is_sleeping = True
                            speech("One is sleeping.")
    
                        elif text == "wake":
                            state.is_sleeping = False
                            speech("One is awake.")
    
                        elif not state.is_sleeping:
                            
                            with measure("Classifier"):
                                
                                #The tf-idf classifier
                                classifier = Classifier()
                                intent_object = classifier.get_intent(text)
                                intent = intent_object.intent
                            

                            with measure("Scanner"):
                                scanner = Scanner(text)
                                scanner.scan()

                            with measure("Parser"):
                                parser = Parser(scanner.tokens, intent)
                                ast_root = parser.parse_command()
                            
                            if ast_root:
                                with measure("AST"):
                                    ast_checker(ast_root)

                except Exception:
                    logger.exception("Error during audio processing pipeline")
                    speech("An error occurred while processing the audio.")
                    
                finally:
                    while not state.q.empty():
                        try:
                            state.q.get_nowait()  # pick an item from the queue and discard it
                        except queue.Empty:
                            break
                    state.is_processing = False
    
    except KeyboardInterrupt:
        speech("Program finished.")
    except Exception:
        logger.exception("Audio listener stopped unexpectedly")

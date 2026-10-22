"""
This is the core part of the code: speech is captured, 
and the resulting bytes are stored in a list (q). 
The data then passes through a transcription function that converts it into text (in English). 
Once converted, the text is processed by a Lexer/Parser/AST structure;
within the AST, it undergoes a conditional check to determine whether it constitutes a valid command.
"""

import logging
import sounddevice as sd
from src.commands.actions import *
import numpy as np
import webrtcvad
from src.lexer.scanner import *
from src.parser.parser import *
from src.ast.checker import ast_checker
from src.audio.speech import speech, transcribe_audio
import src.state as state
from src.classifier.model import *

vad = webrtcvad.Vad(2) #set aggressiveness mode

SAMPLERATE = 16000
FRAMEDURATION = 30 #ms
FRAME_SIZE = int(SAMPLERATE * FRAMEDURATION/ 1000)
         
                        #By default, the event is false
def start_listerning(event_status: threading.Event):
    
    speech("Welcome to One. How can I help you?")
    is_sleeping = False
    buffer = []
    is_recording = False
    offtime = 0
    
    #the callback function, called by the inputStream
    def callback(indata, frames, time, status):
        nonlocal is_recording, offtime
       
        if status:
            print(status)

        #if the event is false, clear the buffer and return
        if not event_status.is_set() or state.is_processing:
            if len(buffer) > 0:
                buffer.clear()
                is_recording = False
                offtime = 0
            return
        
        clear_indata = indata[:, 0]
        clear_bytes = (clear_indata * 32768).astype(np.int16).tobytes()
    
        if vad.is_speech(clear_bytes,SAMPLERATE):
            is_recording = True
            offtime = 0
            buffer.append(clear_indata.copy())
            
        else:
            if is_recording:
                buffer.append(clear_indata.copy())
                offtime += 1
                
                if offtime > 15:
                  if len(buffer) > 30: 
                    final_audio = np.concatenate(buffer)
                    state.q.put(final_audio)
                        
                  buffer.clear()
                  is_recording = False
                  offtime = 0

    
    with sd.InputStream(samplerate= SAMPLERATE, channels= 1, dtype = "float32", callback= callback, blocksize= FRAME_SIZE):

        try:
            while True:
                event_status.wait() #Blocks thread execution until event() is true

                try:
                    audio_chunk = state.q.get(timeout = 0.5)
                except queue.Empty:
                    continue


                state.is_processing = True
                
                try:
                    text = transcribe_audio(audio_chunk)
        
                    if text:
                        if text == "sleep":
                            is_sleeping = True
                            speech("One is sleeping.")
    
                        elif text == "wake":
                            is_sleeping = False
                            speech("One is awake.")
    
                        elif not is_sleeping:
                            classifier = Classifier()
                            intent_object = classifier.get_intent(text)
                            intent = intent_object.intent
                            
                            scanner = Scanner(text)
                            scanner.scan()
        
                            parser = Parser(scanner.tokens, intent)
                            ast_root = parser.parse_command()
        
                            if ast_root:
                                ast_checker(ast_root)
                except Exception: # noqa: S110
                    logging.getLogger(__name__).exception("Error during audio processing pipeline")
                finally:
                    while not state.q.empty():
                        try:
                            state.q.get_nowait()  # pick an item from the queue and discard it
                        except queue.Empty:
                            break
                    state.is_processing = False
    
        except KeyboardInterrupt:
            speech("Program finished.")

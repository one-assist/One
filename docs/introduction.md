# User Guide & Interaction Introduction: Welcome to ONE

This guide serves as your deep-dive companion into how you converse with, command, and navigate **ONE**. If you're looking for installation instructions, check the repository's main [README](../README.md) . 

---

## The Anatomy of a Conversation with ONE

ONE bridges your voice with system actions through a structured, multi-stage pipeline designed to parse natural voice commands into precise execution trees:

1. **Acoustic Capture & VAD (Voice Activity Detection):** 
   When you speak, ONE listens continuously via an audio stream. The Voice Activity Detection engine (`webrtcvad`) filters out silence and isolates your spoken sentences into audio chunks.
2. **Speech-to-Text Transcription:** 
   Your audio chunk is processed by **Faster-Whisper**, converting acoustic waveforms into clean text strings.
3. **Lexical Analysis (Lexer):** 
   The text is corrected by `SymSpell`, replacing any incorrectly interpreted words with the closest match. Afterward, it is tokenized into `AND` Type or `IDENTIFIER`. [Scanner](../src/lexer/scanner.py).
4. **Syntactic Parsing (Parser & AST):** 
   The token stream is transformed into an `Abstract Syntax Tree (AST)`. This allows ONE to understand complex or multi-part instructions (such as sequential commands connected by operators like `and`).
5. **Intent Classification & Execution:** 
   The system validates the syntax rules, matches intents, and executes the requested system or application action.

If an unexpected failure occurs during transcription or command processing, ONE records the technical details in its logs, gives a short spoken error response, clears stale audio, and returns to an available listening state. External services such as Gemini also return a safe fallback response when their request cannot be completed.

---

## Exploring Command Possibilities

ONE supports a wide range of commands, from launching applications and playing music to controlling volume and managing tasks. The variety of commands will constantly expand.

To explore the exact training phrases, intent classes, and underlying categories recognized by the system, inspect the complete dataset structure directly in the [Dataset Configuration](../src/classifier/dataset/dataset.json) file.

### How to Phrase Your Commands
* **Direct Actions:** Single-intent commands such as `"open"`, `"search"`, `"play"`, or `"stop"`.
* **Compound / Chained Commands:** You can string multiple actions together using the `and` operator. For instance:
  > *"open firefox and open kitty"*
* **State Control Commands:** You can pause listening or put the assistant to sleep by saying `"sleep"`, and resume by saying `"wake"`.

---

## Best Practices & What to Avoid

ONE is a project under constant development that may exhibit errors or bugs; to ensure it interprets your voice accurately and operates smoothly, without delays or glitches, please consider the following operational guidelines:

* **Avoid Heavy Background Noise:** 
  Loud ambient sounds (music playing in the background, TV, fans, or overlapping conversations) can deceive the `VAD` or cause `Faster-Whisper` to hallucinate extraneous words.
* **Avoid Clipping Your First Syllable:** 
  Do not start speaking the exact millisecond you trigger the listener. Give a natural, steady lead-in to prevent the `VAD` from cutting off the initial consonant or syllable of your command verb (e.g., cutting the "o" in "open").
* **Avoid Conversational Filler:** 
  ONE is optimized for concise command structures rather than open-ended LLM chat. Avoid conversational filler like *"Um, could you please maybe open..."* and instead use direct phrasing like `"open app"`.
* **Avoid Rapid UI Toggling:** 
  If you are interacting with the visual interface (the Slint Voice Orb), avoid rapidly clicking back and forth before speech processing finishes, as this can desynchronize the audio processing queue.

## Command compatibility

The project does not yet offer broad support for various Linux distributions, Windows, or macOS. Consequently, you may encounter compatibility or program-related errors (such as issues with different music players). Until cross-platform support is implemented, the recommended approach is to identify the correct command for your specific system or program and insert it into the One's code. All commands are located in [actions.py](../src/commands/actions.py); simply modify the `subprocess.Popen()` call.

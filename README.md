# One

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
![Status](https://img.shields.io/badge/status-active-success)

One is a Python-based voice assistant designed to interpret spoken commands and execute actions on the system. It combines real-time audio processing, speech transcription, intent classification, and a command parser to support practical assistant routines such as opening applications, searching the web, controlling media playback, and managing tasks.

## Documentation Map

- [CODE_OF_CONDUCT](CODE_OF_CONDUCT.md)
- [CONTRIBUTING](CONTRIBUTING.md)
- [docs/introduction](docs/introduction.md)

## Overview

One is built to work as a local voice assistant for desktop environments. The system listens for speech, identifies when a user has stopped speaking, transcribes the audio into text, and classifies the user intent before executing the corresponding command.

This architecture is intended to be extensible: new commands can be added by expanding the action handlers and command classification logic.

## Architecture

The application follows a producer-consumer design:

1. Audio capture and VAD
   - Audio is captured continuously in a background thread.
   - Voice Activity Detection (VAD) is used to determine when speech is occurring.
   - The system processes short audio frames and detects when a phrase is complete.

2. Safe audio buffering
   - Captured audio is sent to a queue for thread-safe transfer.
   - This prevents the listener thread from blocking the main processing loop.

3. Speech transcription
   - The queued audio is converted into text using Faster Whisper.
   - Transcription is configured for English and optimized for CPU execution.

4. Intent classification
   - The transcribed text is passed to a classifier trained with scikit-learn.
   - The classifier assigns the user request to a known command category such as open app, search, play music, or task management.

5. Parsing and validation
   - The command is tokenized by a lexer.
   - A parser creates an AST-like structure representing the requested operation.
   - The structure is validated before execution.

6. Action execution
   - Valid commands are routed to the Action layer, which performs system operations such as opening apps, launching searches, or controlling media playback.

## Features

One currently supports a set of practical voice-driven actions:

- Open and close applications
- Search the web using the browser
- Ask Gemini a question using the Google GenAI API
- Play specific songs through Spotify integration
- Control media playback: next, pause, resume, stop
- Increase or decrease system volume
- View and create tasks
- View command history
- Enable sleep and wake modes
- Trigger system update commands on Arch-based Linux systems

## Project Structure

```text
One/
├── docs/
├── database/
├── frontend/
├── src/
│   ├── ast/
│   ├── audio/
│   ├── classifier/
|       └── dataset/
│   ├── commands/
│   ├── lexer/
│   ├── parser/
├── tests/
├── .github/
|     └── workflows/
```

## Dependencies

The project depends on several Python libraries and system tools:

    Python 3.8+
    sounddevice
    webrtcvad
    numpy
    gTTS
    faster-whisper
    spotipy
    scikit-learn
    slint
    symspellpy
    dotenv

## Installation
### Prerequisites

Before starting, make sure you have:

  - Python 3.8 or newer installed
  - A working microphone
  - A compatible audio backend on the operating system

### 1- Clone the project

  ```bash
 git clone https://github.com/one-assist/One.git
 cd One
  ```

### 2- Create a virtual environment

  ```bash
  python -m venv venv
  ```
 #### Activate it:

   - On Linux/macOS:
     
   ```bash
   source venv/bin/activate
   ```
   - On Windows:
   
   ```bash
   venv\Scripts\activate
   ```
### 3- Install dependencies

   ```bash
   pip install -r requirements.txt
   ```
### 4- Configure environment variables
    
   ```bash
   cp .env.example .env
   ```
 #### Then edit .env and add your credentials:
 
   ```bash
    SPOTIPY_CLIENT_ID="your_client_id"
    SPOTIPY_CLIENT_SECRET="your_client_secret"
    SPOTIPY_REDIRECT_URI="http://localhost:8888/callback"
    GEMINI_API_KEY="your_api_key"
   ```
### 5- Run the application

  ```bash
   python -m src.main
  ```

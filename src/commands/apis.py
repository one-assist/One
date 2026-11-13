
"""
This module contains the APIs for interacting with the Gemini and Spotify APIs.
"""

import os 
import spotipy
import time
import logging

from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyOAuth
from src.commands.errors.err_apis import *

_ = load_dotenv()
logger = logging.getLogger(__name__)

def ask_gemini(text: str, retries=3):
    api_key = os.getenv("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    for attempt in range(retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=text,
            )
            return response.text
            
        except APIError as error:
            if error.code == 503 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue

            logger.exception("Gemini API request failed")
            return "Gemini server error"

        except Exception:
            error = GeminiError()
            logger.exception("[%s] %s", error.code, error.user_message)
            return "Gemini server error"
            
sp = spotipy.Spotify(auth_manager= SpotifyOAuth(
    client_id= os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret= os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri= os.getenv("SPOTIPY_REDIRECT_URI"),
    scope= "user-modify-playback-state user-read-playback-state"
))


"""
This module contains the APIs for interacting with the Gemini and Spotify APIs.
"""

import time
from google import genai
from google.genai.errors import APIError
from dotenv import load_dotenv
import os 
import spotipy
from spotipy.oauth2 import SpotifyOAuth

load_dotenv()


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
        except APIError as e:
            if e.code == 503 and attempt < retries - 1:
                time.sleep(2 ** attempt)
                continue
                
            print(f"Gemini API error: {e}")
            return "Gemini server error"

        except Exception as e:
            print(f"Unexpected error:{e}")
            return "Gemini server error"
            
sp = spotipy.Spotify(auth_manager= SpotifyOAuth(
    client_id= os.getenv("SPOTIPY_CLIENT_ID"),
    client_secret= os.getenv("SPOTIPY_CLIENT_SECRET"),
    redirect_uri= os.getenv("SPOTIPY_REDIRECT_URI"),
    scope= "user-modify-playback-state user-read-playback-state"
))

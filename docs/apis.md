# External APIs Integration Module

This module manages external third-party service integrations for the "One" project, specifically handling generative AI capabilities via Google Gemini and media playback control via Spotify, as implemented in [apis.py](../src/commands/apis.py).

## Requirements and Environment Configuration

To successfully utilize this module, several environment variables must be securely configured within a `.env` file at the root of the project. These keys authenticate the application against Google's generative services and Spotify's developer platform (do not share or expose the values of these keys to anyone):

* **Google Gemini Requirements**: Requires a valid `GEMINI_API_KEY` to instantiate the Google GenAI client.
* **Spotify OAuth Requirements**: Requires `SPOTIPY_CLIENT_ID`, `SPOTIPY_CLIENT_SECRET`, and `SPOTIPY_REDIRECT_URI`. Furthermore, the Spotify integration requests specific OAuth scopes (`user-modify-playback-state` and `user-read-playback-state`) to allow the assistant to control playback state and query what is currently playing on the user's account (Requires Spotify Premium).

## Google Gemini Integration

The Gemini integration is designed around the `ask_gemini` function, which accepts a text prompt and returns the generated response string from Google's models. It interacts with the `gemini-3.6-flash` model using the official `google-genai` client library.

To handle transient cloud errors or service overload, the function retries only an `APIError` with status code `503` (Service Unavailable). It waits with exponential backoff (`2 ** attempt` seconds) and makes at most three attempts. Other API errors, a final 503 failure, and unexpected exceptions are logged with traceback details. In those cases, the function returns the fallback string `"Gemini server error"` instead of propagating the failure into the command flow.

## Spotify Integration

The Spotify integration leverages the `spotipy` library coupled with `SpotifyOAuth` authentication manager. Upon module initialization, it authenticates using the credentials provided in the environment variables and establishes an active session object (`sp`). 

The initialized `sp` client exposes full programmatic control over the user's Spotify player, utilizing the pre-configured permission scopes to execute playback commands (such as playing, pausing, or changing tracks) and reading current playback metrics directly through the user's authorized Spotify account.
import json
import os
import spotipy

from dotenv import load_dotenv
from fastapi import HTTPException, Response, Request, status
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "")
SCOPE = "playlist-modify-public"


class CookieCache(CacheHandler):
    def __init__(self, cookie_name="spotify_auth"):
        self.cookie_name = cookie_name
        self._cached_token = None  # Internal storage for Spotipy compatibility

    def get_cached_token(self):
        """Spotipy-compatible method to get cached token"""
        return self._cached_token

    def load_from_request(self, request):
        """Custom method to load token from request cookies"""
        cookie = request.cookies.get(self.cookie_name)
        if cookie:
            self._cached_token = json.loads(cookie)
        return self._cached_token

    def save_token_to_cache(self, token_info, response=None):
        """Save token to both cache and response cookies"""
        self._cached_token = token_info  # Store token internally
        if response:
            response.set_cookie(
                key=self.cookie_name,
                value=json.dumps(token_info),
                httponly=True,
                max_age=3600,
                secure=os.getenv("SECURE_COOKIE", "False") == "True",
                samesite="lax",
            )


# Create the auth manager with our cached instance
def get_auth_manager(request: Request):
    cache_handler = CookieCache()
    token_info = cache_handler.load_from_request(request)  # Load from request cookies

    auth_manager = SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_handler=cache_handler,
        show_dialog=True,
    )

    if token_info:
        auth_manager.cached_token = token_info

    return auth_manager


def get_spotify_client(request: Request, response: Response):
    auth_manager = get_auth_manager(request)

    token_info = auth_manager.cache_handler.get_cached_token()

    if not auth_manager.validate_token(token_info):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated with Spotify",
        )

    return spotipy.Spotify(auth_manager=auth_manager)

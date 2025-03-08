import os
from itsdangerous import URLSafeTimedSerializer
import spotipy

from dotenv import load_dotenv
from fastapi import HTTPException, Response, Request, status
from functools import lru_cache
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheHandler

load_dotenv()

SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = os.getenv("SPOTIFY_REDIRECT_URI", "")
SCOPE = "playlist-modify-public"
SECRET_KEY = os.getenv("SECRET_KEY", "")


class CookieCache(CacheHandler):
    def __init__(self, cookie_name="spotify_auth"):
        self.cookie_name = cookie_name
        self._cached_token = None
        self.serializer = URLSafeTimedSerializer(SECRET_KEY)

    def get_cached_token(self):
        """Spotipy-compatible method to get cached token"""
        return self._cached_token

    def load_from_request(self, request: Request):
        """Load token from encrypted request cookies"""
        cookie = request.cookies.get(self.cookie_name)
        if cookie:
            try:
                decrypted_data = self.serializer.loads(
                    cookie, max_age=3600
                )  # Tokens expire in 1 hour
                self._cached_token = decrypted_data
            except Exception:
                self._cached_token = None  # Handle tampered or expired cookies
        return self._cached_token

    def save_token_to_cache(self, token_info, response: Response = None):
        """Save token to encrypted response cookies"""
        self._cached_token = token_info  # Store internally for Spotipy
        if response:
            encrypted_data = self.serializer.dumps(token_info)
            response.set_cookie(
                key=self.cookie_name,
                value=encrypted_data,
                httponly=True,
                max_age=3600,  # 1 hour
                secure=os.getenv("SECURE_COOKIE", "False") == "True",
                samesite="lax",
            )


@lru_cache(maxsize=1)
def get_auth_manager():
    """Returns a cached SpotifyOAuth instance"""
    return SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope=SCOPE,
        cache_handler=CookieCache(),
        show_dialog=True,
    )


def get_spotify_client(request: Request, response: Response):
    """Returns an authenticated Spotify client or refreshes the token if expired."""
    auth_manager = get_auth_manager()
    cache_handler = auth_manager.cache_handler

    token_info = cache_handler.load_from_request(request)
    if not token_info or not auth_manager.validate_token(token_info):
        try:
            token_info = auth_manager.refresh_access_token(token_info["refresh_token"])
            cache_handler.save_token_to_cache(token_info, response)
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated with Spotify",
            )

    return spotipy.Spotify(auth_manager=auth_manager)

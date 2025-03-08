import os
import requests
import spotipy

from dotenv import load_dotenv
from fastapi import FastAPI, Request, Response, Depends
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import Optional
from ytmusicapi.enums import ResponseStatus
from ytmusicapi import YTMusic, OAuthCredentials

from utils import get_auth_manager, get_spotify_client, CookieCache


load_dotenv()
app = FastAPI()

BASE_URL = "https://api.setlist.fm/rest/"
SETLIST_API_KEY = os.getenv("SETLIST_API_KEY", "")
ENVIRONMENT = os.getenv("ENVIRONMENT", "development")
STREAMLIT_URL = os.getenv("STREAMLIT_URL", "")

allowed_origins = os.getenv("ALLOWED_ORIGINS", "")
origins = [origin.strip() for origin in allowed_origins.split(",") if origin.strip()]

if not origins and os.getenv("ENVIRONMENT") == "development":
    origins = ["http://localhost:8501", "http://127.0.0.1:8501"]

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

secret_key = os.getenv("SECRET_KEY")
if not secret_key and os.getenv("ENVIRONMENT") == "production":
    raise ValueError("SECRET_KEY environment variable not set")

app.add_middleware(SessionMiddleware, secret_key=os.getenv("SECRET_KEY"))


@app.get("/search/{name}")
def search_setlists(name):
    """
    Receives an artist name
    Returns the 3 last full setlists and the compilated list of songs of those setlists
    """
    path = f"1.0/search/setlists?artistName={name}"
    url = BASE_URL + path
    headers = {"x-api-key": SETLIST_API_KEY, "accept": "application/json"}

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        setlists = data.get("setlist", [])
        unique_songs = []
        recent_setlists = []
        valid_setlists = []

        for setlist in setlists:
            sets = setlist.get("sets", {}).get("set", [])
            if sets:  # Ensure the setlist has actual songs
                valid_setlists.append(setlist)
            if len(valid_setlists) == 3:
                break

        for setlist in valid_setlists:
            songs = [
                song["name"]
                for s in setlist.get("sets", {}).get("set", [])
                for song in s.get("song", [])
            ]
            for song in songs:
                if song not in unique_songs:
                    unique_songs.append(song)
            recent_setlists.append(
                {
                    "artist": setlist.get("artist", {}).get("name"),
                    "eventDate": setlist.get("eventDate"),
                    "venue": setlist.get("venue", {}).get("name"),
                    "songs": songs,
                }
            )

        return {"recent_setlists": recent_setlists, "unique_songs": list(unique_songs)}
    else:
        return {"error": "Failed to fetch data", "status_code": response.status_code}


@app.get("/get-setlist/{id}")
def fetch_setlist(id):
    path = f"1.0/setlist/{id}"
    url = BASE_URL + path
    headers = {"x-api-key": SETLIST_API_KEY, "accept": "application/json"}

    # Use the requests library to perform a synchronous HTTP GET request
    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response directly if successful
        data = response.json()
        sets = data.get("sets", {}).get("set", [])
        if sets:
            songs_list = [song["name"] for song in sets[0].get("song", [])]
            return songs_list

    return {"error": "No setlist found", "status_code": response.status_code}


# Route to initiate login
@app.get("/login")
async def login(
    request: Request, redirect_to_streamlit: bool = False, artist: str = None
):
    auth_manager = get_auth_manager()
    auth_url = auth_manager.get_authorize_url()

    if redirect_to_streamlit:
        request.session["pending_artist"] = artist

    return RedirectResponse(url=auth_url)


@app.get("/logout")
def logout(response: Response):
    """
    Clears Spotify authentication cookies.
    """
    response.delete_cookie("spotify_auth")
    return {"message": "Logged out successfully!"}


@app.get("/callback")
async def callback(request: Request, response: Response, code: Optional[str] = None):
    """
    Handles Spotify's OAuth callback and stores the token in cookies.
    If coming from Streamlit, redirect back to Streamlit with `auth_success=true`.
    """
    if code is None:
        return {"error": "No code provided"}

    auth_manager = get_auth_manager()
    token_info = auth_manager.get_access_token(code=code, check_cache=False)

    if not token_info:
        return {"error": "Failed to retrieve access token from Spotify."}

    # Save token to cookie
    cache_handler = CookieCache()
    cache_handler.save_token_to_cache(token_info, response)

    # Handle Streamlit redirection
    artist = request.session.get("pending_artist")
    if artist:
        return RedirectResponse(
            url=f"{STREAMLIT_URL}?auth_success=true&artist={artist}"
        )

    return RedirectResponse(url=f"{STREAMLIT_URL}?auth_success=true")


@app.get("/success")
async def success():
    return {"message": "Successfully authenticated with Spotify!"}


@app.post("/create-playlist/{artist}/")
def create_spotify_playlist(
    artist: str, sp: spotipy.Spotify = Depends(get_spotify_client)
):
    """
    Receives an artist name
    Returns the playlist url of the setlist
    """
    user_id = sp.me()["id"]
    setlist = search_setlists(artist)
    if not setlist and not setlist.get("unique_songs"):
        return f"No setlist found for {artist}"

    artist_name = setlist["recent_setlists"][0]["artist"]
    songs = setlist.get("unique_songs")
    playlist_name = f"{artist_name} - Setlist"
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    playlist_id = playlist["id"]

    track_uris = []
    for song in songs:
        query = f"track:{song} artist:{artist}"
        result = sp.search(q=query, type="track", limit=1)
        tracks = result.get("tracks", {}).get("items", [])
        if tracks:
            track_uris.append(tracks[0]["uri"])

    if track_uris:
        sp.playlist_add_items(playlist_id, track_uris)
        return {
            "message": "Playlist created successfully!",
            "playlist_url": f"https://open.spotify.com/playlist/{playlist_id}",
        }
    else:
        return {"error": "No matching songs found on Spotify."}


@app.post("/create-youtube-playlist/{artist}")
def create_youtube_playlist(artist: str):
    """
    Receives an artist name
    Returns the playlist url of the setlist
    """
    if ENVIRONMENT != "development":
        return {"error": "Only available for development environment"}

    YT_CLIENT_ID = os.getenv("YT_CLIENT_ID", "")
    YT_CLIENT_SECRET = os.getenv("YT_CLIENT_SECRET", "")
    yt = YTMusic(
        "oauth.json",
        oauth_credentials=OAuthCredentials(
            client_id=YT_CLIENT_ID, client_secret=YT_CLIENT_SECRET
        ),
    )
    setlist = search_setlists(artist)
    if not setlist and not setlist.get("unique_songs"):
        return f"No setlist found for {artist}"

    artist = setlist["recent_setlists"][0]["artist"]
    songs = setlist["unique_songs"]

    playlist_name = f"{artist} - Setlist"
    playlist_id = yt.create_playlist(playlist_name, "Generated from Setlist Maker")

    video_ids = []
    for song in songs:
        search_results = yt.search(f"{song} {artist}", filter="songs", limit=1)
        if search_results:
            video_id = search_results[0]["videoId"]
            if video_id not in video_ids:  # Avoid duplicates
                video_ids.append(video_id)

    if video_ids:
        response = yt.add_playlist_items(playlist_id, video_ids)
        if response["status"] == ResponseStatus.SUCCEEDED:
            return {
                "message": "YouTube Music playlist created successfully!",
                "playlist_url": f"https://music.youtube.com/playlist?list={playlist_id}",
            }
        error_message = (
            response.get("error", {})
            .get("actions", [{}])[0]
            .get("confirmDialogEndpoint", {})
            .get("content", {})
            .get("confirmDialogRenderer", {})
            .get("dialogMessages", [{}])[0]
            .get("runs", [{}])[0]
            .get("text", "Unknown error")
        )
        return {"error": error_message}
    return {"error": "No matching songs found on YouTube Music."}

import os
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth

from fastapi import FastAPI

load_dotenv()
app = FastAPI()

BASE_URL = "https://api.setlist.fm/rest/"
SETLIST_API_KEY = os.getenv("SETLIST_API_KEY", "")
SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
SPOTIPY_CLIENT_ID = os.getenv("SPOTIPY_CLIENT_ID", "")
SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
SPOTIPY_CLIENT_SECRET = os.getenv("SPOTIPY_CLIENT_SECRET", "")
SPOTIFY_REDIRECT_URI = "http://localhost:8888/callback"

# Spotify authentication
sp = spotipy.Spotify(
    auth_manager=SpotifyOAuth(
        client_id=SPOTIFY_CLIENT_ID,
        client_secret=SPOTIFY_CLIENT_SECRET,
        redirect_uri=SPOTIFY_REDIRECT_URI,
        scope="playlist-modify-public",
    )
)


@app.get("/search/{name}")
def search_setlist(name):
    path = f"1.0/search/setlists?artistName={name}"
    url = BASE_URL + path
    headers = {"x-api-key": SETLIST_API_KEY, "accept": "application/json"}

    response = requests.get(url, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        # Return the JSON response directly if successful
        return response.json()
    else:
        # If the request failed, return an error response
        print(response.text)
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
            print(len(songs_list))
            return songs_list

    return {"error": "No setlist found", "status_code": response.status_code}


@app.post("/create-playlist/{artist}/")
def creatcrmee_spotify_playlist(artist: str, setlist_id: str):
    user_id = sp.me()["id"]
    setlist = search_setlist(artist)
    setlist_id = ""
    if setlist:
        first_setlist = setlist.get("setlist", {})[0]
        setlist_id = first_setlist.get("id", "") if first_setlist else ""
    songs = fetch_setlist(setlist_id)
    if "error" in songs:
        return songs

    playlist_name = f"{artist} - Live Setlist"
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

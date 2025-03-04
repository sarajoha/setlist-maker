import os
import requests
from dotenv import load_dotenv
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from ytmusicapi import YTMusic, OAuthCredentials
from ytmusicapi.enums import ResponseStatus

from fastapi import FastAPI

load_dotenv()
app = FastAPI()

BASE_URL = "https://api.setlist.fm/rest/"
SETLIST_API_KEY = os.getenv("SETLIST_API_KEY", "")


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
def create_spotify_playlist(artist: str):
    """
    Receives an artist name
    Returns the playlist url of the setlist
    """
    SPOTIFY_CLIENT_ID = os.getenv("SPOTIFY_CLIENT_ID", "")
    SPOTIFY_CLIENT_SECRET = os.getenv("SPOTIFY_CLIENT_SECRET", "")
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

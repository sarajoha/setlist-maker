# Setlist Maker App

Setlist Maker is an app that creates Spotify playlists based on the most recent concerts of an artist. It fetches setlists from [Setlist.fm](https://api.setlist.fm/) and automatically creates playlists.

## How to Run

### 1. Create and Activate Virtual Environment

```sh
python -m venv myvenv
source myvenv/bin/activate  # On macOS/Linux
myvenv\Scripts\activate  # On Windows
```

### 2. Install Dependencies

```sh
pip install -r requirements.txt
```

### 3. Set Up API Credentials

Ensure you have the necessary credentials:

- **Setlist.fm API Key**: Register at [Setlist.fm](https://api.setlist.fm/docs/1.0/index.html) and get your API key.
- **Spotify API Credentials**:
  1. Create an application in the [Spotify Developer Dashboard](https://developer.spotify.com/dashboard/).
  2. Obtain the Client ID, Client Secret, and Redirect URI.
  3. Set them as environment variables:

```sh
export SETLIST_API_KEY="your-setlist-api-key"
export SPOTIFY_CLIENT_ID="your-spotify-client-id"
export SPOTIFY_CLIENT_SECRET="your-spotify-client-secret"
export SPOTIFY_REDIRECT_URI="your-redirect-uri"
```

### 4. Run the Application

```sh
fastapi dev main.py
```

This starts the FastAPI server.

### 5. Access API Documentation

Once the server is running, you can access interactive API documentation at:
[http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

## TODO

- [x] Create account and API key in [Setlist FM](https://api.setlist.fm/docs/1.0/index.html)
- [x] Create virtual environment
- [x] Create FastAPI project/endpoint to connect to Setlist.fm and search for setlists by band and year
- [x] Connect to Spotify with credentials
- [x] Create playlist in Spotify based on a setlist
- [x] Create playlist in Spotify based on the last 3 or 5 setlists, including rare songs
- [ ] Create playlist in YouTube Music based on setlist
- [ ] Make a simple UI in Streamlit
- [ ] Map tours and concerts by band
- [ ] Create a setlist for a specific concert
- [ ] Create a setlist from a date range or tour of a band

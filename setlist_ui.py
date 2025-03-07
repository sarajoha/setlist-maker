import os
import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()

# Define backend API URLs
BACKEND_URL = os.getenv("BACKEND_URL")
SPOTIFY_AUTH_URL = f"{BACKEND_URL}/login"

st.title("Setlist Maker 🎶")

# Disable WebSocket compression
st.config.set_option("server.enableWebsocketCompression", False)
st.config.set_option("server.enableCORS", False)  # Disable CORS issues
st.config.set_option("server.enableXsrfProtection", False)  # Disable XSRF protection
st.config.set_option("server.headless", True)

# Initialize session state variables if they don't exist
if "auth_completed" not in st.session_state:
    st.session_state.auth_completed = False
if "artist" not in st.session_state:
    st.session_state.artist = ""


# Function to store artist in session state
def set_artist(name):
    st.session_state.artist = name


# Check for callback parameters in URL (when returning from Spotify auth)
query_params = st.experimental_get_query_params()
if "auth_success" in query_params and query_params["auth_success"][0] == "true":
    st.session_state.auth_completed = True
    st.success("Successfully authenticated with Spotify!")

    # If we had an artist stored and auth is complete, can offer to create playlist
    if st.session_state.artist:
        st.write(f"Ready to create playlist for {st.session_state.artist}")

# Search for setlists
artist = st.text_input(
    "Enter Artist Name:",
    key="artist_input",
    on_change=lambda: set_artist(st.session_state.artist_input),
)

if st.button("Search Setlists"):
    response = requests.get(f"{BACKEND_URL}/search/{artist}")
    if response.status_code == 200:
        data = response.json()
        if "error" in data:
            st.error(data["error"])
        else:
            st.write("### Last 3 concerts:")
            for setlist in data["recent_setlists"]:
                st.write(f"📅 {setlist['eventDate']} - 📍 {setlist['venue']}")
                st.write("---")
            st.write("### Consolidated Setlist from 3 last concerts:")
            st.write("🎵 Songs:")
            st.write("\n".join(f"- {song}" for song in data["unique_songs"]))
            st.write("---")

            # Store the artist in session state
            st.session_state.artist = artist
    else:
        st.error("Failed to fetch setlists.")

# Create Spotify Playlist - with auth flow
if st.button("Create Spotify Playlist"):
    if not st.session_state.auth_completed:
        # First need to authenticate - open login window and store current artist
        st.session_state.artist = artist
        spotify_auth_url = (
            f"{SPOTIFY_AUTH_URL}?redirect_to_streamlit=true&artist={artist}"
        )
        st.markdown(f"[Click here to authenticate with Spotify]({spotify_auth_url})")
        st.info(
            "You'll be redirected to Spotify for authentication. After authenticating, you'll return to this app."
        )
    else:
        # Already authenticated, can create playlist
        response = requests.post(
            f"{BACKEND_URL}/create-playlist/{st.session_state.artist}/",
            cookies=st.session_state.get("cookies", {}),  # Pass any cookies we have
        )

        if response.status_code == 200:
            data = response.json()
            if "playlist_url" in data:
                st.success(f"Playlist Created! [Open Playlist]({data['playlist_url']})")
            else:
                st.error(data.get("error", "Failed to create playlist."))
        else:
            st.error(f"Error contacting backend: {response.text}")

# Add a logout button when authenticated
if st.session_state.auth_completed:
    if st.button("Logout from Spotify"):
        st.session_state.auth_completed = False
        st.session_state.cookies = {}
        st.experimental_rerun()

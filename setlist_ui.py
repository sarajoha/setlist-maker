import os
import requests
import streamlit as st
import time
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Setlist Maker", page_icon="🎶")

# Define backend API URLs
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")
SPOTIFY_AUTH_URL = f"{BACKEND_URL}/login"
SPOTIFY_LOGOUT_URL = f"{BACKEND_URL}/logout"

st.title("Setlist Maker 🎶")


# Initialize session state variables if they don't exist
if "auth_completed" not in st.session_state:
    st.session_state.auth_completed = False
if "cookies" not in st.session_state:
    st.session_state.cookies = {}
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

# **🔹 Login Button (Appears if user is not authenticated)**
if not st.session_state.auth_completed:
    if st.button("Log in to Spotify 🎧"):
        st.info(
            "You'll be redirected to Spotify for authentication. After authenticating, you'll return to this app."
        )
        spotify_login_url = f"{SPOTIFY_AUTH_URL}?redirect_to_streamlit=true"
        st.markdown(
            f'<meta http-equiv="refresh" content="0; URL={spotify_login_url}">',
            unsafe_allow_html=True,
        )
else:
    if st.button("Logout from Spotify 🚪"):
        requests.get(SPOTIFY_LOGOUT_URL)  # Call backend logout
        st.session_state.auth_completed = False
        st.session_state.cookies = {}
        st.experimental_set_query_params()
        time.sleep(0.5)
        st.experimental_rerun()

# Search for setlists
artist = st.text_input(
    "Enter Artist Name:",
    key="artist_input",
    on_change=lambda: set_artist(st.session_state.artist_input),
)

# **🔹 Create Columns for Side-by-Side Buttons**
col1, col2 = st.columns(2)  # Two equal-width columns

with col1:
    if st.button("Get Setlist"):
        response = requests.get(f"{BACKEND_URL}/search/{artist}")
        if response.status_code == 200:
            data = response.json()
            if "error" in data:
                st.error(data["error"])
            else:
                st.write("### Consolidated Setlist from 3 last concerts:")
                st.write("🎵 Songs:")
                st.write("\n".join(f"- {song}" for song in data["unique_songs"]))
                st.write("---")
                st.write("### Last 3 concerts:")
                for setlist in data["recent_setlists"]:
                    st.write(f"📅 {setlist['eventDate']} - 📍 {setlist['venue']}")

                # Store the artist in session state
                st.session_state.artist = artist
        else:
            st.error("Failed to fetch setlists.")

# **🔹 Playlist Creation Button**
with col2:
    if st.button("Create Spotify Playlist"):
        if not st.session_state.auth_completed:
            st.error(
                "⚠️ You need to log in to Spotify first before creating a playlist."
            )
        else:
            response = requests.post(
                f"{BACKEND_URL}/create-playlist/{artist}/",
                cookies=st.session_state.get("cookies", {}),
            )

            if response.status_code == 200:
                data = response.json()
                if "playlist_url" in data:
                    st.success(
                        f"✅ Playlist Created! [Open Playlist]({data['playlist_url']})"
                    )
                else:
                    st.error(data.get("error", "⚠️ Failed to create playlist."))
            else:
                st.error(f"⚠️ Error contacting backend: {response.text}")

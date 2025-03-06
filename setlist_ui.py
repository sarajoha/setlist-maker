import os
import requests
import streamlit as st

from dotenv import load_dotenv

load_dotenv()

# Define backend API URL
BACKEND_URL = os.getenv("BACKEND_URL")

st.title("Setlist Maker 🎶")

# Search for setlists
artist = st.text_input("Enter Artist Name:")
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
    else:
        st.error("Failed to fetch setlists.")

# Create Spotify Playlist
if st.button("Create Spotify Playlist"):
    response = requests.post(f"{BACKEND_URL}/create-playlist/{artist}/")
    if response.status_code == 200:
        data = response.json()
        if "playlist_url" in data:
            st.success(f"Playlist Created! [Open Playlist]({data['playlist_url']})")
        else:
            st.error("Failed to create playlist.")
    else:
        st.error("Error contacting backend.")

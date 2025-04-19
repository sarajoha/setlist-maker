import React from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function SpotifyAuth({ artist, authCompleted, onCreatePlaylist }) {
  if (!artist) return null;

  if (!authCompleted) {
    const authUrl = `${BACKEND_URL}/login?redirect_to_streamlit=true&artist=${encodeURIComponent(artist)}`;

    return (
      <div className="spotify-auth">
        <p>Please log in to Spotify to continue:</p>
        <a
          href={authUrl}
          className="spotify-login-button"
          target="_blank"
          rel="noopener noreferrer"
        >
          Authenticate with Spotify
        </a>
      </div>
    );
  }

  return (
    <button
      onClick={onCreatePlaylist}
      className="create-playlist-button"
    >
      Create Spotify Playlist
    </button>
  );
}

export default SpotifyAuth;

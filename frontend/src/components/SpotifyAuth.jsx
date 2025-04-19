import React from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function SpotifyAuth({ artist, authCompleted, onCreatePlaylist, isCreating }) {
  if (!artist) return null;

  if (!authCompleted) {
    const authUrl = `${BACKEND_URL}/login?redirect_to_streamlit=true&artist=${encodeURIComponent(artist)}`;

    return (
      <div className="spotify-auth">
        <a
          href={authUrl}
          className="btn"
          target="_blank"
          rel="noopener noreferrer"
        >
          Connect with Spotify 🎧
        </a>
      </div>
    );
  }

  return (
    <button
      onClick={onCreatePlaylist}
      className="btn"
      disabled={isCreating}
    >
      {isCreating ? (
        <span className="loading-text">
          Creating playlist
          <span className="loading-dots">
            <span>.</span><span>.</span><span>.</span>
          </span>
          <span className="loading-notes">
            <span>🎵</span><span>🎶</span><span>🎵</span>
          </span>
        </span>
      ) : (
        'Create Spotify Playlist 🎶'
      )}
    </button>
  );
}

export default SpotifyAuth;

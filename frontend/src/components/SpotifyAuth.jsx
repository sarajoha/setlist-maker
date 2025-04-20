import React, { useEffect } from 'react';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function SpotifyAuth({ artist, authCompleted, onCreatePlaylist, isCreating, onAuthSuccess }) {
  useEffect(() => {
    const handleMessage = (event) => {
      if (event.data.type === 'SPOTIFY_AUTH_SUCCESS') {
        onAuthSuccess();
        if (event.data.artist) {
          // You might want to handle the artist data here
        }
      }
    };

    window.addEventListener('message', handleMessage);
    return () => window.removeEventListener('message', handleMessage);
  }, [onAuthSuccess]);

  if (!artist) return null;

  const handleAuthClick = (e) => {
    e.preventDefault();
    const width = 500;
    const height = 700;
    const left = (window.screen.width / 2) - (width / 2);
    const top = (window.screen.height / 2) - (height / 2);

    const authUrl = `${BACKEND_URL}/login?redirect_to_streamlit=true&artist=${encodeURIComponent(artist)}`;
    window.open(
      authUrl,
      'Spotify Login',
      `width=${width},height=${height},left=${left},top=${top}`
    );
  };

  if (!authCompleted) {
    return (
      <div className="spotify-auth">
        <a
          href="#"
          onClick={handleAuthClick}
          className="btn"
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

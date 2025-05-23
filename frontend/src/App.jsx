import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import SetlistResults from './components/SetlistResults';
import SpotifyAuth from './components/SpotifyAuth';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function App() {
  const [artist, setArtist] = useState('');
  const [setlist, setSetlist] = useState(null);
  const [authCompleted, setAuthCompleted] = useState(false);
  const [playlistUrl, setPlaylistUrl] = useState(null);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('auth_success') === 'true') {
      setAuthCompleted(true);
      const artistParam = params.get('artist');
      if (artistParam) setArtist(artistParam);
    }
  }, []);

  const handleSearch = async (artistName) => {
    try {
      const res = await fetch(`${BACKEND_URL}/search/${artistName}`);
      const data = await res.json();
      setArtist(artistName);
      setSetlist(data);
    } catch (error) {
      console.error('Failed to fetch setlist:', error);
    }
  };

  const handleCreatePlaylist = async () => {
    setIsCreating(true);
    try {
      const res = await fetch(`${BACKEND_URL}/create-playlist/${artist}/`, {
        method: 'POST',
        credentials: 'include',
      });
      const data = await res.json();

      if (data.playlist_url) {
        setPlaylistUrl(data.playlist_url);
      } else if (data.error) {
        console.error('Error:', data.error);
      }
    } catch (error) {
      console.error('Error creating playlist:', error);
    } finally {
      setIsCreating(false);
    }
  };

  const handleAuthSuccess = () => {
    setAuthCompleted(true);
  };

  return (
    <div className="app">
      <h1>Setlist Maker 🎶</h1>

      <div className="main-content">
        <div className="step-container">
          <h2 className="step-title">1. Search for an artist</h2>
          <SearchBar onSearch={handleSearch} />
        </div>

        {setlist && (
          <>
            <div className="step-container">
              <h2 className="step-title">2. Create your playlist</h2>
              <div className="spotify-section">
                <SpotifyAuth
                  artist={artist}
                  authCompleted={authCompleted}
                  onCreatePlaylist={handleCreatePlaylist}
                  isCreating={isCreating}
                  onAuthSuccess={handleAuthSuccess}
                />

                {playlistUrl && (
                  <div className="playlist-success">
                    <p>✨ Your playlist is ready!</p>
                    <a
                      href={playlistUrl}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="playlist-link"
                    >
                      Open in Spotify
                    </a>
                  </div>
                )}
              </div>
            </div>

            <div className="step-container">
              <h2 className="step-title">3. Preview setlist</h2>
              <SetlistResults setlist={setlist} />
            </div>
          </>
        )}
      </div>
    </div>
  );
}

export default App;

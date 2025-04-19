import React, { useState, useEffect } from 'react';
import SearchBar from './components/SearchBar';
import SetlistResults from './components/SetlistResults';
import SpotifyAuth from './components/SpotifyAuth';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL;

function App() {
  const [artist, setArtist] = useState('');
  const [setlist, setSetlist] = useState(null);
  const [authCompleted, setAuthCompleted] = useState(false);

  // Check URL params for auth callback
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
    try {
      const res = await fetch(`${BACKEND_URL}/create-playlist/${artist}/`, {
        method: 'POST',
        credentials: 'include',
      });
      const data = await res.json();
      if (data.playlist_url) {
        window.open(data.playlist_url, '_blank');
      }
    } catch (error) {
      console.error('Error creating playlist:', error);
    }
  };

  return (
    <div className="app">
      <h1>Setlist Maker 🎶</h1>

      <SearchBar onSearch={handleSearch} />

      {setlist && <SetlistResults setlist={setlist} />}

      <SpotifyAuth
        artist={artist}
        authCompleted={authCompleted}
        onCreatePlaylist={handleCreatePlaylist}
      />
    </div>
  );
}

export default App;

import React from 'react';

function SetlistResults({ setlist }) {
  if (!setlist || !setlist.unique_songs) return null;

  return (
    <div className="setlist-results">
      <h2>Recent Setlist for {setlist.recent_setlists[0].artist}</h2>
      <ul className="songs-list">
        {setlist.unique_songs.map((song, index) => (
          <li key={index}>{song}</li>
        ))}
      </ul>
    </div>
  );
}

export default SetlistResults;

import React from 'react';

function SetlistResults({ setlist }) {
  if (!setlist || !setlist.unique_songs) return null;

  return (
    <div className="setlist-results">
      <h2>Consolidated Setlist from 3 last concerts</h2>
      <h3>Songs:</h3>
      <ul className="setlist-tracks">
        {setlist.unique_songs.map((song, index) => (
          <li key={index} className="setlist-track">
            {song}
          </li>
        ))}
      </ul>

      <h3>Last 3 concerts:</h3>
      {setlist.recent_setlists.map((concert, index) => (
        <div key={index} className="concert-info">
          <p>📅 {concert.eventDate} - 📍 {concert.venue}</p>
        </div>
      ))}
    </div>
  );
}

export default SetlistResults;

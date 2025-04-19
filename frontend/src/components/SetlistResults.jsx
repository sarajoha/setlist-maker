import React from 'react';

function SetlistResults({ setlist }) {
  return (
    <div>
      <h3>Setlist:</h3>
      <ul>
        {setlist.unique_songs.map((song, i) => (
          <li key={i}>🎵 {song}</li>
        ))}
      </ul>
      <hr />
      <p>* consolidated list made from the last 3 concerts</p>
      {setlist.recent_setlists.map((concert, idx) => (
        <div key={idx}>
          <p>📅 {concert.eventDate} - 📍 {concert.venue}</p>
        </div>
      ))}
    </div>
  );
}

export default SetlistResults;

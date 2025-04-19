import React, { useState } from 'react';

function SearchBar({ onSearch }) {
  const [input, setInput] = useState('');

  const handleSubmit = (e) => {
    e.preventDefault();
    if (input) onSearch(input);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        placeholder="Enter artist name"
        value={input}
        onChange={(e) => setInput(e.target.value)}
      />
      <button type="submit">Search Setlists</button>
    </form>
  );
}

export default SearchBar;

import React, { useState } from 'react';

export default function HighlightedSection({ children, suggestion }) {
  const [showSuggestion, setShowSuggestion] = useState(false);

  return (
    <span style={{ position: 'relative', cursor: 'pointer' }} onClick={() => setShowSuggestion(!showSuggestion)}>
      {children}
      {showSuggestion && (
        <div style={{
          position: 'absolute',
          top: '100%',
          left: '0',
          background: '#fff',
          border: '1px solid #ccc',
          padding: '10px',
          zIndex: 100,
          maxWidth: '300px'
        }}>
          <strong>Suggestion:</strong>
          <p>{suggestion}</p>
        </div>
      )}
    </span>
  );
}

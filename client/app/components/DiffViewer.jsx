// components/DiffViewer.js
import React from 'react';
import { diffWords } from 'diff';
import HighlightedSection from './HighlightedSection';

export default function DiffViewer({ originalText, correctedText, changes }) {
  // Compute a diff between the original and corrected text.
  const diff = diffWords(originalText, correctedText);
  
  return (
    <div>
      <h2>Side-by-Side Comparison</h2>
      <div style={{ display: 'flex', gap: '20px' }}>
        <div style={{ flex: 1 }}>
          <h3>Original</h3>
          <p>{originalText}</p>
        </div>
        <div style={{ flex: 1 }}>
          <h3>Corrected</h3>
          <p>
            {diff.map((part, index) => {
              if (part.added) {
                // Find the corresponding change data.
                const change = changes.find(c => c.correctedSegment.includes(part.value.trim()));
                return (
                  <HighlightedSection key={index} suggestion={change ? change.suggestion : ''}>
                    <span style={{ backgroundColor: '#d4fcd4' }}>{part.value}</span>
                  </HighlightedSection>
                );
              } else if (part.removed) {
                return <span key={index} style={{ backgroundColor: '#fcd4d4', textDecoration: 'line-through' }}>{part.value}</span>;
              } else {
                return <span key={index}>{part.value}</span>;
              }
            })}
          </p>
        </div>
      </div>
    </div>
  );
}
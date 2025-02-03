'use client';

import React from 'react';
import FileUpload from './components/FileUpload';

export default function HomePage() {
  return (
    <div className="container">
      <h1>EMR Analyzer</h1>
      <p>Upload your EMR document (PDF or image) to get recommendations and improvements.</p>
      <FileUpload />
    </div>
  );
}

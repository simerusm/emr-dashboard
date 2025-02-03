'use client'

import React, { useState } from 'react';
import { useRouter } from 'next/navigation';

export default function FileUpload() {
  const [file, setFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const router = useRouter();

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;

    setUploading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const res = await fetch('/api/upload', {
        method: 'POST',
        body: formData,
      });
      const data = await res.json();
      // Redirect to results page, passing the result as a query parameter.
      router.push({
        pathname: '/results',
        query: { result: JSON.stringify(data) },
      });
    } catch (error) {
      console.error('Error uploading file:', error);
    }
    setUploading(false);
  };

  return (
    <form onSubmit={handleSubmit}>
      <input type="file" accept=".pdf, .png, .jpg, .jpeg, .tiff, .bmp, .gif" onChange={handleFileChange} required />
      <button type="submit" className="upload-btn" disabled={uploading}>
        {uploading ? 'Uploading...' : 'Upload and Analyze'}
      </button>
    </form>
  );
}
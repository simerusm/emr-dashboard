'use client';

import React, { useEffect, useState } from 'react';
import DiffViewer from "./components/DiffViewer"
import { getProcessedEMR } from "./lib/emrProcessor"

export default function HomePage() {
  const [emrData, setEmrData] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const data = await getProcessedEMR();
        setEmrData(data);
      } catch (error) {
        console.error('Error fetching EMR data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return <div>Loading...</div>;
  }

  return (
    <DiffViewer emrData={emrData} />
  )
}

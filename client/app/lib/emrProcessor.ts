"use client"

import type { EMRSection } from "./types"

export async function getProcessedEMR(fileId: string): Promise<EMRSection[]> {
  if (typeof window === 'undefined') {
    return []; // Return null if running on server-side
  }

  const storedData = localStorage.getItem(`analysis_${fileId}`);
  if (!storedData) {
    return [];
  }

  return JSON.parse(storedData);
}

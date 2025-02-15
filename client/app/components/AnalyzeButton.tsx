"use client"

import React from 'react'

export default function AnalyzeButton() {
  return (
    <button
        className="rounded-[1.15rem] px-8 py-6 text-lg font-semibold backdrop-blur-md 
                    bg-white hover:bg-gray-50
                    text-black transition-all duration-300 
                    group-hover:-translate-y-0.5 border border-black/10
                    hover:shadow-md"
        >
        <span className="opacity-90 group-hover:opacity-100 transition-opacity">Analyze EMR</span>
        <span
            className="ml-3 opacity-70 group-hover:opacity-100 group-hover:translate-x-1.5 
                        transition-all duration-300"
        >
            →
        </span>
    </button>
  );
};
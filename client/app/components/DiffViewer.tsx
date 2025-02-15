"use client"

import type React from "react"

import { useState, useCallback } from "react"
import type { EMRSection, EMRChange } from "../lib/types"

interface DiffViewerProps {
  emrData: EMRSection[]
}

interface TooltipState {
  change: EMRChange | null
  x: number
  y: number
}

export default function DiffViewer({ emrData }: DiffViewerProps) {
  const [tooltip, setTooltip] = useState<TooltipState>({ change: null, x: 0, y: 0 })

  const handleMouseEnter = useCallback((e: React.MouseEvent, change: EMRChange) => {
    setTooltip({
      change,
      x: e.clientX,
      y: e.clientY,
    })
  }, [])

  const handleMouseLeave = useCallback(() => {
    setTooltip({ change: null, x: 0, y: 0 })
  }, [])

  return (
    <div className="space-y-4 relative">
      {emrData.map((section, sectionIndex) => (
        <div key={sectionIndex} className="border p-4 rounded">
          <h2 className="text-xl font-bold mb-2">{section.title}</h2>
          <div>
            {section.content.map((item, itemIndex) => {
              if (typeof item === "string") {
                return <span key={itemIndex}>{item}</span>
              } else {
                return (
                  <span
                    key={itemIndex}
                    className="bg-yellow-300 text-black relative group cursor-pointer"
                    onMouseEnter={(e) => handleMouseEnter(e, item)}
                    onMouseLeave={handleMouseLeave}
                  >
                    {item.suggested}
                  </span>
                )
              }
            })}
          </div>
        </div>
      ))}
      {tooltip.change && (
        <div
          className="fixed bg-white border p-2 rounded shadow-lg z-10 w-max max-w-xs text-sm"
          style={{
            left: `${tooltip.x}px`,
            top: `${tooltip.y + 20}px`, // 20px offset to position below the cursor
          }}
        >
          <p className="font-semibold text-red-500">Original: {tooltip.change.original}</p>
          <p className="mt-1 text-gray-600">Reason: {tooltip.change.reason}</p>
        </div>
      )}
    </div>
  )
}


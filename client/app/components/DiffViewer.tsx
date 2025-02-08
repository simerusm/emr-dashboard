import { useState } from "react"
import type { EMRSection } from "../lib/types"

interface DiffViewerProps {
  emrData: EMRSection[]
}

export default function DiffViewer({ emrData }: DiffViewerProps) {
  const [hoveredChange, setHoveredChange] = useState<string | null>(null)

  return (
    <div className="space-y-4">
      {emrData.map((section, sectionIndex) => (
        <div key={sectionIndex} className="border p-4 rounded">
          <h2 className="text-xl font-bold mb-2">{section.title}</h2>
          <div>
            {section.content.map((item, itemIndex) => {
              console.log(item)
              if (typeof item === "string") {
                return <span key={itemIndex}>{item}</span>
              } else {
                return (
                  <span
                    key={itemIndex}
                    className="bg-yellow-300 text-black relative group cursor-pointer"
                    onMouseEnter={() => setHoveredChange(item.original)}
                    onMouseLeave={() => setHoveredChange(null)}
                  >
                    {item.suggested}
                    {hoveredChange === item.original && (
                      <span className="absolute bottom-full left-0 bg-white border p-2 rounded shadow-lg z-10 w-max max-w-xs text-red-500">
                        Original: {item.original}
                        <br />
                        Reason: {item.reason}
                      </span>
                    )}
                  </span>
                )
              }
            })}
          </div>
        </div>
      ))}
    </div>
  )
}


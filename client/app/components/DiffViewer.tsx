"use client"

import type React from "react"

import { useState, useCallback, useRef } from "react"
import { ChevronRight } from "lucide-react"

interface EMRChange {
  original: string
  suggested: string
  reason: string
}

interface EMRSection {
  title: string
  content: (string | EMRChange)[]
}

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
  const [activeSection, setActiveSection] = useState<string>(emrData[0]?.title || "")
  const sectionRefs = useRef<{ [key: string]: HTMLDivElement | null }>({})

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

  const scrollToSection = (title: string) => {
    setActiveSection(title)
    sectionRefs.current[title]?.scrollIntoView({ behavior: "smooth" })
  }

  const getChangeCount = (section: EMRSection) => {
    return section.content.filter((item) => typeof item !== "string").length
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      {/* Navigation Sidebar */}
      <nav className="w-64 bg-white p-4 shadow-lg fixed h-screen overflow-y-auto">
        <h2 className="text-lg font-bold mb-4 text-gray-800">EMR Sections</h2>
        <div className="space-y-2">
          {emrData.map((section) => {
            const changeCount = getChangeCount(section)
            return (
              <button
                key={section.title}
                onClick={() => scrollToSection(section.title)}
                className={`w-full text-left p-2 rounded transition-colors duration-200 flex items-center justify-between group
                  ${activeSection === section.title ? "bg-blue-50 text-blue-700" : "hover:bg-gray-100"}`}
              >
                <span className="text-sm font-medium truncate flex-1">{section.title}</span>
                {changeCount > 0 && (
                  <span className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full ml-2">
                    {changeCount}
                  </span>
                )}
              </button>
            )
          })}
        </div>
      </nav>

      {/* Main Content */}
      <main className="ml-64 flex-1 p-8">
        <div className="max-w-4xl mx-auto space-y-8">
          {emrData.map((section, sectionIndex) => (
            <div
              key={sectionIndex}
              ref={(el) => (sectionRefs.current[section.title] = el)}
              className="bg-white rounded-lg shadow-md overflow-hidden"
            >
              <div className="border-b bg-gray-50 px-6 py-4 flex items-center justify-between">
                <h2 className="text-xl font-bold text-gray-800">{section.title}</h2>
                {getChangeCount(section) > 0 && (
                  <span className="text-sm bg-yellow-100 text-yellow-800 px-3 py-1 rounded-full">
                    {getChangeCount(section)} changes
                  </span>
                )}
              </div>
              <div className="p-6">
                <p className="text-gray-700 leading-relaxed">
                  {section.content.map((item, itemIndex) => {
                    if (typeof item === "string") {
                      return (
                        <span key={itemIndex} className="mr-1">
                          {item}
                        </span>
                      )
                    } else {
                      return (
                        <span
                          key={itemIndex}
                          className="bg-yellow-100 text-black relative group cursor-pointer 
                                   px-1 py-0.5 rounded mr-1 border-b-2 border-yellow-300
                                   hover:bg-yellow-200 transition-colors duration-200"
                          onMouseEnter={(e) => handleMouseEnter(e, item)}
                          onMouseLeave={handleMouseLeave}
                        >
                          {item.suggested}
                          <ChevronRight className="w-3 h-3 inline-block ml-1 text-yellow-600" />
                        </span>
                      )
                    }
                  })}
                </p>
              </div>
            </div>
          ))}
        </div>
      </main>

      {/* Tooltip */}
      {tooltip.change && (
        <div
          className="fixed bg-white border border-gray-200 p-4 rounded-lg shadow-xl z-50 w-max max-w-sm"
          style={{
            left: `${tooltip.x}px`,
            top: `${tooltip.y + 20}px`,
          }}
        >
          <div className="space-y-3">
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-1">Original Text</h3>
              <p className="text-red-600">{tooltip.change.original}</p>
            </div>
            <div>
              <h3 className="text-sm font-semibold text-gray-500 mb-1">Reason for Change</h3>
              <p className="text-gray-700">{tooltip.change.reason}</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}


"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"

export default function FileUpload() {
  const [file, setFile] = useState<File | null>(null)
  const [uploading, setUploading] = useState(false)
  const router = useRouter()

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!file) return

    setUploading(true)
    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      })

      if (response.ok) {
        const data = await response.json()
        router.push(`/analyze/${data.fileId}`)
      } else {
        console.error("File upload failed")
      }
      //router.push(`/analyze/123`)
    } catch (error) {
      console.error("Error uploading file: ", error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-black">
      <div className="bg-white p-8 rounded-lg shadow-lg max-w-md w-full">
        <h2 className="text-2xl font-bold mb-6 text-center text-gray-800">Upload EMR</h2>
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700 mb-2">
              Upload EMR (PDF or PNG)
            </label>
            <input
              id="file-upload"
              type="file"
              onChange={handleFileChange}
              accept=".pdf,.png"
              className="mt-1 block w-full text-sm text-gray-500
                file:mr-4 file:py-2 file:px-4
                file:rounded-full file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                border border-gray-300 rounded-md
                focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>
          <button
            type="submit"
            disabled={!file || uploading}
            className="w-full bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-600 disabled:bg-gray-400 disabled:cursor-not-allowed transition duration-300 ease-in-out transform hover:-translate-y-1 hover:shadow-lg"
          >
            {uploading ? "Uploading..." : "Upload and Process"}
          </button>
        </form>
      </div>
    </div>
  )
}


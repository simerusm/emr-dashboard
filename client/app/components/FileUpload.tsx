"use client"

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
      // const response = await fetch("/api/upload", {
      //   method: "POST",
      //   body: formData,
      // })

      // if (response.ok) {
      //   const data = await response.json()
      //   router.push(`/analyze/${data.fileId}`)
      // } else {
      //   console.error("File upload failed")
      // }
      router.push(`/analyze/123`)
    } catch (error) {
      console.error("Error uploading file:", error)
    } finally {
      setUploading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div>
        <label htmlFor="file-upload" className="block text-sm font-medium text-gray-700">
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
            hover:file:bg-blue-100"
        />
      </div>
      <button
        type="submit"
        disabled={!file || uploading}
        className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 disabled:bg-gray-400"
      >
        {uploading ? "Uploading..." : "Upload and Process"}
      </button>
    </form>
  )
}
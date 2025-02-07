import { useState } from "react"

export default function EMRUploader() {
  const [file, setFile] = useState<File | null>(null)

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFile(e.target.files[0])
    }
  }

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    if (!file) return

    const formData = new FormData()
    formData.append("file", file)

    try {
      const response = await fetch("/api/upload", {
        method: "POST",
        body: formData,
      })
      if (response.ok) {
        console.log("File uploaded successfully")
        // You can add logic here to update the UI or trigger the EMRViewer
      } else {
        console.error("File upload failed")
      }
    } catch (error) {
      console.error("Error uploading file:", error)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="mb-4">
      <input type="file" onChange={handleFileChange} accept=".pdf,.doc,.docx,.txt" className="mb-2" />
      <button type="submit" className="bg-blue-500 text-white px-4 py-2 rounded" disabled={!file}>
        Upload EMR
      </button>
    </form>
  )
}

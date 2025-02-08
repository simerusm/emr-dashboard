import FileUpload from "../components/FileUpload"

export default function UploadPage() {
  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">Upload EMR</h1>
      <FileUpload />
    </main>
  )
}
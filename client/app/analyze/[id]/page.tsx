import DiffViewer from "../../components/DiffViewer"
import { getProcessedEMR } from "../../lib/emrProcessor"

export default async function EMRPage() {
  const emrData = await getProcessedEMR()

  return (
    <main className="container mx-auto p-4">
      <h1 className="text-3xl font-bold mb-4">EMR with Suggested Changes</h1>
      <DiffViewer emrData={emrData} />
    </main>
  )
}
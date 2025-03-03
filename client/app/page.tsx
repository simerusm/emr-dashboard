import BackgroundPaths from "./components/BackgroundPaths"
import Link from "next/link"
import AnalyzeButton from "./components/AnalyzeButton"

export default function Home() {
  return (
    <BackgroundPaths title="EMR Analyzer">
      <Link href="/login" className="inline-block">
        <div
          className="group relative bg-gradient-to-b from-black/10 to-white/10 
                    dark:from-white/10 dark:to-black/10 p-px rounded-2xl backdrop-blur-lg 
                    overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300"
        >
          <AnalyzeButton/>
        </div>
      </Link>
    </BackgroundPaths>
  )
}
import BackgroundPaths from "./components/BackgroundPaths"
import Link from "next/link"

export default function Home() {
  return (
    <BackgroundPaths title="EMR Analyzer">
      <Link href="/upload" className="inline-block">
        <div
          className="group relative bg-gradient-to-b from-black/10 to-white/10 
                    dark:from-white/10 dark:to-black/10 p-px rounded-2xl backdrop-blur-lg 
                    overflow-hidden shadow-lg hover:shadow-xl transition-shadow duration-300"
        >
          <button
            className="rounded-[1.15rem] px-8 py-6 text-lg font-semibold backdrop-blur-md 
                        bg-white/95 hover:bg-white/100 dark:bg-black/95 dark:hover:bg-black/100 
                        text-black dark:text-white transition-all duration-300 
                        group-hover:-translate-y-0.5 border border-black/10 dark:border-white/10
                        hover:shadow-md dark:hover:shadow-neutral-800/50"
          >
            <span className="opacity-90 group-hover:opacity-100 transition-opacity">Analyze EMR</span>
            <span
              className="ml-3 opacity-70 group-hover:opacity-100 group-hover:translate-x-1.5 
                            transition-all duration-300"
            >
              →
            </span>
          </button>
        </div>
      </Link>
    </BackgroundPaths>
  )
}
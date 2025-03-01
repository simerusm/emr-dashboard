export interface EMRChange {
    original: string
    suggested: string
    reason: string
}
  
export interface EMRSection {
    title: string
    content: (string | EMRChange)[]
}

export interface DiffViewerProps {
    emrData: EMRSection[]
}

export interface TooltipState {
    change: EMRChange | null
    x: number
    y: number
}
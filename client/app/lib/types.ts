export interface EMRChange {
    original: string
    suggested: string
    reason: string
}
  
export interface EMRSection {
    title: string
    content: (string | EMRChange)[]
}

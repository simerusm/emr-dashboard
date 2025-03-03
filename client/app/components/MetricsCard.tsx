import type React from "react"
import { Card } from "./ui/Card"
import { ArrowUpRight, AlertTriangle, CheckCircle, XCircle } from "lucide-react"

interface MetricsCardProps {
  title: string
  value: string
  change?: {
    value: string
    percentage: string
    isPositive: boolean
  }
  severity?: "success" | "warning" | "critical"
  chart?: React.ReactNode
}

export function MetricsCard({ title, value, change, severity, chart }: MetricsCardProps) {
  const getSeverityIcon = () => {
    switch (severity) {
      case "success":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "warning":
        return <AlertTriangle className="h-4 w-4 text-yellow-500" />
      case "critical":
        return <XCircle className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  return (
    <Card className="p-4 bg-background/50 backdrop-blur">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <h3 className="text-sm text-muted-foreground">{title}</h3>
          {getSeverityIcon()}
        </div>
        {chart ? <ArrowUpRight className="h-4 w-4 text-muted-foreground" /> : null}
      </div>
      <div className="flex items-end justify-between">
        <div>
          <p className="text-2xl font-bold">{value}</p>
          {change && (
            <div className="flex items-center gap-1 mt-1">
              <span className="text-sm">{change.value}</span>
              <span className={`text-sm ${change.isPositive ? "text-green-500" : "text-red-500"}`}>
                {change.percentage}
              </span>
            </div>
          )}
        </div>
        {chart}
      </div>
    </Card>
  )
}
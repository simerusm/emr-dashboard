import { Avatar } from "./ui/Avatar"
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from "./ui/Table"
import { AlertTriangle, CheckCircle, Info, MoreHorizontal } from "lucide-react"

const complianceData = [
  {
    provider: "Dr. Sarah Chen",
    department: "Cardiology",
    compliantCases: 142,
    totalCases: 150,
    riskScore: "Low",
    lastReview: "2024-03-01",
    status: "Compliant",
  },
  {
    provider: "Dr. Michael Brown",
    department: "Internal Medicine",
    compliantCases: 89,
    totalCases: 100,
    riskScore: "Medium",
    lastReview: "2024-03-01",
    status: "Review",
  },
  {
    provider: "Dr. Emily Wilson",
    department: "Oncology",
    compliantCases: 67,
    totalCases: 75,
    riskScore: "High",
    lastReview: "2024-02-28",
    status: "Alert",
  },
]

export function ComplianceTable() {
  const getStatusIcon = (status: string) => {
    switch (status) {
      case "Compliant":
        return <CheckCircle className="h-4 w-4 text-green-500" />
      case "Review":
        return <Info className="h-4 w-4 text-yellow-500" />
      case "Alert":
        return <AlertTriangle className="h-4 w-4 text-red-500" />
      default:
        return null
    }
  }

  const getComplianceRate = (compliant: number, total: number) => {
    return `${Math.round((compliant / total) * 100)}%`
  }

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableHead>Provider</TableHead>
          <TableHead>Department</TableHead>
          <TableHead>Compliance Rate</TableHead>
          <TableHead>Risk Score</TableHead>
          <TableHead>Last Review</TableHead>
          <TableHead>Status</TableHead>
          <TableHead></TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        {complianceData.map((item) => (
          <TableRow key={item.provider}>
            <TableCell>
              <div className="flex items-center gap-2">
                <Avatar className="h-8 w-8">
                  <img src={`/placeholder.svg?height=32&width=32`} alt={item.provider} />
                </Avatar>
                <div>
                  <div className="font-medium">{item.provider}</div>
                  <div className="text-xs text-muted-foreground">{item.department}</div>
                </div>
              </div>
            </TableCell>
            <TableCell>{item.department}</TableCell>
            <TableCell>{getComplianceRate(item.compliantCases, item.totalCases)}</TableCell>
            <TableCell>
              <span
                className={`inline-flex items-center rounded-full px-2 py-1 text-xs ${
                  item.riskScore === "Low"
                    ? "bg-green-500/10 text-green-500"
                    : item.riskScore === "Medium"
                      ? "bg-yellow-500/10 text-yellow-500"
                      : "bg-red-500/10 text-red-500"
                }`}
              >
                {item.riskScore}
              </span>
            </TableCell>
            <TableCell>{item.lastReview}</TableCell>
            <TableCell>
              <div className="flex items-center gap-2">
                {getStatusIcon(item.status)}
                <span>{item.status}</span>
              </div>
            </TableCell>
            <TableCell>
              <MoreHorizontal className="h-4 w-4 text-muted-foreground" />
            </TableCell>
          </TableRow>
        ))}
      </TableBody>
    </Table>
  )
}
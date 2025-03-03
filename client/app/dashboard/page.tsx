import { Button } from "../components/ui/Button"
import { Card } from "../components/ui/Card"
import Input from "../components/ui/Input"
import { MetricsCard } from "../components/MetricsCard"
import { StatsChart } from "../components/StatsChart"
import { ComplianceTable } from "../components/ComplianceTable"
import {
  AlertCircle,
  BarChart3,
  BrainCircuit,
  ChevronDown,
  FileText,
  LayoutDashboard,
  Settings,
  ShieldCheck,
  UserRound,
} from "lucide-react"

export default function Page() {
  return (
    <div className="min-h-screen bg-[#f0f4f8] dark:bg-[#1a1f2c]">
      <div className="grid lg:grid-cols-[280px_1fr]">
        <aside className="border-r bg-background/50 backdrop-blur">
          <div className="flex h-16 items-center gap-2 border-b px-6">
            <BrainCircuit className="h-6 w-6 text-blue-600" />
            <span className="font-bold">EMR Copilot</span>
          </div>
          <div className="px-4 py-4">
            <Input placeholder="Search providers..." className="bg-background/50" />
          </div>
          <nav className="space-y-2 px-2">
            <Button variant="ghost" className="w-full justify-start gap-2">
              <LayoutDashboard className="h-4 w-4" />
              Overview
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <AlertCircle className="h-4 w-4" />
              Alerts & Compliance
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <UserRound className="h-4 w-4" />
              Providers
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <FileText className="h-4 w-4" />
              Documentation
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <BarChart3 className="h-4 w-4" />
              Analytics
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <ShieldCheck className="h-4 w-4" />
              Audit Log
            </Button>
            <Button variant="ghost" className="w-full justify-start gap-2">
              <Settings className="h-4 w-4" />
              Settings
            </Button>
          </nav>
        </aside>
        <main className="p-6">
          <div className="mb-6 flex items-center justify-between">
            <div className="space-y-1">
              <h1 className="text-2xl font-bold">Compliance Dashboard</h1>
              <div className="text-sm text-muted-foreground">Last updated: March 2, 2024 5:24 PM</div>
            </div>
            <Button variant="outline" className="gap-2">
              All Departments
              <ChevronDown className="h-4 w-4" />
            </Button>
          </div>
          <div className="grid gap-4 md:grid-cols-3">
            <MetricsCard
              title="Overall Compliance Rate"
              value="94.2%"
              change={{ value: "+2.1%", percentage: "vs last month", isPositive: true }}
              severity="success"
            />
            <MetricsCard
              title="Active Alerts"
              value="23"
              change={{ value: "-5", percentage: "vs last week", isPositive: true }}
              severity="warning"
            />
            <MetricsCard
              title="Critical Issues"
              value="3"
              change={{ value: "+1", percentage: "vs yesterday", isPositive: false }}
              severity="critical"
            />
          </div>
          <Card className="mt-6 p-6">
            <div className="mb-4 flex items-center justify-between">
              <h2 className="text-lg font-semibold">Compliance Trends</h2>
              <div className="flex gap-2">
                <Button size="sm" variant="ghost">
                  Week
                </Button>
                <Button size="sm" variant="ghost">
                  Month
                </Button>
                <Button size="sm" variant="ghost">
                  Quarter
                </Button>
                <Button size="sm" variant="ghost">
                  Year
                </Button>
              </div>
            </div>
            <StatsChart />
          </Card>
          <div className="mt-6">
            <h2 className="text-lg font-semibold mb-4">Provider Compliance</h2>
            <ComplianceTable />
          </div>
        </main>
      </div>
    </div>
  )
}
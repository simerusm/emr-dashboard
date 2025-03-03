import Link from "next/link"
import Image from 'next/image';
import {
  BrainCircuit,
  ShieldCheck,
  BarChart3,
  AlertCircle,
  ChevronRight,
  ArrowRight,
  BadgeCheck,
  Zap,
} from "lucide-react"
import { Button } from "./components/ui/Button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/Card"

const stats = [
  { label: "Healthcare Providers", value: "2,000+", prefix: "+" },
  { label: "Compliance Rate", value: "99.9", suffix: "%" },
  { label: "Patient Records", value: "1M", prefix: ">" },
  { label: "Time Saved", value: "40", suffix: "%" },
]

export default function LandingPage() {
  return (
    <div className="flex min-h-screen flex-col bg-gradient-to-b from-background to-background/80">
      {/* Floating Background Elements */}
      <div className="fixed inset-0 -z-10 overflow-hidden">
        <div className="absolute -top-1/2 right-0 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl" />
        <div className="absolute top-1/3 -left-1/4 w-96 h-96 bg-purple-500/10 rounded-full blur-3xl" />
      </div>

      <header className="sticky top-0 z-50 px-4 lg:px-6 h-16 flex items-center backdrop-blur-lg border-b bg-background/60">
        <Link className="flex items-center justify-center" href="/">
          <div className="bg-blue-600 p-2 rounded-lg">
            <BrainCircuit className="h-6 w-6 text-white" />
          </div>
          <span className="ml-2 text-lg font-bold">EMR Copilot</span>
        </Link>
        <nav className="ml-auto flex gap-4 sm:gap-6">
          <Link className="text-sm font-medium hover:text-primary transition-colors" href="#features">
            Features
          </Link>
          <Link className="text-sm font-medium hover:text-primary transition-colors" href="#testimonials">
            Testimonials
          </Link>
          <Link className="text-sm font-medium hover:text-primary transition-colors" href="#pricing">
            Pricing
          </Link>
          <Link href="/login">
            <Button variant="secondary" size="sm">
              Login
              <ChevronRight className="ml-1 h-4 w-4" />
            </Button>
          </Link>
        </nav>
      </header>

      <main className="flex-1">
        <section className="w-full py-12 md:py-24 lg:py-32 xl:py-48 relative">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center space-y-4 text-center relative z-10">
              <div className="space-y-2">
                <h1 className="text-3xl font-bold tracking-tighter sm:text-4xl md:text-5xl lg:text-6xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                  Transform Healthcare Compliance with AI
                </h1>
                <p className="mx-auto max-w-[700px] text-muted-foreground md:text-xl">
                  Empower your medical practice with real-time EMR validation, compliance monitoring, and intelligent
                  insights.
                </p>
              </div>
              <div className="space-x-4">
                <Link href="/login">
                  <Button
                    size="lg"
                    className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                  >
                    Get Started
                    <ArrowRight className="ml-2 h-4 w-4" />
                  </Button>
                </Link>
                <Button size="lg" variant="outline" className="shadow-lg hover:shadow-xl transition-all duration-200">
                  Schedule Demo
                </Button>
              </div>
            </div>
          </div>
        </section>

        {/* Stats Section */}
        <section className="w-full py-12 md:py-24">
          <div className="container px-4 md:px-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
              {stats.map((stat, index) => (
                <Card
                  key={index}
                  className="bg-background/50 backdrop-blur border-none shadow-xl hover:shadow-2xl transition-all duration-200"
                >
                  <CardContent className="p-6">
                    <div className="space-y-2 text-center">
                      <h3 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                        {stat.prefix}
                        {stat.value}
                        {stat.suffix}
                      </h3>
                      <p className="text-sm text-muted-foreground">{stat.label}</p>
                    </div>
                  </CardContent>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 relative" id="features">
          <div className="container px-4 md:px-6">
            <div className="flex flex-col items-center justify-center space-y-4 text-center">
              <div className="space-y-2">
                <h2 className="text-3xl font-bold tracking-tighter md:text-4xl/tight">
                  Advanced Features for Modern Healthcare
                </h2>
                <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl">
                  Comprehensive tools designed to enhance patient care and ensure compliance
                </p>
              </div>
            </div>
            <div className="mx-auto grid max-w-5xl gap-6 py-12 md:grid-cols-2 lg:grid-cols-3">
              {[
                {
                  icon: ShieldCheck,
                  title: "Real-time Validation",
                  description: "Instant verification of medical decisions against best practices and patient history",
                },
                {
                  icon: AlertCircle,
                  title: "Compliance Monitoring",
                  description: "Automated tracking of regulatory requirements and documentation standards",
                },
                {
                  icon: BarChart3,
                  title: "Analytics Dashboard",
                  description: "Comprehensive insights into practice performance and compliance metrics",
                },
              ].map((feature, index) => (
                <Card
                  key={index}
                  className="group relative overflow-hidden bg-background/50 backdrop-blur border-none shadow-xl hover:shadow-2xl transition-all duration-200"
                >
                  <CardHeader>
                    <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 to-purple-600/10 opacity-0 group-hover:opacity-100 transition-opacity duration-200" />
                    <feature.icon className="h-10 w-10 text-blue-600" />
                    <CardTitle>{feature.title}</CardTitle>
                    <CardDescription>{feature.description}</CardDescription>
                  </CardHeader>
                </Card>
              ))}
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 bg-gradient-to-b from-background/50 to-background relative">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 lg:grid-cols-[1fr_400px] lg:gap-12 xl:grid-cols-[1fr_600px]">
              <div className="flex flex-col justify-center space-y-4">
                <div className="space-y-2">
                  <div className="inline-flex items-center rounded-lg bg-blue-600/10 px-3 py-1 text-sm text-blue-600">
                    <BadgeCheck className="mr-1 h-4 w-4" />
                    Trusted by Leading Healthcare Providers
                  </div>
                  <h2 className="text-3xl font-bold tracking-tighter md:text-4xl">Elevate Your Practice</h2>
                  <p className="max-w-[600px] text-muted-foreground md:text-xl">
                    Join thousands of healthcare professionals who trust EMR Copilot to enhance their practice
                    efficiency and compliance.
                  </p>
                </div>
                <div className="flex flex-col gap-2 min-[400px]:flex-row">
                  <Link href="/login">
                    <Button
                      size="lg"
                      className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                    >
                      Start Your Journey
                      <Zap className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                </div>
              </div>
              <div className="relative group">
                <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl blur-xl opacity-50 group-hover:opacity-75 transition-opacity duration-200" />
                <Image
                  src="/placeholder.svg" // Use the path to your image
                  height={310} // Set the height
                  width={550} // Set the width
                  alt="Description of the image" // Add an alt attribute for accessibility
                />
              </div>
            </div>
          </div>
        </section>

        <section className="w-full py-12 md:py-24 lg:py-32 border-t bg-gradient-to-b from-background to-background/80">
          <div className="container px-4 md:px-6">
            <div className="grid gap-6 items-center">
              <div className="flex flex-col justify-center space-y-4 text-center">
                <div className="space-y-2">
                  <h2 className="text-3xl font-bold tracking-tighter md:text-4xl bg-clip-text text-transparent bg-gradient-to-r from-blue-600 to-purple-600">
                    Ready to Transform Your Practice?
                  </h2>
                  <p className="mx-auto max-w-[600px] text-muted-foreground md:text-xl">
                    Join the healthcare revolution with EMR Copilot today.
                  </p>
                </div>
                <div className="mx-auto w-full max-w-sm space-y-2">
                  <Link href="/login">
                    <Button
                      className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 transition-all duration-200 shadow-lg hover:shadow-xl"
                      size="lg"
                    >
                      Get Started Now
                      <ArrowRight className="ml-2 h-4 w-4" />
                    </Button>
                  </Link>
                  <p className="text-xs text-muted-foreground">Try it risk-free. No credit card required.</p>
                </div>
              </div>
            </div>
          </div>
        </section>
      </main>

      <footer className="w-full border-t bg-background/50 backdrop-blur">
        <div className="container flex flex-col gap-4 py-10 md:flex-row md:justify-between">
          <div className="flex flex-col gap-2">
            <Link className="flex items-center justify-center md:justify-start" href="/">
              <div className="bg-blue-600 p-2 rounded-lg">
                <BrainCircuit className="h-6 w-6 text-white" />
              </div>
              <span className="ml-2 text-lg font-bold">EMR Copilot</span>
            </Link>
            <p className="text-sm text-muted-foreground">© 2024 EMR Copilot. All rights reserved.</p>
          </div>
          <nav className="grid gap-4 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4">
            {["Product", "Features", "Pricing", "Company", "Team", "Contact", "Terms", "Privacy"].map((item) => (
              <Link key={item} className="text-sm hover:text-primary transition-colors" href="#">
                {item}
              </Link>
            ))}
          </nav>
        </div>
      </footer>
    </div>
  )
}
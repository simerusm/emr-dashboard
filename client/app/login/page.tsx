"use client"

import type React from "react"

import { useState } from "react"
import { useRouter } from "next/navigation"
import { BrainCircuit } from "lucide-react"
import { Button } from "../components/ui/Button"
import Input from "../components/ui/Input"
import { Label } from "../components/ui/Label"
import { Checkbox } from "../components/ui/Checkbox"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "../components/ui/Card"

export default function LoginPage() {
  const router = useRouter()
  const [isLoading, setIsLoading] = useState(false)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setIsLoading(true)
    // Simulate login - replace with actual authentication
    setTimeout(() => {
      setIsLoading(false)
      router.push("/dashboard")
    }, 1000)
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-[#f0f4f8] dark:bg-[#1a1f2c]">
      <div className="container flex flex-col items-center justify-center space-y-4 px-4 md:px-6">
        <div className="flex items-center space-x-2">
          <BrainCircuit className="h-8 w-8 text-blue-600" />
          <h1 className="text-2xl font-bold">EMR Copilot</h1>
        </div>
        <Card className="w-full max-w-lg">
          <CardHeader className="space-y-1">
            <CardTitle className="text-2xl font-bold text-center">Sign in</CardTitle>
            <CardDescription className="text-center">Enter your credentials to access your account</CardDescription>
          </CardHeader>
          <form onSubmit={handleSubmit}>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" placeholder="m.mitchell@hospital.com" type="email" required autoComplete="email" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="password">Password</Label>
                <Input id="password" type="password" required autoComplete="current-password" />
              </div>
              <div className="flex items-center space-x-2">
                <Checkbox id="remember" />
                <label
                  htmlFor="remember"
                  className="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70"
                >
                  Remember me
                </label>
              </div>
            </CardContent>
            <CardFooter className="flex flex-col space-y-4">
              <Button type="submit" className="w-full" disabled={isLoading}>
                {isLoading ? "Signing in..." : "Sign in"}
              </Button>
              <Button variant="link" className="text-sm text-muted-foreground">
                Forgot your password?
              </Button>
            </CardFooter>
          </form>
        </Card>
      </div>
    </div>
  )
}
"use client"

import { useState } from "react"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { VoiceAssistant } from "@/components/voice-assistant"
import { PortfolioOverview } from "@/components/portfolio-overview"
import { AssetList } from "@/components/asset-list"
import { TransactionHistory } from "@/components/transaction-history"
import { RiskAnalysis } from "@/components/risk-analysis"
import { AIInsights } from "@/components/ai-insights"

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true)

  return (
    <div className="flex h-screen bg-gradient-to-br from-slate-950 via-purple-950 to-slate-900">
      {/* Sidebar */}
      <Sidebar open={sidebarOpen} onToggle={setSidebarOpen} />

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <Header onMenuClick={() => setSidebarOpen(!sidebarOpen)} />

        {/* Content Grid */}
        <main className="flex-1 overflow-auto">
          <div className="p-6 space-y-6">
            {/* Voice Assistant - Hero Element */}
            <VoiceAssistant />

            {/* Main Grid */}
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Left Column */}
              <div className="lg:col-span-2 space-y-6">
                <PortfolioOverview />
                <AssetList />
              </div>

              {/* Right Column */}
              <div className="space-y-6">
                <RiskAnalysis />
                <AIInsights />
              </div>
            </div>

            {/* Transaction History - Full Width */}
            <TransactionHistory />
          </div>
        </main>
      </div>
    </div>
  )
}

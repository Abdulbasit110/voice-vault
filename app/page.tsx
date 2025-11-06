"use client"

import { useState, useEffect } from "react"
import * as Dialog from "@radix-ui/react-dialog"
import { Sidebar } from "@/components/sidebar"
import { Header } from "@/components/header"
import { VoiceAssistant } from "@/components/voice-assistant"
import { PortfolioOverview } from "@/components/portfolio-overview"
import { AssetList } from "@/components/asset-list"
import { TransactionHistory } from "@/components/transaction-history"
import { RiskAnalysis } from "@/components/risk-analysis"
import { AIInsights } from "@/components/ai-insights"
import { WalletSetup } from "@/components/wallet-setup"

const STORAGE_KEY = 'voicevault_user_id'

export default function Dashboard() {
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [showWalletSetup, setShowWalletSetup] = useState(false)

  // Check if wallet exists on mount
  useEffect(() => {
    if (typeof window !== 'undefined') {
      const userId = localStorage.getItem(STORAGE_KEY)
      if (!userId) {
        setShowWalletSetup(true)
      }
    }
  }, [])

  const handleWalletCreated = (walletAddress: string) => {
    console.log('Wallet created:', walletAddress)
    setShowWalletSetup(false)
  }

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

      {/* Wallet Setup Modal */}
      <Dialog.Root open={showWalletSetup} onOpenChange={setShowWalletSetup}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
          <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg p-6">
            <WalletSetup 
              onWalletCreated={handleWalletCreated}
              onClose={() => setShowWalletSetup(false)}
            />
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </div>
  )
}

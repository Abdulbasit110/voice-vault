"use client"

import { useState } from "react"
import { Menu, Bell, User, Coins, Loader2, CheckCircle, AlertCircle } from "lucide-react"
import { motion } from "framer-motion"

const STORAGE_KEY = 'voicevault_user_id'
const CIRCLE_API_KEY = process.env.NEXT_PUBLIC_CIRCLE_API_KEY

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
  const [requesting, setRequesting] = useState(false)
  const [success, setSuccess] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const requestTestTokens = async () => {
    setRequesting(true)
    setError(null)
    setSuccess(false)

    try {
      // Get user ID from localStorage
      const userId = localStorage.getItem(STORAGE_KEY)
      if (!userId) {
        throw new Error('No wallet found. Please create a wallet first.')
      }

      // Get wallet address from Circle API
      const walletsResponse = await fetch(
        `https://api.circle.com/v1/w3s/wallets?userId=${userId}`,
        {
          headers: {
            'Authorization': `Bearer ${CIRCLE_API_KEY}`,
            'Content-Type': 'application/json'
          }
        }
      )

      if (!walletsResponse.ok) {
        throw new Error('Failed to fetch wallet')
      }

      const walletsData = await walletsResponse.json()
      const wallets = walletsData.data?.wallets || []
      
      if (wallets.length === 0) {
        throw new Error('No wallet found')
      }

      const walletAddress = wallets[0].address

      // Request tokens from Circle faucet
      const faucetResponse = await fetch(
        'https://api.circle.com/v1/faucet/drips',
        {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${CIRCLE_API_KEY}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            address: walletAddress,
            blockchain: 'ETH-SEPOLIA',
            native: true,
            usdc: true
          })
        }
      )

      if (!faucetResponse.ok) {
        const errorData = await faucetResponse.json().catch(() => ({}))
        throw new Error(errorData.message || 'Failed to request test tokens')
      }

      setSuccess(true)
      setTimeout(() => setSuccess(false), 5000)
    } catch (err) {
      console.error('Error requesting test tokens:', err)
      setError(err instanceof Error ? err.message : 'Failed to request tokens')
      setTimeout(() => setError(null), 5000)
    } finally {
      setRequesting(false)
    }
  }

  return (
    <header className="sticky top-0 z-30 bg-gradient-to-r from-slate-900/80 to-purple-900/80 backdrop-blur-md border-b border-purple-500/20 px-6 py-4">
      <div className="flex items-center justify-between">
        {/* Left */}
        <div className="flex items-center gap-4">
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={onMenuClick}
            className="md:hidden p-2 hover:bg-purple-500/20 rounded-lg transition-colors"
          >
            <Menu className="w-6 h-6 text-purple-300" />
          </motion.button>
          <h2 className="text-2xl font-bold text-white">Dashboard</h2>
        </div>

        {/* Right */}
        <div className="flex items-center gap-4">
          {/* Request Test Tokens Button */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={requestTestTokens}
            disabled={requesting || success}
            className="hidden sm:flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed text-sm font-medium shadow-lg shadow-purple-500/30 hover:shadow-purple-500/50"
            title={error || (success ? 'Tokens requested!' : 'Request testnet tokens')}
          >
            {requesting ? (
              <>
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Requesting...</span>
              </>
            ) : success ? (
              <>
                <CheckCircle className="w-4 h-4" />
                <span>Requested!</span>
              </>
            ) : (
              <>
                <Coins className="w-4 h-4" />
                <span>Get Test Tokens</span>
              </>
            )}
          </motion.button>

          {/* Mobile version - icon only */}
          <motion.button
            whileHover={{ scale: 1.05 }}
            whileTap={{ scale: 0.95 }}
            onClick={requestTestTokens}
            disabled={requesting || success}
            className="sm:hidden p-2 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-purple-500/30"
            title={error || (success ? 'Tokens requested!' : 'Request testnet tokens')}
          >
            {requesting ? (
              <Loader2 className="w-5 h-5 text-white animate-spin" />
            ) : success ? (
              <CheckCircle className="w-5 h-5 text-white" />
            ) : (
              <Coins className="w-5 h-5 text-white" />
            )}
          </motion.button>

          <motion.button
            whileHover={{ scale: 1.05 }}
            className="p-2 hover:bg-purple-500/20 rounded-lg transition-colors relative"
          >
            <Bell className="w-6 h-6 text-purple-300" />
            <span className="absolute top-1 right-1 w-2 h-2 bg-blue-400 rounded-full" />
          </motion.button>
          <motion.button
            whileHover={{ scale: 1.05 }}
            className="p-2 hover:bg-purple-500/20 rounded-lg transition-colors"
          >
            <User className="w-6 h-6 text-purple-300" />
          </motion.button>
        </div>
      </div>

      {/* Error/Success Toast */}
      {(error || success) && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0 }}
          className={`mt-2 px-4 py-3 rounded-lg text-sm backdrop-blur-xl ${
            error 
              ? 'bg-red-500/20 border border-red-500/50 text-red-300' 
              : 'bg-purple-500/20 border border-purple-500/50 text-purple-300'
          }`}
        >
          <div className="flex items-center gap-2">
            {success && <CheckCircle className="w-4 h-4 flex-shrink-0" />}
            {error && <AlertCircle className="w-4 h-4 flex-shrink-0" />}
            <span>{error || 'Test tokens requested! They should arrive shortly.'}</span>
          </div>
        </motion.div>
      )}
    </header>
  )
}

"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { TrendingUp, TrendingDown, Loader2, Inbox } from "lucide-react"

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Asset {
  symbol: string
  name: string
  amount: number
  value: number
  price: number
  change: number
}

interface TokenBalance {
  amount: string
  token: {
    id: string
    symbol: string
    name: string
    decimals: number
    blockchain: string
    isNative: boolean
  }
}

function mapTokenBalanceToAsset(tokenBalance: TokenBalance): Asset {
  const decimals = tokenBalance.token.decimals || 6
  const amount = parseFloat(tokenBalance.amount) / Math.pow(10, decimals)
  
  // For USDC, price is always 1.0
  // For other tokens, we'd need to fetch prices from an API (future enhancement)
  const price = tokenBalance.token.symbol === 'USDC' ? 1.0 : 0
  
  return {
    symbol: tokenBalance.token.symbol || 'UNKNOWN',
    name: tokenBalance.token.name || tokenBalance.token.symbol || 'Unknown Token',
    amount,
    value: amount * price,
    price,
    change: 0.0 // Price change would require external API
  }
}

export function AssetList() {
  const [assets, setAssets] = useState<Asset[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchBalances = async () => {
      try {
        setLoading(true)
        setError(null)
        
        // Get user_id from localStorage
        const userId = localStorage.getItem(STORAGE_KEY)
        if (!userId) {
          setLoading(false)
          return
        }
        
        const response = await fetch(
          `${API_URL}/api/wallet/balance?user_id=${userId}`
        )
        
        if (!response.ok) {
          throw new Error('Failed to fetch wallet balance')
        }
        
        const data = await response.json()
        const tokenBalances = data.tokenBalances || []
        
        // Map token balances to assets
        const mappedAssets = tokenBalances
          .filter((tb: TokenBalance) => tb.token.symbol) // Only show tokens with symbols
          .map(mapTokenBalanceToAsset)
          .filter((asset: Asset) => asset.amount > 0) // Only show assets with balance
        
        setAssets(mappedAssets)
      } catch (err) {
        console.error('Error fetching balances:', err)
        setError(err instanceof Error ? err.message : 'Failed to load balances')
      } finally {
        setLoading(false)
      }
    }
    
    fetchBalances()
  }, [])
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <h3 className="text-xl font-bold text-white mb-4">Your Assets</h3>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
          <span className="ml-3 text-purple-300">Loading balances...</span>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="p-3 rounded-lg bg-red-500/20 mb-3">
            <Inbox className="w-6 h-6 text-red-400" />
          </div>
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      ) : assets.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="p-4 rounded-full bg-purple-500/20 mb-4">
            <Inbox className="w-8 h-8 text-purple-400" />
          </div>
          <h4 className="text-lg font-semibold text-white mb-2">No Assets Found</h4>
          <p className="text-purple-300 text-sm text-center max-w-md">
            Your wallet balances will appear here once you receive tokens.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr className="border-b border-purple-500/20">
                <th className="text-left py-3 px-4 text-purple-300 font-semibold text-sm">Asset</th>
                <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">Amount</th>
                <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">Price</th>
                <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">Value</th>
                <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">24h</th>
              </tr>
            </thead>
            <tbody>
              {assets.map((asset, index) => (
                <motion.tr
                  key={`${asset.symbol}-${index}`}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  whileHover={{ backgroundColor: "rgba(168, 85, 247, 0.1)" }}
                  className="border-b border-purple-500/10 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div>
                      <p className="text-white font-semibold">{asset.symbol}</p>
                      <p className="text-purple-400 text-sm">{asset.name}</p>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-right text-white">
                    {asset.amount.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 6,
                    })}
                  </td>
                  <td className="py-4 px-4 text-right text-white">
                    ${asset.price.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-right text-white font-semibold">
                    ${asset.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-right">
                    <div className="flex items-center justify-end gap-1">
                      {asset.change >= 0 ? (
                        <>
                          <TrendingUp className="w-4 h-4 text-green-400" />
                          <span className="text-green-400 font-semibold">+{asset.change.toFixed(2)}%</span>
                        </>
                      ) : (
                        <>
                          <TrendingDown className="w-4 h-4 text-red-400" />
                          <span className="text-red-400 font-semibold">{asset.change.toFixed(2)}%</span>
                        </>
                      )}
                    </div>
                  </td>
                </motion.tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </motion.div>
  )
}

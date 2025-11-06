"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { TrendingUp, Loader2 } from "lucide-react"

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const COLORS = ["#3b82f6", "#a855f7", "#ec4899", "#f59e0b", "#10b981"]

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

interface PortfolioAsset {
  name: string
  value: number
  percentage: number
}

export function PortfolioOverview() {
  const [portfolioData, setPortfolioData] = useState<PortfolioAsset[]>([])
  const [totalValue, setTotalValue] = useState(0)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const change24h = 0.0 // Would require price history API

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
        const tokenBalances: TokenBalance[] = data.tokenBalances || []
        
        // Map token balances to portfolio data
        const assets: PortfolioAsset[] = tokenBalances
          .filter((tb: TokenBalance) => tb.token.symbol && parseFloat(tb.amount) > 0)
          .map((tb: TokenBalance) => {
            const decimals = tb.token.decimals || 6
            const amount = parseFloat(tb.amount) / Math.pow(10, decimals)
            // For USDC, price is 1.0. For other tokens, we'd need price API
            const price = tb.token.symbol === 'USDC' ? 1.0 : 0
            const value = amount * price
            
            return {
              name: tb.token.symbol,
              value,
              percentage: 0 // Will calculate after total
            }
          })
          .filter((asset: PortfolioAsset) => asset.value > 0)
        
        // Calculate total value
        const total = assets.reduce((sum, asset) => sum + asset.value, 0)
        
        // Calculate percentages
        const assetsWithPercentages = assets.map(asset => ({
          ...asset,
          percentage: total > 0 ? (asset.value / total) * 100 : 0
        }))
        
        setPortfolioData(assetsWithPercentages)
        setTotalValue(total)
      } catch (err) {
        console.error('Error fetching portfolio:', err)
        setError(err instanceof Error ? err.message : 'Failed to load portfolio')
      } finally {
        setLoading(false)
      }
    }
    
    fetchBalances()
  }, [])

  if (loading) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, delay: 0.1 }}
        className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
      >
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
          <span className="ml-3 text-purple-300">Loading portfolio...</span>
        </div>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.1 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Left - Stats */}
        <div className="flex flex-col justify-center">
          <h3 className="text-purple-300 text-sm font-semibold mb-2">Total Portfolio Value</h3>
          <div className="mb-4">
            <p className="text-4xl font-bold text-white">
              ${totalValue.toLocaleString("en-US", { minimumFractionDigits: 2 })}
            </p>
            {change24h !== 0 && (
              <div className="flex items-center gap-2 mt-2">
                <TrendingUp className="w-5 h-5 text-green-400" />
                <span className="text-green-400 font-semibold">+{change24h}% (24h)</span>
              </div>
            )}
          </div>

          {/* Asset Breakdown */}
          {portfolioData.length > 0 ? (
            <div className="space-y-3">
              {portfolioData.map((asset, index) => (
                <div key={asset.name} className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index % COLORS.length] }} />
                    <span className="text-purple-200 text-sm">{asset.name}</span>
                  </div>
                  <div className="text-right">
                    <p className="text-white font-semibold text-sm">
                      ${asset.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                    </p>
                    <p className="text-purple-400 text-xs">{asset.percentage.toFixed(1)}%</p>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-4">
              <p className="text-purple-300 text-sm">No assets in portfolio</p>
            </div>
          )}
        </div>

        {/* Right - Donut Chart */}
        {portfolioData.length > 0 ? (
          <div className="flex items-center justify-center">
            <ResponsiveContainer width="100%" height={250}>
              <PieChart>
                <Pie
                  data={portfolioData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={100}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {portfolioData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: "rgba(15, 23, 42, 0.9)",
                    border: "1px solid rgba(168, 85, 247, 0.3)",
                    borderRadius: "8px",
                    color: "#fff",
                  }}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        ) : (
          <div className="flex items-center justify-center">
            <div className="text-center">
              <p className="text-purple-300 text-sm">Portfolio chart will appear here</p>
            </div>
          </div>
        )}
      </div>
    </motion.div>
  )
}

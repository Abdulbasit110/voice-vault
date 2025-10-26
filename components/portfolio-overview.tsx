"use client"

import { motion } from "framer-motion"
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip } from "recharts"
import { TrendingUp } from "lucide-react"

const portfolioData = [
  { name: "USDC", value: 11070.19, percentage: 60 },
  { name: "ETH", value: 4612.58, percentage: 25 },
  { name: "BTC", value: 2767.55, percentage: 15 },
]

const COLORS = ["#3b82f6", "#a855f7", "#ec4899"]

export function PortfolioOverview() {
  const totalValue = 18450.32
  const change24h = 2.45

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
            <div className="flex items-center gap-2 mt-2">
              <TrendingUp className="w-5 h-5 text-green-400" />
              <span className="text-green-400 font-semibold">+{change24h}% (24h)</span>
            </div>
          </div>

          {/* Asset Breakdown */}
          <div className="space-y-3">
            {portfolioData.map((asset, index) => (
              <div key={index} className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full" style={{ backgroundColor: COLORS[index] }} />
                  <span className="text-purple-200 text-sm">{asset.name}</span>
                </div>
                <div className="text-right">
                  <p className="text-white font-semibold text-sm">
                    ${asset.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                  </p>
                  <p className="text-purple-400 text-xs">{asset.percentage}%</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Right - Donut Chart */}
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
                  <Cell key={`cell-${index}`} fill={COLORS[index]} />
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
      </div>
    </motion.div>
  )
}

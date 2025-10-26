"use client"

import { motion } from "framer-motion"
import { AlertCircle } from "lucide-react"

export function RiskAnalysis() {
  const riskScore = 35
  const riskLevel = "Low"
  const riskColor = "text-green-400"
  const riskBgColor = "from-green-500/20 to-green-600/20"

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.3 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <h3 className="text-lg font-bold text-white mb-4">Risk Analysis</h3>

      {/* Risk Gauge */}
      <div className="flex flex-col items-center mb-6">
        <div className="relative w-32 h-32 mb-4">
          <svg className="w-full h-full" viewBox="0 0 120 120">
            {/* Background Arc */}
            <circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="rgba(168, 85, 247, 0.2)"
              strokeWidth="8"
              strokeDasharray="157 314"
              transform="rotate(-90 60 60)"
            />
            {/* Progress Arc */}
            <motion.circle
              cx="60"
              cy="60"
              r="50"
              fill="none"
              stroke="url(#riskGradient)"
              strokeWidth="8"
              strokeDasharray={`${(riskScore / 100) * 157} 314`}
              transform="rotate(-90 60 60)"
              initial={{ strokeDasharray: "0 314" }}
              animate={{ strokeDasharray: `${(riskScore / 100) * 157} 314` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
            <defs>
              <linearGradient id="riskGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stopColor="#10b981" />
                <stop offset="100%" stopColor="#059669" />
              </linearGradient>
            </defs>
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <p className="text-3xl font-bold text-white">{riskScore}</p>
            <p className="text-xs text-purple-300">Score</p>
          </div>
        </div>

        <p className={`text-lg font-bold ${riskColor}`}>{riskLevel} Risk</p>
        <p className="text-purple-300 text-sm text-center mt-2">Your portfolio has low volatility</p>
      </div>

      {/* Risk Factors */}
      <div className="space-y-3">
        <div className="flex items-start gap-3 p-3 rounded-lg bg-purple-500/10 border border-purple-500/20">
          <AlertCircle className="w-4 h-4 text-purple-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-purple-200 font-semibold">Diversification</p>
            <p className="text-xs text-purple-400">Good spread across assets</p>
          </div>
        </div>
        <div className="flex items-start gap-3 p-3 rounded-lg bg-green-500/10 border border-green-500/20">
          <AlertCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="text-sm text-green-200 font-semibold">Stability</p>
            <p className="text-xs text-green-400">Stable stablecoin holdings</p>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

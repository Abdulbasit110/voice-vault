"use client"

import { motion } from "framer-motion"
import { Lightbulb, ArrowRight } from "lucide-react"

const insights = [
  {
    title: "Rebalance Opportunity",
    description: "Consider increasing BTC allocation",
    icon: "📊",
  },
  {
    title: "Market Alert",
    description: "ETH showing bullish signals",
    icon: "📈",
  },
  {
    title: "Tax Optimization",
    description: "Review your tax-loss harvesting",
    icon: "💰",
  },
]

export function AIInsights() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.4 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-yellow-400" />
        <h3 className="text-lg font-bold text-white">AI Insights</h3>
      </div>

      <div className="space-y-3">
        {insights.map((insight, index) => (
          <motion.div
            key={index}
            whileHover={{ x: 4 }}
            className="p-3 rounded-lg bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/20 hover:border-blue-400/50 transition-all cursor-pointer group"
          >
            <div className="flex items-start justify-between gap-2">
              <div className="flex-1">
                <p className="text-sm font-semibold text-white group-hover:text-blue-300 transition-colors">
                  {insight.title}
                </p>
                <p className="text-xs text-purple-300 mt-1">{insight.description}</p>
              </div>
              <ArrowRight className="w-4 h-4 text-purple-400 group-hover:text-blue-400 transition-colors flex-shrink-0 mt-0.5" />
            </div>
          </motion.div>
        ))}
      </div>

      <motion.button
        whileHover={{ scale: 1.02 }}
        whileTap={{ scale: 0.98 }}
        className="w-full mt-4 py-2 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white text-sm font-semibold hover:shadow-lg hover:shadow-blue-500/50 transition-all"
      >
        View All Insights
      </motion.button>
    </motion.div>
  )
}

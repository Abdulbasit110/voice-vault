"use client"

import { motion } from "framer-motion"
import { ArrowUpRight, ArrowDownLeft, Send } from "lucide-react"

const transactions = [
  {
    id: 1,
    type: "buy",
    asset: "ETH",
    amount: 0.5,
    value: 1072.61,
    date: "2024-10-24",
    time: "14:32",
    status: "completed",
  },
  {
    id: 2,
    type: "sell",
    asset: "BTC",
    amount: 0.01,
    value: 326.54,
    date: "2024-10-23",
    time: "09:15",
    status: "completed",
  },
  {
    id: 3,
    type: "transfer",
    asset: "USDC",
    amount: 5000,
    value: 5000,
    date: "2024-10-22",
    time: "16:45",
    status: "completed",
  },
  {
    id: 4,
    type: "buy",
    asset: "ETH",
    amount: 1.0,
    value: 2145.21,
    date: "2024-10-21",
    time: "11:20",
    status: "completed",
  },
]

export function TransactionHistory() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <h3 className="text-xl font-bold text-white mb-4">Transaction History</h3>

      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-purple-500/20">
              <th className="text-left py-3 px-4 text-purple-300 font-semibold text-sm">Type</th>
              <th className="text-left py-3 px-4 text-purple-300 font-semibold text-sm">Asset</th>
              <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">Amount</th>
              <th className="text-right py-3 px-4 text-purple-300 font-semibold text-sm">Value</th>
              <th className="text-left py-3 px-4 text-purple-300 font-semibold text-sm">Date & Time</th>
              <th className="text-center py-3 px-4 text-purple-300 font-semibold text-sm">Status</th>
            </tr>
          </thead>
          <tbody>
            {transactions.map((tx, index) => (
              <motion.tr
                key={tx.id}
                whileHover={{ backgroundColor: "rgba(168, 85, 247, 0.1)" }}
                className="border-b border-purple-500/10 transition-colors"
              >
                <td className="py-4 px-4">
                  <div className="flex items-center gap-2">
                    {tx.type === "buy" ? (
                      <div className="p-2 rounded-lg bg-green-500/20">
                        <ArrowDownLeft className="w-4 h-4 text-green-400" />
                      </div>
                    ) : tx.type === "sell" ? (
                      <div className="p-2 rounded-lg bg-red-500/20">
                        <ArrowUpRight className="w-4 h-4 text-red-400" />
                      </div>
                    ) : (
                      <div className="p-2 rounded-lg bg-blue-500/20">
                        <Send className="w-4 h-4 text-blue-400" />
                      </div>
                    )}
                    <span className="text-white font-semibold capitalize">{tx.type}</span>
                  </div>
                </td>
                <td className="py-4 px-4 text-white font-semibold">{tx.asset}</td>
                <td className="py-4 px-4 text-right text-white">
                  {tx.amount.toLocaleString("en-US", {
                    minimumFractionDigits: 2,
                  })}
                </td>
                <td className="py-4 px-4 text-right text-white font-semibold">
                  ${tx.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td className="py-4 px-4 text-purple-300 text-sm">
                  <div>
                    <p>{tx.date}</p>
                    <p className="text-xs text-purple-400">{tx.time}</p>
                  </div>
                </td>
                <td className="py-4 px-4 text-center">
                  <span className="inline-block px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-semibold">
                    {tx.status}
                  </span>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

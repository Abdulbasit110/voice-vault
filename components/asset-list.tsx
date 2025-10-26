"use client"

import { motion } from "framer-motion"
import { TrendingUp, TrendingDown } from "lucide-react"

const assets = [
  {
    symbol: "BTC",
    name: "Bitcoin",
    amount: 0.0847,
    value: 2767.55,
    price: 32654.23,
    change: 5.23,
  },
  {
    symbol: "ETH",
    name: "Ethereum",
    amount: 2.15,
    value: 4612.58,
    price: 2145.21,
    change: 3.12,
  },
  {
    symbol: "USDC",
    name: "USD Coin",
    amount: 11070.19,
    value: 11070.19,
    price: 1.0,
    change: 0.0,
  },
]

export function AssetList() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.2 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <h3 className="text-xl font-bold text-white mb-4">Your Assets</h3>

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
                key={index}
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
                    minimumFractionDigits: 4,
                  })}
                </td>
                <td className="py-4 px-4 text-right text-white">
                  ${asset.price.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td className="py-4 px-4 text-right text-white font-semibold">
                  ${asset.value.toLocaleString("en-US", { minimumFractionDigits: 2 })}
                </td>
                <td className="py-4 px-4 text-right">
                  <div className="flex items-center justify-end gap-1">
                    {asset.change >= 0 ? (
                      <>
                        <TrendingUp className="w-4 h-4 text-green-400" />
                        <span className="text-green-400 font-semibold">+{asset.change}%</span>
                      </>
                    ) : (
                      <>
                        <TrendingDown className="w-4 h-4 text-red-400" />
                        <span className="text-red-400 font-semibold">{asset.change}%</span>
                      </>
                    )}
                  </div>
                </td>
              </motion.tr>
            ))}
          </tbody>
        </table>
      </div>
    </motion.div>
  )
}

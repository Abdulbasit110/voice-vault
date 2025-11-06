"use client"

import { useState, useEffect } from "react"
import { motion } from "framer-motion"
import { ArrowUpRight, ArrowDownLeft, Send, Loader2, Inbox } from "lucide-react"

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface Transaction {
  id: string
  type: string
  asset: string
  amount: number
  value: number
  date: string
  time: string
  status: string
}

interface CircleTransaction {
  id: string
  operation: string
  amounts: string[]
  tokenId?: string
  state: string
  createDate: string
  destinationAddress?: string
  sourceAddress?: string
  transactionType?: string
  blockchain?: string
}

function formatDate(dateString: string): { date: string; time: string } {
  const date = new Date(dateString)
  const dateStr = date.toLocaleDateString('en-US', { year: 'numeric', month: '2-digit', day: '2-digit' })
  const timeStr = date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit', hour12: false })
  return { date: dateStr, time: timeStr }
}

function mapCircleTransaction(circleTx: CircleTransaction): Transaction {
  // Determine transaction type from operation
  let type = 'transfer'
  if (circleTx.operation === 'TRANSFER') {
    type = circleTx.transactionType === 'INBOUND' ? 'receive' : 'transfer'
  }
  
  // Get amount (USDC has 6 decimals, so divide by 1,000,000)
  const amount = circleTx.amounts && circleTx.amounts.length > 0 
    ? parseFloat(circleTx.amounts[0]) / 1_000_000 
    : 0
  
  // Format date
  const { date, time } = formatDate(circleTx.createDate)
  
  // Map state to status
  const statusMap: Record<string, string> = {
    'COMPLETED': 'completed',
    'PENDING': 'pending',
    'FAILED': 'failed',
    'CANCELLED': 'cancelled'
  }
  const status = statusMap[circleTx.state] || circleTx.state.toLowerCase()
  
  return {
    id: circleTx.id,
    type,
    asset: 'USDC', // Default to USDC for now
    amount,
    value: amount, // USDC 1:1 with USD
    date,
    time,
    status
  }
}

export function TransactionHistory() {
  const [transactions, setTransactions] = useState<Transaction[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchTransactions = async () => {
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
          `${API_URL}/api/wallet/transactions?user_id=${userId}&page_size=50`
        )
        
        if (!response.ok) {
          throw new Error('Failed to fetch transactions')
        }
        
        const data = await response.json()
        const mappedTransactions = (data.transactions || []).map(mapCircleTransaction)
        setTransactions(mappedTransactions)
      } catch (err) {
        console.error('Error fetching transactions:', err)
        setError(err instanceof Error ? err.message : 'Failed to load transactions')
      } finally {
        setLoading(false)
      }
    }
    
    fetchTransactions()
  }, [])
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return 'bg-green-500/20 text-green-400'
      case 'pending':
        return 'bg-yellow-500/20 text-yellow-400'
      case 'failed':
        return 'bg-red-500/20 text-red-400'
      case 'cancelled':
        return 'bg-gray-500/20 text-gray-400'
      default:
        return 'bg-purple-500/20 text-purple-400'
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, delay: 0.5 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-6"
    >
      <h3 className="text-xl font-bold text-white mb-4">Transaction History</h3>

      {loading ? (
        <div className="flex items-center justify-center py-12">
          <Loader2 className="w-6 h-6 text-purple-400 animate-spin" />
          <span className="ml-3 text-purple-300">Loading transactions...</span>
        </div>
      ) : error ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="p-3 rounded-lg bg-red-500/20 mb-3">
            <Inbox className="w-6 h-6 text-red-400" />
          </div>
          <p className="text-red-300 text-sm">{error}</p>
        </div>
      ) : transactions.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-12">
          <div className="p-4 rounded-full bg-purple-500/20 mb-4">
            <Inbox className="w-8 h-8 text-purple-400" />
          </div>
          <h4 className="text-lg font-semibold text-white mb-2">No Transactions Yet</h4>
          <p className="text-purple-300 text-sm text-center max-w-md">
            Your transaction history will appear here once you start making transfers or trades.
          </p>
        </div>
      ) : (
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
              {transactions.map((tx) => (
                <motion.tr
                  key={tx.id}
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  whileHover={{ backgroundColor: "rgba(168, 85, 247, 0.1)" }}
                  className="border-b border-purple-500/10 transition-colors"
                >
                  <td className="py-4 px-4">
                    <div className="flex items-center gap-2">
                      {tx.type === "receive" ? (
                        <div className="p-2 rounded-lg bg-green-500/20">
                          <ArrowDownLeft className="w-4 h-4 text-green-400" />
                        </div>
                      ) : tx.type === "transfer" ? (
                        <div className="p-2 rounded-lg bg-blue-500/20">
                          <Send className="w-4 h-4 text-blue-400" />
                        </div>
                      ) : (
                        <div className="p-2 rounded-lg bg-purple-500/20">
                          <ArrowUpRight className="w-4 h-4 text-purple-400" />
                        </div>
                      )}
                      <span className="text-white font-semibold capitalize">{tx.type}</span>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-white font-semibold">{tx.asset}</td>
                  <td className="py-4 px-4 text-right text-white">
                    {tx.amount.toLocaleString("en-US", {
                      minimumFractionDigits: 2,
                      maximumFractionDigits: 6,
                    })}
                  </td>
                  <td className="py-4 px-4 text-right text-white font-semibold">
                    ${tx.value.toLocaleString("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </td>
                  <td className="py-4 px-4 text-purple-300 text-sm">
                    <div>
                      <p>{tx.date}</p>
                      <p className="text-xs text-purple-400">{tx.time}</p>
                    </div>
                  </td>
                  <td className="py-4 px-4 text-center">
                    <span className={`inline-block px-3 py-1 rounded-full text-xs font-semibold ${getStatusColor(tx.status)}`}>
                      {tx.status}
                    </span>
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

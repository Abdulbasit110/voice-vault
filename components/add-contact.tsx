"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { X } from "lucide-react"

interface AddContactProps {
  onClose: () => void
  onSuccess?: () => void
}

export function AddContact({ onClose, onSuccess }: AddContactProps) {
  const [walletAddress, setWalletAddress] = useState("")
  const [name, setName] = useState("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)

    // Get user_id from localStorage
    const userId = localStorage.getItem("voicevault_user_id")
    if (!userId) {
      setError("User ID not found. Please set up your wallet first.")
      return
    }

    // Validate inputs
    if (!walletAddress.trim()) {
      setError("Wallet address is required")
      return
    }

    if (!name.trim()) {
      setError("Name is required")
      return
    }

    // Validate wallet address format
    if (!/^0x[a-fA-F0-9]{40}$/.test(walletAddress.trim())) {
      setError("Invalid wallet address format. Must be a valid Ethereum address (0x followed by 40 hex characters)")
      return
    }

    try {
      setLoading(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://139.59.152.104:8000"

      const response = await fetch(`${apiUrl}/api/contacts/add?user_id=${userId}`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          wallet_address: walletAddress.trim(),
          name: name.trim(),
        }),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.detail || "Failed to add contact")
      }

      // Success
      setWalletAddress("")
      setName("")
      if (onSuccess) {
        onSuccess()
      }
      onClose()
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to add contact")
    } finally {
      setLoading(false)
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.95 }}
      className="bg-gradient-to-br from-slate-800 to-slate-900 rounded-2xl border border-purple-500/30 p-6 w-full max-w-md"
    >
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-2xl font-bold text-white">Add Contact</h2>
        <button
          onClick={onClose}
          className="text-purple-300 hover:text-white transition-colors"
        >
          <X className="w-6 h-6" />
        </button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-purple-200 mb-2">
            Contact Name
          </label>
          <input
            type="text"
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Enter contact name"
            className="w-full px-4 py-3 rounded-lg bg-slate-700/50 border border-purple-500/30 text-white placeholder-purple-400 focus:outline-none focus:border-blue-400 transition-colors"
            required
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-purple-200 mb-2">
            Wallet Address
          </label>
          <input
            type="text"
            value={walletAddress}
            onChange={(e) => setWalletAddress(e.target.value)}
            placeholder="0x..."
            className="w-full px-4 py-3 rounded-lg bg-slate-700/50 border border-purple-500/30 text-white placeholder-purple-400 focus:outline-none focus:border-blue-400 transition-colors font-mono text-sm"
            required
          />
        </div>

        {error && (
          <div className="p-3 rounded-lg bg-red-500/20 border border-red-500/30 text-red-300 text-sm">
            {error}
          </div>
        )}

        <div className="flex gap-3 pt-2">
          <motion.button
            type="button"
            onClick={onClose}
            whileHover={{ scale: 1.02 }}
            whileTap={{ scale: 0.98 }}
            className="flex-1 px-4 py-3 rounded-lg bg-slate-700/50 text-purple-200 hover:bg-slate-700 transition-colors"
          >
            Cancel
          </motion.button>
          <motion.button
            type="submit"
            disabled={loading}
            whileHover={{ scale: loading ? 1 : 1.02 }}
            whileTap={{ scale: loading ? 1 : 0.98 }}
            className="flex-1 px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/50 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? "Adding..." : "Add Contact"}
          </motion.button>
        </div>
      </form>
    </motion.div>
  )
}


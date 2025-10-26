"use client"

import { Menu, Bell, User } from "lucide-react"
import { motion } from "framer-motion"

interface HeaderProps {
  onMenuClick: () => void
}

export function Header({ onMenuClick }: HeaderProps) {
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
    </header>
  )
}

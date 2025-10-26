"use client"

import { motion } from "framer-motion"
import { BarChart3, Wallet, Settings, LogOut, Home } from "lucide-react"

interface SidebarProps {
  open: boolean
  onToggle: (open: boolean) => void
}

export function Sidebar({ open, onToggle }: SidebarProps) {
  const menuItems = [
    { icon: Home, label: "Dashboard", active: true },
    { icon: Wallet, label: "Portfolio", active: false },
    { icon: BarChart3, label: "Analytics", active: false },
    { icon: Settings, label: "Settings", active: false },
  ]

  return (
    <>
      {/* Desktop Sidebar */}
      <motion.aside
        initial={{ x: -280 }}
        animate={{ x: open ? 0 : -280 }}
        transition={{ duration: 0.3 }}
        className="hidden md:flex w-72 bg-gradient-to-b from-slate-900 to-slate-950 border-r border-purple-500/20 flex-col"
      >
        {/* Logo */}
        <div className="p-6 border-b border-purple-500/20">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-blue-400 to-purple-600 flex items-center justify-center">
              <Wallet className="w-6 h-6 text-white" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-white">VoiceVault</h1>
              <p className="text-xs text-purple-300">Crypto Portfolio</p>
            </div>
          </div>
        </div>

        {/* Menu Items */}
        <nav className="flex-1 p-4 space-y-2">
          {menuItems.map((item, index) => (
            <motion.button
              key={index}
              whileHover={{ x: 4 }}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                item.active
                  ? "bg-gradient-to-r from-blue-500 to-purple-600 text-white"
                  : "text-purple-200 hover:bg-purple-500/10"
              }`}
            >
              <item.icon className="w-5 h-5" />
              <span className="font-medium">{item.label}</span>
            </motion.button>
          ))}
        </nav>

        {/* Footer */}
        <div className="p-4 border-t border-purple-500/20 space-y-2">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-purple-200 hover:bg-purple-500/10 transition-all">
            <LogOut className="w-5 h-5" />
            <span className="font-medium">Logout</span>
          </button>
        </div>
      </motion.aside>

      {/* Mobile Overlay */}
      {open && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={() => onToggle(false)}
          className="md:hidden fixed inset-0 bg-black/50 z-40"
        />
      )}
    </>
  )
}

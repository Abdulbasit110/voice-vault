"use client"

import { useState } from "react"
import { motion } from "framer-motion"
import { Mic, MicOff, Send } from "lucide-react"

export function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")

  const handleMicClick = () => {
    setIsListening(!isListening)
  }

  const handleSend = () => {
    if (transcript.trim()) {
      console.log("Sending:", transcript)
      setTranscript("")
    }
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5 }}
      className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-8"
    >
      {/* Animated Background */}
      <div className="absolute inset-0 overflow-hidden">
        <motion.div
          animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.5, 0.3] }}
          transition={{ duration: 4, repeat: Number.POSITIVE_INFINITY }}
          className="absolute -top-1/2 -right-1/2 w-96 h-96 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full blur-3xl"
        />
      </div>

      {/* Content */}
      <div className="relative z-10">
        <div className="flex flex-col items-center gap-6">
          {/* Microphone Button - Hero Element */}
          <motion.button
            onClick={handleMicClick}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            animate={isListening ? { scale: [1, 1.05, 1] } : {}}
            transition={isListening ? { duration: 0.6, repeat: Number.POSITIVE_INFINITY } : {}}
            className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
              isListening
                ? "bg-gradient-to-br from-blue-400 to-blue-600 shadow-lg shadow-blue-500/50"
                : "bg-gradient-to-br from-purple-500 to-purple-700 hover:shadow-lg hover:shadow-purple-500/50"
            }`}
          >
            {/* Ripple Effect */}
            {isListening && (
              <>
                <motion.div
                  animate={{ scale: [1, 1.5], opacity: [1, 0] }}
                  transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY }}
                  className="absolute inset-0 rounded-full border-2 border-blue-400"
                />
                <motion.div
                  animate={{ scale: [1, 1.8], opacity: [1, 0] }}
                  transition={{ duration: 1.5, repeat: Number.POSITIVE_INFINITY, delay: 0.3 }}
                  className="absolute inset-0 rounded-full border-2 border-blue-300"
                />
              </>
            )}

            {isListening ? (
              <MicOff className="w-10 h-10 text-white relative z-10" />
            ) : (
              <Mic className="w-10 h-10 text-white relative z-10" />
            )}
          </motion.button>

          {/* Status Text */}
          <div className="text-center">
            <h3 className="text-2xl font-bold text-white mb-2">{isListening ? "Listening..." : "Voice Assistant"}</h3>
            <p className="text-purple-300 text-sm">
              {isListening ? "Speak your command or question" : "Click the microphone to start"}
            </p>
          </div>

          {/* Waveform Visualization */}
          {isListening && (
            <div className="flex items-center gap-1 h-12">
              {[...Array(5)].map((_, i) => (
                <motion.div
                  key={i}
                  animate={{ height: ["20px", "40px", "20px"] }}
                  transition={{
                    duration: 0.6,
                    repeat: Number.POSITIVE_INFINITY,
                    delay: i * 0.1,
                  }}
                  className="w-1 bg-gradient-to-t from-blue-400 to-blue-600 rounded-full"
                />
              ))}
            </div>
          )}

          {/* Input Area */}
          <div className="w-full max-w-md flex gap-2">
            <input
              type="text"
              value={transcript}
              onChange={(e) => setTranscript(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleSend()}
              placeholder="Or type your command..."
              className="flex-1 px-4 py-3 rounded-lg bg-slate-700/50 border border-purple-500/30 text-white placeholder-purple-400 focus:outline-none focus:border-blue-400 transition-colors"
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSend}
              className="px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/50 transition-all"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </div>
      </div>
    </motion.div>
  )
}

"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Mic, MicOff, Send } from "lucide-react"
import * as Dialog from "@radix-ui/react-dialog"
import { TransactionConfirm } from "@/components/transaction-confirm"

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

export function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [showTransactionConfirm, setShowTransactionConfirm] = useState(false)
  const [transactionData, setTransactionData] = useState<any>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)

  // Check for MediaRecorder support on mount
  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("MediaRecorder not supported in this browser")
    }
  }, [])

  // Speech-to-Text function using ElevenLabs
  const convertAudioToText = async (audioBlob: Blob): Promise<string> => {
    try {
      setIsProcessing(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      // Convert blob to base64
      const reader = new FileReader()
      const base64Audio = await new Promise<string>((resolve, reject) => {
        reader.onloadend = () => {
          const base64String = reader.result as string
          // Remove data:audio/wav;base64, prefix
          const base64Data = base64String.split(",")[1]
          resolve(base64Data)
        }
        reader.onerror = reject
        reader.readAsDataURL(audioBlob)
      })

      // Call ElevenLabs STT API
      const response = await fetch(`${apiUrl}/api/elevenlabs/stt`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ audio: base64Audio }),
      })

      if (!response.ok) {
        throw new Error(`STT API error: ${response.statusText}`)
      }

      const data = await response.json()
      return data.text || ""
    } catch (error) {
      console.error("Error converting audio to text:", error)
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  // Text-to-Speech function
  const speakText = async (text: string) => {
    if (!text.trim()) return

    try {
      setIsPlaying(true)
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

      const response = await fetch(`${apiUrl}/api/elevenlabs/tts`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ text }),
      })

      if (!response.ok) {
        throw new Error(`TTS API error: ${response.statusText}`)
      }

      // Get audio blob
      const audioBlob = await response.blob()
      const audioUrl = URL.createObjectURL(audioBlob)

      // Create audio element and play
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }

      const audio = new Audio(audioUrl)
      audioRef.current = audio

      audio.onended = () => {
        setIsPlaying(false)
        URL.revokeObjectURL(audioUrl)
      }

      audio.onerror = () => {
        setIsPlaying(false)
        URL.revokeObjectURL(audioUrl)
        console.error("Error playing audio")
      }

      await audio.play()
    } catch (error) {
      console.error("Error with TTS:", error)
      setIsPlaying(false)
    }
  }

  const handleMicClick = async () => {
    try {
      if (isListening) {
        // Stop recording
        if (mediaRecorderRef.current && mediaRecorderRef.current.state !== "inactive") {
          mediaRecorderRef.current.stop()
        }
        setIsListening(false)
      } else {
        // Start recording
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
        const mediaRecorder = new MediaRecorder(stream)
        mediaRecorderRef.current = mediaRecorder
        audioChunksRef.current = []

        mediaRecorder.ondataavailable = (event) => {
          if (event.data.size > 0) {
            audioChunksRef.current.push(event.data)
          }
        }

        mediaRecorder.onstop = async () => {
          // Stop all tracks
          stream.getTracks().forEach((track) => track.stop())

          // Create audio blob
          const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" })

          try {
            // Convert to text using ElevenLabs STT
            const text = await convertAudioToText(audioBlob)
            setTranscript((prev) => prev + (prev ? " " : "") + text)
          } catch (error) {
            console.error("Failed to convert audio to text:", error)
            alert("Failed to convert speech to text. Please try again.")
          }
        }

        mediaRecorder.start()
        setIsListening(true)
      }
    } catch (error) {
      console.error("Error accessing microphone:", error)
      alert("Failed to access microphone. Please check permissions.")
      setIsListening(false)
    }
  }

  const handleSend = async () => {
    if (transcript.trim()) {
      console.log("Sending:", transcript)
      const textToSend = transcript
      setTranscript("")
      if (isListening) {
        setIsListening(false)
        if (mediaRecorderRef.current) {
          mediaRecorderRef.current.stop()
        }
      }

      setIsProcessing(true)
      
      try {
        // Get user_id from localStorage
        const userId = localStorage.getItem(STORAGE_KEY)
        
        // Call agent endpoint
        const response = await fetch(
          `${API_URL}/api/agents/execute${userId ? `?user_id=${userId}` : ''}`,
          {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ text: textToSend }),
          }
        )

        if (!response.ok) {
          throw new Error(`Agent API error: ${response.statusText}`)
        }

        const result = await response.json()
        console.log("Agent result:", result)

        // Check if transaction requires confirmation
        if (result.requires_confirmation && result.challenge_id) {
          setTransactionData({
            challengeId: result.challenge_id,
            appId: result.app_id,
            userToken: result.user_token,
            encryptionKey: result.encryption_key,
            transactionDetails: result.echo_intent || {}
          })
          setShowTransactionConfirm(true)
          
          // Speak confirmation message
          await speakText(result.message || "Please confirm the transaction with your PIN.")
        } else {
          // No confirmation needed, just speak the response
          const responseText = result.message || result.status || "Transaction processed."
          await speakText(responseText)
        }
      } catch (error) {
        console.error("Error calling agent:", error)
        await speakText("Sorry, I encountered an error processing your request.")
      } finally {
        setIsProcessing(false)
      }
    }
  }

  const handleTransactionComplete = () => {
    setShowTransactionConfirm(false)
    setTransactionData(null)
    // Trigger dashboard refresh by reloading page or emitting event
    window.location.reload()
  }

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      if (mediaRecorderRef.current) {
        mediaRecorderRef.current.stop()
      }
      if (audioRef.current) {
        audioRef.current.pause()
        audioRef.current = null
      }
    }
  }, [])

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
            disabled={isProcessing}
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.95 }}
            animate={isListening ? { scale: [1, 1.05, 1] } : {}}
            transition={isListening ? { duration: 0.6, repeat: Number.POSITIVE_INFINITY } : {}}
            className={`relative w-24 h-24 rounded-full flex items-center justify-center transition-all ${
              isListening
                ? "bg-gradient-to-br from-blue-400 to-blue-600 shadow-lg shadow-blue-500/50"
                : "bg-gradient-to-br from-purple-500 to-purple-700 hover:shadow-lg hover:shadow-purple-500/50"
            } ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
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
            <h3 className="text-2xl font-bold text-white mb-2">
              {isListening
                ? "Recording..."
                : isProcessing
                ? "Processing..."
                : isPlaying
                ? "Speaking..."
                : "Voice Assistant"}
            </h3>
            <p className="text-purple-300 text-sm">
              {isListening
                ? "Click mic again to stop and convert to text"
                : isProcessing
                ? "Converting speech to text..."
                : isPlaying
                ? "Playing audio response"
                : "Click the microphone to start recording"}
            </p>
          </div>

          {/* Waveform Visualization */}
          {(isListening || isProcessing) && (
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

      {/* Transaction Confirmation Modal */}
      <Dialog.Root open={showTransactionConfirm} onOpenChange={setShowTransactionConfirm}>
        <Dialog.Portal>
          <Dialog.Overlay className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50" />
          <Dialog.Content className="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 z-50 w-full max-w-lg p-6">
            {transactionData && (
              <TransactionConfirm
                challengeId={transactionData.challengeId}
                appId={transactionData.appId}
                userToken={transactionData.userToken}
                encryptionKey={transactionData.encryptionKey}
                transactionDetails={transactionData.transactionDetails}
                onComplete={handleTransactionComplete}
                onClose={() => setShowTransactionConfirm(false)}
              />
            )}
          </Dialog.Content>
        </Dialog.Portal>
      </Dialog.Root>
    </motion.div>
  )
}

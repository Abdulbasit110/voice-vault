"use client"

import { useState, useEffect, useRef } from "react"
import { motion } from "framer-motion"
import { Mic, MicOff, Send } from "lucide-react"
import { W3SSdk } from '@circle-fin/w3s-pw-web-sdk'

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

interface Contact {
  id: string
  wallet_address: string
  name: string
}

export function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState("")
  const [isProcessing, setIsProcessing] = useState(false)
  const [isPlaying, setIsPlaying] = useState(false)
  const [availableContacts, setAvailableContacts] = useState<Contact[]>([])
  const [showContactSelect, setShowContactSelect] = useState(false)
  const [pendingEnhancedQuery, setPendingEnhancedQuery] = useState<string>("")
  const [mentionQuery, setMentionQuery] = useState<string>("")
  const [mentionContacts, setMentionContacts] = useState<Contact[]>([])
  const [showMentionDropdown, setShowMentionDropdown] = useState(false)
  const [selectedMentionIndex, setSelectedMentionIndex] = useState(0)
  const [mentionStartIndex, setMentionStartIndex] = useState(-1)
  const inputRef = useRef<HTMLInputElement>(null)
  const mediaRecorderRef = useRef<MediaRecorder | null>(null)
  const audioChunksRef = useRef<Blob[]>([])
  const audioRef = useRef<HTMLAudioElement | null>(null)
  const circleSdkRef = useRef<W3SSdk | null>(null)

  // Initialize Circle SDK on mount
  useEffect(() => {
    if (!circleSdkRef.current) {
      try {
        circleSdkRef.current = new W3SSdk()
        console.log("Circle SDK initialized")
      } catch (error) {
        console.error("Failed to initialize Circle SDK:", error)
      }
    }
  }, [])

  // Check for MediaRecorder support on mount
  useEffect(() => {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("MediaRecorder not supported in this browser")
    }
  }, [])

  // Speech-to-Text function using ElevenLabs
  const convertAudioToText = async (audioBlob: Blob): Promise<{text: string, extractedName?: string}> => {
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
      const sttResponse = await fetch(`${apiUrl}/api/elevenlabs/stt`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ audio: base64Audio }),
      })

      if (!sttResponse.ok) {
        throw new Error(`STT API error: ${sttResponse.statusText}`)
      }

      const sttData = await sttResponse.json()
      const transcribedText = sttData.text || ""
      
      // If we got text, automatically enhance it
      if (transcribedText.trim()) {
        try {
          // Call enhance API automatically
          const enhanceResponse = await fetch(`${apiUrl}/api/query/enhance`, {
            method: "POST",
            headers: {
              "Content-Type": "application/json",
            },
            body: JSON.stringify({ query: transcribedText }),
          })

          if (enhanceResponse.ok) {
            const enhanceData = await enhanceResponse.json()
            console.log("Original query:", enhanceData.original_query)
            console.log("Enhanced query:", enhanceData.enhanced_query)
            console.log("Extracted name:", enhanceData.extracted_name)
            
            return {
              text: enhanceData.enhanced_query,
              extractedName: enhanceData.extracted_name || undefined
            }
          } else {
            // If enhance fails, return original text
            console.warn("Enhance API failed, using original text")
            return { text: transcribedText }
          }
        } catch (enhanceError) {
          // If enhance fails, return original text
          console.error("Error enhancing query:", enhanceError)
          return { text: transcribedText }
        }
      }
      
      return { text: transcribedText }
    } catch (error) {
      console.error("Error converting audio to text:", error)
      throw error
    } finally {
      setIsProcessing(false)
    }
  }

  // Lookup contacts by name
  const lookupContacts = async (name: string, enhancedQuery: string) => {
    try {
      const userId = localStorage.getItem(STORAGE_KEY)
      if (!userId) {
        console.warn("No user ID found, skipping contact lookup")
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/contacts?user_id=${userId}&name=${encodeURIComponent(name)}`)

      if (!response.ok) {
        console.warn("Failed to fetch contacts")
        return
      }

      const data = await response.json()
      const contacts = data.contacts || []

      if (contacts.length === 0) {
        console.log("No contacts found for name:", name)
        // No contacts found - use TTS to inform user
        const message = `Ah! There is no contact ${name} in your contact list`
        await speakText(message)
        // Still add the enhanced query to transcript
        setTranscript((prev) => {
          if (prev.includes(enhancedQuery)) {
            return prev
          }
          return prev + (prev ? " " : "") + enhancedQuery
        })
        return
      }

      if (contacts.length === 1) {
        // Auto-fill wallet address
        const contact = contacts[0]
        const walletAddress = contact.wallet_address
        // Replace name with wallet address in the query
        const updatedQuery = enhancedQuery.replace(new RegExp(`\\b${name}\\b`, 'gi'), walletAddress)
        // Update transcript with the wallet address
        setTranscript((prev) => {
          // If transcript already contains the enhanced query, replace it
          if (prev.includes(enhancedQuery)) {
            return prev.replace(enhancedQuery, updatedQuery)
          }
          // Otherwise, replace name in the current transcript or add the updated query
          const current = prev.trim()
          if (current) {
            // Try to replace name if it exists in current transcript
            const nameRegex = new RegExp(`\\b${name}\\b`, 'gi')
            if (nameRegex.test(current)) {
              return current.replace(nameRegex, walletAddress)
            }
            return `${current} ${updatedQuery}`
          }
          return updatedQuery
        })
        console.log("Auto-filled wallet address:", walletAddress)
      } else {
        // Multiple contacts found - show dropdown
        setAvailableContacts(contacts)
        setPendingEnhancedQuery(enhancedQuery)
        setShowContactSelect(true)
        console.log("Multiple contacts found, showing selection")
      }
    } catch (error) {
      console.error("Error looking up contacts:", error)
    }
  }

  // Handle contact selection
  const handleContactSelect = (contact: Contact) => {
    const walletAddress = contact.wallet_address
    // Extract name from pending query and replace with wallet address
    const nameMatch = pendingEnhancedQuery.match(/to\s+([^\s]+(?:\s+[^\s]+)*)/i)
    if (nameMatch) {
      const name = nameMatch[1].trim()
      const updatedQuery = pendingEnhancedQuery.replace(new RegExp(`\\b${name}\\b`, 'gi'), walletAddress)
      setTranscript((prev) => {
        const current = prev.trim()
        return current ? `${current} ${updatedQuery}` : updatedQuery
      })
    }
    setShowContactSelect(false)
    setAvailableContacts([])
    setPendingEnhancedQuery("")
    console.log("Selected contact:", contact.name, "Wallet:", walletAddress)
  }

  // Debounced search for contacts
  const searchContactsForMention = async (query: string) => {
    if (!query.trim()) {
      setMentionContacts([])
      setShowMentionDropdown(false)
      return
    }

    try {
      const userId = localStorage.getItem(STORAGE_KEY)
      if (!userId) {
        return
      }

      const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"
      const response = await fetch(`${apiUrl}/api/contacts?user_id=${userId}&name=${encodeURIComponent(query)}`)

      if (!response.ok) {
        return
      }

      const data = await response.json()
      const contacts = data.contacts || []
      
      setMentionContacts(contacts)
      setShowMentionDropdown(contacts.length > 0)
      setSelectedMentionIndex(0)
    } catch (error) {
      console.error("Error searching contacts:", error)
      setMentionContacts([])
      setShowMentionDropdown(false)
    }
  }

  // Debounce timer ref
  const mentionSearchTimeoutRef = useRef<NodeJS.Timeout | null>(null)

  // Handle mention selection
  const handleMentionSelect = (contact: Contact) => {
    if (mentionStartIndex === -1) return

    const beforeMention = transcript.substring(0, mentionStartIndex)
    const afterMention = transcript.substring(mentionStartIndex + 1 + mentionQuery.length)
    const newTranscript = `${beforeMention}${contact.wallet_address}${afterMention}`

    setTranscript(newTranscript)
    setShowMentionDropdown(false)
    setMentionQuery("")
    setMentionStartIndex(-1)
    setMentionContacts([])
    
    // Focus back on input
    if (inputRef.current) {
      inputRef.current.focus()
      // Set cursor position after the inserted wallet address
      const newCursorPos = mentionStartIndex + contact.wallet_address.length
      setTimeout(() => {
        if (inputRef.current) {
          inputRef.current.setSelectionRange(newCursorPos, newCursorPos)
        }
      }, 0)
    }
  }

  // Handle input change with @mention detection
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value
    setTranscript(value)

    // Find the last @ symbol and text after it
    const cursorPos = e.target.selectionStart || 0
    const textBeforeCursor = value.substring(0, cursorPos)
    const lastAtIndex = textBeforeCursor.lastIndexOf("@")
    
    // Check if @ is valid mention (at start of input or after whitespace)
    const charBeforeAt = lastAtIndex > 0 ? textBeforeCursor[lastAtIndex - 1] : " "
    const isValidMention = lastAtIndex !== -1 && (lastAtIndex === 0 || /\s/.test(charBeforeAt))

    if (isValidMention) {
      const query = textBeforeCursor.substring(lastAtIndex + 1)
      // Check if query contains space (mention ended)
      if (query.includes(" ") || query.includes("\n")) {
        setShowMentionDropdown(false)
        setMentionQuery("")
        setMentionStartIndex(-1)
      } else {
        setMentionQuery(query)
        setMentionStartIndex(lastAtIndex)
        
        // Debounce the search
        if (mentionSearchTimeoutRef.current) {
          clearTimeout(mentionSearchTimeoutRef.current)
        }
        mentionSearchTimeoutRef.current = setTimeout(() => {
          searchContactsForMention(query)
        }, 300) // 300ms debounce
      }
    } else {
      setShowMentionDropdown(false)
      setMentionQuery("")
      setMentionStartIndex(-1)
    }
  }

  // Handle keyboard navigation in mention dropdown
  const handleInputKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (showMentionDropdown && mentionContacts.length > 0) {
      if (e.key === "ArrowDown") {
        e.preventDefault()
        setSelectedMentionIndex((prev) => 
          prev < mentionContacts.length - 1 ? prev + 1 : prev
        )
      } else if (e.key === "ArrowUp") {
        e.preventDefault()
        setSelectedMentionIndex((prev) => (prev > 0 ? prev - 1 : 0))
      } else if (e.key === "Enter" && selectedMentionIndex >= 0) {
        e.preventDefault()
        handleMentionSelect(mentionContacts[selectedMentionIndex])
      } else if (e.key === "Escape") {
        e.preventDefault()
        setShowMentionDropdown(false)
        setMentionQuery("")
        setMentionStartIndex(-1)
      }
    } else if (e.key === "Enter") {
      handleSend()
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
            // Convert to text using ElevenLabs STT and enhance
            const { text, extractedName } = await convertAudioToText(audioBlob)
            
            // If a name is extracted, lookup contacts
            if (extractedName) {
              await lookupContacts(extractedName, text)
              // lookupContacts will update the transcript, so we don't need to append here
            } else {
              // No name extracted, just append the enhanced text
              setTranscript((prev) => {
                // If the text is already in the transcript, don't duplicate
                if (prev.includes(text)) {
                  return prev
                }
                return prev + (prev ? " " : "") + text
              })
            }
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
        console.log("Checking for transaction confirmation:", {
          requires_confirmation: result.requires_confirmation,
          challenge_id: result.challenge_id,
          has_app_id: !!result.app_id,
          has_user_token: !!result.user_token
        })

        // Check if transaction requires confirmation
        if (result.requires_confirmation && result.challenge_id) {
          console.log("Transaction requires confirmation - triggering Circle SDK popup")
          
          // Trigger Circle SDK popup
          if (circleSdkRef.current && result.app_id && result.user_token && result.encryption_key) {
            try {
              // Configure SDK
              circleSdkRef.current.setAppSettings({ appId: result.app_id })
              circleSdkRef.current.setAuthentication({
                userToken: result.user_token,
                encryptionKey: result.encryption_key
              })
              
              // Execute the challenge - SDK will show its own popup
              circleSdkRef.current.execute(result.challenge_id, (error, sdkResult) => {
                if (error) {
                  console.error('Transaction confirmation error:', error)
                  speakText(`Transaction failed: ${error.message || 'Confirmation failed'}`)
                } else {
                  console.log('Transaction confirmed successfully:', sdkResult)
                  speakText("Transaction confirmed successfully!")
                  // Optionally refresh the page or update UI
                  setTimeout(() => {
                    window.location.reload()
                  }, 2000)
                }
              })
            } catch (err) {
              console.error('Error executing Circle SDK:', err)
              speakText("Failed to open transaction confirmation. Please try again.")
            }
          } else {
            console.error("Circle SDK or required data not available", {
              hasSdk: !!circleSdkRef.current,
              hasAppId: !!result.app_id,
              hasUserToken: !!result.user_token,
              hasEncryptionKey: !!result.encryption_key
            })
            speakText("Transaction confirmation setup failed. Please try again.")
          }
          
          // Speak message if available
          if (result.message) {
            await speakText(result.message)
          }
        } else {
          // No confirmation needed - speak the message automatically
          if (result.message) {
            await speakText(result.message)
          } else {
            // Fallback message if no message field
            const fallbackMessage = result.status === "failed" 
              ? "Transaction failed. Please check your request and try again."
              : result.confirmed 
                ? "Transaction completed successfully."
                : "Transaction processed."
            await speakText(fallbackMessage)
          }
        }
      } catch (error) {
        console.error("Error calling agent:", error)
        // Speak error message
        await speakText("Sorry, I encountered an error processing your request. Please try again.")
      } finally {
        setIsProcessing(false)
      }
    }
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
      if (mentionSearchTimeoutRef.current) {
        clearTimeout(mentionSearchTimeoutRef.current)
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
                ? "Converting speech to text and enhancing query..."
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
          <div className="w-full max-w-md flex gap-2 relative">
            <input
              ref={inputRef}
              type="text"
              value={transcript}
              onChange={handleInputChange}
              onKeyDown={handleInputKeyDown}
              placeholder="Or type your command... (use @ to mention contacts)"
              className="flex-1 px-4 py-3 rounded-lg bg-slate-700/50 border border-purple-500/30 text-white placeholder-purple-400 focus:outline-none focus:border-blue-400 transition-colors"
            />
            
            {/* Mention Autocomplete Dropdown */}
            {showMentionDropdown && mentionContacts.length > 0 && (
              <motion.div
                initial={{ opacity: 0, y: -10 }}
                animate={{ opacity: 1, y: 0 }}
                className="absolute bottom-full left-0 mb-2 w-full bg-slate-700/95 border border-purple-500/30 rounded-lg shadow-xl backdrop-blur-xl z-50 max-h-48 overflow-y-auto"
              >
                <div className="p-2">
                  {mentionContacts.map((contact, index) => (
                    <motion.button
                      key={contact.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleMentionSelect(contact)}
                      className={`w-full text-left px-3 py-2 rounded-lg transition-all ${
                        index === selectedMentionIndex
                          ? "bg-purple-600/50 border border-purple-400"
                          : "bg-slate-600/50 hover:bg-slate-600 border border-transparent"
                      }`}
                    >
                      <div className="text-white font-medium">{contact.name}</div>
                      <div className="text-purple-300 text-xs mt-0.5 truncate">
                        {contact.wallet_address}
                      </div>
                    </motion.button>
                  ))}
                </div>
              </motion.div>
            )}
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={handleSend}
              className="px-4 py-3 rounded-lg bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:shadow-lg hover:shadow-blue-500/50 transition-all"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>

          {/* Contact Selection Dropdown */}
          {showContactSelect && availableContacts.length > 0 && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="w-full max-w-md mt-4"
            >
              <div className="bg-slate-700/90 border border-purple-500/30 rounded-lg p-4 backdrop-blur-xl">
                <p className="text-white text-sm mb-3 font-medium">
                  Multiple contacts found. Please select one:
                </p>
                <div className="space-y-2 max-h-48 overflow-y-auto">
                  {availableContacts.map((contact) => (
                    <motion.button
                      key={contact.id}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => handleContactSelect(contact)}
                      className="w-full text-left px-4 py-3 rounded-lg bg-slate-600/50 hover:bg-slate-600 border border-purple-500/20 hover:border-purple-400/50 transition-all"
                    >
                      <div className="text-white font-medium">{contact.name}</div>
                      <div className="text-purple-300 text-xs mt-1 truncate">
                        {contact.wallet_address}
                      </div>
                    </motion.button>
                  ))}
                </div>
                <button
                  onClick={() => {
                    // Add the enhanced query (with name) to transcript when cancelled
                    if (pendingEnhancedQuery) {
                      setTranscript((prev) => {
                        if (prev.includes(pendingEnhancedQuery)) {
                          return prev
                        }
                        return prev + (prev ? " " : "") + pendingEnhancedQuery
                      })
                    }
                    setShowContactSelect(false)
                    setAvailableContacts([])
                    setPendingEnhancedQuery("")
                  }}
                  className="mt-3 text-purple-300 text-sm hover:text-purple-200 transition-colors"
                >
                  Cancel
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </div>

    </motion.div>
  )
}

"use client"

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { W3SSdk } from '@circle-fin/w3s-pw-web-sdk'
import { Wallet, CheckCircle, Loader2 } from 'lucide-react'

const STORAGE_KEY = 'voicevault_user_id'
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface WalletSetupProps {
  onWalletCreated?: (walletAddress: string) => void
  onClose?: () => void
}

export function WalletSetup({ onWalletCreated, onClose }: WalletSetupProps) {
  const [loading, setLoading] = useState(false)
  const [step, setStep] = useState<'create' | 'confirm' | 'complete'>('create')
  const [walletData, setWalletData] = useState<{
    appId: string
    userToken: string
    encryptionKey: string
    challengeId: string
    userId: string
  } | null>(null)
  const [sdk, setSdk] = useState<W3SSdk | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [walletAddress, setWalletAddress] = useState<string | null>(null)

  // Initialize WebSDK
  useEffect(() => {
    const initSdk = async () => {
      try {
        const sdkInstance = new W3SSdk()
        setSdk(sdkInstance)
      } catch (err) {
        console.error('Failed to initialize Circle SDK:', err)
        setError('Failed to initialize wallet SDK')
      }
    }
    initSdk()
  }, [])

  // Helper functions for localStorage
  const getStoredUserId = useCallback(() => {
    if (typeof window === 'undefined') return null
    return localStorage.getItem(STORAGE_KEY)
  }, [])

  const saveUserId = useCallback((userId: string) => {
    if (typeof window === 'undefined') return
    localStorage.setItem(STORAGE_KEY, userId)
  }, [])

  // Step 1: Create wallet via backend
  const createWallet = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Check if user already exists
      const existingUserId = getStoredUserId()
      const url = existingUserId 
        ? `${API_URL}/api/wallet/create?user_id=${existingUserId}`
        : `${API_URL}/api/wallet/create`

      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      })
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ detail: 'Failed to create wallet' }))
        throw new Error(errorData.detail || 'Failed to create wallet')
      }
      
      const data = await response.json()
      console.log('Wallet creation response:', data)
      
      // Save user_id immediately
      saveUserId(data.user_id)
      
      // Map snake_case response to camelCase for frontend use
      const walletData = {
        appId: data.app_id,
        userToken: data.user_token,
        encryptionKey: data.encryption_key,
        challengeId: data.challenge_id,
        userId: data.user_id
      }
      
      console.log('Mapped wallet data:', walletData)
      
      // Configure SDK with received data (these are synchronous, not async)
      if (sdk) {
        try {
          console.log('Setting SDK with data:', walletData)
          sdk.setAppSettings({ appId: walletData.appId })
          sdk.setAuthentication({
            userToken: walletData.userToken,
            encryptionKey: walletData.encryptionKey
          })
          
          // Set wallet data and move to confirm step
          setWalletData(walletData)
          setStep('confirm')
        } catch (sdkErr) {
          console.error('SDK configuration error:', sdkErr)
          throw new Error('Failed to configure wallet SDK')
        }
      } else {
        throw new Error('SDK not initialized')
      }
    } catch (err) {
      console.error('Wallet creation error:', err)
      setError(err instanceof Error ? err.message : 'Failed to create wallet')
      setLoading(false)
    }
  }

  // Step 2: Confirm PIN via WebSDK
  const confirmPin = useCallback(() => {
    if (!sdk || !walletData) {
      console.error('SDK or walletData not ready', { sdk: !!sdk, walletData: !!walletData })
      return
    }

    console.log('Executing challenge:', walletData.challengeId)
    setLoading(true)
    setError(null)
    
    try {
      // Execute the challenge - SDK will show its own modal UI
      sdk.execute(walletData.challengeId, (error, result) => {
        setLoading(false)
        
        if (error) {
          console.error('PIN confirmation error:', error)
          setError(error.message || 'PIN setup failed')
          return
        }

        // Wallet created successfully!
        console.log('Challenge completed:', result)
        
        // Get wallet address after successful PIN setup
        const checkWalletStatus = async () => {
          try {
            const statusResponse = await fetch(
              `${API_URL}/api/wallet/status?user_id=${walletData.userId}`
            )
            
            if (statusResponse.ok) {
              const statusData = await statusResponse.json()
              if (statusData.exists && statusData.wallet) {
                setWalletAddress(statusData.wallet.address)
                setStep('complete')
                
                // Call callback if provided
                if (onWalletCreated) {
                  onWalletCreated(statusData.wallet.address)
                }
              } else {
                // Wallet might not be ready yet, wait a bit and retry
                setTimeout(checkWalletStatus, 2000)
              }
            }
          } catch (err) {
            console.error('Failed to get wallet status:', err)
            // Still mark as complete even if status check fails
            setStep('complete')
          }
        }
        
        checkWalletStatus()
      })
    } catch (err) {
      console.error('Confirmation error:', err)
      setError(err instanceof Error ? err.message : 'Failed to confirm PIN')
      setLoading(false)
    }
  }, [sdk, walletData, onWalletCreated, API_URL])

  // Auto-trigger PIN confirmation when SDK and walletData are ready
  useEffect(() => {
    if (step === 'confirm' && sdk && walletData) {
      // Give SDK time to initialize and render
      const timer = setTimeout(() => {
        console.log('Auto-triggering PIN confirmation')
        confirmPin()
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [step, sdk, walletData, confirmPin])

  if (step === 'complete') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-8 max-w-md mx-auto"
      >
        <div className="text-center">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ delay: 0.2, type: "spring" }}
            className="mx-auto w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-4"
          >
            <CheckCircle className="w-8 h-8 text-green-400" />
          </motion.div>
          <h3 className="text-2xl font-bold text-white mb-2">Wallet Created!</h3>
          <p className="text-purple-300 mb-4">Your Circle wallet is ready to use</p>
          {walletAddress && (
            <div className="bg-slate-800/50 rounded-lg p-4 mb-4">
              <p className="text-xs text-purple-300 mb-1">Wallet Address</p>
              <p className="text-sm text-white font-mono break-all">{walletAddress}</p>
            </div>
          )}
          {onClose && (
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              onClick={onClose}
              className="px-6 py-2 bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors"
            >
              Close
            </motion.button>
          )}
        </div>
      </motion.div>
    )
  }

  if (step === 'confirm') {
    return (
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-8 max-w-md mx-auto"
      >
        <div className="text-center mb-6">
          <Wallet className="w-12 h-12 text-purple-400 mx-auto mb-4" />
          <h3 className="text-2xl font-bold text-white mb-2">Complete Wallet Setup</h3>
          <p className="text-purple-300 mb-4">The Circle SDK will open a secure PIN entry window</p>
          {loading && (
            <div className="flex items-center justify-center gap-2 text-purple-300">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Opening PIN entry...</span>
            </div>
          )}
        </div>
        
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 mb-4"
          >
            <p className="text-sm text-red-300">{error}</p>
          </motion.div>
        )}
        
        <p className="text-xs text-purple-400/70 text-center">
          If the PIN entry window doesn't appear, check your browser's popup blocker settings.
        </p>
      </motion.div>
    )
  }

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="rounded-2xl bg-gradient-to-br from-slate-800/50 to-purple-900/50 border border-purple-500/30 backdrop-blur-xl p-8 max-w-md mx-auto"
    >
      <div className="text-center">
        <Wallet className="w-12 h-12 text-purple-400 mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-white mb-2">Create Wallet</h3>
        <p className="text-purple-300 mb-6">
          Set up your Circle wallet to start trading with voice commands
        </p>
        
        {error && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="bg-red-500/20 border border-red-500/50 rounded-lg p-3 mb-4"
          >
            <p className="text-sm text-red-300">{error}</p>
          </motion.div>
        )}
        
        <motion.button
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          onClick={createWallet}
          disabled={loading || !sdk}
          className="px-6 py-3 bg-gradient-to-r from-purple-600 to-purple-700 hover:from-purple-700 hover:to-purple-800 text-white rounded-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 mx-auto"
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>Creating...</span>
            </>
          ) : (
            <>
              <Wallet className="w-4 h-4" />
              <span>Create Wallet</span>
            </>
          )}
        </motion.button>
      </div>
    </motion.div>
  )
}


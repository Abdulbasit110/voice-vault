'use client'

import { useState, useEffect, useCallback } from 'react'
import { motion } from 'framer-motion'
import { W3SSdk } from '@circle-fin/w3s-pw-web-sdk'
import { Loader2, CheckCircle, XCircle } from 'lucide-react'

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

interface TransactionConfirmProps {
  challengeId: string
  appId: string
  userToken: string
  encryptionKey: string
  transactionDetails: {
    action: string
    asset: string
    amount: number
    destination: string
  }
  onComplete?: () => void
  onClose?: () => void
}

export function TransactionConfirm({
  challengeId,
  appId,
  userToken,
  encryptionKey,
  transactionDetails,
  onComplete,
  onClose
}: TransactionConfirmProps) {
  const [loading, setLoading] = useState(false)
  const [sdk, setSdk] = useState<W3SSdk | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState(false)

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

  // Execute challenge when SDK is ready
  const executeChallenge = useCallback(() => {
    if (!sdk || !challengeId) {
      console.error('SDK or challengeId not ready', { sdk: !!sdk, challengeId: !!challengeId })
      return
    }

    console.log('Executing transaction challenge:', challengeId)
    setLoading(true)
    setError(null)
    
    try {
      // Configure SDK
      sdk.setAppSettings({ appId })
      sdk.setAuthentication({
        userToken,
        encryptionKey
      })
      
      // Execute the challenge - SDK will show PIN entry UI
      sdk.execute(challengeId, (error, result) => {
        setLoading(false)
        
        if (error) {
          console.error('Transaction confirmation error:', error)
          setError(error.message || 'Transaction confirmation failed')
          return
        }

        // Transaction confirmed successfully!
        console.log('Challenge completed:', result)
        setSuccess(true)
        
        // Call completion callback after a short delay
        setTimeout(() => {
          if (onComplete) {
            onComplete()
          }
        }, 2000)
      })
    } catch (err) {
      console.error('Execution error:', err)
      setError(err instanceof Error ? err.message : 'Failed to confirm transaction')
      setLoading(false)
    }
  }, [sdk, challengeId, appId, userToken, encryptionKey, onComplete])

  // Auto-trigger challenge execution when SDK is ready
  useEffect(() => {
    if (sdk && challengeId && !loading && !success && !error) {
      const timer = setTimeout(() => {
        console.log('Auto-triggering transaction confirmation')
        executeChallenge()
      }, 500)
      return () => clearTimeout(timer)
    }
  }, [sdk, challengeId, loading, success, error, executeChallenge])

  return (
    <motion.div
      initial={{ opacity: 0, scale: 0.95 }}
      animate={{ opacity: 1, scale: 1 }}
      className="bg-gradient-to-br from-slate-800/95 to-purple-900/95 backdrop-blur-xl rounded-2xl border border-purple-500/30 p-6 max-w-md w-full"
    >
      <div className="text-center">
        {success ? (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="mx-auto w-16 h-16 bg-green-500/20 rounded-full flex items-center justify-center mb-4"
            >
              <CheckCircle className="w-8 h-8 text-green-400" />
            </motion.div>
            <h3 className="text-xl font-bold text-white mb-2">Transaction Confirmed!</h3>
            <p className="text-purple-300 text-sm mb-4">
              Your transaction has been successfully submitted.
            </p>
          </>
        ) : error ? (
          <>
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              className="mx-auto w-16 h-16 bg-red-500/20 rounded-full flex items-center justify-center mb-4"
            >
              <XCircle className="w-8 h-8 text-red-400" />
            </motion.div>
            <h3 className="text-xl font-bold text-white mb-2">Transaction Failed</h3>
            <p className="text-red-300 text-sm mb-4">{error}</p>
            {onClose && (
              <button
                onClick={onClose}
                className="px-4 py-2 rounded-lg bg-purple-600 text-white hover:bg-purple-700 transition-colors"
              >
                Close
              </button>
            )}
          </>
        ) : loading ? (
          <>
            <Loader2 className="w-12 h-12 text-purple-400 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Confirm Transaction</h3>
            <p className="text-purple-300 text-sm mb-4">
              Please enter your PIN in the Circle window to confirm the transaction.
            </p>
            <div className="bg-slate-700/50 rounded-lg p-4 text-left">
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-purple-300">Action:</span>
                  <span className="text-white font-semibold capitalize">{transactionDetails.action}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">Amount:</span>
                  <span className="text-white font-semibold">
                    {transactionDetails.amount} {transactionDetails.asset}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-purple-300">To:</span>
                  <span className="text-white font-mono text-xs">
                    {transactionDetails.destination.slice(0, 6)}...{transactionDetails.destination.slice(-4)}
                  </span>
                </div>
              </div>
            </div>
          </>
        ) : (
          <>
            <Loader2 className="w-12 h-12 text-purple-400 animate-spin mx-auto mb-4" />
            <h3 className="text-xl font-bold text-white mb-2">Preparing Transaction</h3>
            <p className="text-purple-300 text-sm">Initializing confirmation...</p>
          </>
        )}
      </div>
    </motion.div>
  )
}


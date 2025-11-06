import React, { useCallback, useEffect, useState } from 'react'
import { ToastContainer, toast } from 'react-toastify'
import TextField from '@mui/material/TextField'
import Button from '@mui/material/Button'
import { W3SSdk } from '@circle-fin/w3s-pw-web-sdk'

let sdk: W3SSdk

function App() {
  useEffect(() => {
    sdk = new W3SSdk({
      configs: {
        appSettings: { appId: 'someAppId' },
        authentication: {
          userToken: 'someUserToken',
          encryptionKey: 'someEncryptionKey'
        },
        socialLoginConfig: {}
      },
      socialLoginCompleteCallback: (error, result) => {
        if (error) {
          toast.error(`Social Login Error: ${error.message ?? 'Error!'}`)
          return
        }
        toast.success(`Social Login Success: ${result?.userToken}`)
      }
    })
  }, [])

  const [appId, setAppId] = useState(localStorage.getItem('appId') || 'someAppId')
  const [userToken, setUserToken] = useState(localStorage.getItem('userToken') || 'someUserToken')
  const [encryptionKey, setEncryptionKey] = useState(localStorage.getItem('encryptionKey') || 'someEncryptionKey')
  const [challengeId, setChallengeId] = useState(localStorage.getItem('challengeId') || 'someChallengeId')

  const onChangeHandler = useCallback(
    (setState, key) => (e) => {
      const value = e.target.value
      setState(value)
      localStorage.setItem(key, value)
    },
    []
  )

  const onSubmit = useCallback(() => {
    sdk.setAppSettings({ appId })
    sdk.setAuthentication({ userToken, encryptionKey })

    sdk.execute(challengeId, (error, result) => {
      if (error) {
        toast.error(`Error: ${error?.message ?? 'Error!'}`)
        return
      }
      toast.success(`Challenge: ${result?.type}, Status: ${result?.status}`)
    })
  }, [appId, userToken, encryptionKey, challengeId])

  return (
    <div className="p-4">
      <TextField
        label="App Id"
        onChange={onChangeHandler(setAppId, 'appId')}
        value={appId}
      />
      <TextField
        label="User Token"
        onChange={onChangeHandler(setUserToken, 'userToken')}
        value={userToken}
      />
      <TextField
        label="Encryption Key"
        onChange={onChangeHandler(setEncryptionKey, 'encryptionKey')}
        value={encryptionKey}
      />
      <TextField
        label="Challenge Id"
        onChange={onChangeHandler(setChallengeId, 'challengeId')}
        value={challengeId}
      />
      <Button variant="contained" color="primary" onClick={onSubmit}>
        Verify Challenge
      </Button>
      <ToastContainer />
    </div>
  )
}

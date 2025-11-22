import { useState, useEffect, useRef } from 'react'

function AvatarPanel({ currentMessage }) {
  const [isLoading, setIsLoading] = useState(false)
  const [debug, setDebug] = useState('')
  const [sessionData, setSessionData] = useState(null)
  const [lastSpokenMessage, setLastSpokenMessage] = useState(null)
  const videoRef = useRef(null)
  const peerConnectionRef = useRef(null)

  // Speak when new AI message arrives (only if different from last spoken)
  useEffect(() => {
    if (currentMessage && sessionData && currentMessage.trim() && currentMessage !== lastSpokenMessage) {
      console.log('Avatar speaking:', currentMessage.substring(0, 50) + '...')
      speakText(currentMessage)
      setLastSpokenMessage(currentMessage)
    }
  }, [currentMessage, sessionData])

  const startAvatar = async () => {
    setIsLoading(true)
    setDebug('Starting...')

    try {
      const apiKey = import.meta.env.VITE_HEYGEN_API_KEY
      
      if (!apiKey || apiKey === 'your_heygen_api_key_here') {
        throw new Error('Add your HeyGen API key to .env file')
      }

      // Step 1: Get access token
      setDebug('Getting token...')
      const tokenRes = await fetch('https://api.heygen.com/v1/streaming.create_token', {
        method: 'POST',
        headers: { 'x-api-key': apiKey }
      })
      const tokenData = await tokenRes.json()
      
      if (!tokenData.data || !tokenData.data.token) {
        throw new Error(tokenData.message || 'Failed to get token')
      }
      
      const token = tokenData.data.token
      console.log('Token received')

      // Step 2: Create streaming avatar
      setDebug('Creating avatar...')
      const sessionRes = await fetch('https://api.heygen.com/v1/streaming.new', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          quality: 'low',  // Use 'low' for faster/more reliable connection
          avatar_name: 'Katya_ProfessionalLook2_public',  // Back to Anna - confirmed working
          voice: {
            voice_id: 'e0cc82c22f414c95b1f25696c732f058'
          }
        })
      })
      const session = await sessionRes.json()
      console.log('Session response:', session)
      
      if (!session.data) {
        throw new Error(session.message || JSON.stringify(session) || 'Failed to create session')
      }
      
      const sessionId = session.data.session_id
      setSessionData({ session_id: sessionId, token })
      setDebug('Session: ' + sessionId)
      console.log('Session created successfully')
      console.log('Session data:', session.data)

      // Step 3: Setup WebRTC
      setDebug('Setting up WebRTC...')
      
      const iceServers = session.data.ice_servers2 || session.data.ice_servers || [
        { urls: 'stun:stun.l.google.com:19302' }
      ]
      
      const pc = new RTCPeerConnection({ 
        iceServers: iceServers,
        iceTransportPolicy: 'all'
      })
      peerConnectionRef.current = pc

      pc.ontrack = (event) => {
        setDebug('Video track received!')
        console.log('Track event:', event)
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0]
          videoRef.current.play().catch(e => console.log('Play error:', e))
          setDebug('Video stream connected')
        }
      }
      
      pc.onconnectionstatechange = () => {
        const state = pc.connectionState
        setDebug(`Connection: ${state}`)
        console.log('Connection state:', state)
        
        if (state === 'connected') {
          setDebug('Avatar connected!')
        } else if (state === 'failed' || state === 'disconnected') {
          setDebug('Connection failed - retrying...')
        }
      }
      
      pc.oniceconnectionstatechange = () => {
        console.log('ICE connection state:', pc.iceConnectionState)
      }

      pc.onicecandidate = async ({ candidate }) => {
        if (candidate) {
          console.log('Sending ICE candidate')
          try {
            await fetch('https://api.heygen.com/v1/streaming.ice', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${token}`
              },
              body: JSON.stringify({
                session_id: session.data.session_id,
                candidate: {
                  candidate: candidate.candidate,
                  sdpMid: candidate.sdpMid,
                  sdpMLineIndex: candidate.sdpMLineIndex
                }
              })
            })
          } catch (error) {
            console.error('ICE error:', error)
          }
        }
      }

      // Set remote description
      const remoteSdp = new RTCSessionDescription(session.data.sdp)
      await pc.setRemoteDescription(remoteSdp)
      setDebug('Remote SDP set')
      
      // Create answer
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)
      setDebug('Local SDP set')

      // Step 4: Start the session
      setDebug('Starting session...')
      const startRes = await fetch('https://api.heygen.com/v1/streaming.start', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          session_id: session.data.session_id,
          sdp: answer
        })
      })
      
      const startResult = await startRes.json()
      console.log('Start session result:', startResult)

      setDebug('Avatar started!')
      setIsLoading(false)

    } catch (error) {
      setDebug('Error: ' + error.message)
      setIsLoading(false)
      console.error('Full error:', error)
    }
  }

  const speakText = async (text) => {
    if (!sessionData) {
      console.log('No session - cannot speak')
      return
    }
    
    if (!text || !text.trim()) {
      console.log('No text to speak')
      return
    }
    
    try {
      console.log('=== SENDING TO HEYGEN ===')
      console.log('Full text to speak:', text)
      console.log('Session ID:', sessionData.session_id)
      
      setDebug('Speaking...')
      
      const payload = {
        session_id: sessionData.session_id,
        text: text,
        task_type: 'repeat'  // Use 'repeat' for exact text reading, not 'talk' which may use chat
      }
      
      console.log('Payload:', JSON.stringify(payload, null, 2))
      
      const response = await fetch('https://api.heygen.com/v1/streaming.task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionData.token}`
        },
        body: JSON.stringify(payload)
      })
      
      const result = await response.json()
      console.log('HeyGen speak response:', JSON.stringify(result, null, 2))
      
      // Check for error in response
      if (result.error) {
        console.error('HeyGen API error:', result.error)
        setDebug('HeyGen error: ' + result.error.message)
      }
      
      if (result.data) {
        setDebug('✓ Sent to avatar: ' + text.substring(0, 50) + '...')
      } else if (result.error) {
        setDebug('Error: ' + result.error.message)
        console.error('HeyGen error:', result.error)
      }
    } catch (error) {
      console.error('Speak error:', error)
      setDebug('Speak error: ' + error.message)
    }
  }

  const stopAvatar = async () => {
    if (sessionData) {
      try {
        await fetch('https://api.heygen.com/v1/streaming.stop', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${sessionData.token}`
          },
          body: JSON.stringify({ session_id: sessionData.session_id })
        })
      } catch (error) {
        console.error('Stop error:', error)
      }
    }
    
    if (peerConnectionRef.current) {
      peerConnectionRef.current.close()
      peerConnectionRef.current = null
    }
    
    setSessionData(null)
    setLastSpokenMessage(null)
    setDebug('Stopped')
  }

  return (
    <div style={{
      width: '500px',
      background: '#1F2937',
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'center',
      padding: '20px'
    }}>
      <div style={{
        width: '100%',
        maxWidth: '400px',
        aspectRatio: '3/4',
        background: '#111827',
        borderRadius: '16px',
        overflow: 'hidden',
        position: 'relative',
        boxShadow: '0 10px 40px rgba(0,0,0,0.5)'
      }}>
        <video
          ref={videoRef}
          autoPlay
          playsInline
          style={{
            width: '100%',
            height: '100%',
            objectFit: 'cover',
            display: sessionData ? 'block' : 'none'
          }}
        />
        
        {!sessionData && !isLoading && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9CA3AF',
            textAlign: 'center'
          }}>
            <div>
              <div style={{ fontSize: '48px', marginBottom: '16px' }}>🎭</div>
              <div>Click Start Avatar</div>
            </div>
          </div>
        )}
        
        {isLoading && (
          <div style={{
            position: 'absolute',
            inset: 0,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: '#9CA3AF'
          }}>
            <div>Loading...</div>
          </div>
        )}
      </div>

      <div style={{ marginTop: '24px', width: '100%', maxWidth: '400px' }}>
        {!sessionData ? (
          <button
            onClick={startAvatar}
            disabled={isLoading}
            style={{
              width: '100%',
              padding: '12px',
              background: '#6366F1',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: isLoading ? 'not-allowed' : 'pointer',
              opacity: isLoading ? 0.5 : 1
            }}
          >
            Start Avatar
          </button>
        ) : (
          <button
            onClick={stopAvatar}
            style={{
              width: '100%',
              padding: '12px',
              background: '#DC2626',
              color: 'white',
              border: 'none',
              borderRadius: '8px',
              cursor: 'pointer'
            }}
          >
            Stop Avatar
          </button>
        )}
      </div>

      {debug && (
        <div style={{
          marginTop: '16px',
          padding: '12px',
          background: '#111827',
          borderRadius: '8px',
          color: '#9CA3AF',
          fontSize: '12px',
          width: '100%',
          maxWidth: '400px',
          fontFamily: 'monospace'
        }}>
          {debug}
        </div>
      )}
    </div>
  )
}

export default AvatarPanel

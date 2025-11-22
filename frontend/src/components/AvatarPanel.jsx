import { useState, useEffect, useRef } from 'react'

function AvatarPanel({ currentMessage }) {
  const [isLoading, setIsLoading] = useState(false)
  const [debug, setDebug] = useState('')
  const [sessionData, setSessionData] = useState(null)
  const videoRef = useRef(null)
  const peerConnectionRef = useRef(null)

  // Speak when new message arrives
  useEffect(() => {
    if (currentMessage && sessionData) {
      speakText(currentMessage)
    }
  }, [currentMessage])

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
          quality: 'medium',
          avatar_name: 'Anna_public_3_20240108',
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
      
      setSessionData({ session_id: session.data.session_id, token })
      setDebug('Session: ' + session.data.session_id)
      console.log('Session created successfully')

      // Step 3: Setup WebRTC
      const pc = new RTCPeerConnection({ iceServers: session.data.ice_servers2 })
      peerConnectionRef.current = pc

      pc.ontrack = (event) => {
        if (videoRef.current && event.streams[0]) {
          videoRef.current.srcObject = event.streams[0]
        }
      }

      pc.onicecandidate = async ({ candidate }) => {
        if (candidate) {
          await fetch('https://api.heygen.com/v1/streaming.ice', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
              'Authorization': `Bearer ${token}`
            },
            body: JSON.stringify({
              session_id: session.data.session_id,
              candidate
            })
          })
        }
      }

      await pc.setRemoteDescription(session.data.sdp)
      const answer = await pc.createAnswer()
      await pc.setLocalDescription(answer)

      // Step 4: Start the session
      await fetch('https://api.heygen.com/v1/streaming.start', {
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

      setDebug('Avatar started!')
      setIsLoading(false)

    } catch (error) {
      setDebug('Error: ' + error.message)
      setIsLoading(false)
      console.error('Full error:', error)
    }
  }

  const speakText = async (text) => {
    if (!sessionData) return
    
    try {
      await fetch('https://api.heygen.com/v1/streaming.task', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${sessionData.token}`
        },
        body: JSON.stringify({
          session_id: sessionData.session_id,
          text: text,
          task_type: 'talk'
        })
      })
    } catch (error) {
      console.error('Speak error:', error)
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

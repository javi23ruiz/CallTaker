import { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { v4 as uuidv4 } from 'uuid'
import AvatarPanel from './components/AvatarPanel'

function App() {
  const [messages, setMessages] = useState([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState('')
  const [agentState, setAgentState] = useState(null)
  const chatContainerRef = useRef(null)
  const textareaRef = useRef(null)

  // Initialize session
  useEffect(() => {
    const newSessionId = uuidv4()
    setSessionId(newSessionId)
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    if (chatContainerRef.current) {
      chatContainerRef.current.scrollTop = chatContainerRef.current.scrollHeight
    }
  }, [messages])

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = '24px'
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`
    }
  }, [inputValue])

  const sendMessage = async () => {
    if (!inputValue.trim() || isLoading) return

    const userMessage = inputValue.trim()
    setInputValue('')

    // Add user message to chat
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const response = await axios.post('/api/chat', {
        session_id: sessionId,
        message: userMessage
      })

      // Add AI response to chat
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: response.data.response 
      }])
      
      setAgentState(response.data.agent_state)

    } catch (error) {
      console.error('Error sending message:', error)
      setMessages(prev => [...prev, { 
        role: 'assistant', 
        content: 'Sorry, I encountered an error. Please try again.' 
      }])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      sendMessage()
    }
  }

  const clearChat = () => {
    setMessages([])
    const newSessionId = uuidv4()
    setSessionId(newSessionId)
    axios.post('/api/session/clear', null, { params: { session_id: sessionId } })
  }

  return (
    <div style={{ display: 'flex', height: '100vh', background: '#F9FAFB' }}>
      {/* Chat Section - Left Side */}
      <div style={{ flex: 1, display: 'flex', flexDirection: 'column' }}>
        {/* Header */}
        <header style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          padding: '12px 24px',
          background: 'transparent'
        }}>
          <div style={{ 
            fontWeight: 600, 
            fontSize: '16px', 
            display: 'flex', 
            alignItems: 'center', 
            gap: '8px',
            color: '#374151'
          }}>
            <span style={{ cursor: 'pointer', opacity: 0.6 }}>☰</span> Camila AI
          </div>
          <div 
            onClick={clearChat}
            style={{ 
              color: '#4B5563', 
              cursor: 'pointer', 
              fontSize: '20px' 
            }}
          >
            +
          </div>
        </header>

        {/* Chat Container */}
        <div 
          ref={chatContainerRef}
          style={{
            flex: 1,
            overflowY: 'auto',
            padding: '20px',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            maxWidth: '800px',
            margin: '0 auto',
            width: '100%'
          }}
        >
          {messages.length === 0 && (
            <div style={{ 
              textAlign: 'center', 
              color: '#9CA3AF', 
              marginTop: '50px',
              fontSize: '15px'
            }}>
              <p style={{ marginBottom: '8px', fontSize: '18px' }}>👋 Hi! I'm Camila</p>
              <p>I'm here to help you report technical issues and complaints.</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              style={{
                display: 'flex',
                gap: '16px',
                alignItems: 'flex-start',
                justifyContent: msg.role === 'user' ? 'flex-end' : 'flex-start'
              }}
            >
              {msg.role === 'assistant' && (
                <div style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: '50%',
                  background: '#6366F1',
                  flexShrink: 0,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'white',
                  fontWeight: 'bold',
                  fontSize: '14px',
                  boxShadow: '0 2px 10px rgba(99, 102, 241, 0.3)'
                }}>
                  C
                </div>
              )}
              
              <div style={{
                maxWidth: '85%',
                padding: '12px 16px',
                borderRadius: '12px',
                lineHeight: 1.6,
                fontSize: '15px',
                background: msg.role === 'user' ? '#F3F4F6' : '#FFFFFF',
                color: msg.role === 'user' ? '#111827' : '#1F2937',
                border: msg.role === 'assistant' ? '1px solid #E5E7EB' : 'none',
                borderTopRightRadius: msg.role === 'user' ? '2px' : '12px',
                borderTopLeftRadius: msg.role === 'assistant' ? '2px' : '12px',
                boxShadow: msg.role === 'assistant' ? '0 1px 2px rgba(0,0,0,0.05)' : 'none',
                whiteSpace: 'pre-wrap'
              }}>
                {msg.content}
              </div>
            </div>
          ))}

          {isLoading && (
            <div style={{ display: 'flex', gap: '16px', alignItems: 'flex-start' }}>
              <div style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                background: '#6366F1',
                flexShrink: 0,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: 'white',
                fontWeight: 'bold',
                fontSize: '14px'
              }}>
                C
              </div>
              <div style={{
                padding: '12px 16px',
                borderRadius: '12px',
                background: '#FFFFFF',
                border: '1px solid #E5E7EB',
                color: '#9CA3AF'
              }}>
                Typing...
              </div>
            </div>
          )}
        </div>

        {/* Input Area */}
        <div style={{
          padding: '24px',
          background: '#F9FAFB',
          display: 'flex',
          justifyContent: 'center'
        }}>
          <div style={{
            width: '100%',
            maxWidth: '800px',
            position: 'relative',
            background: '#FFFFFF',
            border: '1px solid #E5E7EB',
            borderRadius: '16px',
            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.05)',
            display: 'flex',
            alignItems: 'flex-end',
            padding: '12px'
          }}>
            <span style={{ color: '#9CA3AF', padding: '0 8px' }}>📎</span>
            <textarea
              ref={textareaRef}
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Message Camila..."
              style={{
                width: '100%',
                border: 'none',
                resize: 'none',
                outline: 'none',
                maxHeight: '200px',
                padding: '4px 8px',
                fontSize: '16px',
                color: '#1F2937',
                height: '24px',
                fontFamily: 'inherit'
              }}
            />
            <div
              onClick={sendMessage}
              style={{
                background: inputValue.trim() ? '#6366F1' : '#E5E7EB',
                color: inputValue.trim() ? 'white' : '#9CA3AF',
                borderRadius: '8px',
                padding: '6px',
                cursor: inputValue.trim() ? 'pointer' : 'default',
                transition: 'all 0.2s'
              }}
            >
              ➤
            </div>
          </div>
        </div>
        
        <div style={{
          textAlign: 'center',
          fontSize: '11px',
          color: '#9CA3AF',
          paddingBottom: '12px',
          marginTop: '-10px'
        }}>
          Camila can make mistakes. Check important info.
        </div>
      </div>

      {/* Avatar Panel - Right Side */}
      <AvatarPanel currentMessage={messages[messages.length - 1]?.content} />
    </div>
  )
}

export default App


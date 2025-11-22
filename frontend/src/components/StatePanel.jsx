import { useState, useEffect, useRef } from 'react'

function StatePanel({ agentState }) {
  const [isExpanded, setIsExpanded] = useState(true)
  const [updatedFields, setUpdatedFields] = useState(new Set())
  const prevStateRef = useRef(null)

  useEffect(() => {
    if (!agentState) return

    // Track which fields changed
    const newUpdatedFields = new Set()
    
    if (prevStateRef.current) {
      const prev = prevStateRef.current
      const current = agentState

      // Check top-level fields
      Object.keys(current).forEach(key => {
        if (key === 'messages') return // Skip messages array comparison
        
        if (JSON.stringify(prev[key]) !== JSON.stringify(current[key])) {
          newUpdatedFields.add(key)
          
          // If it's customer_data, check nested fields
          if (key === 'customer_data' && typeof current[key] === 'object') {
            Object.keys(current[key] || {}).forEach(nestedKey => {
              if (JSON.stringify(prev[key]?.[nestedKey]) !== JSON.stringify(current[key]?.[nestedKey])) {
                newUpdatedFields.add(`customer_data.${nestedKey}`)
              }
            })
          }
        }
      })
    }

    setUpdatedFields(newUpdatedFields)
    prevStateRef.current = agentState

    // Clear highlights after 2 seconds
    if (newUpdatedFields.size > 0) {
      setTimeout(() => setUpdatedFields(new Set()), 2000)
    }
  }, [agentState])

  const renderValue = (value, path = '') => {
    const isHighlighted = updatedFields.has(path)
    
    if (value === null || value === undefined) {
      return (
        <span style={{ 
          color: '#6B7280',
          fontStyle: 'italic',
          background: isHighlighted ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
          padding: isHighlighted ? '2px 4px' : '0',
          borderRadius: '3px',
          transition: 'background 0.3s'
        }}>
          null
        </span>
      )
    }
    
    if (typeof value === 'boolean') {
      return (
        <span style={{ 
          color: value ? '#10B981' : '#EF4444',
          fontWeight: 600,
          background: isHighlighted ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
          padding: isHighlighted ? '2px 4px' : '0',
          borderRadius: '3px',
          transition: 'background 0.3s'
        }}>
          {value.toString()}
        </span>
      )
    }
    
    if (typeof value === 'string') {
      return (
        <span style={{ 
          color: '#F59E0B',
          background: isHighlighted ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
          padding: isHighlighted ? '2px 4px' : '0',
          borderRadius: '3px',
          transition: 'background 0.3s'
        }}>
          "{value}"
        </span>
      )
    }
    
    if (typeof value === 'object' && !Array.isArray(value)) {
      return (
        <div style={{ marginLeft: '20px' }}>
          {'{'}
          {Object.entries(value).map(([k, v]) => (
            <div key={k} style={{ marginLeft: '20px' }}>
              <span style={{ color: '#8B5CF6' }}>"{k}"</span>: {renderValue(v, `${path}.${k}`.replace(/^\./, ''))}
              {Object.keys(value).indexOf(k) < Object.keys(value).length - 1 && ','}
            </div>
          ))}
          {'}'}
        </div>
      )
    }
    
    return <span style={{ color: '#3B82F6' }}>{JSON.stringify(value)}</span>
  }

  // Default initial state if no agentState exists
  const defaultState = {
    complaint: null,
    mobile_number: null,
    is_registered: null,
    customer_data: {
      priorityId: null,
      sectorId: null,
      networkId: null,
      areaId: null,
      labId: null,
      commercialBranchCode: null,
      clientAddress: null
    },
    address_loaded_from_system: null,
    address_updated_by_user: null,
    confirmation: null,
    submitted: false
  }
  
  const displayState = agentState || defaultState

  return (
    <div style={{
      width: '350px',
      background: '#111827',
      color: '#E5E7EB',
      display: 'flex',
      flexDirection: 'column',
      borderRight: '1px solid #374151'
    }}>
      {/* Header */}
      <div style={{
        padding: '16px 20px',
        borderBottom: '1px solid #374151',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        cursor: 'pointer',
        background: '#1F2937'
      }}
      onClick={() => setIsExpanded(!isExpanded)}
      >
        <div style={{ 
          fontWeight: 600,
          fontSize: '14px',
          color: '#F3F4F6'
        }}>
          🔄 Agent State
        </div>
        <div style={{ 
          fontSize: '18px',
          transition: 'transform 0.2s',
          transform: isExpanded ? 'rotate(90deg)' : 'rotate(0deg)'
        }}>
          ▶
        </div>
      </div>

      {/* Content */}
      {isExpanded && (
        <div style={{
          padding: '20px',
          overflowY: 'auto',
          flex: 1,
          fontFamily: 'monospace',
          fontSize: '13px',
          lineHeight: '1.6'
        }}>
          {/* Filter out messages for cleaner view */}
          {'{'}
          {Object.entries(displayState)
            .filter(([key]) => key !== 'messages') // Skip messages array
            .map(([key, value], index, arr) => (
            <div key={key} style={{ marginLeft: '20px', marginTop: index === 0 ? '8px' : '0' }}>
              <span style={{ 
                color: '#8B5CF6',
                background: updatedFields.has(key) ? 'rgba(34, 197, 94, 0.2)' : 'transparent',
                padding: updatedFields.has(key) ? '2px 4px' : '0',
                borderRadius: '3px',
                transition: 'background 0.3s'
              }}>
                "{key}"
              </span>
              : {renderValue(value, key)}
              {index < arr.length - 1 && ','}
            </div>
          ))}
          {'}'}
        </div>
      )}

      {/* Legend */}
      {isExpanded && (
        <div style={{
          padding: '12px 20px',
          borderTop: '1px solid #374151',
          fontSize: '11px',
          color: '#9CA3AF',
          background: '#0F172A'
        }}>
          <div style={{ marginBottom: '4px' }}>
            <span style={{ 
              display: 'inline-block',
              width: '10px',
              height: '10px',
              background: 'rgba(34, 197, 94, 0.3)',
              marginRight: '6px',
              borderRadius: '2px'
            }}></span>
            Recently updated
          </div>
        </div>
      )}
    </div>
  )
}

export default StatePanel


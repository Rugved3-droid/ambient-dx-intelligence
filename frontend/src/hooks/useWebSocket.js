import { useEffect, useRef, useCallback, useState } from 'react'

export function useWebSocket(url) {
  const wsRef = useRef(null)
  const [connected, setConnected] = useState(false)
  const [lastMessage, setLastMessage] = useState(null)
  const handlersRef = useRef({})
  const reconnectTimeoutRef = useRef(null)

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const host = window.location.host
    const wsUrl = `${protocol}//${host}${url}`

    try {
      const ws = new WebSocket(wsUrl)

      ws.onopen = () => {
        setConnected(true)
        console.log(`WS connected: ${url}`)
      }

      ws.onmessage = (event) => {
        try {
          const msg = JSON.parse(event.data)
          setLastMessage(msg)
          const handler = handlersRef.current[msg.type]
          if (handler) handler(msg.data)
          const allHandler = handlersRef.current['*']
          if (allHandler) allHandler(msg)
        } catch (e) {
          console.error('WS parse error:', e)
        }
      }

      ws.onclose = () => {
        setConnected(false)
        // Reconnect after 2 seconds
        reconnectTimeoutRef.current = setTimeout(connect, 2000)
      }

      ws.onerror = () => {
        ws.close()
      }

      wsRef.current = ws
    } catch (e) {
      console.error('WS connection error:', e)
      reconnectTimeoutRef.current = setTimeout(connect, 2000)
    }
  }, [url])

  useEffect(() => {
    connect()
    return () => {
      if (reconnectTimeoutRef.current) clearTimeout(reconnectTimeoutRef.current)
      if (wsRef.current) wsRef.current.close()
    }
  }, [connect])

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify(data))
    }
  }, [])

  const on = useCallback((type, handler) => {
    handlersRef.current[type] = handler
  }, [])

  const off = useCallback((type) => {
    delete handlersRef.current[type]
  }, [])

  return { connected, lastMessage, send, on, off }
}

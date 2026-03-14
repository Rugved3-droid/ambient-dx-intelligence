import { useState, useCallback, useRef, useEffect } from 'react'

/**
 * Hook for live microphone capture.
 * Tries Deepgram via backend proxy first, falls back to Web Speech API.
 */
export function useLiveMic({ onFinalTranscript, onPartialTranscript, onError }) {
  const [active, setActive] = useState(false)
  const [mode, setMode] = useState(null) // 'deepgram' | 'webspeech'
  const wsRef = useRef(null)
  const recorderRef = useRef(null)
  const streamRef = useRef(null)
  const recognitionRef = useRef(null)
  const activeRef = useRef(false)
  const callbacksRef = useRef({ onFinalTranscript, onPartialTranscript, onError })

  // Keep callbacks ref fresh
  useEffect(() => {
    callbacksRef.current = { onFinalTranscript, onPartialTranscript, onError }
  }, [onFinalTranscript, onPartialTranscript, onError])

  useEffect(() => {
    activeRef.current = active
  }, [active])

  const stopAll = useCallback(() => {
    activeRef.current = false

    if (recorderRef.current && recorderRef.current.state !== 'inactive') {
      try { recorderRef.current.stop() } catch (e) { /* ignore */ }
    }
    recorderRef.current = null

    if (streamRef.current) {
      streamRef.current.getTracks().forEach(t => t.stop())
    }
    streamRef.current = null

    if (wsRef.current && wsRef.current.readyState <= 1) {
      try { wsRef.current.close() } catch (e) { /* ignore */ }
    }
    wsRef.current = null

    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch (e) { /* ignore */ }
    }
    recognitionRef.current = null

    setActive(false)
    setMode(null)
  }, [])

  // ─── Web Speech API (reliable fallback) ───
  const startWebSpeech = useCallback(() => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      throw new Error('Speech recognition not supported — use Chrome')
    }

    // Clean up any previous recognition
    if (recognitionRef.current) {
      try { recognitionRef.current.abort() } catch (e) { /* ignore */ }
    }

    const recognition = new SpeechRecognition()
    recognition.continuous = true
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onresult = (event) => {
      let finalText = ''
      let interimText = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalText += transcript
        } else {
          interimText += transcript
        }
      }

      if (interimText && callbacksRef.current.onPartialTranscript) {
        callbacksRef.current.onPartialTranscript(interimText)
      }
      if (finalText && callbacksRef.current.onFinalTranscript) {
        callbacksRef.current.onFinalTranscript(finalText, 0.9)
      }
    }

    recognition.onerror = (event) => {
      console.error('[Mic] Web Speech error:', event.error)
      if (event.error === 'no-speech' || event.error === 'aborted') return
      if (callbacksRef.current.onError) callbacksRef.current.onError(event.error)
    }

    recognition.onend = () => {
      // Auto-restart if still supposed to be active
      if (activeRef.current && recognitionRef.current) {
        console.log('[Mic] Web Speech ended, restarting...')
        setTimeout(() => {
          if (activeRef.current && recognitionRef.current) {
            try { recognitionRef.current.start() } catch (e) { /* ignore */ }
          }
        }, 100)
      }
    }

    recognitionRef.current = recognition
    recognition.start()
    activeRef.current = true
    setActive(true)
    setMode('webspeech')
    console.log('[Mic] Web Speech API started')
  }, [])

  // ─── Deepgram via backend proxy ───
  const startDeepgram = useCallback(async () => {
    const stream = await navigator.mediaDevices.getUserMedia({
      audio: { channelCount: 1, sampleRate: 48000, echoCancellation: true, noiseSuppression: true }
    })
    streamRef.current = stream

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:'
    const wsUrl = `${protocol}//${window.location.host}/ws/audio`
    const ws = new WebSocket(wsUrl)
    wsRef.current = ws

    return new Promise((resolve, reject) => {
      const timeout = setTimeout(() => reject(new Error('Deepgram timeout')), 8000)

      ws.onmessage = (e) => {
        try {
          const msg = JSON.parse(e.data)
          if (msg.type === 'connected') {
            clearTimeout(timeout)
            const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
              ? 'audio/webm;codecs=opus' : 'audio/webm'
            const recorder = new MediaRecorder(stream, { mimeType })
            recorderRef.current = recorder
            recorder.ondataavailable = (event) => {
              if (event.data.size > 0 && ws.readyState === WebSocket.OPEN) {
                ws.send(event.data)
              }
            }
            recorder.start(250)
            setActive(true)
            activeRef.current = true
            setMode('deepgram')
            resolve(true)
          } else if (msg.type === 'partial' && callbacksRef.current.onPartialTranscript) {
            callbacksRef.current.onPartialTranscript(msg.text)
          } else if (msg.type === 'final' && callbacksRef.current.onFinalTranscript) {
            callbacksRef.current.onFinalTranscript(msg.text, msg.confidence)
          } else if (msg.type === 'error') {
            clearTimeout(timeout)
            reject(new Error(msg.message))
          }
        } catch (err) { /* ignore parse errors */ }
      }

      ws.onerror = () => { clearTimeout(timeout); reject(new Error('WebSocket failed')) }

      ws.onclose = () => {
        // If Deepgram dies while we're supposed to be active, fallback to Web Speech
        if (activeRef.current) {
          console.warn('[Mic] Deepgram disconnected mid-session, switching to Web Speech...')
          // Clean up Deepgram resources
          if (recorderRef.current && recorderRef.current.state !== 'inactive') {
            try { recorderRef.current.stop() } catch (e) { /* ignore */ }
          }
          recorderRef.current = null
          wsRef.current = null
          // Don't stop the mic stream — Web Speech uses the default mic
          try {
            startWebSpeech()
          } catch (err) {
            console.error('[Mic] Web Speech fallback also failed:', err)
            stopAll()
          }
        }
      }
    })
  }, [startWebSpeech, stopAll])

  // ─── Start (try Deepgram, fallback to Web Speech) ───
  const start = useCallback(async () => {
    try {
      await startDeepgram()
    } catch (err) {
      console.warn('[Mic] Deepgram failed, falling back to Web Speech:', err.message)
      // Clean up failed Deepgram
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(t => t.stop())
        streamRef.current = null
      }
      if (wsRef.current) {
        try { wsRef.current.close() } catch (e) { /* ignore */ }
        wsRef.current = null
      }
      try {
        startWebSpeech()
      } catch (err2) {
        console.error('[Mic] Both failed:', err2.message)
        if (onError) onError(`Mic unavailable: ${err2.message}`)
      }
    }
  }, [startDeepgram, startWebSpeech, onError])

  const stop = useCallback(() => { stopAll() }, [stopAll])

  useEffect(() => { return () => stopAll() }, [stopAll])

  return { active, mode, start, stop }
}

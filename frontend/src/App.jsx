import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import { useLiveMic } from './hooks/useLiveMic'
import EMRView from './components/EMRView'
import PatientBanner from './components/PatientBanner'
import TranscriptPanel from './components/TranscriptPanel'
import PreArrivalPanel from './components/PreArrivalPanel'
import RealTimePanel from './components/RealTimePanel'
import SafetyAlert from './components/SafetyAlert'
import DemoControls from './components/DemoControls'

export default function App() {
  // ─── Mode State ───
  const [mode, setMode] = useState('emr') // 'emr' | 'transitioning' | 'dashboard'

  // ─── Dashboard State ───
  const [patient, setPatient] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [intents, setIntents] = useState(null)
  const [diagnostic, setDiagnostic] = useState(null)
  const [safety, setSafety] = useState(null)
  const [preArrival, setPreArrival] = useState(null)
  const [queryResponses, setQueryResponses] = useState([])
  const [status, setStatus] = useState({ stage: 'idle' })
  const [showSafetyAlert, setShowSafetyAlert] = useState(false)
  const [dismissedSafetyAlert, setDismissedSafetyAlert] = useState(false)
  const [partialTranscript, setPartialTranscript] = useState('')
  const [demoPhase, setDemoPhase] = useState(-1) // -1 = not started, 0 = pre-arrival, 1-4 = phases

  const ws = useWebSocket('/ws/dashboard')
  const wsRef = useRef(null)
  useEffect(() => { wsRef.current = ws }, [ws])

  // ─── Live Mic ───
  const mic = useLiveMic({
    onFinalTranscript: useCallback((text, confidence) => {
      setPartialTranscript('')
      if (text.trim().length > 3 && wsRef.current) {
        wsRef.current.send({ command: 'query', question: text.trim(), speaker: 'Live Speaker' })
      }
    }, []),
    onPartialTranscript: useCallback((text) => {
      setPartialTranscript(text)
    }, []),
    onError: useCallback((msg) => {
      console.error('Mic error:', msg)
    }, []),
  })

  // Load patient data on mount
  useEffect(() => {
    fetch('/api/patient')
      .then(r => r.json())
      .then(setPatient)
      .catch(console.error)
  }, [])

  // WebSocket event handlers
  useEffect(() => {
    ws.on('transcript', (data) => {
      setTranscript(prev => [...prev, data])
    })

    ws.on('intents', (data) => {
      setIntents(data)
    })

    ws.on('diagnostic', (data) => {
      setDiagnostic(data)
    })

    ws.on('pre_arrival', (data) => {
      setPreArrival(data)
    })

    ws.on('answer', (data) => {
      // Add to query responses
      const qr = {
        question: data.question,
        answer: data.answer,
        citations: data.citations || [],
        confidence: data.confidence,
        followUp: data.follow_up_suggestions || [],
        timestamp: Date.now() / 1000,
      }
      setQueryResponses(prev => [...prev, qr])

      // Also show in transcript
      setTranscript(prev => [...prev, {
        speaker: 'AI Assistant',
        text: data.answer,
        isAnswer: true,
        citations: data.citations || [],
        confidence: data.confidence,
        followUp: data.follow_up_suggestions || [],
        timestamp: Date.now() / 1000,
      }])
    })

    ws.on('safety_alert', (data) => {
      setSafety(data)
      if (data?.safety_alerts?.length) {
        setShowSafetyAlert(true)
        setDismissedSafetyAlert(false)
        playAlertChime()
      }
    })

    ws.on('phase', (data) => {
      setDemoPhase(data.phase)
    })

    ws.on('status', (data) => {
      setStatus(data)
    })

    ws.on('demo', (data) => {
      if (data.status === 'complete') {
        setStatus({ stage: 'demo_complete' })
      }
    })

    ws.on('reset', () => {
      setTranscript([])
      setIntents(null)
      setDiagnostic(null)
      setSafety(null)
      setPreArrival(null)
      setQueryResponses([])
      setStatus({ stage: 'idle' })
      setShowSafetyAlert(false)
      setDismissedSafetyAlert(false)
      setPartialTranscript('')
      setDemoPhase(-1)
    })
  }, [ws])

  const playAlertChime = useCallback(() => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      const playTone = (freq, start, duration) => {
        const osc = ctx.createOscillator()
        const gain = ctx.createGain()
        osc.connect(gain)
        gain.connect(ctx.destination)
        osc.frequency.value = freq
        osc.type = 'sine'
        gain.gain.setValueAtTime(0.3, ctx.currentTime + start)
        gain.gain.exponentialRampToValueAtTime(0.01, ctx.currentTime + start + duration)
        osc.start(ctx.currentTime + start)
        osc.stop(ctx.currentTime + start + duration)
      }
      playTone(880, 0, 0.2)
      playTone(1100, 0.25, 0.2)
      playTone(880, 0.5, 0.3)
    } catch (e) {
      // Audio not available
    }
  }, [])

  // ─── Handlers ───

  const handleReset = useCallback(() => {
    ws.send({ command: 'reset' })
  }, [ws])

  const handleProcess = useCallback(() => {
    ws.send({ command: 'process' })
  }, [ws])

  const handleToggleMic = useCallback(() => {
    if (mic.active) {
      mic.stop()
      setPartialTranscript('')
    } else {
      mic.start()
    }
  }, [mic])

  const handleQuery = useCallback((question) => {
    ws.send({ command: 'query', question, speaker: 'Judge' })
  }, [ws])

  const handleLoadPatient = useCallback(() => {
    // Trigger pre-arrival intelligence (Phase 0)
    ws.send({ command: 'demo_phase', phase: 0 })
  }, [ws])

  const handleStartDemo = useCallback((phaseDelay) => {
    ws.send({ command: 'demo_start', phase_delay: phaseDelay || 8.0 })
  }, [ws])

  const handleRunPhase = useCallback((phase) => {
    ws.send({ command: 'demo_phase', phase })
  }, [ws])

  const handleDismissSafetyAlert = useCallback(() => {
    setShowSafetyAlert(false)
    setDismissedSafetyAlert(true)
  }, [])

  // ─── Mode Transition ───

  const handleLaunchAmbient = useCallback(() => {
    setMode('transitioning')
    setTimeout(() => {
      setMode('dashboard')
    }, 2000)
  }, [])

  const handleBackToEMR = useCallback(() => {
    setMode('emr')
  }, [])

  const isProcessing = status?.stage && !['idle', 'complete', 'demo_complete'].includes(status.stage)

  // ─── EMR MODE ───
  if (mode === 'emr') {
    return (
      <EMRView
        patient={patient?.patient || patient}
        onLaunchAmbient={handleLaunchAmbient}
      />
    )
  }

  // ─── TRANSITION OVERLAY ───
  if (mode === 'transitioning') {
    return (
      <div className="transition-overlay">
        <div className="transition-content">
          <div className="transition-ring"></div>
          <div className="transition-text">
            <div className="transition-title">AMBIENT Dx INTELLIGENCE</div>
            <div className="transition-subtitle">Activating Clinical Decision Support</div>
            <div className="transition-dots">
              <span className="transition-dot"></span>
              <span className="transition-dot"></span>
              <span className="transition-dot"></span>
            </div>
          </div>
        </div>
      </div>
    )
  }

  // ─── DASHBOARD MODE ───
  return (
    <div className="h-screen flex flex-col bg-clinical-bg overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-clinical-border px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-clinical-critical live-dot"></div>
          <h1 className="text-sm font-bold tracking-wider text-clinical-text uppercase">
            Ambient Dx Intelligence
          </h1>
          {demoPhase >= 0 && (
            <div className="flex items-center gap-1 ml-4">
              {[0, 1, 2, 3, 4].map(p => (
                <div
                  key={p}
                  className={`w-6 h-1.5 rounded-full transition-all ${
                    p < demoPhase ? 'bg-clinical-normal' :
                    p === demoPhase ? 'bg-clinical-info live-dot' :
                    'bg-clinical-border-light'
                  }`}
                  title={p === 0 ? 'Pre-Arrival' : `Phase ${p}`}
                />
              ))}
            </div>
          )}
        </div>
        <div className="flex items-center gap-4">
          <button
            onClick={handleBackToEMR}
            className="px-3 py-1 text-[10px] font-bold uppercase tracking-wider text-clinical-text-muted hover:text-clinical-text bg-clinical-surface hover:bg-clinical-border-light border border-clinical-border rounded transition-colors"
          >
            View EMR
          </button>
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${ws.connected ? 'bg-clinical-normal' : 'bg-clinical-critical'}`}></div>
            <span className="text-xs text-clinical-text-muted">
              {ws.connected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
        </div>
      </header>

      {/* Safety Alert Overlay */}
      {showSafetyAlert && safety?.safety_alerts?.length > 0 && (
        <SafetyAlert
          alerts={safety.safety_alerts}
          onDismiss={handleDismissSafetyAlert}
        />
      )}

      {/* Patient Banner */}
      {patient && <PatientBanner patient={patient.patient || patient} />}

      {/* Main Content — Left 35% / Right 65% */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel — Conversation + Queries (35%) */}
        <div className="w-[35%] border-r border-clinical-border flex flex-col">
          <div className="px-3 py-2 border-b border-clinical-border flex items-center justify-between">
            <h2 className="text-xs font-bold text-clinical-text-muted tracking-wider uppercase">
              {transcript.length > 0 ? 'Live Transcript' : 'Clinical Q&A'}
            </h2>
            <div className="flex items-center gap-2">
              {mic.active && (
                <span className="mic-live-badge">
                  <span className="mic-live-dot"></span>
                  LIVE
                </span>
              )}
              {demoPhase >= 1 && (
                <span className="px-1.5 py-0.5 text-[9px] font-bold bg-clinical-info/20 text-clinical-info border border-clinical-info/30 rounded">
                  DEMO
                </span>
              )}
            </div>
          </div>
          <TranscriptPanel
            transcript={transcript}
            intents={intents}
            partialTranscript={partialTranscript}
            onQuery={handleQuery}
            isProcessing={isProcessing}
          />
        </div>

        {/* Right Panel — Clinical Intelligence (65%) */}
        <div className="w-[65%] flex flex-col overflow-hidden">
          <div className="flex-1 overflow-y-auto">
            {/* Pre-Arrival Intelligence Section */}
            <PreArrivalPanel
              preArrival={preArrival}
              diagnostic={diagnostic}
              patient={patient?.patient || patient}
              highlightedDifferentials={intents?.intents?.flatMap(i => i.differentials_mentioned || []) || []}
            />

            {/* Real-Time Intelligence Section */}
            <RealTimePanel
              patient={patient?.patient || patient}
              diagnostic={diagnostic}
              queryResponses={queryResponses}
              safety={safety}
              dismissedSafetyAlert={dismissedSafetyAlert}
              intents={intents}
            />
          </div>
        </div>
      </div>

      {/* Disclaimer Bar */}
      <div className="flex-shrink-0 bg-[#0d1117] border-t border-clinical-border px-4 py-1 text-center">
        <span className="text-[10px] text-clinical-text-muted tracking-wider">
          AI-generated clinical support — Verify all data independently — Clinician judgment required
        </span>
      </div>

      {/* Bottom Controls */}
      <DemoControls
        status={status}
        demoPhase={demoPhase}
        onReset={handleReset}
        onProcess={handleProcess}
        onLoadPatient={handleLoadPatient}
        onStartDemo={handleStartDemo}
        onRunPhase={handleRunPhase}
        connected={ws.connected}
        micActive={mic.active}
        micMode={mic.mode}
        onToggleMic={handleToggleMic}
        preArrivalLoaded={!!preArrival}
      />
    </div>
  )
}

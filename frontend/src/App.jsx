import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import { useLiveMic } from './hooks/useLiveMic'
import EMRView from './components/EMRView'
import PatientBanner from './components/PatientBanner'
import TranscriptPanel from './components/TranscriptPanel'
import Dashboard from './components/Dashboard'
import Differentials from './components/Differentials'
import ClinicalScores from './components/ClinicalScores'
import Timeline from './components/Timeline'
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
  const [activeTab, setActiveTab] = useState('dashboard')
  const [status, setStatus] = useState({ stage: 'idle' })
  const [showSafetyAlert, setShowSafetyAlert] = useState(false)
  const [partialTranscript, setPartialTranscript] = useState('')

  const ws = useWebSocket('/ws/dashboard')
  const wsRef = useRef(null)
  useEffect(() => { wsRef.current = ws }, [ws])

  // ─── Live Mic ───
  const mic = useLiveMic({
    onFinalTranscript: useCallback((text, confidence) => {
      setPartialTranscript('')
      // Auto-send spoken text as a query to the AI
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
      if (data?.differential_diagnoses?.length) {
        setActiveTab('differentials')
      }
    })

    ws.on('answer', (data) => {
      // Show AI answer inline in the transcript
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
        playAlertChime()
        setTimeout(() => setActiveTab('differentials'), 1000)
      }
    })

    ws.on('status', (data) => {
      setStatus(data)
    })

    ws.on('reset', () => {
      setTranscript([])
      setIntents(null)
      setDiagnostic(null)
      setSafety(null)
      setStatus({ stage: 'idle' })
      setShowSafetyAlert(false)
      setActiveTab('dashboard')
      setPartialTranscript('')
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

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'differentials', label: 'Differentials' },
    { id: 'scores', label: 'Clinical Scores' },
    { id: 'timeline', label: 'Timeline / Notes' },
  ]

  const isProcessing = status?.stage && !['idle', 'complete', 'demo_complete'].includes(status.stage)
  const processingStages = [
    { key: 'data_retrieval', label: 'Retrieving Data' },
    { key: 'generating_answer', label: 'AI Reasoning' },
  ]

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

      {/* Processing Stage Banner */}
      {isProcessing && (
        <div className="processing-banner">
          <div className="processing-banner-inner">
            {processingStages.map((s, i) => {
              const currentIdx = processingStages.findIndex(ps => ps.key === status.stage)
              const isDone = i < currentIdx
              const isCurrent = s.key === status.stage
              return (
                <div key={s.key} className={`processing-stage ${isDone ? 'stage-done' : isCurrent ? 'stage-active' : 'stage-pending'}`}>
                  <span className="stage-number">{isDone ? '\u2713' : i + 1}</span>
                  <span className="stage-label">{s.label}</span>
                  {i < processingStages.length - 1 && <span className="stage-connector"></span>}
                </div>
              )
            })}
          </div>
        </div>
      )}

      {/* Safety Alert Overlay */}
      {showSafetyAlert && safety?.safety_alerts?.length > 0 && (
        <SafetyAlert
          alerts={safety.safety_alerts}
          onDismiss={() => setShowSafetyAlert(false)}
        />
      )}

      {/* Patient Banner */}
      {patient && <PatientBanner patient={patient.patient || patient} />}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel — Conversation */}
        <div className="w-[38%] border-r border-clinical-border flex flex-col">
          <div className="px-3 py-2 border-b border-clinical-border flex items-center justify-between">
            <h2 className="text-xs font-bold text-clinical-text-muted tracking-wider uppercase">
              Clinical Q&A
            </h2>
            {mic.active && (
              <span className="mic-live-badge">
                <span className="mic-live-dot"></span>
                LIVE
              </span>
            )}
          </div>
          <TranscriptPanel
            transcript={transcript}
            intents={intents}
            partialTranscript={partialTranscript}
            onQuery={handleQuery}
            isProcessing={isProcessing}
          />
        </div>

        {/* Right Panel — Diagnostic Workspace */}
        <div className="w-[62%] flex flex-col overflow-hidden">
          {/* Tabs */}
          <div className="flex-shrink-0 border-b border-clinical-border">
            <div className="flex">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`px-4 py-2 text-xs font-medium tracking-wider uppercase transition-colors ${
                    activeTab === tab.id ? 'tab-active' : 'tab-inactive'
                  }`}
                >
                  {tab.label}
                  {tab.id === 'differentials' && diagnostic?.differential_diagnoses?.length > 0 && (
                    <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-clinical-info/20 text-clinical-info rounded">
                      {diagnostic.differential_diagnoses.length}
                    </span>
                  )}
                  {tab.id === 'scores' && diagnostic?.clinical_scores?.length > 0 && (
                    <span className="ml-2 px-1.5 py-0.5 text-[10px] bg-clinical-warning/20 text-clinical-warning rounded">
                      {diagnostic.clinical_scores.length}
                    </span>
                  )}
                </button>
              ))}
            </div>
          </div>

          {/* Tab Content */}
          <div className="flex-1 overflow-y-auto p-4">
            {activeTab === 'dashboard' && patient && (
              <Dashboard patient={patient.patient || patient} diagnostic={diagnostic} />
            )}
            {activeTab === 'differentials' && (
              <Differentials
                diagnostic={diagnostic}
                safety={safety}
              />
            )}
            {activeTab === 'scores' && (
              <ClinicalScores diagnostic={diagnostic} />
            )}
            {activeTab === 'timeline' && patient && (
              <Timeline
                patient={patient.patient || patient}
                safetyAlertActive={showSafetyAlert}
              />
            )}
          </div>
        </div>
      </div>

      {/* Bottom Controls */}
      <DemoControls
        status={status}
        onReset={handleReset}
        onProcess={handleProcess}
        connected={ws.connected}
        micActive={mic.active}
        micMode={mic.mode}
        onToggleMic={handleToggleMic}
      />
    </div>
  )
}

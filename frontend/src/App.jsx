import { useState, useEffect, useCallback, useRef } from 'react'
import { useWebSocket } from './hooks/useWebSocket'
import PatientBanner from './components/PatientBanner'
import TranscriptPanel from './components/TranscriptPanel'
import Dashboard from './components/Dashboard'
import Differentials from './components/Differentials'
import ClinicalScores from './components/ClinicalScores'
import Timeline from './components/Timeline'
import SafetyAlert from './components/SafetyAlert'
import DemoControls from './components/DemoControls'

export default function App() {
  const [patient, setPatient] = useState(null)
  const [transcript, setTranscript] = useState([])
  const [intents, setIntents] = useState(null)
  const [diagnostic, setDiagnostic] = useState(null)
  const [safety, setSafety] = useState(null)
  const [phase, setPhase] = useState({ phase: 0, title: '', status: '' })
  const [activeTab, setActiveTab] = useState('dashboard')
  const [status, setStatus] = useState({ stage: 'idle' })
  const [showSafetyAlert, setShowSafetyAlert] = useState(false)
  const audioRef = useRef(null)

  const ws = useWebSocket('/ws/dashboard')

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
      // Auto-switch to differentials tab when diagnostic arrives
      if (data?.differential_diagnoses?.length) {
        setActiveTab('differentials')
      }
    })

    ws.on('safety_alert', (data) => {
      setSafety(data)
      if (data?.safety_alerts?.length) {
        setShowSafetyAlert(true)
        // Play alert chime
        playAlertChime()
        // Auto-switch to timeline to show the 2023 discharge summary
        setTimeout(() => setActiveTab('differentials'), 1000)
      }
    })

    ws.on('phase', (data) => {
      setPhase(data)
    })

    ws.on('status', (data) => {
      setStatus(data)
    })

    ws.on('reset', () => {
      setTranscript([])
      setIntents(null)
      setDiagnostic(null)
      setSafety(null)
      setPhase({ phase: 0, title: '', status: '' })
      setStatus({ stage: 'idle' })
      setShowSafetyAlert(false)
      setActiveTab('dashboard')
    })

    ws.on('demo', (data) => {
      if (data.status === 'complete') {
        setStatus({ stage: 'demo_complete' })
      }
    })
  }, [ws])

  const playAlertChime = useCallback(() => {
    try {
      const ctx = new (window.AudioContext || window.webkitAudioContext)()
      // Two-tone alert chime
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

  const handleStartDemo = useCallback(() => {
    ws.send({ command: 'demo_start', phase_delay: 6 })
  }, [ws])

  const handleRunPhase = useCallback((phaseNum) => {
    ws.send({ command: 'demo_phase', phase: phaseNum })
  }, [ws])

  const handleReset = useCallback(() => {
    ws.send({ command: 'reset' })
  }, [ws])

  const handleProcess = useCallback(() => {
    ws.send({ command: 'process', phase: phase.phase })
  }, [ws, phase])

  const tabs = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'differentials', label: 'Differentials' },
    { id: 'scores', label: 'Clinical Scores' },
    { id: 'timeline', label: 'Timeline / Notes' },
  ]

  return (
    <div className="h-screen flex flex-col bg-clinical-bg overflow-hidden">
      {/* Header */}
      <header className="flex-shrink-0 border-b border-clinical-border px-4 py-2 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="w-2 h-2 rounded-full bg-clinical-critical live-dot"></div>
          <h1 className="text-sm font-bold tracking-wider text-clinical-text uppercase">
            Ambient Dx Intelligence
          </h1>
          <span className="text-xs text-clinical-text-muted">v1.0</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="flex items-center gap-2">
            <div className={`w-2 h-2 rounded-full ${ws.connected ? 'bg-clinical-normal' : 'bg-clinical-critical'}`}></div>
            <span className="text-xs text-clinical-text-muted">
              {ws.connected ? 'CONNECTED' : 'DISCONNECTED'}
            </span>
          </div>
          {status.stage !== 'idle' && status.stage !== 'complete' && status.stage !== 'demo_complete' && (
            <span className="text-xs text-clinical-info animate-pulse">
              {status.stage?.replace(/_/g, ' ').toUpperCase()}
            </span>
          )}
        </div>
      </header>

      {/* Safety Alert Overlay */}
      {showSafetyAlert && safety?.safety_alerts?.length > 0 && (
        <SafetyAlert
          alerts={safety.safety_alerts}
          onDismiss={() => setShowSafetyAlert(false)}
        />
      )}

      {/* Patient Banner */}
      {patient && <PatientBanner patient={patient.patient} />}

      {/* Main Content */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel — Conversation Intelligence */}
        <div className="w-[40%] border-r border-clinical-border flex flex-col">
          <div className="px-3 py-2 border-b border-clinical-border">
            <h2 className="text-xs font-bold text-clinical-text-muted tracking-wider uppercase">
              Conversation Intelligence
            </h2>
          </div>
          <TranscriptPanel
            transcript={transcript}
            intents={intents}
            phase={phase}
          />
        </div>

        {/* Right Panel — Diagnostic Workspace */}
        <div className="w-[60%] flex flex-col overflow-hidden">
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
              <Dashboard patient={patient.patient} diagnostic={diagnostic} />
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
                patient={patient.patient}
                safetyAlertActive={showSafetyAlert}
              />
            )}
          </div>
        </div>
      </div>

      {/* Demo Controls */}
      <DemoControls
        phase={phase}
        status={status}
        onStartDemo={handleStartDemo}
        onRunPhase={handleRunPhase}
        onReset={handleReset}
        onProcess={handleProcess}
        connected={ws.connected}
      />
    </div>
  )
}

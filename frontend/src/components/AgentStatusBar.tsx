import React, { useEffect, useState } from 'react'
import { ShieldAlert, CheckCircle, Clock } from 'lucide-react'
import type { LogEvent } from '../stores/jobStore'

interface AgentStatusBarProps {
  logs: LogEvent[]
  jobStatus?: string
}

export const AgentStatusBar: React.FC<AgentStatusBarProps> = ({ logs, jobStatus }) => {
  const [seconds, setSeconds] = useState(0)
  const [timerRunning, setTimerRunning] = useState(false)

  const latestEvent = logs[logs.length - 1]

  const activeAgent = latestEvent?.agent || 'system'
  const activeTool = latestEvent?.tool || 'N/A'
  const activeMessage = latestEvent?.message || 'Awaiting audit start...'

  const isFinished = jobStatus === 'READY' || (latestEvent?.agent === 'compile_report' && latestEvent?.status === 'done')
  const isFailed = jobStatus === 'FAILED'

  useEffect(() => {
    let interval: any = null

    if (logs.length > 0 && !isFinished && !isFailed) {
      if (!timerRunning) {
        setTimerRunning(true)
        setSeconds(0)
      }
      interval = setInterval(() => {
        setSeconds((prev) => prev + 1)
      }, 1000)
    } else if (isFinished || isFailed) {
      setTimerRunning(false)
    }

    return () => {
      if (interval) clearInterval(interval)
    }
  }, [logs.length, isFinished, isFailed, timerRunning])

  const formatTime = (secs: number) => {
    const mins = Math.floor(secs / 60)
    const s = secs % 60
    return `${mins.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`
  }

  const agentStages = [
    { key: 'initialize', label: 'INITIALIZE' },
    { key: 'relevance_reasoner', label: 'RELEVANCE' },
    { key: 'tool_caller', label: 'EVIDENCE SEARCH' },
    { key: 'gap_analyzer', label: 'GAP ANALYSIS' },
    { key: 'compile_report', label: 'REPORT GENERATION' }
  ]

  const getStageStatus = (stageKey: string) => {
    if (isFailed) return 'failed'
    if (isFinished) return 'completed'

    const activeIndex = agentStages.findIndex(s => s.key === latestEvent?.tool)
    const stageIndex = agentStages.findIndex(s => s.key === stageKey)
    
    if (latestEvent?.tool === stageKey) {
      return latestEvent.status === 'done' ? 'completed' : 'running'
    }
    
    if (stageIndex !== -1 && activeIndex !== -1 && stageIndex < activeIndex) {
      return 'completed'
    }
    return 'pending'
  }

  return (
    <div className="bg-surface border border-borderCustom p-5 font-mono rounded-sm">
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-borderCustom pb-4 mb-4">
        
        <div className="flex items-center gap-3">
          <div className="relative">
            {timerRunning ? (
              <span className="flex h-3.5 w-3.5">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-teal opacity-75"></span>
                <span className="relative inline-flex rounded-full h-3.5 w-3.5 bg-teal"></span>
              </span>
            ) : isFinished ? (
              <CheckCircle className="w-5.5 h-5.5 text-teal" />
            ) : isFailed ? (
              <ShieldAlert className="w-5.5 h-5.5 text-red" />
            ) : (
              <span className="inline-flex rounded-full h-3.5 w-3.5 bg-gray-600"></span>
            )}
          </div>
          <div>
            <div className="text-[10px] text-gray-500 uppercase tracking-widest">ACTIVE AGENT</div>
            <div className="text-sm font-bold text-white uppercase tracking-wider">
              {isFinished ? 'COMPLIANCE AUDIT COMPLETED' : isFailed ? 'AUDIT FAILURE' : activeAgent}
            </div>
          </div>
        </div>

        <div className="flex items-center gap-6 text-xs text-gray-400">
          <div>
            <span className="text-gray-500">STAGE:</span>{' '}
            <span className="text-gold uppercase">{latestEvent?.tool || 'STANDBY'}</span>
          </div>
          <div className="flex items-center gap-1.5 bg-bg border border-borderCustom px-2.5 py-1 rounded-sm">
            <Clock className="w-3.5 h-3.5 text-gray-500" />
            <span className="text-white text-[11px] font-bold">{formatTime(seconds)}</span>
          </div>
        </div>

      </div>

      <div className="grid grid-cols-2 md:grid-cols-5 gap-2.5 mb-4">
        {agentStages.map((stage) => {
          const status = getStageStatus(stage.key)
          let borderCol = 'border-borderCustom text-gray-600'
          let indicator = 'bg-gray-800'
          
          if (status === 'completed') {
            borderCol = 'border-teal/30 text-teal'
            indicator = 'bg-teal'
          } else if (status === 'running') {
            borderCol = 'border-gold text-gold font-bold'
            indicator = 'bg-gold animate-pulse-teal'
          } else if (status === 'failed') {
            borderCol = 'border-red text-red'
            indicator = 'bg-red'
          }
          
          return (
            <div 
              key={stage.key} 
              className={`border p-2.5 rounded-sm flex flex-col justify-between h-16 transition-colors duration-150 ${borderCol}`}
            >
              <span className="text-[9px] tracking-wider font-semibold">{stage.label}</span>
              <div className="flex items-center justify-between mt-1">
                <span className="text-[8px] text-gray-500">
                  {status === 'completed' && 'OK'}
                  {status === 'running' && 'ACTIVE'}
                  {status === 'pending' && 'WAITING'}
                  {status === 'failed' && 'ERR'}
                </span>
                <span className={`w-2 h-2 rounded-full ${indicator}`}></span>
              </div>
            </div>
          )
        })}
      </div>

      <div className="bg-bg border border-borderCustom p-3.5 font-mono text-xs rounded-sm max-h-32 overflow-y-auto">
        <div className="text-[9px] text-gray-500 uppercase tracking-widest border-b border-borderCustom pb-1 mb-2">
          Real-Time Log Stream Output
        </div>
        <div className="text-gray-400 leading-relaxed font-mono whitespace-pre-wrap">
          <span className="text-gold">[{latestEvent?.timestamp || new Date().toLocaleTimeString()}]</span>{' '}
          <span className="text-blue">({activeAgent}:{activeTool})</span>{' '}
          <span className="text-gray-200">{activeMessage}</span>
        </div>
      </div>

    </div>
  )
}

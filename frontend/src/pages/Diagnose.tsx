import React, { useEffect, useState } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { useJobStore } from '../stores/jobStore'
import { AgentStatusBar } from '../components/AgentStatusBar'
import { ViolationCard } from '../components/ViolationCard'
import { 
  Play, 
  Terminal, 
  AlertOctagon, 
  CheckCircle, 
  FileText, 
  ArrowLeft,
  Settings,
  Cpu
} from 'lucide-react'

export const Diagnose: React.FC = () => {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  
  const queryJobId = searchParams.get('job_id')
  
  const { 
    activeJob, 
    logs, 
    findings, 
    createJob, 
    connectSSE, 
    disconnectSSE, 
    fetchJobDetails 
  } = useJobStore()

  const [selectedAgent, setSelectedAgent] = useState<'rbi_compliance' | 'api_compliance' | 'codebase'>('rbi_compliance')
  const [submitting, setSubmitting] = useState(false)
  const [activeTab, setActiveTab] = useState<'gaps' | 'console'>('gaps')

  // Load job details and connect to SSE on mount or when job_id query param changes
  useEffect(() => {
    if (queryJobId) {
      fetchJobDetails(queryJobId)
      connectSSE(queryJobId)
    }
    return () => {
      disconnectSSE()
    }
  }, [queryJobId, fetchJobDetails, connectSSE, disconnectSSE])

  const handleStartAudit = async (e: React.FormEvent) => {
    e.preventDefault()
    setSubmitting(true)
    try {
      const jobId = await createJob(selectedAgent, 'full_diagnosis')
      navigate(`/diagnose?job_id=${jobId}`)
    } catch (err) {
      console.error(err)
    } finally {
      setSubmitting(false)
    }
  }

  const getAgentLabel = (agent: string) => {
    switch (agent) {
      case 'rbi_compliance':
        return 'RBI Regulations Agent'
      case 'api_compliance':
        return 'API Specification Agent'
      case 'codebase':
        return 'Source Code Compliance Agent'
      default:
        return agent
    }
  }

  return (
    <div className="min-h-screen bg-bg text-gray-300 flex flex-col font-mono">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        
        {/* Back Link */}
        <div className="mb-6">
          <button 
            onClick={() => navigate('/dashboard')}
            className="flex items-center gap-2 text-gray-500 hover:text-white text-xs border border-transparent hover:border-borderCustom px-2.5 py-1.5 rounded-sm transition-all duration-150 cursor-pointer"
          >
            <ArrowLeft className="w-3.5 h-3.5" />
            <span>RETURN TO DASHBOARD</span>
          </button>
        </div>

        {/* Dynamic Split Screen Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Column: Form & Status Bar */}
          <div className="lg:col-span-5 space-y-6">
            
            {/* Run Audit Form */}
            <div className="bg-surface border border-borderCustom p-6 rounded-sm">
              <h2 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
                <Settings className="w-4 h-4 text-gold" />
                Audit Configuration
              </h2>
              
              <form onSubmit={handleStartAudit} className="space-y-4">
                <div>
                  <label className="block text-[9px] text-gray-500 uppercase tracking-widest mb-1.5">
                    Target Compliance Agent
                  </label>
                  <select
                    value={selectedAgent}
                    onChange={(e) => setSelectedAgent(e.target.value as any)}
                    disabled={!!queryJobId || submitting}
                    className="w-full bg-bg border border-borderCustom text-white text-xs py-2 px-3 rounded-sm font-mono focus:border-gold outline-none transition-colors duration-150 disabled:opacity-50"
                  >
                    <option value="rbi_compliance">RBI Regulations Agent (Mode A)</option>
                    <option value="api_compliance">API Specification Agent (Mode A)</option>
                    <option value="codebase">Source Code Compliance Agent (Mode A)</option>
                  </select>
                </div>

                {!queryJobId && (
                  <button
                    type="submit"
                    disabled={submitting}
                    className="w-full flex items-center justify-center gap-2 border border-gold bg-gold/5 hover:bg-gold hover:text-black text-gold text-xs py-2.5 rounded-sm font-bold uppercase tracking-wider transition-all duration-150 cursor-pointer"
                  >
                    <Play className="w-3.5 h-3.5" />
                    <span>{submitting ? 'INITIALIZING AUDIT...' : 'START RUN'}</span>
                  </button>
                )}
              </form>
            </div>

            {/* SSE Log Output Status Bar */}
            {queryJobId && (
              <AgentStatusBar logs={logs} jobStatus={activeJob?.status} />
            )}

          </div>

          {/* Right Column: Violation Cards & Report details */}
          <div className="lg:col-span-7 space-y-6">
            
            {queryJobId ? (
              <div className="bg-surface border border-borderCustom p-6 rounded-sm flex flex-col h-[calc(100vh-240px)] min-h-[500px]">
                
                {/* Header with Title & Report download if ready */}
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3 border-b border-borderCustom pb-4 mb-4 select-none">
                  <div>
                    <h2 className="text-sm font-bold text-white uppercase tracking-wider flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-teal animate-pulse" />
                      Run ID: {queryJobId.substring(0, 8)}
                    </h2>
                    <p className="text-[9px] text-gray-500 uppercase tracking-widest mt-1">
                      Target: {activeJob ? getAgentLabel(activeJob.agent_type) : 'Loading...'}
                    </p>
                  </div>
                  
                  {activeJob?.report_url && (
                    <a
                      href={activeJob.report_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-2 border border-teal text-teal hover:bg-teal hover:text-black text-xs px-3.5 py-1.5 rounded-sm uppercase tracking-wider font-bold transition-all duration-150"
                    >
                      <FileText className="w-3.5 h-3.5" />
                      <span>Download PDF Report</span>
                    </a>
                  )}
                </div>

                {/* Tabs to switch views */}
                <div className="flex border-b border-borderCustom mb-4 text-[10px] tracking-wider uppercase font-bold">
                  <button
                    onClick={() => setActiveTab('gaps')}
                    className={`pb-2.5 px-4 border-b-2 transition-all duration-150 cursor-pointer ${
                      activeTab === 'gaps' ? 'border-gold text-white font-bold' : 'border-transparent text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    Compliance Gaps ({findings.length})
                  </button>
                  <button
                    onClick={() => setActiveTab('console')}
                    className={`pb-2.5 px-4 border-b-2 transition-all duration-150 cursor-pointer ${
                      activeTab === 'console' ? 'border-gold text-white font-bold' : 'border-transparent text-gray-500 hover:text-gray-300'
                    }`}
                  >
                    Console Output ({logs.length})
                  </button>
                </div>

                {/* Tab content */}
                <div className="flex-1 overflow-y-auto pr-1">
                  
                  {activeTab === 'gaps' && (
                    <div className="space-y-3">
                      {findings.length === 0 ? (
                        <div className="py-20 flex flex-col items-center justify-center text-center">
                          {activeJob?.status === 'READY' ? (
                            <>
                              <CheckCircle className="w-10 h-10 text-teal mb-3" />
                              <h3 className="text-white text-xs font-bold uppercase tracking-wider">No Compliance Gaps Detected</h3>
                              <p className="text-gray-500 text-[10px] uppercase tracking-widest mt-1 max-w-sm">
                                The agent successfully verified all compliance mandates against retrieved policies.
                              </p>
                            </>
                          ) : activeJob?.status === 'FAILED' ? (
                            <>
                              <AlertOctagon className="w-10 h-10 text-red mb-3" />
                              <h3 className="text-white text-xs font-bold uppercase tracking-wider">Audit Failed</h3>
                              <p className="text-gray-500 text-[10px] uppercase tracking-widest mt-1">
                                Review the console output tab to troubleshoot worker exceptions.
                              </p>
                            </>
                          ) : (
                            <>
                              <span className="flex h-5 w-5 mb-3">
                                <span className="animate-ping absolute inline-flex h-5 w-5 rounded-full bg-gold opacity-75"></span>
                                <span className="relative inline-flex rounded-full h-5 w-5 bg-gold"></span>
                              </span>
                              <h3 className="text-white text-xs font-bold uppercase tracking-wider animate-pulse">Running Scan...</h3>
                              <p className="text-gray-500 text-[10px] uppercase tracking-widest mt-1">
                                Gap analysis nodes are running vector checks in the background.
                              </p>
                            </>
                          )}
                        </div>
                      ) : (
                        findings.map((finding, idx) => (
                          <ViolationCard key={finding.chunk_id} finding={finding} index={idx} />
                        ))
                      )}
                    </div>
                  )}

                  {activeTab === 'console' && (
                    <div className="space-y-2.5 font-mono text-[11px] leading-relaxed bg-bg border border-borderCustom p-4 rounded-sm min-h-full">
                      {logs.map((log, index) => (
                        <div key={index} className="border-b border-borderCustom/30 pb-1.5 last:border-0">
                          <span className="text-gray-500 select-none">[{log.timestamp}]</span>{' '}
                          <span className="text-gold font-bold select-none">{log.agent}:{log.tool}</span>{' '}
                          <span className="text-gray-400 select-none">&gt;&gt;</span>{' '}
                          <span className={log.status === 'finding' ? 'text-red font-semibold' : 'text-gray-300'}>
                            {log.message}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}

                </div>

              </div>
            ) : (
              <div className="bg-surface border border-borderCustom p-8 rounded-sm text-center py-24 select-none">
                <Terminal className="w-12 h-12 text-gray-700 mx-auto mb-4" />
                <h3 className="text-white text-xs uppercase tracking-wider font-bold">Awaiting Diagnostic Run</h3>
                <p className="text-gray-500 text-[10px] uppercase tracking-widest mt-2 max-w-md mx-auto leading-relaxed">
                  Configure a target compliance agent on the left panel to execute real-time multi-agent rule scanning.
                </p>
              </div>
            )}

          </div>

        </div>

      </main>
    </div>
  )
}

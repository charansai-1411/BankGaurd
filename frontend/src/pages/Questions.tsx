import React, { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { api } from '../lib/api'
import { 
  ClipboardList, 
  Play, 
  Loader2, 
  AlertTriangle,
  ShieldCheck
} from 'lucide-react'

interface PredefinedQuestion {
  id: string
  agent_domain: string
  question_text: string
  is_active: boolean
}

export const Questions: React.FC = () => {
  const navigate = useNavigate()
  
  const [selectedDomain, setSelectedDomain] = useState<'rbi_compliance' | 'api_compliance' | 'codebase'>('rbi_compliance')
  const [questions, setQuestions] = useState<PredefinedQuestion[]>([])
  const [loading, setLoading] = useState(false)
  const [running, setRunning] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Fetch predefined questions when active domain tab changes
  useEffect(() => {
    const fetchQuestions = async () => {
      setLoading(true)
      setError(null)
      try {
        const response = await api.get('/questions/', {
          params: { agent_domain: selectedDomain }
        })
        setQuestions(response.data || [])
      } catch (err: any) {
        console.error(err)
        setError('Failed to fetch predefined questions for this domain.')
      } finally {
        setLoading(false)
      }
    }

    fetchQuestions()
  }, [selectedDomain])

  const handleRunChecklist = async () => {
    setRunning(true)
    setError(null)
    try {
      const response = await api.post('/questions/run', null, {
        params: { agent_domain: selectedDomain }
      })
      const { job_id } = response.data
      if (job_id) {
        navigate(`/diagnose?job_id=${job_id}`)
      } else {
        throw new Error('No job ID returned from server.')
      }
    } catch (err: any) {
      console.error(err)
      setError(err?.response?.data?.detail || 'Failed to trigger predefined checklist audit.')
    } finally {
      setRunning(false)
    }
  }

  const getDomainLabel = (domain: string) => {
    switch (domain) {
      case 'rbi_compliance':
        return 'RBI Regulations Checklist'
      case 'api_compliance':
        return 'API Specification Checklist'
      case 'codebase':
        return 'Codebase Compliance Checklist'
      default:
        return domain.toUpperCase()
    }
  }

  return (
    <div className="min-h-screen bg-bg text-gray-300 flex flex-col font-mono">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        
        {/* Page Title */}
        <div className="mb-8">
          <h1 className="font-serif text-3xl text-white font-normal tracking-tight">
            Preset Checklists
          </h1>
          <p className="font-mono text-[9px] uppercase tracking-widest text-gray-500 mt-1">
            Mode B: Predefined compliance requirements verification
          </p>
        </div>

        {/* Tab selection */}
        <div className="flex border-b border-borderCustom mb-8 text-[11px] uppercase tracking-wider font-bold select-none">
          <button
            onClick={() => setSelectedDomain('rbi_compliance')}
            className={`pb-3 px-6 border-b-2 transition-all duration-150 cursor-pointer ${
              selectedDomain === 'rbi_compliance' ? 'border-gold text-white font-bold' : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            RBI Regulations
          </button>
          <button
            onClick={() => setSelectedDomain('api_compliance')}
            className={`pb-3 px-6 border-b-2 transition-all duration-150 cursor-pointer ${
              selectedDomain === 'api_compliance' ? 'border-gold text-white font-bold' : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            API Specifications
          </button>
          <button
            onClick={() => setSelectedDomain('codebase')}
            className={`pb-3 px-6 border-b-2 transition-all duration-150 cursor-pointer ${
              selectedDomain === 'codebase' ? 'border-gold text-white font-bold' : 'border-transparent text-gray-500 hover:text-gray-300'
            }`}
          >
            Source Code
          </button>
        </div>

        {error && (
          <div className="bg-red/10 border border-red p-4 rounded-sm mb-6 flex items-start gap-3">
            <AlertTriangle className="w-4.5 h-4.5 text-red shrink-0 mt-0.5" />
            <div>
              <h3 className="text-white text-xs font-bold uppercase tracking-wider">Error Encountered</h3>
              <p className="text-[10px] uppercase text-red mt-1">{error}</p>
            </div>
          </div>
        )}

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left panel: Info & Run Action */}
          <div className="lg:col-span-4 space-y-6">
            
            <div className="bg-surface border border-borderCustom p-6 rounded-sm">
              <h2 className="text-xs font-bold text-white uppercase tracking-wider mb-3.5 flex items-center gap-2">
                <ClipboardList className="w-4.5 h-4.5 text-gold" />
                Audit Scope
              </h2>
              <p className="text-[11px] text-gray-400 leading-relaxed mb-6">
                Executing a checklist audit runs vector comparisons for all active preset guidelines in this category. The results are streamed live in the Diagnose panel, followed by a generated compliance report.
              </p>

              <div className="border border-borderCustom bg-bg p-4 rounded-sm text-[10px] space-y-3 mb-6">
                <div className="flex items-center justify-between">
                  <span className="text-gray-500">ACTIVE RULES:</span>
                  <span className="text-white font-bold">{questions.length}</span>
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-gray-500">CATEGORY:</span>
                  <span className="text-teal font-bold uppercase">{selectedDomain.replace('_', ' ')}</span>
                </div>
              </div>

              <button
                onClick={handleRunChecklist}
                disabled={loading || running || questions.length === 0}
                className="w-full flex items-center justify-center gap-2 border border-gold bg-gold/5 hover:bg-gold hover:text-black text-gold text-xs py-3 rounded-sm font-bold uppercase tracking-wider transition-all duration-150 disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
              >
                {running ? (
                  <>
                    <Loader2 className="w-4.5 h-4.5 animate-spin" />
                    <span>ENQUEUING AUDIT...</span>
                  </>
                ) : (
                  <>
                    <Play className="w-4.5 h-4.5" />
                    <span>RUN {questions.length} PRESETS SCAN</span>
                  </>
                )}
              </button>
            </div>

          </div>

          {/* Right panel: Preset List */}
          <div className="lg:col-span-8">
            <div className="bg-surface border border-borderCustom rounded-sm p-6">
              <h3 className="text-xs font-bold text-white uppercase tracking-wider border-b border-borderCustom pb-3.5 mb-4">
                {getDomainLabel(selectedDomain)}
              </h3>

              {loading ? (
                <div className="py-20 flex flex-col items-center justify-center gap-3">
                  <Loader2 className="w-5 h-5 text-gold animate-spin" />
                  <span className="text-[10px] text-gray-500 uppercase tracking-widest">LOADING PRESETS...</span>
                </div>
              ) : questions.length === 0 ? (
                <div className="py-20 text-center text-gray-500 text-xs">
                  NO ACTIVE PRESETS RECORDED FOR THIS DOMAIN
                </div>
              ) : (
                <div className="space-y-3.5 max-h-[600px] overflow-y-auto pr-1">
                  {questions.map((q, idx) => (
                    <div 
                      key={q.id} 
                      className="bg-bg border border-borderCustom/80 p-4 rounded-sm flex items-start gap-4 hover:border-gray-700 transition-colors duration-150"
                    >
                      <span className="text-[9px] text-gray-600 bg-surface border border-borderCustom px-2 py-0.5 rounded-sm">
                        #{idx + 1}
                      </span>
                      <div className="flex-1">
                        <p className="text-xs text-white leading-relaxed">{q.question_text}</p>
                      </div>
                      <ShieldCheck className="w-4.5 h-4.5 text-teal shrink-0 mt-0.5" />
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

        </div>

      </main>
    </div>
  )
}

import React, { useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { Navbar } from '../components/Navbar'
import { useJobStore } from '../stores/jobStore'
import { 
  Play, 
  FileText, 
  Eye, 
  CheckCircle, 
  Loader2, 
  RefreshCw 
} from 'lucide-react'

export const Dashboard: React.FC = () => {
  const navigate = useNavigate()
  const { jobs, fetchJobs, loading } = useJobStore()

  useEffect(() => {
    fetchJobs()
  }, [fetchJobs])

  const getStatusBadge = (status: string) => {
    switch (status) {
      case 'READY':
        return (
          <span className="border border-teal bg-teal/10 text-teal px-2 py-0.5 rounded-sm text-[8px] font-bold tracking-wider uppercase font-mono">
            READY
          </span>
        )
      case 'RUNNING':
        return (
          <span className="border border-gold bg-gold/10 text-gold px-2 py-0.5 rounded-sm text-[8px] font-bold tracking-wider uppercase font-mono flex items-center gap-1.5 w-max">
            <Loader2 className="w-2.5 h-2.5 animate-spin" />
            RUNNING
          </span>
        )
      case 'PENDING':
        return (
          <span className="border border-blue bg-blue/10 text-blue px-2 py-0.5 rounded-sm text-[8px] font-bold tracking-wider uppercase font-mono">
            PENDING
          </span>
        )
      case 'FAILED':
        return (
          <span className="border border-red bg-red/10 text-red px-2 py-0.5 rounded-sm text-[8px] font-bold tracking-wider uppercase font-mono">
            FAILED
          </span>
        )
      default:
        return (
          <span className="border border-gray-600 bg-gray-900 text-gray-400 px-2 py-0.5 rounded-sm text-[8px] font-bold tracking-wider uppercase font-mono">
            {status}
          </span>
        )
    }
  }

  const formatMode = (mode: string) => {
    switch (mode) {
      case 'file_upload':
        return 'POLICY FILE CHECK'
      case 'predefined_questions':
        return 'PRESET CHECKLIST'
      case 'github_clone':
        return 'GITHUB CODEBASE CLONE'
      default:
        return mode.toUpperCase().replace(/_/g, ' ')
    }
  }

  const formatAgent = (agent: string) => {
    switch (agent) {
      case 'rbi_compliance':
        return 'RBI REGULATIONS AGENT'
      case 'api_compliance':
        return 'API SPEC COMPLIANCE AGENT'
      case 'codebase':
        return 'SOURCE CODE COMPLIANCE AGENT'
      default:
        return agent.toUpperCase()
    }
  }

  return (
    <div className="min-h-screen bg-bg text-gray-300 flex flex-col">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8">
        
        {/* Page Title */}
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-8">
          <div>
            <h1 className="font-serif text-3xl text-white font-normal tracking-tight">
              Compliance Console
            </h1>
            <p className="font-mono text-[9px] uppercase tracking-widest text-gray-500 mt-1">
              Active operational runs and continuous validation logs
            </p>
          </div>

          <div className="flex gap-3">
            <button 
              onClick={() => fetchJobs()}
              className="flex items-center gap-2 border border-borderCustom hover:border-gray-700 px-4 py-2 text-xs font-mono tracking-wider uppercase rounded-sm transition-colors duration-150 cursor-pointer"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              <span>Refresh</span>
            </button>
            <button 
              onClick={() => navigate('/diagnose')}
              className="flex items-center gap-2 border border-gold bg-gold/5 text-gold hover:bg-gold hover:text-black px-4 py-2 text-xs font-mono tracking-wider uppercase rounded-sm transition-all duration-150 cursor-pointer"
            >
              <Play className="w-3.5 h-3.5" />
              <span>Run Diagnostic</span>
            </button>
          </div>
        </div>

        {/* Dashboard Cards / Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-8">
          
          <div className="bg-surface border border-borderCustom p-5 rounded-sm flex items-center justify-between">
            <div>
              <span className="block font-mono text-[9px] text-gray-500 uppercase tracking-widest">TOTAL AUDITS RUN</span>
              <span className="block font-mono text-3xl font-bold text-white mt-1.5">{jobs.length}</span>
            </div>
            <FileText className="w-8 h-8 text-gray-600" />
          </div>

          <div className="bg-surface border border-borderCustom p-5 rounded-sm flex items-center justify-between">
            <div>
              <span className="block font-mono text-[9px] text-gray-500 uppercase tracking-widest">ACTIVE AUDITS</span>
              <span className="block font-mono text-3xl font-bold text-gold mt-1.5">
                {jobs.filter(j => j.status === 'RUNNING' || j.status === 'PENDING').length}
              </span>
            </div>
            <Loader2 className="w-8 h-8 text-gold animate-spin" />
          </div>

          <div className="bg-surface border border-borderCustom p-5 rounded-sm flex items-center justify-between">
            <div>
              <span className="block font-mono text-[9px] text-gray-500 uppercase tracking-widest">READY REPORTS</span>
              <span className="block font-mono text-3xl font-bold text-teal mt-1.5">
                {jobs.filter(j => j.status === 'READY').length}
              </span>
            </div>
            <CheckCircle className="w-8 h-8 text-teal" />
          </div>

        </div>

        {/* Audit Runs Table */}
        <div className="bg-surface border border-borderCustom rounded-sm overflow-hidden">
          <div className="border-b border-borderCustom px-5 py-4 flex items-center justify-between">
            <span className="font-mono text-[10px] tracking-wider uppercase text-white font-bold">
              COMPLIANCE AUDIT PIPELINE LOG
            </span>
          </div>

          {loading && jobs.length === 0 ? (
            <div className="py-20 flex flex-col items-center justify-center gap-3">
              <Loader2 className="w-6 h-6 text-gold animate-spin" />
              <span className="font-mono text-xs text-gray-500">RETRIEVING HISTORICAL RUNS...</span>
            </div>
          ) : jobs.length === 0 ? (
            <div className="py-20 text-center">
              <span className="block font-mono text-xs text-gray-500 uppercase">No audits recorded. Start a new run to begin.</span>
            </div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-left font-mono text-xs border-collapse">
                <thead>
                  <tr className="border-b border-borderCustom text-gray-500 text-[9px] tracking-wider uppercase bg-bg/40 select-none">
                    <th className="px-5 py-3.5">Job ID</th>
                    <th className="px-5 py-3.5">Agent Type</th>
                    <th className="px-5 py-3.5">Execution Mode</th>
                    <th className="px-5 py-3.5">Status</th>
                    <th className="px-5 py-3.5">Created At</th>
                    <th className="px-5 py-3.5 text-right">Actions</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-borderCustom/50">
                  {jobs.map((job) => (
                    <tr key={job.id} className="hover:bg-bg/20 transition-colors duration-150">
                      <td className="px-5 py-4 font-bold text-white select-all">{job.id.substring(0, 8)}...</td>
                      <td className="px-5 py-4 text-gray-300">{formatAgent(job.agent_type)}</td>
                      <td className="px-5 py-4 text-gray-400">{formatMode(job.mode)}</td>
                      <td className="px-5 py-4">{getStatusBadge(job.status)}</td>
                      <td className="px-5 py-4 text-gray-500">
                        {new Date(job.created_at).toLocaleString()}
                      </td>
                      <td className="px-5 py-4 text-right">
                        <div className="flex items-center justify-end gap-2.5">
                          {(job.status === 'RUNNING' || job.status === 'PENDING') ? (
                            <button
                              onClick={() => navigate(`/diagnose?job_id=${job.id}`)}
                              className="border border-gold text-gold hover:bg-gold hover:text-black px-2.5 py-1 text-[10px] tracking-wider uppercase rounded-sm font-mono flex items-center gap-1 transition-all duration-150 cursor-pointer"
                            >
                              <Loader2 className="w-3 h-3 animate-spin" />
                              <span>Stream</span>
                            </button>
                          ) : (
                            <button
                              onClick={() => navigate(`/diagnose?job_id=${job.id}`)}
                              className="border border-borderCustom hover:border-gray-500 text-gray-300 px-2.5 py-1 text-[10px] tracking-wider uppercase rounded-sm font-mono flex items-center gap-1 transition-all duration-150 cursor-pointer"
                            >
                              <Eye className="w-3 h-3" />
                              <span>Inspect</span>
                            </button>
                          )}
                          
                          {job.report_url && (
                            <a
                              href={job.report_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="border border-teal bg-teal/5 text-teal hover:bg-teal hover:text-black px-2.5 py-1 text-[10px] tracking-wider uppercase rounded-sm font-mono flex items-center gap-1 transition-all duration-150"
                            >
                              <FileText className="w-3 h-3" />
                              <span>Report</span>
                            </a>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

      </main>
    </div>
  )
}

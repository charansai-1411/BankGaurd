import { create } from 'zustand'
import { api } from '../lib/api'
import { supabase } from '../lib/supabase'

export interface Job {
  id: string
  status: 'PENDING' | 'RUNNING' | 'READY' | 'FAILED'
  agent_type: string
  mode: string
  report_url: string | null
  created_at: string
}

export interface LogEvent {
  agent: string
  tool: string
  status: string
  message: string
  timestamp: string
}

export interface Finding {
  chunk_id: string
  regulation_text: string
  has_gap: boolean
  coverage_level: string
  gap_description: string
  cited_text: string
  validation_status: string
  severity: 'HIGH' | 'MEDIUM' | 'LOW' | string
}

interface JobState {
  jobs: Job[]
  activeJob: Job | null
  logs: LogEvent[]
  findings: Finding[]
  loading: boolean
  sseConnection: EventSource | null
  fetchJobs: () => Promise<void>
  fetchJobDetails: (jobId: string) => Promise<void>
  createJob: (agentType: string, mode: string) => Promise<string>
  connectSSE: (jobId: string) => void
  disconnectSSE: () => void
}

export const useJobStore = create<JobState>((set, get) => ({
  jobs: [],
  activeJob: null,
  logs: [],
  findings: [],
  loading: false,
  sseConnection: null,

  fetchJobs: async () => {
    set({ loading: true })
    try {
      const { data, error } = await supabase
        .from('jobs')
        .select('*')
        .order('created_at', { ascending: false })
      if (error) throw error
      set({ jobs: data || [] })
    } catch (err) {
      console.error('Error fetching jobs:', err)
    } finally {
      set({ loading: false })
    }
  },

  fetchJobDetails: async (jobId: string) => {
    try {
      const { data, error } = await supabase
        .from('jobs')
        .select('*')
        .eq('id', jobId)
        .single()
      if (error) throw error
      set({ activeJob: data })
    } catch (err) {
      console.error('Error fetching job details:', err)
    }
  },

  createJob: async (agentType: string, mode: string) => {
    try {
      const response = await api.post('/jobs/diagnose', {
        agent_type: agentType,
        mode
      })
      const job_id = response.data.job_id
      await get().fetchJobs()
      return job_id
    } catch (err) {
      console.error('Error creating job:', err)
      throw err
    }
  },

  connectSSE: (jobId: string) => {
    get().disconnectSSE()
    set({ logs: [], findings: [] })

    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000'
    const eventSource = new EventSource(`${baseUrl}/diagnose/stream/${jobId}`)

    eventSource.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data)
        const newLog: LogEvent = {
          agent: payload.agent || 'system',
          tool: payload.tool || 'info',
          status: payload.status || 'info',
          message: payload.message || '',
          timestamp: new Date().toLocaleTimeString()
        }

        set((state) => {
          const nextLogs = [...state.logs, newLog]
          const nextFindings = [...state.findings]

          if (payload.status === 'finding' && payload.data) {
            const exists = nextFindings.some(f => f.chunk_id === payload.data.chunk_id)
            if (!exists) {
              nextFindings.push(payload.data)
            }
          }

          return {
            logs: nextLogs,
            findings: nextFindings
          }
        })
        
        if (payload.status === 'done' && payload.agent === 'compile_report') {
          setTimeout(() => {
            get().fetchJobDetails(jobId)
            get().fetchJobs()
          }, 2000)
        }
      } catch (err) {
        console.error('Error parsing SSE message:', err)
      }
    }

    eventSource.onerror = (err) => {
      console.error('SSE connection error:', err)
      eventSource.close()
    }

    set({ sseConnection: eventSource })
  },

  disconnectSSE: () => {
    const { sseConnection } = get()
    if (sseConnection) {
      sseConnection.close()
      set({ sseConnection: null })
    }
  }
}))

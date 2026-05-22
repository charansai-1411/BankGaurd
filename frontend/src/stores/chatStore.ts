import { create } from 'zustand'
import { api } from '../lib/api'

export interface ChatMessage {
  role: 'user' | 'model'
  content: string
  citations?: string[]
}

interface ChatState {
  sessionId: string
  messages: ChatMessage[]
  loading: boolean
  setSessionId: (id: string) => void
  sendMessage: (text: string) => Promise<void>
  clearChat: () => void
}

export const useChatStore = create<ChatState>((set, get) => ({
  sessionId: 'session_' + Math.random().toString(36).substring(2, 9),
  messages: [],
  loading: false,

  setSessionId: (id: string) => set({ sessionId: id, messages: [] }),

  sendMessage: async (text: string) => {
    const { sessionId, messages } = get()
    
    const userMsg: ChatMessage = { role: 'user', content: text }
    set({ messages: [...messages, userMsg], loading: true })

    try {
      const response = await api.post('/chat/', {
        session_id: sessionId,
        message: text
      })

      const botMsg: ChatMessage = {
        role: 'model',
        content: response.data.response_text,
        citations: response.data.citations || []
      }

      set((state) => ({
        messages: [...state.messages, botMsg]
      }))
    } catch (err) {
      console.error('Error sending message:', err)
      const errorMsg: ChatMessage = {
        role: 'model',
        content: 'Error: Failed to fetch response from the gateway server. Please ensure the backend is running.'
      }
      set((state) => ({
        messages: [...state.messages, errorMsg]
      }))
    } finally {
      set({ loading: false })
    }
  },

  clearChat: () => {
    set({
      messages: [],
      sessionId: 'session_' + Math.random().toString(36).substring(2, 9)
    })
  }
}))

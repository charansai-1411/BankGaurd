import { create } from 'zustand'
import { supabase } from '../lib/supabase'
import type { User, Session } from '@supabase/supabase-js'

interface AuthState {
  user: User | null
  session: Session | null
  loading: boolean
  initialized: boolean
  loginWithGoogle: () => Promise<void>
  logout: () => Promise<void>
  initialize: () => Promise<void>
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  session: null,
  loading: true,
  initialized: false,
  loginWithGoogle: async () => {
    set({ loading: true })
    const { error } = await supabase.auth.signInWithOAuth({
      provider: 'google',
      options: {
        redirectTo: window.location.origin + '/dashboard'
      }
    })
    if (error) {
      console.error('Google Sign In Error:', error)
      set({ loading: false })
      throw error
    }
  },
  logout: async () => {
    set({ loading: true })
    const { error } = await supabase.auth.signOut()
    if (error) {
      console.error('Sign Out Error:', error)
    }
    set({ user: null, session: null, loading: false })
  },
  initialize: async () => {
    // Check active session
    const { data: { session } } = await supabase.auth.getSession()
    set({
      session,
      user: session?.user ?? null,
      loading: false,
      initialized: true
    })

    // Listen for auth state changes
    supabase.auth.onAuthStateChange((_event, session) => {
      set({
        session,
        user: session?.user ?? null,
        loading: false
      })
    })
  }
}))

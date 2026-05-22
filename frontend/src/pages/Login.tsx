import React, { useState } from 'react'
import { useAuthStore } from '../stores/authStore'
import { Shield, KeyRound, AlertCircle } from 'lucide-react'

export const Login: React.FC = () => {
  const { loginWithGoogle, loading } = useAuthStore()
  const [error, setError] = useState<string | null>(null)

  const handleLogin = async () => {
    setError(null)
    try {
      await loginWithGoogle()
    } catch (err: any) {
      setError(err?.message || 'Authentication redirection failed.')
    }
  }

  return (
    <div className="min-h-screen bg-bg flex items-center justify-center p-6 select-none">
      <div className="w-full max-w-md bg-surface border border-borderCustom p-8 rounded-sm text-center">
        
        {/* Shield Icon Decoration */}
        <div className="flex justify-center mb-6">
          <div className="border border-borderCustom p-4 rounded-sm bg-bg">
            <Shield className="w-10 h-10 text-gold" />
          </div>
        </div>

        {/* Title */}
        <h1 className="font-serif text-3xl font-normal tracking-tight text-white mb-2">
          BANK<span className="text-gold">GUARD</span>
        </h1>

        {/* Tagline */}
        <p className="font-mono text-[9px] uppercase tracking-widest text-gray-500 mb-8">
          AI-Powered RBI Banking Compliance Platform
        </p>

        {/* Error notification */}
        {error && (
          <div className="bg-red/10 border border-red p-3 mb-6 rounded-sm text-left flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-red shrink-0 mt-0.5" />
            <span className="font-mono text-[10px] text-red uppercase tracking-wider">{error}</span>
          </div>
        )}

        {/* Action Button */}
        <button
          onClick={handleLogin}
          disabled={loading}
          className="w-full flex items-center justify-center gap-3 bg-bg border border-borderCustom hover:border-gold hover:text-gold text-white font-mono text-xs tracking-wider uppercase py-3 px-4 rounded-sm transition-all duration-150 active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed cursor-pointer"
        >
          <KeyRound className="w-4 h-4" />
          <span>{loading ? 'AUTHENTICATING...' : 'ACCESS VIA GOOGLE OAUTH'}</span>
        </button>

        {/* Security Note */}
        <div className="mt-8 pt-6 border-t border-borderCustom font-mono text-[8px] text-gray-600 uppercase tracking-widest leading-normal">
          Authorized banking operators only. Access is monitored and logs are cryptographically sealed.
        </div>

      </div>
    </div>
  )
}

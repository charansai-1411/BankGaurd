import React from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '../stores/authStore'
import { Shield, LogOut } from 'lucide-react'

export const Navbar: React.FC = () => {
  const { user, logout } = useAuthStore()
  const navigate = useNavigate()

  const handleLogout = async () => {
    await logout()
    navigate('/login')
  }

  const activeStyle = "text-gold border-b border-gold"
  const inactiveStyle = "text-gray-400 hover:text-white border-b border-transparent transition-colors duration-150"

  return (
    <nav className="sticky top-0 z-50 w-full bg-surface border-b border-borderCustom px-6 py-4 font-mono select-none">
      <div className="max-w-7xl mx-auto flex items-center justify-between">
        
        {/* Brand Logo */}
        <div className="flex items-center gap-2 cursor-pointer" onClick={() => navigate('/dashboard')}>
          <Shield className="w-5 h-5 text-gold" />
          <span className="font-mono text-sm tracking-wider font-bold text-white">
            BANK<span className="text-gold">GUARD</span>
          </span>
        </div>

        {/* Navigation Links */}
        <div className="flex items-center gap-8 text-[11px] tracking-wider uppercase">
          <NavLink 
            to="/dashboard" 
            className={({ isActive }) => `${isActive ? activeStyle : inactiveStyle} pb-1`}
          >
            DASHBOARD
          </NavLink>
          <NavLink 
            to="/diagnose" 
            className={({ isActive }) => `${isActive ? activeStyle : inactiveStyle} pb-1`}
          >
            LIVE AUDIT
          </NavLink>
          <NavLink 
            to="/questions" 
            className={({ isActive }) => `${isActive ? activeStyle : inactiveStyle} pb-1`}
          >
            PRESET CHECKLIST
          </NavLink>
          <NavLink 
            to="/chat" 
            className={({ isActive }) => `${isActive ? activeStyle : inactiveStyle} pb-1`}
          >
            TERMINAL CHAT
          </NavLink>
        </div>

        {/* User Stats & Logout */}
        <div className="flex items-center gap-4 text-[10px]">
          {user && (
            <div className="hidden md:flex items-center gap-2 bg-bg border border-borderCustom px-3 py-1.5 rounded-sm">
              <span className="text-gray-500">OPERATOR:</span>
              <span className="text-teal font-medium">{user.email}</span>
            </div>
          )}
          <button 
            onClick={handleLogout}
            className="flex items-center gap-2 border border-borderCustom hover:border-red hover:text-red px-3 py-1.5 rounded-sm transition-colors duration-150 font-mono text-[10px] tracking-wider uppercase text-gray-400"
          >
            <LogOut className="w-3.5 h-3.5" />
            <span>EXIT</span>
          </button>
        </div>

      </div>
    </nav>
  )
}

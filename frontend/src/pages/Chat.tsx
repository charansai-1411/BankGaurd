import React, { useEffect, useRef, useState } from 'react'
import { Navbar } from '../components/Navbar'
import { useChatStore } from '../stores/chatStore'
import { Terminal, Send, Trash2, Cpu, FileText, ChevronRight, Loader2 } from 'lucide-react'

export const Chat: React.FC = () => {
  const { messages, sendMessage, loading, clearChat, sessionId } = useChatStore()
  const [inputVal, setInputVal] = useState('')
  const terminalEndRef = useRef<HTMLDivElement>(null)

  // Scroll to bottom of terminal whenever messages list updates
  useEffect(() => {
    terminalEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, loading])

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputVal.trim() || loading) return
    
    const text = inputVal.trim()
    setInputVal('')

    // Handle slash commands or simple terminal commands
    if (text.toLowerCase() === 'clear') {
      clearChat()
      return
    }

    await sendMessage(text)
  }

  // Format citations into readable badges
  const renderCitations = (citations: string[]) => {
    if (!citations || citations.length === 0) return null
    return (
      <div className="mt-3 pt-2.5 border-t border-borderCustom/50 flex flex-wrap items-center gap-2 select-none">
        <span className="text-[8px] text-gray-500 font-bold uppercase tracking-wider">CITATIONS:</span>
        {citations.map((cite, index) => {
          const parts = cite.split(':')
          const namespace = parts[0]
          const source = parts[1] || 'unknown'
          
          let nsColor = 'text-gold border-gold/30 bg-gold/5'
          if (namespace === 'codebase') {
            nsColor = 'text-teal border-teal/30 bg-teal/5'
          } else if (namespace === 'api_specs') {
            nsColor = 'text-blue border-blue/30 bg-blue/5'
          }

          return (
            <span 
              key={index}
              className={`border ${nsColor} px-2 py-0.5 rounded-sm text-[8px] font-mono tracking-wide flex items-center gap-1`}
            >
              <FileText className="w-2.5 h-2.5 shrink-0" />
              <span>{namespace.toUpperCase()}: {source}</span>
            </span>
          )
        })}
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-bg text-gray-300 flex flex-col font-mono">
      <Navbar />

      <main className="flex-1 max-w-7xl mx-auto w-full px-6 py-8 flex flex-col">
        
        {/* Page Title */}
        <div className="flex items-center justify-between gap-4 mb-6">
          <div>
            <h1 className="font-serif text-3xl text-white font-normal tracking-tight flex items-center gap-2.5">
              Compliance Terminal
            </h1>
            <p className="font-mono text-[9px] uppercase tracking-widest text-gray-500 mt-1">
              Mode C: Grounded retrieval conversational compliance sandbox
            </p>
          </div>

          <button 
            onClick={clearChat}
            className="flex items-center gap-2 border border-borderCustom hover:border-red hover:text-red px-3 py-1.5 text-xs font-mono tracking-wider uppercase rounded-sm transition-colors duration-150 cursor-pointer text-gray-400"
          >
            <Trash2 className="w-3.5 h-3.5" />
            <span>Reset Terminal</span>
          </button>
        </div>

        {/* Terminal Sandbox Shell */}
        <div className="flex-1 bg-surface border border-borderCustom rounded-sm flex flex-col overflow-hidden min-h-[500px] max-h-[calc(100vh-250px)]">
          
          {/* Terminal Title Bar */}
          <div className="bg-bg border-b border-borderCustom px-4 py-2.5 flex items-center justify-between select-none">
            <div className="flex items-center gap-2">
              <Terminal className="w-4 h-4 text-gold" />
              <span className="text-[10px] text-gray-400 font-bold uppercase tracking-wider">
                BANKGUARD SECURE SHELL v2.0
              </span>
            </div>
            <div className="flex items-center gap-1.5">
              <span className="w-2 h-2 rounded-full bg-teal animate-pulse-teal"></span>
              <span className="text-[9px] text-teal font-bold uppercase tracking-wider">CONNECTED</span>
            </div>
          </div>

          {/* Chat / Terminal Log window */}
          <div className="flex-1 overflow-y-auto p-5 space-y-4">
            
            {/* MOTD / Welcome message */}
            <div className="bg-bg border border-borderCustom p-4 rounded-sm text-[10px] text-gray-400 leading-relaxed font-mono">
              <div className="text-white font-bold mb-1 flex items-center gap-1.5 uppercase">
                <Cpu className="w-3.5 h-3.5 text-gold" />
                SYSTEM MESSAGE OF THE DAY (MOTD)
              </div>
              <p>Welcome to BankGuard grounded audit sandbox. Query RBI banking regulations, OpenAPI specifications, or source code compliance rules instantly.</p>
              <div className="text-gray-500 mt-2">
                SESSION ID: <span className="text-gold select-all">{sessionId}</span>
              </div>
              <div className="text-gray-500 mt-1">
                Enter command <span className="text-white font-bold">"clear"</span> or click reset to refresh chat history.
              </div>
            </div>

            {/* Messages */}
            {messages.map((msg, index) => {
              const isBot = msg.role === 'model'
              return (
                <div 
                  key={index} 
                  className={`flex flex-col ${isBot ? 'bg-bg/40 border border-borderCustom p-4 rounded-sm' : 'pl-2 border-l border-gold/40'}`}
                >
                  {/* Sender line */}
                  <div className="flex items-center gap-2 mb-1.5 select-none">
                    <span className="text-[9px] text-gray-500 font-bold">
                      {isBot ? 'BANKGUARD_COGNITIVE_CORE' : 'OPERATOR'}
                    </span>
                    <span className="text-[9px] text-gray-600">
                      {isBot ? '>> ANALYSIS COMPLETE' : '>> SENT'}
                    </span>
                  </div>

                  {/* Message body */}
                  <div className="text-xs text-gray-200 leading-relaxed whitespace-pre-wrap font-mono select-text">
                    {msg.content}
                  </div>

                  {/* Citations list */}
                  {isBot && msg.citations && renderCitations(msg.citations)}
                </div>
              )
            })}

            {/* Loading indicator */}
            {loading && (
              <div className="bg-bg/40 border border-borderCustom p-4 rounded-sm flex items-center gap-3">
                <Loader2 className="w-4 h-4 text-gold animate-spin" />
                <span className="text-[10px] text-gray-500 uppercase tracking-widest animate-pulse font-bold">
                  Evaluating vector namespaces and generating response...
                </span>
              </div>
            )}

            <div ref={terminalEndRef} />
          </div>

          {/* Command Input Form */}
          <form 
            onSubmit={handleSend}
            className="border-t border-borderCustom bg-bg px-4 py-3 flex items-center gap-3"
          >
            <div className="flex items-center gap-1.5 text-gold text-xs shrink-0 select-none">
              <span>operator@bankguard:~$</span>
              <ChevronRight className="w-3.5 h-3.5" />
            </div>
            
            <input
              type="text"
              value={inputVal}
              onChange={(e) => setInputVal(e.target.value)}
              placeholder="Ask compliance questions or enter 'clear'..."
              disabled={loading}
              className="flex-1 bg-transparent border-0 text-white text-xs font-mono outline-none placeholder-gray-600"
              autoFocus
            />

            <button
              type="submit"
              disabled={!inputVal.trim() || loading}
              className="border border-borderCustom hover:border-gold hover:text-gold text-white p-1.5 rounded-sm transition-colors duration-150 disabled:opacity-30 cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </form>

        </div>

      </main>
    </div>
  )
}
export default Chat

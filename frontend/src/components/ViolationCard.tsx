import React, { useState } from 'react'
import { ChevronDown, ChevronUp, CheckCircle2, XCircle, HelpCircle } from 'lucide-react'
import type { Finding } from '../stores/jobStore'

interface ViolationCardProps {
  finding: Finding
  index: number
}

export const ViolationCard: React.FC<ViolationCardProps> = ({ finding, index }) => {
  const [isOpen, setIsOpen] = useState(false)

  const severityColors: Record<string, { border: string; bg: string; text: string }> = {
    HIGH: { border: 'border-red', bg: 'bg-red/10', text: 'text-red' },
    CRITICAL: { border: 'border-red', bg: 'bg-red/10', text: 'text-red' },
    MEDIUM: { border: 'border-gold', bg: 'bg-gold/10', text: 'text-gold' },
    LOW: { border: 'border-blue', bg: 'bg-blue/10', text: 'text-blue' }
  }

  const sev = (finding.severity || 'MEDIUM').toUpperCase()
  const theme = severityColors[sev] || severityColors.MEDIUM

  const getValidationIcon = (status: string) => {
    switch (status) {
      case 'match':
        return <CheckCircle2 className="w-4 h-4 text-teal" />
      case 'mismatch':
        return <XCircle className="w-4 h-4 text-red" />
      case 'partial_match':
        return <HelpCircle className="w-4 h-4 text-gold" />
      default:
        return <HelpCircle className="w-4 h-4 text-gray-500" />
    }
  }

  const getValidationLabel = (status: string) => {
    switch (status) {
      case 'match':
        return 'VERIFIED MATCH'
      case 'mismatch':
        return 'CITATION MISMATCH'
      case 'partial_match':
        return 'PARTIAL ALIGNMENT'
      default:
        return 'UNVERIFIED'
    }
  }

  return (
    <div className={`bg-surface border border-borderCustom rounded-sm transition-all duration-150 overflow-hidden mb-3 hover:border-gray-700`}>
      
      {/* Header Info */}
      <div 
        className="p-4 flex items-center justify-between cursor-pointer select-none"
        onClick={() => setIsOpen(!isOpen)}
      >
        <div className="flex items-center gap-3.5 flex-1 min-w-0">
          
          {/* Index indicator */}
          <span className="text-[10px] text-gray-500 font-mono">
            #{String(index + 1).padStart(2, '0')}
          </span>

          {/* Severity Badge */}
          <span className={`border ${theme.border} ${theme.bg} ${theme.text} px-2 py-0.5 rounded-sm text-[8px] tracking-wider font-mono font-bold uppercase`}>
            {sev}
          </span>

          {/* Finding title / description snippet */}
          <div className="flex-1 min-w-0">
            <h4 className="text-white text-xs font-mono truncate">
              {finding.gap_description || 'Compliance vulnerability identified.'}
            </h4>
            <p className="text-gray-500 text-[10px] font-mono truncate mt-0.5">
              REG-ID: {finding.chunk_id || 'N/A'}
            </p>
          </div>

        </div>

        {/* Action icons */}
        <div className="flex items-center gap-3 ml-4">
          <div className="flex items-center gap-1.5 bg-bg border border-borderCustom px-2 py-1 rounded-sm text-[9px] font-mono">
            {getValidationIcon(finding.validation_status)}
            <span className="text-gray-400">{getValidationLabel(finding.validation_status)}</span>
          </div>
          {isOpen ? (
            <ChevronUp className="w-4 h-4 text-gray-400" />
          ) : (
            <ChevronDown className="w-4 h-4 text-gray-400" />
          )}
        </div>

      </div>

      {/* Expanded Content Drawer */}
      {isOpen && (
        <div className="border-t border-borderCustom bg-bg/50 p-4 font-mono text-xs space-y-4">
          
          {/* Regulation Mandate */}
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-widest mb-1.5">
              Target Regulation / Mandate
            </div>
            <div className="bg-bg border border-borderCustom p-3 rounded-sm text-gray-300 whitespace-pre-wrap leading-relaxed">
              {finding.regulation_text}
            </div>
          </div>

          {/* Detailed Vulnerability Description */}
          <div>
            <div className="text-[9px] text-gray-500 uppercase tracking-widest mb-1.5">
              Gap Analysis Findings
            </div>
            <div className="bg-bg border border-borderCustom p-3 rounded-sm text-gray-300 whitespace-pre-wrap leading-relaxed border-l-2 border-l-gold">
              {finding.gap_description}
            </div>
          </div>

          {/* Cited Evidence */}
          {finding.cited_text && (
            <div>
              <div className="text-[9px] text-gray-500 uppercase tracking-widest mb-1.5">
                Cited Document Evidence
              </div>
              <div className="bg-bg border border-borderCustom p-3 rounded-sm text-gray-300 font-mono text-[11px] overflow-x-auto whitespace-pre leading-normal">
                <code>{finding.cited_text}</code>
              </div>
            </div>
          )}

          {/* Audit Metadata */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-[10px] text-gray-500 bg-surface border border-borderCustom p-3 rounded-sm">
            <div>
              <span className="block text-gray-600 uppercase text-[8px] tracking-wider">COVERAGE LEVEL</span>
              <span className="text-white uppercase font-bold">{finding.coverage_level || 'NONE'}</span>
            </div>
            <div>
              <span className="block text-gray-600 uppercase text-[8px] tracking-wider">COMPLIANT</span>
              <span className={finding.has_gap ? 'text-red font-bold' : 'text-teal font-bold'}>
                {finding.has_gap ? 'NO' : 'YES'}
              </span>
            </div>
            <div>
              <span className="block text-gray-600 uppercase text-[8px] tracking-wider">VALIDATION STATUS</span>
              <span className="text-white uppercase">{finding.validation_status || 'UNVERIFIED'}</span>
            </div>
            <div>
              <span className="block text-gray-600 uppercase text-[8px] tracking-wider">SEVERITY FACTOR</span>
              <span className="text-white uppercase">{sev}</span>
            </div>
          </div>

        </div>
      )}

    </div>
  )
}

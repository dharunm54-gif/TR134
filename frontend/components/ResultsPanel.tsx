'use client'

import { useState } from 'react'
import {
  AlertTriangle, ShieldAlert, AlertOctagon, CheckCircle2,
  ChevronDown, ChevronUp, FlaskConical, Pill, Clock,
  BookOpen, ArrowLeft, MessageSquare, rotate3D, RefreshCw,
  Eye, TrendingUp, Database, Info
} from 'lucide-react'
import { Doughnut } from 'react-chartjs-2'
import { Chart as ChartJS, ArcElement, Tooltip, Legend } from 'chart.js'

ChartJS.register(ArcElement, Tooltip, Legend)

interface ResultsPanelProps {
  result: any
  mode: 'doctor' | 'patient'
  onNewAnalysis: () => void
  onOpenChat: () => void
}

const SEVERITY_CONFIG: Record<string, {
  icon: any; color: string; bg: string; border: string; badgeClass: string; glowClass: string; label: string
}> = {
  Contraindicated: {
    icon: AlertOctagon, color: '#ff2d55', bg: 'rgba(255,45,85,0.08)',
    border: 'rgba(255,45,85,0.3)', badgeClass: 'badge-contraindicated', glowClass: 'glow-contraindicated',
    label: '☠️ Contraindicated'
  },
  Major: {
    icon: ShieldAlert, color: '#ff6b35', bg: 'rgba(255,107,53,0.08)',
    border: 'rgba(255,107,53,0.3)', badgeClass: 'badge-major', glowClass: 'glow-major',
    label: '⚠️ Major'
  },
  Moderate: {
    icon: AlertTriangle, color: '#ffd60a', bg: 'rgba(255,214,10,0.06)',
    border: 'rgba(255,214,10,0.25)', badgeClass: 'badge-moderate', glowClass: 'glow-moderate',
    label: '⚡ Moderate'
  },
  Minor: {
    icon: CheckCircle2, color: '#34c759', bg: 'rgba(52,199,89,0.06)',
    border: 'rgba(52,199,89,0.2)', badgeClass: 'badge-minor', glowClass: 'glow-minor',
    label: '✓ Minor'
  },
}

const MECHANISM_LABELS: Record<string, string> = {
  CYP450_inhibition: '🧬 CYP450 Inhibition',
  CYP450_induction:  '🧬 CYP450 Induction',
  receptor_conflict: '⚡ Receptor Conflict',
  pharmacokinetic:   '🔄 Pharmacokinetic',
  pharmacodynamic:   '💊 Pharmacodynamic',
  transporter:       '🚂 Transporter Mediated',
  unknown:           '❓ Unknown Mechanism',
}

function InteractionCard({ ia, mode, idx }: { ia: any; mode: string; idx: number }) {
  const [expanded, setExpanded] = useState(idx === 0)
  const cfg = SEVERITY_CONFIG[ia.severity] || SEVERITY_CONFIG.Minor
  const Icon = cfg.icon

  return (
    <div
      className={`rounded-2xl overflow-hidden transition-all duration-300 animate-fade-in-up ${cfg.glowClass}`}
      style={{
        background: cfg.bg,
        border: `1px solid ${cfg.border}`,
        animationDelay: `${idx * 80}ms`
      }}
    >
      {/* Card Header */}
      <button
        className="w-full flex items-center gap-3 p-4 text-left"
        onClick={() => setExpanded(!expanded)}
      >
        <div className="w-9 h-9 flex items-center justify-center rounded-xl flex-shrink-0"
             style={{ background: `${cfg.color}20`, border: `1px solid ${cfg.color}35` }}>
          <Icon size={17} style={{ color: cfg.color }} />
        </div>

        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-white font-semibold text-sm">
              {ia.drug_pair?.join(' + ')}
            </span>
            <span className={cfg.badgeClass}>{ia.severity}</span>
            {ia.mechanism_type && (
              <span className="text-[0.67rem] px-2 py-0.5 rounded-md font-medium"
                    style={{ background: 'rgba(139,92,246,0.15)', color: '#a78bfa', border: '1px solid rgba(139,92,246,0.2)' }}>
                {MECHANISM_LABELS[ia.mechanism_type] || ia.mechanism_type}
              </span>
            )}
          </div>
          <p className="text-[0.75rem] text-gray-400 mt-0.5 truncate pr-4">
            {ia.clinical_risk}
          </p>
        </div>

        {/* Risk Score */}
        <div className="flex-shrink-0 flex flex-col items-center mr-2">
          <span className="text-lg font-bold" style={{ color: cfg.color }}>
            {ia.severity_score?.toFixed(1)}
          </span>
          <span className="text-[0.6rem] text-gray-600 uppercase">/ 10</span>
        </div>

        {expanded ? <ChevronUp size={15} className="text-gray-500 flex-shrink-0" />
                  : <ChevronDown size={15} className="text-gray-500 flex-shrink-0" />}
      </button>

      {/* Expanded Details */}
      {expanded && (
        <div className="px-4 pb-4 border-t space-y-3" style={{ borderColor: `${cfg.border}50` }}>
          {/* Risk Score Bar */}
          <div className="pt-3">
            <div className="flex items-center justify-between mb-1">
              <span className="text-[0.7rem] text-gray-500 uppercase tracking-wider">Risk Score</span>
              <span className="text-xs font-mono" style={{ color: cfg.color }}>{ia.severity_score?.toFixed(1)}/10</span>
            </div>
            <div className="risk-bar">
              <div className="risk-bar-fill" style={{ width: `${(ia.severity_score / 10) * 100}%`, background: cfg.color }} />
            </div>
          </div>

          {/* Mechanism */}
          <InfoRow icon={FlaskConical} label="Mechanism" color={cfg.color}>
            <p className="text-sm text-gray-300 leading-relaxed">{ia.mechanism}</p>
          </InfoRow>

          {/* Clinical Manifestation */}
          {ia.clinical_manifestation && (
            <InfoRow icon={Eye} label="Clinical Signs" color={cfg.color}>
              <p className="text-sm text-gray-300">{ia.clinical_manifestation}</p>
            </InfoRow>
          )}

          {/* Recommendation */}
          <InfoRow icon={ShieldAlert} label="Recommendation" color="#8b5cf6">
            <p className="text-sm text-purple-200 leading-relaxed font-medium">{ia.recommendation}</p>
          </InfoRow>

          {/* Dose Adjustment */}
          {ia.dose_adjustment && (
            <InfoRow icon={Clock} label="Dose Adjustment" color="#ffd60a">
              <p className="text-sm text-yellow-200">{ia.dose_adjustment}</p>
            </InfoRow>
          )}

          {/* Alternatives */}
          {ia.alternatives?.length > 0 && (
            <InfoRow icon={Pill} label="Safer Alternatives" color="#34c759">
              <div className="flex flex-wrap gap-1.5 mt-1">
                {ia.alternatives.map((alt: string, i: number) => (
                  <span key={i} className="text-xs px-2 py-0.5 rounded-md"
                        style={{ background: 'rgba(52,199,89,0.12)', color: '#34c759', border: '1px solid rgba(52,199,89,0.25)' }}>
                    {alt}
                  </span>
                ))}
              </div>
            </InfoRow>
          )}

          {/* Monitoring */}
          {ia.monitoring_parameters?.length > 0 && mode === 'doctor' && (
            <InfoRow icon={TrendingUp} label="Monitor" color="#00c7be">
              <div className="flex flex-wrap gap-1.5 mt-1">
                {ia.monitoring_parameters.map((p: string, i: number) => (
                  <span key={i} className="text-xs px-2 py-0.5 rounded-md"
                        style={{ background: 'rgba(0,199,190,0.1)', color: '#00c7be', border: '1px solid rgba(0,199,190,0.2)' }}>
                    {p}
                  </span>
                ))}
              </div>
            </InfoRow>
          )}

          {/* Evidence */}
          {ia.evidence?.length > 0 && (
            <InfoRow icon={BookOpen} label="Evidence Sources" color="#6b7280">
              <div className="space-y-1 mt-1">
                {ia.evidence.map((ev: any, i: number) => (
                  <div key={i} className="flex items-center gap-2">
                    <div className="w-1.5 h-1.5 rounded-full bg-purple-600 flex-shrink-0" />
                    <span className="text-[0.72rem] text-gray-500">
                      {ev.pubmed_id && `PubMed: ${ev.pubmed_id} · `}
                      {ev.source}
                      {ev.confidence_score && ` (confidence: ${Math.round(ev.confidence_score * 100)}%)`}
                    </span>
                  </div>
                ))}
              </div>
            </InfoRow>
          )}

          {/* Onset */}
          {ia.onset && (
            <div className="flex items-center gap-2 pt-1">
              <Clock size={12} className="text-gray-600" />
              <span className="text-[0.72rem] text-gray-500">
                Onset: <span className="text-gray-400 font-medium capitalize">{ia.onset}</span>
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}

function InfoRow({ icon: Icon, label, color, children }: any) {
  return (
    <div className="pt-2">
      <div className="flex items-center gap-1.5 mb-1">
        <Icon size={12} style={{ color }} />
        <span className="text-[0.7rem] font-semibold uppercase tracking-wider" style={{ color }}>
          {label}
        </span>
      </div>
      {children}
    </div>
  )
}

export default function ResultsPanel({ result, mode, onNewAnalysis, onOpenChat }: ResultsPanelProps) {
  const { risk_summary: rs, interactions, medications_analyzed, processing_time_ms } = result

  const donut = {
    labels: ['Contraindicated', 'Major', 'Moderate', 'Minor'],
    datasets: [{
      data: [rs.contraindicated_count, rs.major_count, rs.moderate_count, rs.minor_count],
      backgroundColor: ['rgba(255,45,85,0.85)', 'rgba(255,107,53,0.85)', 'rgba(255,214,10,0.75)', 'rgba(52,199,89,0.75)'],
      borderColor: ['#ff2d55', '#ff6b35', '#ffd60a', '#34c759'],
      borderWidth: 2,
    }]
  }

  const donutOpts = {
    responsive: true,
    cutout: '72%',
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15,15,26,0.95)',
        borderColor: 'rgba(139,92,246,0.4)',
        borderWidth: 1,
        titleColor: '#a78bfa',
        bodyColor: '#d1d5db',
      }
    }
  }

  const highestCfg = SEVERITY_CONFIG[rs.highest_severity] || SEVERITY_CONFIG.Minor

  return (
    <div className="p-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-5">
        <div>
          <div className="flex items-center gap-3 mb-1">
            <button onClick={onNewAnalysis} className="btn-ghost text-xs">
              <ArrowLeft size={13} /> New Analysis
            </button>
            <span className="text-gray-600">|</span>
            <span className="text-xs font-mono text-gray-500">{result.analysis_id}</span>
          </div>
          <h1 className="text-xl font-bold text-white">
            Interaction Analysis Results
          </h1>
          <p className="text-gray-400 text-xs mt-0.5">
            {medications_analyzed?.length} medications · {(processing_time_ms / 1000).toFixed(2)}s · {new Date(result.timestamp).toLocaleString()}
          </p>
        </div>
        <button onClick={onOpenChat} className="btn-primary text-sm">
          <MessageSquare size={14} />
          Ask AI Assistant
        </button>
      </div>

      {/* Summary Strip */}
      <div className="glass-card p-4 mb-5 animate-fade-in-up"
           style={{ borderColor: highestCfg.border, background: highestCfg.bg }}>
        {mode === 'patient' ? (
          <div className="flex items-start gap-3">
            <highestCfg.icon size={18} style={{ color: highestCfg.color, flexShrink: 0, marginTop: 2 }} />
            <div>
              <p className="text-sm font-semibold text-white mb-1">
                {interactions.length === 0 ? '✅ No interactions found' : `${interactions.length} interaction(s) detected`}
              </p>
              <p className="text-sm text-gray-300 leading-relaxed">{result.patient_friendly_summary}</p>
            </div>
          </div>
        ) : (
          <div className="flex items-start gap-3">
            <highestCfg.icon size={18} style={{ color: highestCfg.color, flexShrink: 0, marginTop: 2 }} />
            <div>
              <p className="text-sm font-semibold text-white mb-1">Clinical Summary</p>
              <p className="text-sm text-gray-300 leading-relaxed">{result.doctor_notes}</p>
            </div>
          </div>
        )}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5 mb-5">
        {/* Donut Chart */}
        <div className="glass-card p-5">
          <h2 className="text-sm font-semibold text-white mb-3">Risk Distribution</h2>
          <div className="relative" style={{ maxWidth: 160, margin: '0 auto' }}>
            <Doughnut data={donut} options={donutOpts} />
            <div className="absolute inset-0 flex flex-col items-center justify-center">
              <span className="text-2xl font-bold" style={{ color: highestCfg.color }}>
                {rs.overall_risk_score?.toFixed(1)}
              </span>
              <span className="text-[0.65rem] text-gray-500 uppercase">Risk/10</span>
            </div>
          </div>
          <div className="mt-4 space-y-1.5">
            {(['Contraindicated','Major','Moderate','Minor'] as const).map(sev => {
              const cfg = SEVERITY_CONFIG[sev]
              const count = rs[`${sev.toLowerCase()}_count`] ?? rs[`${sev === 'Contraindicated' ? 'contraindicated' : sev.toLowerCase()}_count`] ?? 0
              return (
                <div key={sev} className="flex items-center justify-between">
                  <div className="flex items-center gap-2">
                    <div className="w-2 h-2 rounded-full" style={{ background: cfg.color }} />
                    <span className="text-xs text-gray-400">{sev}</span>
                  </div>
                  <span className="text-xs font-semibold" style={{ color: cfg.color }}>
                    {sev === 'Contraindicated' ? rs.contraindicated_count :
                     sev === 'Major' ? rs.major_count :
                     sev === 'Moderate' ? rs.moderate_count : rs.minor_count}
                  </span>
                </div>
              )
            })}
          </div>
        </div>

        {/* Medications Analyzed */}
        <div className="glass-card p-5 lg:col-span-2">
          <h2 className="text-sm font-semibold text-white mb-3">Medications Analyzed</h2>
          <div className="flex flex-wrap gap-2 mb-4">
            {medications_analyzed?.map((drug: string, i: number) => (
              <span key={i} className="drug-tag">
                <Pill size={11} />
                {drug}
              </span>
            ))}
          </div>

          {result.insufficient_evidence_pairs?.length > 0 && (
            <div className="p-3 rounded-xl"
                 style={{ background: 'rgba(139,92,246,0.08)', border: '1px solid rgba(139,92,246,0.15)' }}>
              <div className="flex items-start gap-2">
                <Info size={13} className="text-purple-400 flex-shrink-0 mt-0.5" />
                <div>
                  <p className="text-xs font-medium text-purple-300 mb-1">Insufficient Evidence</p>
                  <p className="text-[0.72rem] text-gray-500">
                    No interaction data found for:{' '}
                    {result.insufficient_evidence_pairs.map((pair: string[]) => pair.join(' + ')).join('; ')}.
                    This does not guarantee safety — verify in DrugBank or consult a pharmacist.
                  </p>
                </div>
              </div>
            </div>
          )}

          <div className="mt-3 flex items-center gap-2 text-xs text-gray-600">
            <Database size={11} />
            <span>Data sources: {result.data_sources_used?.join(' · ') || 'DrugBank · PubMed · FDA'}</span>
          </div>
        </div>
      </div>

      {/* Interactions List */}
      {interactions.length === 0 ? (
        <div className="glass-card p-8 text-center">
          <CheckCircle2 size={40} className="text-green-400 mx-auto mb-3" />
          <p className="text-lg font-semibold text-white mb-2">No Known Interactions Detected</p>
          <p className="text-sm text-gray-400 max-w-md mx-auto">
            No clinically significant drug interactions were found among the analyzed medications.
            This analysis is based on verified medical literature. Consult a clinical pharmacist for comprehensive review.
          </p>
        </div>
      ) : (
        <div>
          <div className="flex items-center justify-between mb-3">
            <h2 className="text-sm font-semibold text-white">
              Detected Interactions ({interactions.length})
            </h2>
            <span className="text-xs text-gray-500">Sorted by severity score ↓</span>
          </div>
          <div className="space-y-3">
            {interactions.map((ia: any, i: number) => (
              <InteractionCard key={i} ia={ia} mode={mode} idx={i} />
            ))}
          </div>
        </div>
      )}

      {/* Action Footer */}
      <div className="mt-5 flex flex-wrap gap-3">
        <button onClick={onNewAnalysis} className="btn-ghost flex-1 justify-center">
          <RefreshCw size={14} /> Run New Analysis
        </button>
        <button onClick={onOpenChat} className="btn-primary flex-1 justify-center">
          <MessageSquare size={14} /> Ask AI About These Results
        </button>
      </div>
    </div>
  )
}

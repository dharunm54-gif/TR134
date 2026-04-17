'use client'

import { useEffect, useState } from 'react'
import { AlertTriangle, ShieldAlert, User, Pill, Clock, ChevronRight } from 'lucide-react'

const MOCK_HIGH_RISK = [
  {
    patient_id: 'P-001', name: 'John Martinez', age: 72, medication_count: 7,
    risk_level: 'Major', interaction_count: 3, last_analyzed: '2026-04-16T08:30:00Z',
    alerts: ['Warfarin + Aspirin', 'Digoxin + Amiodarone', 'Warfarin + Amiodarone']
  },
  {
    patient_id: 'P-002', name: 'Sarah Thompson', age: 64, medication_count: 5,
    risk_level: 'Contraindicated', interaction_count: 2, last_analyzed: '2026-04-16T09:15:00Z',
    alerts: ['Simvastatin + Clarithromycin', 'Sertraline + Phenelzine']
  },
  {
    patient_id: 'P-005', name: 'Michael Brown', age: 81, medication_count: 9,
    risk_level: 'Contraindicated', interaction_count: 4, last_analyzed: '2026-04-16T12:00:00Z',
    alerts: ['Oxycodone + Diazepam', 'Warfarin + Fluconazole', 'Allopurinol + Azathioprine']
  },
]

const RISK_CONFIG: Record<string, { color: string; badgeClass: string; icon: any }> = {
  Contraindicated: { color: '#ff2d55', badgeClass: 'badge-contraindicated', icon: ShieldAlert },
  Major:           { color: '#ff6b35', badgeClass: 'badge-major',           icon: AlertTriangle },
}

export default function HighRiskCases({ mode }: { mode: string }) {
  const [patients, setPatients] = useState(MOCK_HIGH_RISK)
  const [selected, setSelected] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/v1/patients/high-risk')
      .then(r => r.json())
      .then(data => { if (Array.isArray(data) && data.length) setPatients(data) })
      .catch(() => {})
  }, [])

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-1">🚨 High Risk Cases</h1>
        <p className="text-gray-400 text-sm">Patients with Major or Contraindicated drug interactions requiring immediate review</p>
      </div>

      <div className="space-y-3">
        {patients.map(patient => {
          const cfg = RISK_CONFIG[patient.risk_level] || RISK_CONFIG.Major
          const Icon = cfg.icon
          const isExpanded = selected === patient.patient_id

          return (
            <div
              key={patient.patient_id}
              className={`glass-card overflow-hidden transition-all duration-300 ${isExpanded ? 'ring-1' : ''}`}
              style={{ ...(isExpanded ? { ringColor: cfg.color } : {}) }}
            >
              <button
                className="w-full p-4 text-left flex items-center gap-4"
                onClick={() => setSelected(isExpanded ? null : patient.patient_id)}
              >
                <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
                     style={{ background: `${cfg.color}15`, border: `1px solid ${cfg.color}30` }}>
                  <Icon size={18} style={{ color: cfg.color }} />
                </div>

                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2 flex-wrap">
                    <span className="font-semibold text-white text-sm">{patient.name}</span>
                    <span className={cfg.badgeClass}>{patient.risk_level}</span>
                    <span className="text-xs text-gray-500 font-mono">{patient.patient_id}</span>
                  </div>
                  <div className="flex items-center gap-4 mt-1">
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <User size={10} /> Age {patient.age}
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Pill size={10} /> {patient.medication_count} meds
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <AlertTriangle size={10} /> {patient.interaction_count} interactions
                    </div>
                    <div className="flex items-center gap-1 text-xs text-gray-500">
                      <Clock size={10} /> {new Date(patient.last_analyzed).toLocaleDateString()}
                    </div>
                  </div>
                </div>

                <ChevronRight size={15} className={`text-gray-500 transition-transform ${isExpanded ? 'rotate-90' : ''}`} />
              </button>

              {isExpanded && (
                <div className="px-4 pb-4 border-t" style={{ borderColor: `${cfg.color}20` }}>
                  <p className="text-xs text-gray-500 font-semibold uppercase tracking-wider mb-2 pt-3">Drug Interaction Alerts</p>
                  <div className="space-y-2">
                    {patient.alerts.map((alert, i) => (
                      <div key={i} className="flex items-center gap-2 p-2.5 rounded-xl"
                           style={{ background: `${cfg.color}08`, border: `1px solid ${cfg.color}18` }}>
                        <div className="w-1.5 h-1.5 rounded-full flex-shrink-0" style={{ background: cfg.color }} />
                        <span className="text-sm text-gray-300">{alert}</span>
                        <span className={`ml-auto ${cfg.badgeClass}`}>{patient.risk_level}</span>
                      </div>
                    ))}
                  </div>
                  <button className="btn-primary mt-3 text-xs">
                    View Full Analysis →
                  </button>
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

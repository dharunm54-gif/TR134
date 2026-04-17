'use client'

import { useEffect, useState } from 'react'
import { Users, Search, Pill, AlertTriangle, Clock, Filter } from 'lucide-react'

const MOCK_PATIENTS = [
  { patient_id:'P-001', name:'John Martinez',   age:72, medication_count:7, risk_level:'Major',           interaction_count:3, last_analyzed:'2026-04-16T08:30:00Z', alerts:['Warfarin + Aspirin'] },
  { patient_id:'P-002', name:'Sarah Thompson',  age:64, medication_count:5, risk_level:'Contraindicated', interaction_count:2, last_analyzed:'2026-04-16T09:15:00Z', alerts:['Simvastatin + Clarithromycin'] },
  { patient_id:'P-003', name:'Robert Chen',     age:58, medication_count:4, risk_level:'Moderate',        interaction_count:1, last_analyzed:'2026-04-16T10:00:00Z', alerts:['Clopidogrel + Omeprazole'] },
  { patient_id:'P-004', name:'Emily Davis',     age:45, medication_count:3, risk_level:'Minor',           interaction_count:0, last_analyzed:'2026-04-16T11:30:00Z', alerts:[] },
  { patient_id:'P-005', name:'Michael Brown',   age:81, medication_count:9, risk_level:'Contraindicated', interaction_count:4, last_analyzed:'2026-04-16T12:00:00Z', alerts:['Oxycodone + Diazepam'] },
]

const SEVERITY_ORDER: Record<string,number> = { Contraindicated:0, Major:1, Moderate:2, Minor:3, Unknown:4 }
const BADGE_CLASS: Record<string,string> = {
  Contraindicated:'badge-contraindicated', Major:'badge-major', Moderate:'badge-moderate', Minor:'badge-minor'
}

export default function AllPatients({ mode }: { mode: string }) {
  const [patients, setPatients] = useState(MOCK_PATIENTS)
  const [search, setSearch] = useState('')
  const [filter, setFilter] = useState('all')

  useEffect(() => {
    fetch('/api/v1/patients')
      .then(r => r.json())
      .then(data => { if (Array.isArray(data) && data.length) setPatients(data) })
      .catch(() => {})
  }, [])

  const filtered = patients
    .filter(p => {
      const matchSearch = p.name.toLowerCase().includes(search.toLowerCase()) ||
                          p.patient_id.toLowerCase().includes(search.toLowerCase())
      const matchFilter = filter === 'all' || p.risk_level === filter
      return matchSearch && matchFilter
    })
    .sort((a, b) => (SEVERITY_ORDER[a.risk_level] ?? 4) - (SEVERITY_ORDER[b.risk_level] ?? 4))

  return (
    <div className="p-6 max-w-5xl mx-auto">
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-white mb-1">👥 All Patients</h1>
        <p className="text-gray-400 text-sm">Complete patient medication profiles and risk assessments</p>
      </div>

      {/* Search + Filter */}
      <div className="flex gap-3 mb-5">
        <div className="relative flex-1">
          <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-500" />
          <input
            type="text"
            className="form-input pl-9"
            placeholder="Search patients..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <div className="flex items-center gap-2">
          <Filter size={13} className="text-gray-500" />
          {['all','Contraindicated','Major','Moderate','Minor'].map(f => (
            <button
              key={f}
              onClick={() => setFilter(f)}
              className={`text-xs px-3 py-1.5 rounded-lg transition-all font-medium ${
                filter === f
                  ? 'bg-purple-700 text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
              style={filter !== f ? { background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)' } : {}}
            >
              {f === 'all' ? 'All' : f}
            </button>
          ))}
        </div>
      </div>

      {/* Table */}
      <div className="glass-card overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead>
              <tr style={{ borderBottom: '1px solid rgba(139,92,246,0.15)' }}>
                {['Patient', 'Age', 'Medications', 'Risk Level', 'Interactions', 'Alerts', 'Last Analysis'].map(h => (
                  <th key={h} className="text-left py-3 px-4 text-xs font-semibold text-gray-500 uppercase tracking-wider">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.map((p, i) => (
                <tr
                  key={p.patient_id}
                  className="transition-colors hover:bg-purple-900/10 cursor-pointer"
                  style={{ borderBottom: '1px solid rgba(255,255,255,0.04)', animationDelay: `${i*60}ms` }}
                >
                  <td className="py-3 px-4">
                    <div>
                      <p className="text-sm font-medium text-white">{p.name}</p>
                      <p className="text-xs text-gray-600 font-mono">{p.patient_id}</p>
                    </div>
                  </td>
                  <td className="py-3 px-4 text-sm text-gray-400">{p.age}</td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 text-sm text-gray-300">
                      <Pill size={12} className="text-purple-400" />
                      {p.medication_count}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <span className={BADGE_CLASS[p.risk_level] || 'badge-minor'}>{p.risk_level}</span>
                  </td>
                  <td className="py-3 px-4">
                    {p.interaction_count > 0 ? (
                      <div className="flex items-center gap-1.5 text-sm">
                        <AlertTriangle size={12} className="text-orange-400" />
                        <span className="text-orange-300 font-medium">{p.interaction_count}</span>
                      </div>
                    ) : (
                      <span className="text-xs text-green-400">None</span>
                    )}
                  </td>
                  <td className="py-3 px-4 max-w-xs">
                    <div className="flex flex-wrap gap-1">
                      {p.alerts.slice(0,2).map((a, j) => (
                        <span key={j} className="drug-tag text-[0.65rem] px-1.5 py-0.5">{a}</span>
                      ))}
                      {p.alerts.length > 2 && (
                        <span className="text-xs text-gray-600">+{p.alerts.length - 2} more</span>
                      )}
                    </div>
                  </td>
                  <td className="py-3 px-4">
                    <div className="flex items-center gap-1.5 text-xs text-gray-500">
                      <Clock size={10} />
                      {new Date(p.last_analyzed).toLocaleString('en-US', { month:'short', day:'numeric', hour:'2-digit', minute:'2-digit' })}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="px-4 py-3 border-t text-xs text-gray-600" style={{ borderColor: 'rgba(139,92,246,0.1)' }}>
          Showing {filtered.length} of {patients.length} patients
        </div>
      </div>
    </div>
  )
}

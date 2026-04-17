'use client'

import { useEffect, useState } from 'react'
import { PageView } from '@/app/page'
import {
  AlertTriangle, Shield, Activity, Users, TrendingUp,
  Zap, ArrowRight, Clock, Database
} from 'lucide-react'
import { Bar } from 'react-chartjs-2'
import {
  Chart as ChartJS, CategoryScale, LinearScale,
  BarElement, Title, Tooltip, Legend
} from 'chart.js'

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend)

interface DashboardProps {
  onNavigate: (page: PageView) => void
  mode: 'doctor' | 'patient'
}

const MOCK_STATS = {
  total_patients: 5,
  high_risk_patients: 3,
  interactions_detected_today: 10,
  average_medications_per_patient: 5.6,
  severity_distribution: { Contraindicated: 2, Major: 4, Moderate: 3, Minor: 1 },
  most_common_interactions: [
    { pair: 'Warfarin + Aspirin',           count: 12, severity: 'Major' },
    { pair: 'Simvastatin + Clarithromycin', count: 8,  severity: 'Contraindicated' },
    { pair: 'Clopidogrel + Omeprazole',     count: 7,  severity: 'Moderate' },
    { pair: 'Oxycodone + Diazepam',         count: 5,  severity: 'Major' },
    { pair: 'Allopurinol + Azathioprine',   count: 4,  severity: 'Contraindicated' },
  ],
  interactions_trend: [3, 5, 2, 7, 4, 6, 10],
}

const SEVERITY_CONFIG: Record<string, { color: string; bgClass: string; labelClass: string }> = {
  Contraindicated: { color: '#ff2d55', bgClass: 'badge-contraindicated', labelClass: 'text-red-400' },
  Major:           { color: '#ff6b35', bgClass: 'badge-major',           labelClass: 'text-orange-400' },
  Moderate:        { color: '#ffd60a', bgClass: 'badge-moderate',         labelClass: 'text-yellow-400' },
  Minor:           { color: '#34c759', bgClass: 'badge-minor',            labelClass: 'text-green-400' },
}

function StatCard({ icon: Icon, label, value, sub, color }: any) {
  return (
    <div className="stat-card flex items-start gap-3">
      <div className="w-10 h-10 rounded-xl flex items-center justify-center flex-shrink-0"
           style={{ background: `${color}18`, border: `1px solid ${color}30` }}>
        <Icon size={18} style={{ color }} />
      </div>
      <div>
        <p className="text-2xl font-bold text-white leading-tight">{value}</p>
        <p className="text-xs font-medium text-gray-400 mt-0.5">{label}</p>
        {sub && <p className="text-[0.7rem] text-gray-600 mt-0.5">{sub}</p>}
      </div>
    </div>
  )
}

export default function Dashboard({ onNavigate, mode }: DashboardProps) {
  const [stats, setStats] = useState(MOCK_STATS)
  const [loaded, setLoaded] = useState(false)

  useEffect(() => {
    setTimeout(() => setLoaded(true), 300)
    fetch('/api/v1/dashboard/stats')
      .then(r => r.json())
      .then(data => setStats({ ...MOCK_STATS, ...data }))
      .catch(() => {})
  }, [])

  const barData = {
    labels: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Today'],
    datasets: [{
      label: 'Interactions Detected',
      data: stats.interactions_trend,
      backgroundColor: 'rgba(139,92,246,0.5)',
      borderColor: 'rgba(139,92,246,0.9)',
      borderWidth: 2,
      borderRadius: 6,
      borderSkipped: false,
    }]
  }

  const barOptions = {
    responsive: true,
    plugins: {
      legend: { display: false },
      tooltip: {
        backgroundColor: 'rgba(15,15,26,0.95)',
        borderColor: 'rgba(139,92,246,0.4)',
        borderWidth: 1,
        titleColor: '#a78bfa',
        bodyColor: '#d1d5db',
      }
    },
    scales: {
      x: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#6b7280', font: { size: 11 } } },
      y: { grid: { color: 'rgba(255,255,255,0.04)' }, ticks: { color: '#6b7280', font: { size: 11 } }, beginAtZero: true },
    }
  }

  return (
    <div className={`p-6 max-w-7xl mx-auto transition-opacity duration-500 ${loaded ? 'opacity-100' : 'opacity-0'}`}>
      {/* Header */}
      <div className="flex items-start justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold text-white mb-1">
            {mode === 'doctor' ? '🩺 Clinical Dashboard' : '💊 My Health Overview'}
          </h1>
          <p className="text-gray-400 text-sm">
            Real-time polypharmacy risk monitoring · RAG-grounded analysis
          </p>
        </div>
        <button className="btn-primary" onClick={() => onNavigate('analyze')}>
          <Zap size={15} />
          Run Analysis
          <ArrowRight size={14} />
        </button>
      </div>

      {/* Alert Banner */}
      {stats.high_risk_patients > 0 && (
        <div className="mb-5 animate-fade-in-up"
             style={{ background: 'rgba(255,45,85,0.08)', border: '1px solid rgba(255,45,85,0.25)', borderRadius: 12, padding: '12px 16px' }}>
          <div className="flex items-center gap-3">
            <AlertTriangle size={16} className="text-red-400 flex-shrink-0" />
            <p className="text-sm text-red-300">
              <strong>{stats.high_risk_patients} patients</strong> have critical drug interactions requiring immediate review.{' '}
              <button onClick={() => onNavigate('high-risk')} className="underline text-red-400 hover:text-red-300">
                View cases →
              </button>
            </p>
          </div>
        </div>
      )}

      {/* Stat Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <StatCard icon={Users}         label="Total Patients"           value={stats.total_patients}                     color="#8b5cf6" />
        <StatCard icon={AlertTriangle} label="High Risk Patients"       value={stats.high_risk_patients}                 color="#ff2d55" />
        <StatCard icon={Activity}      label="Interactions Today"       value={stats.interactions_detected_today}        color="#ff6b35" />
        <StatCard icon={Shield}        label="Avg Medications / Patient" value={stats.average_medications_per_patient}   color="#34c759" />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-5 gap-4 mb-6">
        {/* Trend Chart */}
        <div className="glass-card p-5 lg:col-span-3">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-sm font-semibold text-white">Interactions Trend</h2>
              <p className="text-xs text-gray-500">Last 7 days</p>
            </div>
            <TrendingUp size={16} className="text-purple-400" />
          </div>
          <Bar data={barData} options={barOptions} height={120} />
        </div>

        {/* Severity Distribution */}
        <div className="glass-card p-5 lg:col-span-2">
          <h2 className="text-sm font-semibold text-white mb-4">Severity Breakdown</h2>
          <div className="space-y-3">
            {Object.entries(stats.severity_distribution).map(([severity, count]) => {
              const cfg = SEVERITY_CONFIG[severity]
              const total = Object.values(stats.severity_distribution).reduce((a: any, b: any) => a + b, 0)
              const pct = Math.round(((count as number) / total) * 100)
              return (
                <div key={severity}>
                  <div className="flex items-center justify-between mb-1">
                    <span className={`text-xs font-medium ${cfg.labelClass}`}>{severity}</span>
                    <span className="text-xs text-gray-400">{count as number} ({pct}%)</span>
                  </div>
                  <div className="risk-bar">
                    <div className="risk-bar-fill" style={{ width: `${pct}%`, background: cfg.color }} />
                  </div>
                </div>
              )
            })}
          </div>
          <div className="mt-4 pt-3 border-t border-purple-900/20">
            <div className="flex items-center gap-2 text-xs text-gray-500">
              <Database size={11} />
              <span>Sources: DrugBank · FAERS · PubMed</span>
            </div>
          </div>
        </div>
      </div>

      {/* Common Interactions Table */}
      <div className="glass-card p-5">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-sm font-semibold text-white">Most Common Interactions</h2>
          <span className="text-xs text-gray-500">Based on current patient population</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-purple-900/20">
                {['Drug Pair', 'Severity', 'Occurrences', 'Frequency'].map(h => (
                  <th key={h} className="text-left py-2 px-3 text-xs font-semibold text-gray-500 uppercase tracking-wider">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {stats.most_common_interactions.map((item, i) => {
                const cfg = SEVERITY_CONFIG[item.severity]
                const maxCount = stats.most_common_interactions[0].count
                return (
                  <tr key={i} className="border-b border-purple-900/10 hover:bg-purple-900/10 transition-colors">
                    <td className="py-2.5 px-3">
                      <span className="drug-tag">{item.pair}</span>
                    </td>
                    <td className="py-2.5 px-3">
                      <span className={cfg.bgClass}>{item.severity}</span>
                    </td>
                    <td className="py-2.5 px-3 text-gray-300 font-mono text-xs">{item.count}</td>
                    <td className="py-2.5 px-3 w-28">
                      <div className="risk-bar w-20">
                        <div className="risk-bar-fill" style={{ width: `${(item.count / maxCount) * 100}%`, background: cfg.color }} />
                      </div>
                    </td>
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-4">
        {[
          { label: 'Analyze New Patient', desc: 'Run interaction screening', icon: Activity, page: 'analyze' as PageView, color: '#8b5cf6' },
          { label: 'High Risk Cases',     desc: 'Review critical alerts',    icon: AlertTriangle, page: 'high-risk' as PageView, color: '#ff2d55' },
          { label: 'AI Chat Assistant',   desc: 'Ask clinical questions',    icon: Clock, page: 'chat' as PageView, color: '#34c759' },
        ].map(({ label, desc, icon: Icon, page, color }) => (
          <button
            key={page}
            onClick={() => onNavigate(page)}
            className="glass-card p-4 text-left hover:scale-[1.01] transition-transform duration-200 w-full group"
          >
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg flex items-center justify-center"
                   style={{ background: `${color}18`, border: `1px solid ${color}25` }}>
                <Icon size={16} style={{ color }} />
              </div>
              <div>
                <p className="text-sm font-semibold text-white group-hover:text-purple-300 transition-colors">{label}</p>
                <p className="text-xs text-gray-500 mt-0.5">{desc}</p>
              </div>
              <ArrowRight size={14} className="ml-auto text-gray-600 group-hover:text-purple-400 transition-colors" />
            </div>
          </button>
        ))}
      </div>
    </div>
  )
}

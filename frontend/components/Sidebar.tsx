'use client'

import { PageView } from '@/app/page'
import {
  LayoutDashboard, AlertTriangle, Users, MessageSquare,
  Pill, Activity, ShieldAlert, UserCog, ChevronRight
} from 'lucide-react'

interface SidebarProps {
  currentPage: PageView
  onNavigate: (page: PageView) => void
  mode: 'doctor' | 'patient'
  onModeToggle: () => void
}

const navItems = [
  { id: 'dashboard' as PageView,  label: 'Dashboard',       icon: LayoutDashboard },
  { id: 'analyze'   as PageView,  label: 'Analyze Patient', icon: Activity },
  { id: 'high-risk' as PageView,  label: 'High Risk Cases', icon: ShieldAlert },
  { id: 'patients'  as PageView,  label: 'All Patients',    icon: Users },
  { id: 'chat'      as PageView,  label: 'AI Assistant',    icon: MessageSquare },
]

export default function Sidebar({ currentPage, onNavigate, mode, onModeToggle }: SidebarProps) {
  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="p-5 border-b border-purple-900/30">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl flex items-center justify-center"
               style={{ background: 'linear-gradient(135deg,#7c3aed,#5b21b6)' }}>
            <Pill size={18} className="text-white" />
          </div>
          <div>
            <p className="text-white font-bold text-sm leading-tight">MediGuard</p>
            <p className="text-purple-400 text-xs font-medium">AI Risk Screener</p>
          </div>
        </div>
      </div>

      {/* Mode Toggle */}
      <div className="mx-3 mt-4 mb-2">
        <button
          onClick={onModeToggle}
          className="w-full flex items-center justify-between px-3 py-2.5 rounded-xl
                     border border-purple-800/30 transition-all duration-200 group"
          style={{ background: 'rgba(124,58,237,0.1)' }}
        >
          <div className="flex items-center gap-2">
            <UserCog size={14} className="text-purple-400" />
            <span className="text-xs font-semibold text-purple-300 uppercase tracking-wider">
              {mode === 'doctor' ? '🩺 Doctor Mode' : '🧑‍⚕️ Patient Mode'}
            </span>
          </div>
          <ChevronRight size={13} className="text-purple-500 group-hover:text-purple-300 transition-colors" />
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 py-2 space-y-0.5">
        <p className="px-4 pt-3 pb-1.5 text-[0.65rem] font-semibold text-gray-600 uppercase tracking-widest">
          Navigation
        </p>
        {navItems.map(({ id, label, icon: Icon }) => (
          <button
            key={id}
            onClick={() => onNavigate(id)}
            className={`nav-item w-full text-left ${currentPage === id ? 'active' : ''}`}
          >
            <Icon size={16} />
            <span>{label}</span>
          </button>
        ))}
      </nav>

      {/* Bottom info */}
      <div className="p-4 border-t border-purple-900/20">
        <div className="glass-card p-3">
          <p className="text-[0.68rem] text-gray-500 font-medium uppercase tracking-wider mb-1">Data Sources</p>
          <div className="space-y-1">
            {['DrugBank', 'FAERS', 'PubMed', 'FDA Labels'].map(src => (
              <div key={src} className="flex items-center gap-1.5">
                <div className="w-1.5 h-1.5 rounded-full bg-purple-500" />
                <span className="text-[0.72rem] text-gray-400">{src}</span>
              </div>
            ))}
          </div>
        </div>
        <p className="text-center text-[0.65rem] text-gray-600 mt-3">
          v1.0 · RAG-Grounded · No Hallucination
        </p>
      </div>
    </aside>
  )
}

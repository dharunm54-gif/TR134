'use client'

import { useState } from 'react'
import Sidebar from '@/components/Sidebar'
import Dashboard from '@/components/Dashboard'
import PatientForm from '@/components/PatientForm'
import ResultsPanel from '@/components/ResultsPanel'
import ChatAssistant from '@/components/ChatAssistant'
import HighRiskCases from '@/components/HighRiskCases'
import AllPatients from '@/components/AllPatients'

export type PageView = 'dashboard' | 'analyze' | 'high-risk' | 'patients' | 'chat'

export default function Home() {
  const [currentPage, setCurrentPage] = useState<PageView>('dashboard')
  const [analysisResult, setAnalysisResult] = useState<any>(null)
  const [mode, setMode] = useState<'doctor' | 'patient'>('doctor')

  const handleAnalysisComplete = (result: any) => {
    setAnalysisResult(result)
    setCurrentPage('analyze')
  }

  return (
    <div className="app-layout">
      <Sidebar
        currentPage={currentPage}
        onNavigate={setCurrentPage}
        mode={mode}
        onModeToggle={() => setMode(m => m === 'doctor' ? 'patient' : 'doctor')}
      />
      <main className="main-content">
        {currentPage === 'dashboard' && (
          <Dashboard onNavigate={setCurrentPage} mode={mode} />
        )}
        {currentPage === 'analyze' && !analysisResult && (
          <PatientForm onAnalysisComplete={handleAnalysisComplete} mode={mode} />
        )}
        {currentPage === 'analyze' && analysisResult && (
          <ResultsPanel
            result={analysisResult}
            mode={mode}
            onNewAnalysis={() => setAnalysisResult(null)}
            onOpenChat={() => setCurrentPage('chat')}
          />
        )}
        {currentPage === 'high-risk' && (
          <HighRiskCases mode={mode} />
        )}
        {currentPage === 'patients' && (
          <AllPatients mode={mode} />
        )}
        {currentPage === 'chat' && (
          <ChatAssistant mode={mode} analysisContext={analysisResult} />
        )}
      </main>
    </div>
  )
}

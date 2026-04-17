import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'MediGuard AI — Drug Interaction Risk Screener',
  description: 'AI-powered polypharmacy drug interaction detection system using RAG pipelines and verified medical databases. Safe, evidence-based clinical decision support.',
  keywords: 'drug interaction, polypharmacy, RAG, clinical decision support, medication safety',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  )
}

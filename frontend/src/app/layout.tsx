import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'ProtoForge - AI Prototyping Engine',
  description: 'AI-Powered Prototyping Super Agent Harness',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}

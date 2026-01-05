import './globals.css'
import type { Metadata } from 'next'

export const metadata: Metadata = {
  title: 'CryptoFS++ - AI-Governed File System',
  description: 'AI-powered, blockchain-audited virtual file system',
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


import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'ParseHub Dashboard',
  description: 'Real-time ParseHub project monitoring and management',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className="bg-slate-900 text-slate-100">{children}</body>
    </html>
  )
}

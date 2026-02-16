'use client'

import { useEffect, useState } from 'react'

export default function Header() {
  const [time, setTime] = useState<string>('')

  useEffect(() => {
    setTime(new Date().toLocaleTimeString())
    const interval = setInterval(() => {
      setTime(new Date().toLocaleTimeString())
    }, 1000)
    return () => clearInterval(interval)
  }, [])

  return (
    <header className="bg-gradient-to-r from-slate-800 to-slate-900 border-b border-slate-700 sticky top-0 z-50">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
              ParseHub Dashboard
            </h1>
            <p className="text-slate-400 mt-1">Real-time project monitoring & management</p>
          </div>
          <div className="text-right">
            <p className="text-xs text-slate-500 h-5">
              {time && `Last updated: ${time}`}
            </p>
          </div>
        </div>
      </div>
    </header>
  )
}

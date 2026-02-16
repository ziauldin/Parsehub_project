'use client'

import { useEffect, useState } from 'react'
import Modal from './Modal'

interface LogEntry {
  timestamp: string
  status: string
  pages: number
  message: string
}

interface LogsModalProps {
  isOpen: boolean
  onClose: () => void
  projectToken: string
  projectTitle: string
}

export default function LogsModal({
  isOpen,
  onClose,
  projectToken,
  projectTitle,
}: LogsModalProps) {
  const [logs, setLogs] = useState<LogEntry[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (isOpen) {
      fetchLogs()
    }
  }, [isOpen])

  const fetchLogs = async () => {
    setLoading(true)
    try {
      const response = await fetch(`/api/logs?token=${projectToken}`)
      if (response.ok) {
        const data = await response.json()
        setLogs(data.logs || [])
      }
    } catch (error) {
      console.error('Failed to fetch logs:', error)
      setLogs([
        {
          timestamp: new Date().toISOString(),
          status: 'error',
          pages: 0,
          message: 'Failed to fetch logs',
        },
      ])
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${projectTitle} - Monitoring Logs`}
      size="large"
    >
      <div className="space-y-4">
        {loading ? (
          <div className="text-center py-8">
            <p className="text-slate-400">Loading logs...</p>
          </div>
        ) : logs.length === 0 ? (
          <div className="text-center py-8">
            <p className="text-slate-400">No logs available yet</p>
            <p className="text-xs text-slate-500 mt-2">
              Logs will appear when the project runs
            </p>
          </div>
        ) : (
          <div className="space-y-2 font-mono text-xs">
            {logs.map((log, idx) => (
              <div
                key={idx}
                className="bg-slate-700/30 p-3 rounded border-l-2 border-blue-500"
              >
                <div className="flex items-start gap-2">
                  <span className="text-slate-500 flex-shrink-0">
                    [{new Date(log.timestamp).toLocaleTimeString()}]
                  </span>
                  <span
                    className={
                      log.status === 'complete'
                        ? 'text-green-400'
                        : log.status === 'running'
                          ? 'text-yellow-400'
                          : 'text-red-400'
                    }
                  >
                    {log.status.toUpperCase()}
                  </span>
                  <span className="text-slate-400 flex-grow">
                    {log.message}
                  </span>
                  {log.pages > 0 && (
                    <span className="text-blue-400 flex-shrink-0">
                      Pages: {log.pages}
                    </span>
                  )}
                </div>
              </div>
            ))}
          </div>
        )}

        <div className="mt-6 pt-4 border-t border-slate-700">
          <p className="text-xs text-slate-500">
            💡 Tip: Logs are generated during project runs. Run the project to see
            real-time monitoring data.
          </p>
        </div>
      </div>
    </Modal>
  )
}

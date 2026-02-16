'use client'

import { useState } from 'react'
import Modal from './Modal'
import { Download } from 'lucide-react'

interface ExportModalProps {
  isOpen: boolean
  onClose: () => void
  projectToken: string
  projectTitle: string
}

export default function ExportModal({
  isOpen,
  onClose,
  projectToken,
  projectTitle,
}: ExportModalProps) {
  const [exporting, setExporting] = useState<string | null>(null)
  const [message, setMessage] = useState<string | null>(null)

  const handleExport = async (format: string) => {
    setExporting(format)
    setMessage(null)

    try {
      const response = await fetch(`/api/export?token=${projectToken}&format=${format}`)

      if (response.ok) {
        const blob = await response.blob()
        const url = window.URL.createObjectURL(blob)
        const a = document.createElement('a')
        a.href = url

        const filename = `${projectTitle.replace(/\s+/g, '_')}_${new Date().getTime()}.${format === 'json' ? 'json' : 'csv'}`
        a.download = filename
        document.body.appendChild(a)
        a.click()
        document.body.removeChild(a)
        window.URL.revokeObjectURL(url)

        setMessage(`Successfully exported as ${format.toUpperCase()}`)
      } else {
        setMessage(`Error exporting as ${format.toUpperCase()}`)
      }
    } catch (error) {
      console.error('Export failed:', error)
      setMessage('Failed to export data')
    } finally {
      setExporting(null)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${projectTitle} - Export Data`}
    >
      <div className="space-y-6">
        <div>
          <h3 className="font-semibold text-white mb-4">Choose Export Format</h3>
          <div className="grid grid-cols-2 gap-4">
            <button
              onClick={() => handleExport('json')}
              disabled={exporting === 'json'}
              className="flex items-center justify-center gap-2 p-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 rounded-lg transition-all border border-slate-600 hover:border-slate-500 disabled:border-slate-700"
            >
              <Download className="w-5 h-5" />
              <div className="text-left">
                <p className="font-semibold text-white">JSON</p>
                <p className="text-xs text-slate-400">Native format</p>
              </div>
            </button>

            <button
              onClick={() => handleExport('csv')}
              disabled={exporting === 'csv'}
              className="flex items-center justify-center gap-2 p-4 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 rounded-lg transition-all border border-slate-600 hover:border-slate-500 disabled:border-slate-700"
            >
              <Download className="w-5 h-5" />
              <div className="text-left">
                <p className="font-semibold text-white">CSV</p>
                <p className="text-xs text-slate-400">Spreadsheet format</p>
              </div>
            </button>
          </div>
        </div>

        {message && (
          <div
            className={`p-4 rounded-lg text-sm font-medium ${
              message.includes('Success')
                ? 'bg-green-500/10 text-green-400 border border-green-500/20'
                : 'bg-red-500/10 text-red-400 border border-red-500/20'
            }`}
          >
            {message}
          </div>
        )}

        <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
          <h3 className="font-semibold text-white text-sm mb-2">Data Information</h3>
          <ul className="text-xs text-slate-400 space-y-1">
            <li>• Data file: <span className="text-slate-300">data_{projectToken}.json</span></li>
            <li>• Format: Depends on last run output configuration</li>
            <li>• Location: Server backend storage</li>
          </ul>
        </div>
      </div>
    </Modal>
  )
}

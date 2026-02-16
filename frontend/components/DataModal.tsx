'use client'

import { useState, useEffect } from 'react'
import { ChevronDown, ChevronRight, Database, Copy, Download } from 'lucide-react'
import Modal from './Modal'

interface DataRecord {
  key: string
  value: string
}

interface RunData {
  id: number
  run_token: string
  status: string
  pages: number
  start_time: string
  end_time: string
  records_count: number
  data: DataRecord[]
}

interface ProjectDataProps {
  token: string
  title: string
  isOpen: boolean
  onClose: () => void
}

export default function DataModal({ token, title, isOpen, onClose }: ProjectDataProps) {
  const [data, setData] = useState<any>(null)
  const [loading, setLoading] = useState(false)
  const [expandedRuns, setExpandedRuns] = useState<Set<number>>(new Set())
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen && token) {
      fetchData()
    }
  }, [isOpen, token])

  const fetchData = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/data?token=${token}`)
      if (!response.ok) {
        throw new Error('Failed to fetch data')
      }
      const result = await response.json()
      setData(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unknown error')
    } finally {
      setLoading(false)
    }
  }

  const toggleRun = (runId: number) => {
    const newSet = new Set(expandedRuns)
    if (newSet.has(runId)) {
      newSet.delete(runId)
    } else {
      newSet.add(runId)
    }
    setExpandedRuns(newSet)
  }

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text)
  }

  const downloadAsJson = () => {
    if (!data) return
    const dataStr = JSON.stringify(data, null, 2)
    const element = document.createElement('a')
    element.setAttribute('href', 'data:application/json;charset=utf-8,' + encodeURIComponent(dataStr))
    element.setAttribute('download', `${token}-data.json`)
    element.style.display = 'none'
    document.body.appendChild(element)
    element.click()
    document.body.removeChild(element)
  }

  if (!isOpen) return null

  return (
    <Modal isOpen={isOpen} onClose={onClose} title="Scraped Data" size="large">
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500"></div>
        </div>
      ) : error ? (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          Error: {error}
        </div>
      ) : data ? (
        <div className="space-y-6">
          {/* Header with download button */}
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Database className="w-5 h-5 text-blue-500" />
              <h3 className="text-lg font-semibold">{title}</h3>
            </div>
            <button
              onClick={downloadAsJson}
              className="flex items-center gap-2 px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition"
            >
              <Download className="w-4 h-4" />
              Download JSON
            </button>
          </div>

          {/* Runs list */}
          <div className="space-y-3">
            {data.runs && data.runs.length > 0 ? (
              data.runs.map((run: RunData) => (
                <div key={run.id} className="border border-gray-300 rounded-lg overflow-hidden">
                  {/* Run header */}
                  <button
                    onClick={() => toggleRun(run.id)}
                    className="w-full px-4 py-3 bg-gray-100 hover:bg-gray-200 transition flex items-center justify-between"
                  >
                    <div className="flex items-center gap-3 flex-1 text-left">
                      {expandedRuns.has(run.id) ? (
                        <ChevronDown className="w-5 h-5 text-gray-600" />
                      ) : (
                        <ChevronRight className="w-5 h-5 text-gray-600" />
                      )}
                      <div className="flex-1">
                        <div className="font-medium text-gray-800">{run.run_token}</div>
                        <div className="text-sm text-gray-600">
                          Records: {run.records_count} | Pages: {run.pages} | Status: {run.status}
                        </div>
                      </div>
                    </div>
                  </button>

                  {/* Run data */}
                  {expandedRuns.has(run.id) && (
                    <div className="bg-white border-t border-gray-300 p-4 max-h-96 overflow-y-auto">
                      {run.data && run.data.length > 0 ? (
                        <div className="space-y-3">
                          {run.data.map((record: DataRecord, idx: number) => (
                            <div key={idx} className="border border-gray-200 rounded p-3 hover:bg-gray-50 transition">
                              <div className="flex items-start justify-between gap-2">
                                <div className="flex-1 min-w-0">
                                  <div className="text-xs font-semibold text-gray-600 uppercase tracking-wide mb-1">
                                    {record.key}
                                  </div>
                                  <div className="text-sm text-gray-800 break-all font-mono text-xs bg-gray-100 p-2 rounded">
                                    {record.value}
                                  </div>
                                </div>
                                <button
                                  onClick={() => copyToClipboard(record.value)}
                                  className="mt-1 p-2 hover:bg-gray-200 rounded transition"
                                  title="Copy value"
                                >
                                  <Copy className="w-4 h-4 text-gray-600" />
                                </button>
                              </div>
                            </div>
                          ))}
                        </div>
                      ) : (
                        <div className="text-gray-500 text-sm text-center py-4">No data records found</div>
                      )}
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="text-gray-500 text-sm text-center py-8">No runs found for this project</div>
            )}
          </div>
        </div>
      ) : null}
    </Modal>
  )
}

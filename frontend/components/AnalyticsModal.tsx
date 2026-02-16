'use client'

import { useEffect, useState } from 'react'
import Modal from './Modal'
import { BarChart3, TrendingUp } from 'lucide-react'

interface Analytics {
  project_token: string
  total_runs: number
  completed_runs: number
  total_records: number
  avg_duration: number
  latest_run?: {
    run_token: string
    status: string
    pages_scraped: number
    start_time?: string
    records_count?: number
  } | null
  pages_trend?: Array<{
    pages_scraped: number
    start_time: string
  }>
}

interface AnalyticsModalProps {
  isOpen: boolean
  onClose: () => void
  projectToken: string
  projectTitle: string
}

export default function AnalyticsModal({
  isOpen,
  onClose,
  projectToken,
  projectTitle,
}: AnalyticsModalProps) {
  const [analytics, setAnalytics] = useState<Analytics | null>(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (isOpen) {
      fetchAnalytics()
    }
  }, [isOpen])

  const fetchAnalytics = async () => {
    setLoading(true)
    setError(null)
    try {
      const response = await fetch(`/api/analytics?token=${projectToken}`)
      if (response.ok) {
        const data = await response.json()
        setAnalytics(data)
      } else {
        setError('Failed to load analytics')
      }
    } catch (err) {
      console.error('Error fetching analytics:', err)
      setError('Failed to load analytics data')
    } finally {
      setLoading(false)
    }
  }

  return (
    <Modal
      isOpen={isOpen}
      onClose={onClose}
      title={`${projectTitle} - Analytics Dashboard`}
      size="large"
    >
      {loading ? (
        <div className="flex items-center justify-center py-12">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-400"></div>
          <p className="text-slate-400 ml-4">Loading analytics...</p>
        </div>
      ) : error ? (
        <div className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 text-red-400">
          {error}
        </div>
      ) : analytics ? (
        <div className="space-y-6">
          {/* Key Metrics */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <p className="text-slate-400 text-xs mb-1">Total Runs</p>
              <p className="text-2xl font-bold text-blue-400">
                {analytics.total_runs}
              </p>
            </div>
            <div className="bg-green-500/10 border border-green-500/20 rounded-lg p-4">
              <p className="text-slate-400 text-xs mb-1">Completed</p>
              <p className="text-2xl font-bold text-green-400">
                {analytics.completed_runs}
              </p>
            </div>
            <div className="bg-purple-500/10 border border-purple-500/20 rounded-lg p-4">
              <p className="text-slate-400 text-xs mb-1">Total Records</p>
              <p className="text-2xl font-bold text-purple-400">
                {analytics.total_records.toLocaleString()}
              </p>
            </div>
            <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-lg p-4">
              <p className="text-slate-400 text-xs mb-1">Avg Duration</p>
              <p className="text-2xl font-bold text-yellow-400">
                {analytics.avg_duration.toFixed(0)}s
              </p>
            </div>
          </div>

          {/* Success Rate */}
          {analytics.total_runs > 0 && (
            <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
              <h3 className="font-semibold text-white mb-3">Success Rate</h3>
              <div className="flex items-center gap-4">
                <div className="flex-1">
                  <div className="bg-slate-700 rounded-full h-2 overflow-hidden">
                    <div
                      className="bg-green-500 h-full"
                      style={{
                        width: `${(analytics.completed_runs / analytics.total_runs) * 100}%`,
                      }}
                    ></div>
                  </div>
                </div>
                <p className="text-sm font-semibold text-slate-200">
                  {(
                    (analytics.completed_runs / analytics.total_runs) *
                    100
                  ).toFixed(0)}
                  %
                </p>
              </div>
            </div>
          )}

          {/* Latest Run */}
          {analytics.latest_run && (
            <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
              <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                <TrendingUp className="w-4 h-4" />
                Latest Run
              </h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Status</span>
                  <span className="text-slate-200 font-mono">
                    {analytics.latest_run.status.toUpperCase()}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Pages Scraped</span>
                  <span className="text-slate-200 font-mono">
                    {analytics.latest_run.pages_scraped}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span className="text-slate-400">Records</span>
                  <span className="text-slate-200 font-mono">
                    {analytics.latest_run.records_count || 0}
                  </span>
                </div>
                {analytics.latest_run.start_time && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">Timestamp</span>
                    <span className="text-slate-200 text-xs">
                      {new Date(
                        analytics.latest_run.start_time
                      ).toLocaleString()}
                    </span>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Pages Trend */}
          {analytics.pages_trend && analytics.pages_trend.length > 0 && (
            <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
              <h3 className="font-semibold text-white mb-3 flex items-center gap-2">
                <BarChart3 className="w-4 h-4" />
                Pages Scraped (Last 10 Runs)
              </h3>
              <div className="space-y-2">
                {analytics.pages_trend.map((item, idx) => (
                  <div key={idx} className="flex items-center gap-2">
                    <span className="text-xs text-slate-500 w-24">
                      {new Date(item.start_time).toLocaleDateString()}
                    </span>
                    <div className="flex-1 bg-slate-700 rounded-full h-1.5">
                      <div
                        className="bg-blue-500 h-full rounded-full"
                        style={{
                          width: `${Math.min(
                            (item.pages_scraped / 100) * 100,
                            100
                          )}%`,
                        }}
                      ></div>
                    </div>
                    <span className="text-xs text-slate-300 w-12 text-right">
                      {item.pages_scraped}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Storage Info */}
          <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
            <h3 className="font-semibold text-white text-sm mb-2">Database Storage</h3>
            <p className="text-xs text-slate-400">
              All project data is automatically stored in SQLite database for persistent analytics and reporting.
            </p>
          </div>
        </div>
      ) : null}
    </Modal>
  )
}

'use client'

import Modal from './Modal'

interface StatsModalProps {
  isOpen: boolean
  onClose: () => void
  project: {
    token: string
    title: string
    last_run?: {
      pages: number
      status: string
      start_time: string
      end_time?: string
    } | null
  }
}

export default function StatsModal({
  isOpen,
  onClose,
  project,
}: StatsModalProps) {
  const calculateDuration = () => {
    if (!project.last_run?.start_time || !project.last_run?.end_time) {
      return 'N/A'
    }
    const start = new Date(project.last_run.start_time).getTime()
    const end = new Date(project.last_run.end_time).getTime()
    const seconds = Math.floor((end - start) / 1000)
    
    if (seconds < 60) return `${seconds}s`
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ${seconds % 60}s`
    return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`
  }

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`${project.title} - Statistics`}>
      <div className="space-y-6">
        {project.last_run ? (
          <>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-2">Total Pages</p>
                <p className="text-3xl font-bold text-blue-400">
                  {project.last_run.pages}
                </p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-2">Status</p>
                <p className="text-2xl font-bold text-green-400">
                  {project.last_run.status.toUpperCase()}
                </p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-2">Duration</p>
                <p className="text-2xl font-bold text-purple-400">
                  {calculateDuration()}
                </p>
              </div>
              <div className="bg-slate-700/50 rounded-lg p-4">
                <p className="text-slate-400 text-sm mb-2">Last Run</p>
                <p className="text-sm text-slate-300">
                  {new Date(project.last_run.start_time).toLocaleDateString()}
                  <br />
                  {new Date(project.last_run.start_time).toLocaleTimeString()}
                </p>
              </div>
            </div>

            <div className="bg-slate-700/20 rounded-lg p-4 border border-slate-700">
              <h3 className="font-semibold text-white mb-3">Run Details</h3>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span className="text-slate-400">Start Time</span>
                  <span className="text-slate-200">
                    {new Date(project.last_run.start_time).toLocaleString()}
                  </span>
                </div>
                {project.last_run.end_time && (
                  <div className="flex justify-between">
                    <span className="text-slate-400">End Time</span>
                    <span className="text-slate-200">
                      {new Date(project.last_run.end_time).toLocaleString()}
                    </span>
                  </div>
                )}
                <div className="flex justify-between">
                  <span className="text-slate-400">Pages Scraped</span>
                  <span className="text-slate-200 font-mono">
                    {project.last_run.pages}
                  </span>
                </div>
              </div>
            </div>
          </>
        ) : (
          <div className="text-center py-12">
            <p className="text-slate-400">No run data available</p>
          </div>
        )}
      </div>
    </Modal>
  )
}

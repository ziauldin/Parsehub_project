'use client'

import { useState } from 'react'
import { Play, Download, View, BarChart3, Database } from 'lucide-react'
import StatsModal from './StatsModal'
import DetailsModal from './DetailsModal'
import LogsModal from './LogsModal'
import ExportModal from './ExportModal'
import AnalyticsModal from './AnalyticsModal'
import DataModal from './DataModal'

interface Project {
  token: string
  title: string
  owner_email: string
  last_run: {
    status: string
    pages: number
    start_time: string
    run_token?: string
    end_time?: string
  } | null
}

interface ProjectsListProps {
  projects: Project[]
  onRefresh: () => void
}

interface ModalState {
  stats: boolean
  details: boolean
  logs: boolean
  export: boolean
  analytics: boolean
  data: boolean
}

export default function ProjectsList({ projects, onRefresh }: ProjectsListProps) {
  const [running, setRunning] = useState<string | null>(null)
  const [selectedProject, setSelectedProject] = useState<Project | null>(null)
  const [modals, setModals] = useState<ModalState>({
    stats: false,
    details: false,
    logs: false,
    export: false,
    analytics: false,
    data: false,
  })

  const handleRunProject = async (token: string) => {
    setRunning(token)
    try {
      const response = await fetch('/api/projects/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token }),
      })

      if (response.ok) {
        setTimeout(() => {
          onRefresh()
          setRunning(null)
        }, 1000)
      }
    } catch (error) {
      console.error('Failed to run project:', error)
      setRunning(null)
    }
  }

  const openModal = (modalName: keyof ModalState, project: Project) => {
    setSelectedProject(project)
    setModals({ ...modals, [modalName]: true })
  }

  const closeModal = (modalName: keyof ModalState) => {
    setModals({ ...modals, [modalName]: false })
  }

  const getStatusColor = (status: string | undefined) => {
    switch (status) {
      case 'running':
        return 'text-green-400 bg-green-400/10 border-green-400/20'
      case 'complete':
        return 'text-blue-400 bg-blue-400/10 border-blue-400/20'
      case 'queued':
        return 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20'
      case 'error':
        return 'text-red-400 bg-red-400/10 border-red-400/20'
      default:
        return 'text-slate-400 bg-slate-400/10 border-slate-400/20'
    }
  }

  const getStatusEmoji = (status: string | undefined) => {
    switch (status) {
      case 'running':
        return '🔄'
      case 'complete':
        return '✅'
      case 'queued':
        return '⏳'
      case 'error':
        return '❌'
      default:
        return '❓'
    }
  }

  if (projects.length === 0) {
    return (
      <div className="text-center py-12 bg-slate-800 rounded-lg border border-slate-700">
        <p className="text-slate-400">No projects found</p>
      </div>
    )
  }

  return (
    <div className="grid gap-4">
      {projects.map((project) => (
        <div
          key={project.token}
          className="bg-slate-800 rounded-lg p-6 border border-slate-700 hover:border-slate-600 transition-all"
        >
          <div className="flex items-start justify-between mb-4">
            <div className="flex-1">
              <h3 className="text-lg font-semibold text-white mb-1">
                {project.title}
              </h3>
              <p className="text-sm text-slate-400">{project.owner_email}</p>
              <p className="text-xs text-slate-500 font-mono mt-1">
                {project.token}
              </p>
            </div>
            <div className="text-right">
              {project.last_run && (
                <div
                  className={`inline-block px-3 py-1 rounded-full text-xs font-medium border ${getStatusColor(
                    project.last_run.status
                  )}`}
                >
                  {getStatusEmoji(project.last_run.status)} {project.last_run.status.toUpperCase()}
                </div>
              )}
            </div>
          </div>

          {project.last_run && (
            <div className="grid grid-cols-4 gap-4 mb-4 text-sm bg-slate-700/30 rounded p-3">
              <div>
                <p className="text-slate-500 text-xs">Pages</p>
                <p className="text-lg font-semibold text-white">
                  {project.last_run.pages}
                </p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Last Run</p>
                <p className="text-xs text-slate-300">
                  {new Date(project.last_run.start_time).toLocaleDateString()}
                </p>
                <p className="text-xs text-slate-400">
                  {new Date(project.last_run.start_time).toLocaleTimeString()}
                </p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Run Token</p>
                <p className="text-xs font-mono text-slate-300">
                  {project.last_run.run_token?.slice(0, 8) || 'N/A'}...
                </p>
              </div>
              <div>
                <p className="text-slate-500 text-xs">Duration</p>
                <p className="text-xs text-slate-300">
                  {project.last_run.status === 'running' ? '⏳ Running' : 'ℹ️ See logs'}
                </p>
              </div>
            </div>
          )}

          {!project.last_run && (
            <div className="text-sm text-slate-400 mb-4 bg-slate-700/30 rounded p-3">
              Never run before
            </div>
          )}

          <div className="flex gap-2 flex-wrap">
            <button
              onClick={() => handleRunProject(project.token)}
              disabled={running === project.token}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-slate-700 disabled:cursor-not-allowed rounded-lg font-medium transition-all text-sm"
            >
              <Play className="w-4 h-4" />
              {running === project.token ? 'Starting...' : 'Run Project'}
            </button>
            <button
              onClick={() => openModal('stats', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <BarChart3 className="w-4 h-4" />
              Stats
            </button>
            <button
              onClick={() => openModal('export', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <Download className="w-4 h-4" />
              Export
            </button>
            <button
              onClick={() => openModal('logs', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <View className="w-4 h-4" />
              Logs
            </button>
            <button
              onClick={() => openModal('analytics', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <BarChart3 className="w-4 h-4" />
              Analytics
            </button>
            <button
              onClick={() => openModal('data', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <Database className="w-4 h-4" />
              Data
            </button>
            <button
              onClick={() => openModal('details', project)}
              className="flex items-center gap-2 px-4 py-2 bg-slate-700 hover:bg-slate-600 rounded-lg font-medium transition-all text-sm"
            >
              <BarChart3 className="w-4 h-4" />
              Details
            </button>
          </div>
        </div>
      ))}

      {selectedProject && (
        <>
          <StatsModal
            isOpen={modals.stats}
            onClose={() => closeModal('stats')}
            project={selectedProject}
          />
          <DetailsModal
            isOpen={modals.details}
            onClose={() => closeModal('details')}
            project={selectedProject}
          />
          <LogsModal
            isOpen={modals.logs}
            onClose={() => closeModal('logs')}
            projectToken={selectedProject.token}
            projectTitle={selectedProject.title}
          />
          <ExportModal
            isOpen={modals.export}
            onClose={() => closeModal('export')}
            projectToken={selectedProject.token}
            projectTitle={selectedProject.title}
          />
          <AnalyticsModal
            isOpen={modals.analytics}
            onClose={() => closeModal('analytics')}
            projectToken={selectedProject.token}
            projectTitle={selectedProject.title}
          />
          <DataModal
            isOpen={modals.data}
            onClose={() => closeModal('data')}
            token={selectedProject.token}
            title={selectedProject.title}
          />
        </>
      )}
    </div>
  )
}

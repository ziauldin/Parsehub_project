import { NextRequest, NextResponse } from 'next/server'
import * as path from 'path'
import * as fs from 'fs'
import { execSync } from 'child_process'

// Get analytics by executing Python script
async function getAnalytics(token: string) {
  try {
    // Execute Python analytics script to get database info
    const pythonDir = path.resolve(process.cwd(), '..', '..')
    const pythonScriptPath = path.join(pythonDir, 'analytics.py')
    
    if (fs.existsSync(pythonScriptPath)) {
      try {
        const pythonExe = path.join(pythonDir, '.venv', 'Scripts', 'python.exe')
        if (fs.existsSync(pythonExe)) {
          const output = execSync(
            `"${pythonExe}" "${pythonScriptPath}" "${token}"`,
            { 
              cwd: pythonDir,
              encoding: 'utf-8',
              maxBuffer: 10 * 1024 * 1024,
              stdio: ['pipe', 'pipe', 'pipe']
            }
          )
          
          // Parse JSON output
          const data = JSON.parse(output.trim())
          if (data && !data.error) {
            return {
              project_token: token,
              total_runs: data.total_runs || 0,
              completed_runs: data.completed_runs || 0,
              total_records: data.total_records || 0,
              avg_duration: data.avg_duration || 0,
              latest_run: data.latest_run || {},
              pages_trend: data.pages_trend || [],
            }
          }
        }
      } catch (execError) {
        console.log('Python script error, falling back to JSON:', execError)
      }
    }
    
    // Fallback to monitoring results JSON
    const monitPath = path.join(process.cwd(), '..', 'monitoring_results.json')
    
    if (fs.existsSync(monitPath)) {
      const content = fs.readFileSync(monitPath, 'utf-8')
      const results = JSON.parse(content)

      if (results.project_data) {
        const projectData = results.project_data.find(
          (p: any) => p.token === token
        )

        if (projectData) {
          return {
            project_token: token,
            total_runs: 1,
            completed_runs: projectData.status === 'complete' ? 1 : 0,
            total_records: projectData.records || 0,
            avg_duration: 0,
            latest_run: {
              run_token: projectData.run_token,
              status: projectData.status,
              pages_scraped: projectData.pages_scraped || 0,
              records_count: projectData.records || 0,
            },
            pages_trend: [],
          }
        }
      }
    }

    return null
  } catch (error) {
    console.error('Error getting analytics:', error)
    return null
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const token = searchParams.get('token') || process.env.PARSEHUB_API_KEY

    if (!token) {
      return NextResponse.json(
        { error: 'Token is required' },
        { status: 400 }
      )
    }

    const analytics = await getAnalytics(token)

    if (!analytics) {
      return NextResponse.json(
        { error: 'No analytics data available' },
        { status: 404 }
      )
    }

    return NextResponse.json(analytics)
  } catch (error) {
    console.error('Error fetching analytics:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

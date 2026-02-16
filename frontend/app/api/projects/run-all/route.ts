import { NextResponse } from 'next/server'
import axios from 'axios'
import * as path from 'path'
import * as fs from 'fs'

const API_KEY = process.env.PARSEHUB_API_KEY || ''
const BASE_URL = process.env.PARSEHUB_BASE_URL || 'https://www.parsehub.com/api/v2'

function saveRunTokens(runsList: any[]) {
  try {
    const filePath = path.join(process.cwd(), '..', 'active_runs.json')
    const data: any = {
      timestamp: new Date().toISOString(),
      runs: []
    }
    
    for (const run of runsList) {
      if (run.run_token) {
        data.runs.push({
          token: run.token,
          project: run.project,
          run_token: run.run_token,
          status: 'started',
        })
      }
    }
    
    fs.writeFileSync(filePath, JSON.stringify(data, null, 2), 'utf-8')
    console.log(`Saved ${data.runs.length} run tokens to active_runs.json`)
    return true
  } catch (error) {
    console.error('Error saving run tokens:', error)
    return false
  }
}

export async function POST() {
  try {
    // Get all projects first
    const projectsResponse = await axios.get(`${BASE_URL}/projects`, {
      params: { api_key: API_KEY },
    })

    const projects = projectsResponse.data.projects || []
    const results = []

    // Run each project
    for (const project of projects) {
      try {
        const response = await axios.post(
          `${BASE_URL}/projects/${project.token}/run`,
          {},
          { params: { api_key: API_KEY } }
        )

        results.push({
          project: project.title,
          token: project.token,
          run_token: response.data.run_token,
          status: 'started',
        })

        // Small delay between requests
        await new Promise((resolve) => setTimeout(resolve, 500))
      } catch (error) {
        results.push({
          project: project.title,
          token: project.token,
          status: 'error',
          error: String(error),
        })
      }
    }

    // Save all run tokens for monitoring
    saveRunTokens(results)

    return NextResponse.json({ 
      success: true,
      results,
      message: `Started ${results.filter((r: any) => r.run_token).length} project runs`
    })
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Failed to run projects' },
      { status: 500 }
    )
  }
}

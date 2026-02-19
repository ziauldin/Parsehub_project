import { NextResponse } from 'next/server'
import axios from 'axios'

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:5000'
const BACKEND_API_KEY = process.env.BACKEND_API_KEY || 't_hmXetfMCq3'
const REQUEST_TIMEOUT = 300000 // 300 seconds (5 minutes) for pagination through all projects

export async function GET() {
  try {
    console.log('[API] Fetching projects from backend...')
    console.log(`[API] Backend URL: ${BACKEND_URL}`)

    // Backend will use its own API key - don't pass frontend's API key
    const response = await axios.get(`${BACKEND_URL}/api/projects`, {
      headers: {
        'Authorization': `Bearer ${BACKEND_API_KEY}`,
        'Content-Type': 'application/json'
      },
      timeout: REQUEST_TIMEOUT
    })

    const data = response.data
    console.log(`[API] Backend response status: ${response.status}`)
    console.log(`[API] Backend response keys: ${Object.keys(data)}`)
    
    // Handle new grouped format (by_website) or old flat format (projects)
    let projects = []
    let by_website = []
    
    if (data.by_website && Array.isArray(data.by_website)) {
      // New grouped format
      by_website = data.by_website
      console.log(`[API] Processing grouped format with ${by_website.length} website groups`)
      
      // Flatten projects from groups for compatibility
      for (const group of by_website) {
        if (group.projects && Array.isArray(group.projects)) {
          projects.push(...group.projects)
        }
      }
    } else if (data.projects && Array.isArray(data.projects)) {
      // Old flat format
      projects = data.projects
    }
    
    console.log(`[API] Total projects extracted: ${projects.length}`)
    console.log(`[API] Website groups: ${by_website.length}`)
    
    if (projects.length > 0) {
      console.log(`[API] First 3 projects: ${projects.slice(0, 3).map((p: any) => p.title || p.name || 'Unknown').join(', ')}`)
    }

    console.log(`[API] ✅ Successfully fetched ${projects.length} projects from backend`)
    
    const responsePayload = {
      success: true,
      total: projects.length,
      total_count: projects.length,
      by_website: by_website,
      projects: projects
    }
    
    console.log(`[API] Returning to frontend: ${responsePayload.projects.length} projects in ${responsePayload.by_website.length} groups`)
    
    return NextResponse.json(responsePayload)

  } catch (error) {
    console.error('[API] Error fetching projects:', error)
    
    if (axios.isAxiosError(error)) {
      if (error.code === 'ECONNREFUSED') {
        console.error('[API] ❌ Backend server not running on', BACKEND_URL)
        return NextResponse.json(
          { error: 'Backend server not running. Please start the Flask server.' },
          { status: 503 }
        )
      }
      if (error.response?.status === 401) {
        console.error('[API] ❌ Unauthorized - check API key')
        return NextResponse.json(
          { error: 'Unauthorized - invalid API key' },
          { status: 401 }
        )
      }
      if (error.code === 'ECONNABORTED') {
        console.error('[API] ❌ Request timeout - took longer than 30 seconds')
        return NextResponse.json(
          { error: 'Request timeout - pagination took too long' },
          { status: 504 }
        )
      }
    }

  }
}


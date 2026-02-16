import { NextRequest, NextResponse } from 'next/server'
import * as path from 'path'
import * as fs from 'fs'
import { execSync } from 'child_process'

async function getProjectData(token: string) {
  try {
    // Get data from JSON files instead
    const projectDir = path.join(process.cwd(), '..')
    const dataFile = path.join(projectDir, `data_${token}.json`)
    
    let data: any = {
      project: { token, title: token },
      runs: []
    }
    
    if (fs.existsSync(dataFile)) {
      try {
        const content = fs.readFileSync(dataFile, 'utf-8')
        const fileData = JSON.parse(content)
        
        // Parse the data file format - check for common key names
        let records: any[] = []
        
        if (Array.isArray(fileData)) {
          records = fileData
        } else if (typeof fileData === 'object' && fileData !== null) {
          // Check for array keys like 'product', 'data', 'items', etc.
          for (const key of ['product', 'data', 'items', 'results', 'records']) {
            if (Array.isArray(fileData[key])) {
              records = fileData[key]
              break
            }
          }
          
          // If still no records and object is not empty, convert to array
          if (records.length === 0 && Object.keys(fileData).length > 0) {
            records = [fileData]
          }
        }
        
        if (records.length > 0) {
          data.runs.push({
            id: 1,
            run_token: 'latest',
            status: 'complete',
            pages: 0,
            start_time: null,
            end_time: null,
            records_count: records.length,
            data: records.slice(0, 100).map((record, idx) => ({
              key: `Record ${idx + 1}`,
              value: typeof record === 'string' ? record : JSON.stringify(record, null, 2)
            }))
          })
        }
      } catch (e) {
        console.log('Error parsing data file:', e)
      }
    }
    
    return data.runs.length > 0 ? data : null
  } catch (error) {
    console.error('Error fetching data:', error)
    return null
  }
}

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url)
    const token = searchParams.get('token')

    if (!token) {
      return NextResponse.json(
        { error: 'Token is required' },
        { status: 400 }
      )
    }

    const data = await getProjectData(token)

    if (!data) {
      return NextResponse.json(
        { error: 'No data available' },
        { status: 404 }
      )
    }

    return NextResponse.json(data)
  } catch (error) {
    console.error('Error fetching data:', error)
    return NextResponse.json(
      { error: 'Internal server error' },
      { status: 500 }
    )
  }
}

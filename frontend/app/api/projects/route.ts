import { NextResponse } from 'next/server'
import axios from 'axios'

const API_KEY = process.env.PARSEHUB_API_KEY || ''
const BASE_URL = process.env.PARSEHUB_BASE_URL || 'https://www.parsehub.com/api/v2'

export async function GET() {
  try {
    const response = await axios.get(`${BASE_URL}/projects`, {
      params: { api_key: API_KEY },
    })

    const projects = response.data.projects || []

    return NextResponse.json({ projects })
  } catch (error) {
    console.error('API Error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch projects' },
      { status: 500 }
    )
  }
}

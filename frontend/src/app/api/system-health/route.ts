import { NextRequest, NextResponse } from 'next/server';

export async function GET() {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    const response = await fetch(`${apiUrl}/api/system-health`);
    
    if (!response.ok) {
      throw new Error(`Backend responded with status ${response.status}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Health proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to fetch system health from backend' },
      { status: 500 }
    );
  }
}

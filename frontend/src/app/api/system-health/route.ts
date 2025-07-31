import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl } from '@/config/api';

export async function GET(request: NextRequest) {
  try {
    const apiUrl = getApiUrl();
    const response = await fetch(`${apiUrl}/api/system-health`);
    
    if (!response.ok) {
      throw new Error(`Backend responded with ${response.status}: ${response.statusText}`);
    }
    
    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('System health proxy error:', error);
    return NextResponse.json(
      { 
        status: 'error',
        error: error instanceof Error ? error.message : 'Unknown error',
        timestamp: new Date().toISOString()
      },
      { status: 500 }
    );
  }
}

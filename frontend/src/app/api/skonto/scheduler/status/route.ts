import { NextRequest, NextResponse } from 'next/server';
import { getApiUrl } from '@/config/api';

export async function GET(request: NextRequest) {
  try {
    // Get backend URL with fallback
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.INTERNAL_API_URL || 'http://localhost:8000';
    const apiUrl = `${backendUrl}/api/skonto/scheduler/status`;
    
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(errorData, { status: response.status });
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Skonto scheduler status proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to fetch Skonto scheduler status' },
      { status: 500 }
    );
  }
}
import { NextRequest, NextResponse } from 'next/server';
import { buildApiUrl, API_CONFIG } from '@/config/api';

export async function GET(request: NextRequest) {
  try {
    // Extract query parameters
    const { searchParams } = new URL(request.url);
    const queryParams = new URLSearchParams(searchParams);
    
    const response = await fetch(`${buildApiUrl(API_CONFIG.ENDPOINTS.SKONTO.OPPORTUNITIES)}?${queryParams.toString()}`, {
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
    console.error('Skonto opportunities proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to fetch Skonto opportunities' },
      { status: 500 }
    );
  }
}

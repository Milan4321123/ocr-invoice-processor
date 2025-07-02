import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const { searchParams } = new URL(request.url);
    const urgency = searchParams.get('urgency') || 'all';
    const limit = searchParams.get('limit') || '100';
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const queryParams = new URLSearchParams();
    if (urgency) queryParams.append('urgency', urgency);
    if (limit) queryParams.append('limit', limit);
    
    const response = await fetch(`${apiUrl}/api/skonto/dashboard/opportunities?${queryParams.toString()}`, {
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

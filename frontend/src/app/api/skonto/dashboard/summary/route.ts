import { NextRequest, NextResponse } from 'next/server';

export async function GET(request: NextRequest) {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    const response = await fetch(`${apiUrl}/api/skonto/dashboard/summary`, {
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
    console.error('Skonto summary proxy error:', error);
    return NextResponse.json(
      { detail: 'Failed to fetch Skonto summary' },
      { status: 500 }
    );
  }
}

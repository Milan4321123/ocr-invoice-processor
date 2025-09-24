import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    // Try both JSON and FormData parsing
    let username: string;
    let password: string;
    
    const contentType = request.headers.get('content-type') || '';
    
    if (contentType.includes('application/json')) {
      const body = await request.json();
      username = body.username;
      password = body.password;
    } else {
      const formData = await request.formData();
      username = formData.get('username') as string;
      password = formData.get('password') as string;
    }
    
    if (!username || !password) {
      return NextResponse.json(
        { detail: 'Username and password are required' },
        { status: 400 }
      );
    }
    
    // Get backend URL with fallback
    const backendUrl = process.env.NEXT_PUBLIC_API_URL || process.env.INTERNAL_API_URL || 'http://localhost:8000';
    const loginUrl = `${backendUrl}/api/auth/login`;
    
    const formData = new URLSearchParams();
    formData.append('username', username);
    formData.append('password', password);
    
    const response = await fetch(loginUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });
    
    if (!response.ok) {
      const errorText = await response.text();
      console.error('Backend login error:', response.status, errorText);
      try {
        const errorData = JSON.parse(errorText);
        return NextResponse.json(errorData, { status: response.status });
      } catch {
        return NextResponse.json(
          { detail: `Backend error: ${response.status}` },
          { status: response.status }
        );
      }
    }

    // Success path: ensure response is JSON before parsing
    const respType = response.headers.get('content-type') || '';
    if (!respType.toLowerCase().includes('application/json')) {
      const text = await response.text();
      console.error('Unexpected non-JSON success from backend:', respType, text.slice(0, 200));
      return NextResponse.json(
        { detail: 'Unexpected response from backend', contentType: respType, bodyPreview: text.slice(0, 200) },
        { status: 502 }
      );
    }

    const data = await response.json();
    return NextResponse.json(data);
  } catch (error) {
    console.error('Login proxy error:', error);
    return NextResponse.json(
      { detail: 'Authentication failed' },
      { status: 500 }
    );
  }
}

import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const username = formData.get('username') as string;
    const password = formData.get('password') as string;
    
    if (!username || !password) {
      return NextResponse.json(
        { detail: 'Username and password are required' },
        { status: 400 }
      );
    }
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Forward the login request to the backend
    const backendFormData = new FormData();
    backendFormData.append('username', username);
    backendFormData.append('password', password);
    
    const response = await fetch(`${apiUrl}/api/auth/login`, {
      method: 'POST',
      body: backendFormData,
    });
    
    if (!response.ok) {
      const errorData = await response.json();
      return NextResponse.json(errorData, { status: response.status });
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

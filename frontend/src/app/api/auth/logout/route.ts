import { NextRequest, NextResponse } from 'next/server';

export async function POST(request: NextRequest) {
  try {
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    const response = await fetch(`${apiUrl}/logout`, {
      method: 'POST',
      headers: authHeader ? {
        'Authorization': authHeader,
      } : {},
    });
    
    // Return success regardless of backend response for logout
    return NextResponse.json({ success: true, message: 'Logged out successfully' });
  } catch (error) {
    console.error('Logout proxy error:', error);
    // Return success even if backend fails for logout
    return NextResponse.json({ success: true, message: 'Logged out successfully' });
  }
}

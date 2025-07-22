import { NextRequest, NextResponse } from 'next/server';
import { buildApiUrl, API_CONFIG } from '@/config/api';

export async function POST(request: NextRequest) {
  try {
    // Get the authorization header
    const authHeader = request.headers.get('authorization');
    
    const response = await fetch(buildApiUrl(API_CONFIG.ENDPOINTS.AUTH.LOGOUT), {
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

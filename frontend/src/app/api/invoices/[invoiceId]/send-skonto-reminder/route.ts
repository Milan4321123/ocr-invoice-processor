import { NextRequest, NextResponse } from 'next/server';

export async function POST(
  request: NextRequest,
  { params }: { params: { invoiceId: string } }
) {
  try {
    const { invoiceId } = params;
    
    // Get the search params for optional recipient_email and recipient_name
    const { searchParams } = new URL(request.url);
    const recipientEmail = searchParams.get('recipient_email');
    const recipientName = searchParams.get('recipient_name');
    
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    
    // Build the query string
    const queryParams = new URLSearchParams();
    if (recipientEmail) queryParams.append('recipient_email', recipientEmail);
    if (recipientName) queryParams.append('recipient_name', recipientName);
    
    const queryString = queryParams.toString();
    const endpoint = `${apiUrl}/api/invoices/${invoiceId}/send-skonto-reminder${queryString ? `?${queryString}` : ''}`;
    
    const response = await fetch(endpoint, {
      method: 'POST',
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
    console.error('Send skonto reminder proxy error:', error);
    return NextResponse.json(
      { error: 'Failed to send skonto reminder' },
      { status: 500 }
    );
  }
}

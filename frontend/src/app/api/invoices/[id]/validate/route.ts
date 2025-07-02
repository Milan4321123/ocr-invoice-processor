import { NextRequest, NextResponse } from 'next/server';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const resolvedParams = await params;
    const invoiceId = resolvedParams.id;

    // Basic validation
    if (!invoiceId || invoiceId.trim() === '') {
      return NextResponse.json(
        { error: 'Invalid invoice ID' },
        { status: 400 }
      );
    }

    // TODO: Replace with actual validation logic
    // For now, we'll do a simple check against the backend
    const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000';
    const response = await fetch(`${backendUrl}/api/invoices/${invoiceId}/validate`, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        // TODO: Add authentication headers
      },
    });

    if (response.status === 404) {
      return NextResponse.json(
        { error: 'Invoice not found' },
        { status: 404 }
      );
    }

    if (!response.ok) {
      throw new Error(`Backend API error: ${response.statusText}`);
    }

    const data = await response.json();
    return NextResponse.json({ valid: true, ...data });

  } catch (error) {
    console.error('Error validating invoice:', error);
    return NextResponse.json(
      { error: 'Failed to validate invoice' },
      { status: 500 }
    );
  }
}

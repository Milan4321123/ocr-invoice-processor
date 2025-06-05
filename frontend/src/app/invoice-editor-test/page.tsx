'use client';

import React from 'react';
import InvoiceEditorDashboard from '../../components/InvoiceEditorDashboard';
import { GermanInvoiceFields, ConfidenceScores } from '../../components/InvoiceForm';

export default function InvoiceEditorTestPage() {
  // Mock data for testing
  const mockInvoiceData = {
    pdfUrl: '/test_invoice_1748551760.pdf', // Use one of the test PDFs
    fields: {
      rechnungsempfaenger: 'ACME Construction GmbH',
      rechnungssteller: 'Test Vendor Services',
      projekt: 'Residential Building Project',
      gewerk: 'Electrical Installation',
      rechnungsbetrag: 15750.50,
      rechnungseingang: '2025-05-30',
      faelligkeit: '2025-06-29',
      skonto_datum: '2025-06-09',
      skonto_prozent: 2.0,
      rechnungsart: 'rechnung',
      kfw_anrechenbar: true,
      rechnungspruefung_email: 'review@acme-construction.de',
      weiter_berechnen_an: 'Client Invoice Department'
    } as GermanInvoiceFields,
    confidenceScores: {
      rechnungsempfaenger: 0.95,
      rechnungssteller: 0.88,
      projekt: 0.75,
      gewerk: 0.82,
      rechnungsbetrag: 0.98,
      rechnungseingang: 0.92,
      faelligkeit: 0.89,
      skonto_datum: 0.76,
      skonto_prozent: 0.85,
      rechnungsart: 0.91,
      kfw_anrechenbar: 0.68,
      rechnungspruefung_email: 0.45,
      weiter_berechnen_an: 0.52
    } as ConfidenceScores,
    filename: 'test_invoice_1748551760.pdf'
  };

  return (
    <InvoiceEditorDashboard 
      invoiceId="test-123"
      initialData={mockInvoiceData}
    />
  );
}

# Google Cloud Billing Setup Guide

## Enable Billing for OCR Functionality

To complete the OCR implementation, you need to enable billing on your Google Cloud project.

### Step 1: Enable Billing
1. Visit: https://console.developers.google.com/billing/enable?project=ocr-implementation-461310
2. Select or create a billing account
3. Enable billing for the project
4. Wait 5-10 minutes for changes to propagate

### Step 2: Verify Document AI API
1. Go to: https://console.cloud.google.com/apis/library/documentai.googleapis.com?project=ocr-implementation-461310
2. Ensure the Document AI API is enabled
3. If not enabled, click "ENABLE"

### Step 3: Test OCR Functionality
```bash
# Upload a test invoice
curl -X POST "http://localhost:8000/upload" \
  -F "file=@20250529_INV001_TESTVENDOR_SERVICE.pdf"

# Should return success: true with extracted data
```

### Step 4: Check OCR Status
```bash
curl -X GET "http://localhost:8000/ocr/status"
# Should show service_available: true
```

## Cost Information

### Document AI Pricing (EU region)
- **Form Parser**: €0.50 per page for first 500 pages/month
- **Layout Parser**: €1.50 per page for first 500 pages/month
- **Free Tier**: 1,000 pages per month across all processors

### Estimated Costs
- **Small usage** (10 invoices/day): ~€15-45/month
- **Medium usage** (50 invoices/day): ~€75-225/month
- **Large usage** (200 invoices/day): ~€300-900/month

*Actual costs depend on:*
- Number of pages per document
- Which parsers are used
- Total monthly volume

## Free Tier Usage
For testing and small volumes, the free tier provides:
- 1,000 pages/month free
- Perfect for evaluation and small deployments

## Security Notes
- Service account key is already configured
- Permissions are minimal (Document AI access only)
- No additional security setup required

## Support
- Google Cloud Documentation: https://cloud.google.com/document-ai/docs
- Billing Support: https://cloud.google.com/support

Once billing is enabled, the OCR system will be fully operational! 🚀

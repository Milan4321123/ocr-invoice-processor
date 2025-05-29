# Google Cloud Document AI Setup Guide

This guide will help you set up Google Cloud Document AI for OCR functionality in the invoice processing application.

## Prerequisites

- Google Cloud Platform account
- Access to billing (Document AI requires a paid project)
- Administrative permissions to create projects and enable APIs

## Step 1: Create a Google Cloud Project

1. Go to the [Google Cloud Console](https://console.cloud.google.com/)
2. Click "Select a project" at the top of the page
3. Click "New Project"
4. Enter a project name (e.g., "invoice-ocr-processor")
5. Select your billing account
6. Click "Create"

## Step 2: Enable Required APIs

1. In the Google Cloud Console, navigate to "APIs & Services" > "Library"
2. Search for and enable the following APIs:
   - **Document AI API**
   - **Cloud Storage API** (if using cloud storage)

Or use the gcloud CLI:
```bash
gcloud services enable documentai.googleapis.com
gcloud services enable storage.googleapis.com
```

## Step 3: Create a Document AI Processor

1. Navigate to the [Document AI Console](https://console.cloud.google.com/ai/document-ai)
2. Click "Create Processor"
3. Select **"Form Parser"** as the processor type
4. Choose your region (recommend: `us-central1` for general use)
5. Enter a processor name (e.g., "invoice-form-parser")
6. Click "Create"
7. **Important**: Note down the processor ID and location from the processor details page

## Step 4: Create Service Account Credentials

1. Go to "IAM & Admin" > "Service Accounts"
2. Click "Create Service Account"
3. Enter service account details:
   - Name: `invoice-ocr-service`
   - Description: `Service account for invoice OCR processing`
4. Click "Create and Continue"
5. Grant the following roles:
   - **Document AI API User**
   - **Storage Object Viewer** (if using cloud storage)
6. Click "Continue" and then "Done"
7. Click on the created service account
8. Go to the "Keys" tab
9. Click "Add Key" > "Create new key"
10. Select "JSON" format
11. Click "Create" - this will download a JSON credentials file

## Step 5: Configure Environment Variables

1. Place the downloaded JSON credentials file in a secure location (e.g., `~/.config/gcloud/invoice-ocr-credentials.json`)
2. Update your `.env` file with the following variables:

```bash
# Google Cloud Document AI Configuration
ENABLE_OCR=true
GOOGLE_CLOUD_PROJECT_ID=your-project-id
GOOGLE_CLOUD_PROCESSOR_ID=your-processor-id
GOOGLE_CLOUD_PROCESSOR_LOCATION=us-central1
GOOGLE_APPLICATION_CREDENTIALS=/path/to/your/credentials.json

# Optional: OCR Configuration
OCR_MAX_FILE_SIZE_MB=20
OCR_TIMEOUT_SECONDS=60
```

## Step 6: Test the Setup

1. Restart your backend server:
   ```bash
   cd backend
   source venv/bin/activate
   uvicorn main:app --reload --port 8000
   ```

2. Test the OCR status endpoint:
   ```bash
   curl -X GET "http://localhost:8000/ocr/status"
   ```

3. You should see output similar to:
   ```json
   {
     "status": "success",
     "ocr": {
       "ocr_enabled": true,
       "service_available": true,
       "processor_name": "projects/YOUR_PROJECT/locations/us-central1/processors/YOUR_PROCESSOR",
       "supported_formats": ["application/pdf", "image/jpeg", "image/png", "image/tiff", "image/bmp", "image/webp"],
       "max_file_size_mb": 20,
       "form_parser_enabled": true,
       "layout_parser_enabled": false
     }
   }
   ```

## Pricing Information

- Document AI charges per page processed
- Form Parser: $1.50 per 1,000 pages for first 1M pages
- See [Document AI Pricing](https://cloud.google.com/document-ai/pricing) for current rates

## Troubleshooting

### Common Issues

1. **"Service account not found" error**
   - Verify the credentials file path is correct
   - Ensure the service account has the proper roles

2. **"Processor not found" error**
   - Check the processor ID and location in your environment variables
   - Ensure the processor was created in the same project

3. **"Permission denied" error**
   - Verify the service account has "Document AI API User" role
   - Check that the Document AI API is enabled

4. **"distutils module not found" error**
   - Install setuptools: `pip install setuptools`

### Verification Commands

Test Google Cloud authentication:
```bash
# Set credentials
export GOOGLE_APPLICATION_CREDENTIALS="/path/to/your/credentials.json"

# Test authentication
gcloud auth list

# Test Document AI access
gcloud ai document-processors list --location=us-central1
```

## Security Best Practices

1. **Never commit credentials to version control**
2. **Use environment variables for all sensitive configuration**
3. **Restrict service account permissions to minimum required**
4. **Regularly rotate service account keys**
5. **Monitor API usage in Google Cloud Console**

## Next Steps

Once OCR is configured:
1. Update your database schema using the provided migration script
2. Test invoice upload and OCR processing
3. Configure the frontend to display OCR results
4. Set up monitoring and alerting for OCR processing

## Support

For Google Cloud specific issues:
- [Google Cloud Support](https://cloud.google.com/support)
- [Document AI Documentation](https://cloud.google.com/document-ai/docs)

For application specific issues:
- Check the backend logs
- Review the OCR configuration in your `.env` file
- Test with the provided OCR status endpoint

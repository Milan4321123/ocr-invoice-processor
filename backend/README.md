# Invoice OCR Backend

FastAPI backend for the Invoice OCR Processing System.

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Create a `.env` file based on `.env.example` and fill in your Supabase credentials

4. Run the development server:
   ```bash
   uvicorn main:app --reload
   ```

5. Access the API documentation at http://localhost:8000/docs

## Features (Planned)

- PDF file upload endpoint
- Supabase storage integration
- Invoice metadata management
- OCR processing pipeline
- Data validation
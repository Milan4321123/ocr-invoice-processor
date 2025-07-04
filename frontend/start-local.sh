#!/bin/bash
# Local development setup script

echo "🚀 Starting OCR Invoice Processor locally..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Please run this from the frontend directory"
    exit 1
fi

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if .env file exists
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Creating one..."
    cat > .env << EOF
# Local Development Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SUPABASE_URL=https://bdtcfypvadryfeabqnlc.supabase.co
NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkdGNmeXB2YWRyeWZlYWJxbmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTA1ODgyMjMsImV4cCI6MjA2NjE2NDIyM30.FANL4kJJJpCeBd3ghc5xLTyY5unMoyf32jRLYCBP5NY
NODE_ENV=development
EOF
    echo "✅ Created .env file with local configuration"
fi

echo "🌐 Starting development server on http://localhost:3000"
echo "🔧 Make sure backend is running on http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"

# Start the development server
npm run dev

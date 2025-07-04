FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies needed for build)
RUN npm install

# Copy source code
COPY . .

# Copy environment file
COPY .env .env

# Set environment variables for Next.js build
ENV NEXT_PUBLIC_API_URL=https://ocr-invoice-processor.onrender.com
ENV NEXT_PUBLIC_SUPABASE_URL=https://bdtcfypvadryfeabqnlc.supabase.co
ENV NEXT_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImJkdGNmeXB2YWRyeWZlYWJxbmxjIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzU4MjAyNDIsImV4cCI6MjA1MTM5NjI0Mn0.s7u-u0t0e4cP2aIyWsGaDy4jjxLZqVfQRoMN66RGUOI

# Build the application for production
RUN npm run build

# Use dynamic port from Render
ENV PORT=10000
EXPOSE $PORT

# Start production server
CMD ["npm", "start"]

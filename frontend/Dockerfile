FROM node:18-alpine

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies (including dev dependencies needed for build)
RUN npm install

# Copy source code
COPY . .

# Build the application for production
RUN npm run build

# Use dynamic port from Render
ENV PORT=10000
EXPOSE $PORT

# Start production server
CMD ["npm", "start"]

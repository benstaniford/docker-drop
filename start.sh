#!/bin/bash

# Docker Drop Startup Script
echo "🐳 Docker Drop - Starting Application"
echo "=================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker first."
    exit 1
fi

# Check if Docker Compose is available
if ! command -v docker-compose > /dev/null 2>&1; then
    echo "❌ Error: Docker Compose is not installed."
    exit 1
fi

# Create output directory if it doesn't exist
if [ ! -d "output" ]; then
    echo "📁 Creating output directory..."
    mkdir output
fi

# Build and start the application
echo "🔨 Building and starting Docker Drop..."
docker-compose up -d

# Wait a moment for containers to start
sleep 3

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Docker Drop is now running!"
    echo ""
    echo "🌐 Access the application:"
    echo "   Main App:     http://localhost:5000"
    echo "   File Browser: http://localhost:8080"
    echo ""
    echo "💾 Files will be saved to: ./output"
    echo ""
    echo "To stop: docker-compose down"
    echo "To view logs: docker-compose logs -f"
else
    echo "❌ Error: Failed to start containers. Check logs with: docker-compose logs"
    exit 1
fi

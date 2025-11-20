#!/bin/bash
# Quick Start Script for Docker Web Deployment (Linux/macOS)

echo "🚀 Nextcloud Log Analyzer - Docker Setup"
echo ""

# Check if Docker is installed
echo "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed!"
    echo "Please install Docker from https://docs.docker.com/get-docker/"
    exit 1
fi
echo "✅ Docker found: $(docker --version)"
echo ""

# Check if docker-compose is available
echo "Checking Docker Compose..."
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose found: $(docker-compose --version)"
    USE_COMPOSE="docker-compose"
else
    echo "⚠️  docker-compose not found, will use 'docker compose' instead"
    USE_COMPOSE="docker compose"
fi
echo ""

# Ask user how to proceed
echo "How would you like to start the application?"
echo "1) Docker Compose (recommended)"
echo "2) Docker run (manual)"
echo "3) Development mode (local Python)"
read -p "Enter choice (1-3): " choice

case $choice in
    1)
        echo ""
        echo "Starting with Docker Compose..."
        
        # Build and start
        $USE_COMPOSE build
        $USE_COMPOSE up -d
        
        if [ $? -eq 0 ]; then
            echo ""
            echo "✅ Application started successfully!"
            echo ""
            echo "🌐 Access the application at: http://localhost:8000"
            echo "📊 Health check: http://localhost:8000/health"
            echo ""
            echo "View logs with: $USE_COMPOSE logs -f"
            echo "Stop with: $USE_COMPOSE down"
        fi
        ;;
    
    2)
        echo ""
        echo "Building Docker image..."
        docker build -t log-scanner .
        
        if [ $? -eq 0 ]; then
            echo "Starting container..."
            docker run -d \
                -p 8000:8000 \
                -v $(pwd)/uploads:/app/uploads \
                -v $(pwd)/results:/app/results \
                -v $(pwd)/logs:/app/logs \
                --name log-scanner \
                log-scanner
            
            if [ $? -eq 0 ]; then
                echo ""
                echo "✅ Container started successfully!"
                echo ""
                echo "🌐 Access at: http://localhost:8000"
                echo ""
                echo "View logs: docker logs -f log-scanner"
                echo "Stop: docker stop log-scanner"
                echo "Remove: docker rm log-scanner"
            fi
        fi
        ;;
    
    3)
        echo ""
        echo "Starting development mode..."
        echo "Installing dependencies..."
        
        # Install all dependencies from requirements.txt
        pip install -r requirements.txt
        
        if [ $? -eq 0 ]; then
            echo "Starting server..."
            echo ""
            echo "🌐 Server will start at: http://localhost:8000"
            echo "Press Ctrl+C to stop"
            echo ""
            
            # Start uvicorn with increased limits for large file uploads (2GB)
            python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 300
        fi
        ;;
    
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

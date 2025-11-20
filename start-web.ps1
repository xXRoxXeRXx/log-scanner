# Quick Start Script for Docker Web Deployment

Write-Host "🚀 Nextcloud Log Analyzer - Docker Setup" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is installed
Write-Host "Checking Docker installation..." -ForegroundColor Yellow
$dockerVersion = docker --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Docker is not installed!" -ForegroundColor Red
    Write-Host "Please install Docker Desktop from https://www.docker.com/products/docker-desktop" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Docker found: $dockerVersion" -ForegroundColor Green
Write-Host ""

# Check if docker-compose is available
Write-Host "Checking Docker Compose..." -ForegroundColor Yellow
$composeVersion = docker-compose --version 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "⚠️  Docker Compose not found, will use 'docker compose' instead" -ForegroundColor Yellow
    $useCompose = "docker compose"
} else {
    Write-Host "✅ Docker Compose found: $composeVersion" -ForegroundColor Green
    $useCompose = "docker-compose"
}
Write-Host ""

# Ask user how to proceed
Write-Host "How would you like to start the application?" -ForegroundColor Cyan
Write-Host "1) Docker Compose (recommended)" -ForegroundColor White
Write-Host "2) Docker run (manual)" -ForegroundColor White
Write-Host "3) Development mode (local Python)" -ForegroundColor White
$choice = Read-Host "Enter choice (1-3)"

switch ($choice) {
    "1" {
        Write-Host ""
        Write-Host "Starting with Docker Compose..." -ForegroundColor Cyan
        
        # Build and start
        if ($useCompose -eq "docker-compose") {
            docker-compose build
            docker-compose up -d
        } else {
            docker compose build
            docker compose up -d
        }
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "✅ Application started successfully!" -ForegroundColor Green
            Write-Host ""
            Write-Host "🌐 Access the application at: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "📊 Health check: http://localhost:8000/health" -ForegroundColor Cyan
            Write-Host ""
            Write-Host "View logs with: $useCompose logs -f" -ForegroundColor Yellow
            Write-Host "Stop with: $useCompose down" -ForegroundColor Yellow
        }
    }
    
    "2" {
        Write-Host ""
        Write-Host "Building Docker image..." -ForegroundColor Cyan
        docker build -t log-scanner .
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Starting container..." -ForegroundColor Cyan
            docker run -d `
                -p 8000:8000 `
                -v ${PWD}/uploads:/app/uploads `
                -v ${PWD}/results:/app/results `
                -v ${PWD}/logs:/app/logs `
                --name log-scanner `
                log-scanner
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host ""
                Write-Host "✅ Container started successfully!" -ForegroundColor Green
                Write-Host ""
                Write-Host "🌐 Access at: http://localhost:8000" -ForegroundColor Cyan
                Write-Host ""
                Write-Host "View logs: docker logs -f log-scanner" -ForegroundColor Yellow
                Write-Host "Stop: docker stop log-scanner" -ForegroundColor Yellow
                Write-Host "Remove: docker rm log-scanner" -ForegroundColor Yellow
            }
        }
    }
    
    "3" {
        Write-Host ""
        Write-Host "Starting development mode..." -ForegroundColor Cyan
        Write-Host "Installing dependencies..." -ForegroundColor Yellow
        
        # Install all dependencies from requirements.txt
        pip install -r requirements.txt
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "Starting server..." -ForegroundColor Cyan
            Write-Host ""
            Write-Host "🌐 Server will start at: http://localhost:8000" -ForegroundColor Cyan
            Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
            Write-Host ""
            
            # Start uvicorn with increased limits for large file uploads (2GB)
            python -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 --timeout-keep-alive 300
        }
    }
    
    default {
        Write-Host "❌ Invalid choice" -ForegroundColor Red
        exit 1
    }
}

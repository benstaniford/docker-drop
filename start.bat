@echo off
echo 🐳 Docker Drop - Starting Application
echo ==================================

REM Check if Docker is running
docker info >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker is not running. Please start Docker first.
    pause
    exit /b 1
)

REM Check if Docker Compose is available
docker-compose --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Error: Docker Compose is not installed.
    pause
    exit /b 1
)

REM Create output directory if it doesn't exist
if not exist "output" (
    echo 📁 Creating output directory...
    mkdir output
)

REM Build and start the application
echo 🔨 Building and starting Docker Drop...
docker-compose up -d

REM Wait a moment for containers to start
timeout /t 3 /nobreak >nul

REM Check if containers are running
docker-compose ps | findstr "Up" >nul
if errorlevel 1 (
    echo ❌ Error: Failed to start containers. Check logs with: docker-compose logs
    pause
    exit /b 1
)

echo.
echo ✅ Docker Drop is now running!
echo.
echo 🌐 Access the application:
echo    Main App:     http://localhost:5000
echo    File Browser: http://localhost:8080
echo.
echo 💾 Files will be saved to: .\output
echo.
echo To stop: docker-compose down
echo To view logs: docker-compose logs -f
echo.
pause

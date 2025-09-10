# Docker Drop 🐳

[![CI](https://github.com/benstaniford/docker-drop/actions/workflows/ci.yml/badge.svg)](https://github.com/benstaniford/docker-drop/actions/workflows/ci.yml)
[![Docker](https://github.com/benstaniford/docker-drop/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/benstaniford/docker-drop/actions/workflows/docker-publish.yml)
[![Docker Hub](https://img.shields.io/docker/pulls/nerwander/docker-drop)](https://hub.docker.com/r/nerwander/docker-drop)
[![Docker Image Size](https://img.shields.io/docker/image-size/nerwander/docker-drop/latest)](https://hub.docker.com/r/nerwander/docker-drop)

A simple Flask web application that allows users to drag and drop text or images to store them in files. The application runs in a Docker container and saves files to a mapped external directory.

## Features

- **Drag & Drop Interface**: Intuitive web interface for dropping text and images
- **Multiple Input Methods**: 
  - Drag and drop files or text
  - Click to select files
  - Paste text or images (Ctrl+V)
- **File Support**: 
  - Text files (.txt)
  - Images (PNG, JPG, GIF, SVG, WebP, BMP)
- **Unique Filenames**: Files are saved with timestamp and unique ID
- **Dockerized**: Runs in a secure Docker container
- **External Storage**: Files are saved to a mapped external directory
- **Optional File Browser**: Browse stored files via web interface

## Quick Start

### Using Pre-built Docker Image (Recommended)

The easiest way to run Docker Drop is using the pre-built image from Docker Hub:

```bash
# Create output directory
mkdir output

# Run with Docker
docker run -d \
  --name docker-drop \
  -p 5000:5000 \
  -v $(pwd)/output:/output \
  nerwander/docker-drop:latest

# Or run with Docker Compose
curl -o docker-compose.yml https://raw.githubusercontent.com/benstaniford/docker-drop/main/docker-compose.yml
docker-compose up -d
```

### Building from Source

If you want to build the image yourself:

### Prerequisites

- Docker and Docker Compose installed on your system
- Port 5000 and 8080 available (or modify the ports in docker-compose.yml)

### 1. Clone or Download

```bash
git clone <repository-url>
cd docker-drop
```

### 2. Create Output Directory

Create a local directory where files will be stored:

```bash
mkdir output
```

### 3. Start the Application

```bash
docker-compose up -d
```

This will:
- Build the Docker image
- Start the Flask application on port 5000
- Start an optional file browser on port 8080
- Map the `./output` directory to `/output` in the container

### 4. Access the Application

- **Main Application**: http://localhost:5000
- **File Browser**: http://localhost:8080 (optional, to view stored files)

## Usage

1. Open http://localhost:5000 in your web browser
2. **Drop content** in one of these ways:
   - Drag and drop text or image files onto the drop zone
   - Click the drop zone to select files
   - Copy text or images and paste them (Ctrl+V) anywhere on the page
3. **Preview** your content in the preview area
4. **Click "Store Content"** to save the file
5. Files will be saved in the `./output` directory with unique names

## File Naming Convention

Files are automatically named using the following pattern:
- **Format**: `YYYYMMDD_HHMMSS_UNIQUEID.extension`
- **Example**: `20250910_143052_a1b2c3d4.txt`

## Configuration

### Custom Output Directory

To use a different output directory, modify the volume mapping in `docker-compose.yml`:

```yaml
volumes:
  - /path/to/your/directory:/output  # Change this path
```

### Custom Ports

To use different ports, modify the port mappings in `docker-compose.yml`:

```yaml
ports:
  - "3000:5000"  # Application will be available on port 3000
```

### Disable File Browser

If you don't want the file browser, comment out or remove the `file-browser` service in `docker-compose.yml`.

## Development

### Running Locally (without Docker)

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Create output directory**:
   ```bash
   mkdir output
   ```

3. **Set environment variable** (optional):
   ```bash
   export FLASK_ENV=development
   ```

4. **Run the application**:
   ```bash
   python app.py
   ```

5. Access at http://localhost:5000

### Building the Docker Image

```bash
docker build -t docker-drop .
```

### Running with Docker (without compose)

```bash
docker run -d \
  --name docker-drop \
  -p 5000:5000 \
  -v $(pwd)/output:/output \
  docker-drop
```

## API Endpoints

### POST /store
Store text or image content.

**Request Body**:
```json
{
  "type": "text|image",
  "content": "content_data"
}
```

**Response**:
```json
{
  "success": true,
  "filename": "20250910_143052_a1b2c3d4.txt",
  "message": "Text saved as 20250910_143052_a1b2c3d4.txt"
}
```

### GET /health
Health check endpoint.

**Response**:
```json
{
  "status": "healthy"
}
```

## Security Considerations

- The application runs as a non-root user inside the container
- File uploads are validated for type and content
- The output directory is the only writable location
- No file execution capabilities
- Basic input sanitization is implemented

## Troubleshooting

### Application won't start
- Check if ports 5000 and 8080 are available
- Ensure Docker and Docker Compose are installed
- Check logs: `docker-compose logs docker-drop`

### Files not saving
- Verify the output directory exists and has write permissions
- Check the volume mapping in docker-compose.yml
- Check container logs for errors

### Can't access the application
- Ensure the application is running: `docker-compose ps`
- Check if the port is accessible: `curl http://localhost:5000/health`
- Verify firewall settings

## License

This project is licensed under the MIT License - see the LICENSE file for details.
A python flask application that allows anything to be dropped into a web site to then be saved as a date stamped file.

# Docker Setup for Chatterbox TTS Server

This document describes the Docker configuration for the Chatterbox TTS Server, including GPU and CPU-only versions.

## Quick Start

### GPU Version (Recommended)
```bash
# Build and run with GPU support
./docker-build.sh
./docker-run.sh

# Or using docker-compose
docker-compose up --build
```

### CPU Version (For users without GPU)
```bash
# Build and run CPU-only version
./docker-build.sh --cpu
./docker-run.sh --cpu

# Or using docker-compose
docker-compose --profile cpu up --build
```

## Docker Files

### Main Dockerfile
- **Base Image**: `nvidia/cuda:12.4.1-devel-ubuntu22.04`
- **Python Version**: 3.12
- **GPU Support**: Yes (CUDA 12.4)
- **Use Case**: Production with GPU acceleration

### Production Dockerfile (Dockerfile.prod)
- **Base Image**: `nvidia/cuda:12.4.1-devel-ubuntu22.04` (multi-stage build)
- **Optimizations**: Multi-stage build, non-root user, minimal runtime image
- **Use Case**: Production deployment with optimized image size

### CPU Dockerfile (Dockerfile.cpu)
- **Base Image**: `python:3.12-slim`
- **GPU Support**: No
- **Use Case**: Development, testing, or systems without GPU support

## Source Code Included

The Docker containers now include all necessary source code files:

### Core Application Files
- `tts_server.py` - Main FastAPI server
- `tts_server_api.py` - API routes and handlers
- `run_tts_server.py` - Server startup script
- `system_events.py` - Model loading and system events
- `configuration.py` - Configuration management
- `utils.py` - Utility functions

### API Directory
- `api/acast.py` - Acast-specific API functionality
- `api/api.py` - General API utilities

### Source Code
- `src/chatterbox_tts/` - Main TTS package source code
- `docs/` - Documentation and sample files
- `t3-model/` - Pre-trained model files

## Build Scripts

### docker-build.sh
Builds Docker images with various options:

```bash
./docker-build.sh [options]

Options:
  --cpu     Build CPU-only version (no GPU support)
  --prod    Build production-optimized version
  --help    Show usage information
```

### docker-run.sh
Runs Docker containers with proper configuration:

```bash
./docker-run.sh [options]

Options:
  --cpu     Run CPU-only version
  --help    Show usage information
```

## Docker Compose

The `docker-compose.yml` includes two services:

### GPU Service (tts-server)
- **Port**: 8081
- **GPU Support**: Yes
- **Container Name**: chatterbox-tts-server

### CPU Service (tts-server-cpu)
- **Port**: 8082
- **GPU Support**: No
- **Container Name**: chatterbox-tts-server-cpu
- **Profile**: cpu (use `--profile cpu` to run)

## Environment Variables

### GPU Version
- `CUDA_VISIBLE_DEVICES=0` - Use first GPU
- `PYTHONUNBUFFERED=1` - Unbuffered Python output

### CPU Version
- `PYTHONUNBUFFERED=1` - Unbuffered Python output
- `CUDA_VISIBLE_DEVICES=""` - Disable CUDA

## Volume Mounts

Both versions mount the following directories:
- `./t3-model:/app/t3-model` - Model files (read-only)
- `./docs:/app/docs:ro` - Documentation and samples (read-only)
- `./output:/app/output` - Generated audio output (read-write)

## Health Checks

All containers include health checks that:
- Test HTTP endpoint every 30 seconds
- Allow 60 seconds for startup
- Retry 3 times before marking as unhealthy

## Security Features

### Non-Root User
All Dockerfiles create and use a non-root user (`ttsuser`) for security.

### Minimal Base Images
- Production Dockerfile uses multi-stage builds
- CPU Dockerfile uses slim Python base image
- Unnecessary packages are removed

## Troubleshooting

### GPU Issues
If you encounter GPU-related issues:
1. Ensure NVIDIA Docker runtime is installed
2. Try CPU version: `./docker-run.sh --cpu`
3. Check GPU availability: `nvidia-smi`

### Port Conflicts
- GPU version uses port 8081
- CPU version uses port 8082
- Change ports in docker-compose.yml if needed

### Build Failures
1. Check Docker is running: `docker info`
2. Ensure sufficient disk space
3. Try building without cache: `docker build --no-cache`

## Development

For development with live code changes, consider:
1. Using volume mounts for source code
2. Enabling hot reload in development mode
3. Using the CPU version for faster iteration

## Production Deployment

For production:
1. Use `Dockerfile.prod` for optimized builds
2. Set appropriate resource limits
3. Configure logging and monitoring
4. Use container orchestration (Kubernetes, Docker Swarm)

## API Endpoints

Once running, the server provides:
- `GET /` - Health check
- `POST /tts` - Single text-to-speech
- `POST /tts-batch` - Batch text-to-speech
- `POST /process-file` - Process text file
- `POST /set-prompt` - Upload voice prompt

Example usage:
```bash
curl -X POST http://localhost:8081/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}' \
  --output audio.mp3
```

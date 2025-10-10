#!/bin/bash
# Docker build script for Chatterbox TTS Server

set -e

echo "🐳 Building Chatterbox TTS Server Docker Image"
echo "=============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Parse command line arguments
DOCKERFILE="Dockerfile"
TAG="chatterbox-tts-server:latest"
CPU_ONLY=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --cpu)
            CPU_ONLY=true
            DOCKERFILE="Dockerfile.cpu"
            TAG="chatterbox-tts-server:cpu"
            echo "🖥️  Building CPU-only version"
            shift
            ;;
        --prod)
            DOCKERFILE="Dockerfile.prod"
            TAG="chatterbox-tts-server:prod"
            echo "🏭 Building production version"
            shift
            ;;
        --help)
            echo "Usage: $0 [--cpu] [--prod]"
            echo "  --cpu   Build CPU-only version (no GPU support)"
            echo "  --prod  Build production-optimized version"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check NVIDIA Docker runtime for GPU builds
if [ "$CPU_ONLY" = false ]; then
    if ! docker info | grep -q nvidia; then
        echo "⚠️  NVIDIA Docker runtime not detected."
        echo "   GPU support may not work. Make sure you have nvidia-docker2 installed."
        echo "   Use --cpu flag for CPU-only build: $0 --cpu"
    fi
fi

# Test base image availability
echo "🔍 Testing base image availability..."
if [ "$CPU_ONLY" = true ]; then
    BASE_IMAGE="ubuntu:22.04"
else
    BASE_IMAGE="nvidia/cuda:12.4.1-devel-ubuntu22.04"
fi

echo "   Testing: $BASE_IMAGE"
if ! docker pull "$BASE_IMAGE" > /dev/null 2>&1; then
    echo "❌ Cannot pull base image: $BASE_IMAGE"
    echo ""
    echo "🔧 Troubleshooting options:"
    echo "   1. Check your internet connection"
    echo "   2. Try CPU-only build: $0 --cpu"
    echo "   3. Use different CUDA version in Dockerfile"
    echo "   4. Check Docker Hub status"
    exit 1
fi
echo "✅ Base image available"

# Build the image
echo "📦 Building Docker image using $DOCKERFILE..."
echo "   Tag: $TAG"
docker build -f "$DOCKERFILE" -t "$TAG" .

if [ $? -eq 0 ]; then
    echo "✅ Docker image built successfully!"
    echo ""
    echo "🚀 To run the container:"
    if [ "$CPU_ONLY" = true ]; then
        echo "   docker run -p 8000:8000 $TAG"
        echo "   (CPU-only version, no GPU support)"
    else
        echo "   docker-compose up"
        echo ""
        echo "   Or manually:"
        echo "   docker run --gpus all -p 8000:8000 $TAG"
    fi
    echo ""
    echo "🔍 To test the server:"
    echo "   curl http://localhost:8000/"
    echo ""
    echo "📊 Image size:"
    docker images "$TAG" --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    echo ""
    echo "📋 Build summary:"
    echo "   Dockerfile: $DOCKERFILE"
    echo "   Tag: $TAG"
    echo "   GPU Support: $([ "$CPU_ONLY" = true ] && echo "No" || echo "Yes")"
else
    echo "❌ Docker build failed!"
    exit 1
fi

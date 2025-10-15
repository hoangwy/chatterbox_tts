#!/bin/bash
# Docker run script for Chatterbox TTS Server

set -e

echo "🚀 Starting Chatterbox TTS Server with Docker"
echo "============================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Parse command line arguments
CPU_ONLY=false
while [[ $# -gt 0 ]]; do
    case $1 in
        --cpu)
            CPU_ONLY=true
            echo "🖥️  Running CPU-only version"
            shift
            ;;
        --help)
            echo "Usage: $0 [--cpu]"
            echo "  --cpu   Run CPU-only version (no GPU support)"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            echo "Use --help for usage information"
            exit 1
            ;;
    esac
done

# Check if image exists
if [ "$CPU_ONLY" = true ]; then
    if ! docker images | grep -q "chatterbox-tts-server.*cpu"; then
        echo "❌ CPU Docker image not found. Building first..."
        ./docker-build.sh --cpu
    fi
    IMAGE_NAME="chatterbox-tts-server:cpu"
    PORT="8082"
else
    if ! docker images | grep -q chatterbox-tts-server; then
        echo "❌ Docker image not found. Building first..."
        ./docker-build.sh
    fi
    IMAGE_NAME="chatterbox-tts-server:latest"
    PORT="8081"
fi

# Create audio directory if it doesn't exist
mkdir -p audio

echo "🐳 Starting container..."
echo "   Port: $PORT"
echo "   GPU: $([ "$CPU_ONLY" = true ] && echo "Disabled (CPU-only)" || echo "Enabled (if available)")"
echo "   Audio directory: ./audio"
echo ""

# Run with docker-compose if available, otherwise run manually
if command -v docker-compose &> /dev/null; then
    echo "📦 Using docker-compose..."
    if [ "$CPU_ONLY" = true ]; then
        docker-compose --profile cpu up --build
    else
        docker-compose up --build
    fi
else
    echo "📦 Using docker run..."
    if [ "$CPU_ONLY" = true ]; then
        docker run --rm -it \
            -p $PORT:8081 \
            -v "$(pwd)/docs:/app/docs:ro" \
            -v "$(pwd)/t3-model:/app/t3-model:ro" \
            -v "$(pwd)/audio:/app/audio" \
            --name chatterbox-tts-server-cpu \
            "$IMAGE_NAME"
    else
        docker run --rm -it \
            --gpus all \
            -p $PORT:8081 \
            -v "$(pwd)/docs:/app/docs:ro" \
            -v "$(pwd)/t3-model:/app/t3-model:ro" \
            -v "$(pwd)/audio:/app/audio" \
            --name chatterbox-tts-server \
            "$IMAGE_NAME"
    fi
fi

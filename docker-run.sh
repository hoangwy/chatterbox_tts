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

# Check if image exists
if ! docker images | grep -q chatterbox-tts-server; then
    echo "❌ Docker image not found. Building first..."
    ./docker-build.sh
fi

# Create output directory if it doesn't exist
mkdir -p output

echo "🐳 Starting container..."
echo "   Port: 8081"
echo "   GPU: Enabled (if available)"
echo "   Output directory: ./output"
echo ""

# Run with docker-compose if available, otherwise run manually
if command -v docker-compose &> /dev/null; then
    echo "📦 Using docker-compose..."
    docker-compose up --build
else
    echo "📦 Using docker run..."
    docker run --rm -it \
        --gpus all \
        -p 8081:8081 \
        -v "$(pwd)/docs:/app/docs:ro" \
        -v "$(pwd)/t3-model:/app/t3-model:ro" \
        -v "$(pwd)/output:/app/output" \
        --name chatterbox-tts-server \
        chatterbox-tts-server:latest
fi

# Use NVIDIA CUDA base image for GPU support
# RTX 3090 with CUDA 12.8 support
FROM nvidia/cuda:12.4.1-devel-ubuntu22.04

# Set environment variables
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1
ENV CUDA_VISIBLE_DEVICES=0

# Install system dependencies
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    git \
    wget \
    curl \
    ffmpeg \
    libsndfile1 \
    libsndfile1-dev \
    && rm -rf /var/lib/apt/lists/*

# Install uv
RUN pip3 install uv

# Create symbolic link for python
RUN ln -s /usr/bin/python3 /usr/bin/python

# Set working directory
WORKDIR /app

# Copy requirements and source code for package installation
COPY pyproject.toml ./
COPY setup.py ./
COPY uv.lock ./
COPY src/ ./src/
COPY docs/ ./docs/
COPY t3-model/ ./t3-model/

# Copy the TTS server and related files
COPY tts_server.py ./
COPY tts_server_api.py ./
COPY run_tts_server.py ./
COPY system_events.py ./
COPY configuration.py ./
COPY utils.py ./
COPY test_*.py ./
COPY demo_*.py ./
COPY docker-startup.sh ./

# Copy API directory
COPY api/ ./api/

# Copy additional files that might be needed
COPY *.py ./

# Make startup script executable
RUN chmod +x docker-startup.sh

# Install Python dependencies using uv
# Use editable install to ensure the package is available
RUN uv pip install --system -e .

# Create audio directory outside /app and set permissions
RUN mkdir -p /audio && chmod 755 /audio

# Expose the port
EXPOSE 8081

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8081/ || exit 1

# Default command - use startup script for better debugging
CMD ["./docker-startup.sh"]

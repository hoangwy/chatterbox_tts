#!/usr/bin/env python3
"""
Startup script for the TTS server
"""

import uvicorn
from tts_server import app

if __name__ == "__main__":
    print("🚀 Starting Chatterbox TTS Server")
    print("=" * 50)
    print("The model will load once on startup and stay in memory.")
    print("This allows for fast subsequent requests without reloading.")
    print()
    print("Endpoints available:")
    print("  GET  /                    - Health check")
    print("  POST /tts                 - Single text-to-speech")
    print("  POST /tts-batch           - Batch text-to-speech")
    print("  POST /process-file        - Process text file (like benchmark.py)")
    print("  POST /set-prompt          - Upload new voice prompt")
    print()
    print("Example usage:")
    print("  curl -X POST http://localhost:8081/tts \\")
    print('    -H "Content-Type: application/json" \\')
    print('    -d \'{"text": "Hello world!"}\' \\')
    print('    --output audio.mp3')
    print()
    print("Starting server...")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8081,
        log_level="info",
        reload=False,  # Set to True for development
    )

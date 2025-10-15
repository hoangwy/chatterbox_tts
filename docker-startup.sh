#!/bin/bash

echo "Starting Chatterbox TTS Server..."

# Debug: Show Python path and installed packages
echo "Python path:"
python -c "import sys; print('\n'.join(sys.path))"

echo "Installed packages:"
uv pip list | grep -E "(chatterbox|torch|vllm)" || echo "No relevant packages found"

# Test basic imports
echo "Testing basic imports..."
python -c "import chatterbox_tts; print('✓ chatterbox_tts imported')" || echo "❌ chatterbox_tts import failed"

python -c "from chatterbox_tts.models.t3.modules.t3_config import T3Config; print('✓ T3Config imported')" || echo "❌ T3Config import failed"

# Test audio directory creation
echo "Testing audio directory creation..."
if [ -f "test_audio_directory.py" ]; then
    python test_audio_directory.py || echo "❌ Audio directory test failed"
else
    echo "⚠️  test_audio_directory.py not found, skipping test"
fi

# Try to start the server
echo "Starting TTS server..."
python tts_server.py

# If server fails, keep container alive for debugging
if [ $? -ne 0 ]; then
    echo "Server failed to start. Keeping container alive for debugging..."
    echo "You can now exec into the container to debug:"
    echo "docker exec -it <container_id> /bin/bash"
    echo ""
    echo "Debug commands you can run inside the container:"
    echo "  python -c 'import sys; print(sys.path)'"
    echo "  uv pip list"
    echo "  find /app -name '*.py' | head -10"
    tail -f /dev/null
fi

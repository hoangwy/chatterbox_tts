#!/bin/bash

# Chatterbox TTS API - curl Examples
# Make sure your Docker container is running on port 15734

echo "🎤 Chatterbox TTS API - curl Examples"
echo "======================================"

# Health check endpoint
echo ""
echo "1. Health Check:"
echo "curl -X GET http://209.226.130.75:15734/"
curl -X GET http://209.226.130.75:15734/ | jq '.'


echo ""
echo "6. Process Text File:"
echo "curl -X POST 'http://209.226.130.75:15734/process-file?file_path=docs/benchmark-text-1.txt&exaggeration=0.5&min_p=0.1' \\"
echo "  --output processed_file.mp3"
curl -X POST "http://209.226.130.75:15734/process-file?file_path=docs/benchmark-text-1.txt&exaggeration=0.5&min_p=0.1" \
  --output processed_file.mp3

echo ""
echo "7. Process Long Text Directly (With Chunking) - Speech Endpoint:"
echo "curl -X POST 'http://209.226.130.75:15734/speech' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"input\": \"This is a long text that will be automatically chunked into smaller pieces. Each piece will be processed separately and then stitched together into one audio file. This is useful for processing articles, stories, or any long-form content.\", \"exaggeration\": 0.5, \"min_p\": 0.1}' \\"
echo "  --output long_text.mp3"
curl -X POST "http://209.226.130.75:15734/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "This is a long text that will be automatically chunked into smaller pieces. Each piece will be processed separately and then stitched together into one audio file. This is useful for processing articles, stories, or any long-form content.", "exaggeration": 0.5, "min_p": 0.1}' \
  --output long_text.mp3

echo ""
echo "8. Simple Speech Test:"
echo "curl -X POST 'http://209.226.130.75:15734/speech' \\"
echo "  -H 'Content-Type: application/json' \\"
echo "  -d '{\"input\": \"Hello world this is a simple test\", \"exaggeration\": 0.5}' \\"
echo "  --output simple_speech.mp3"
curl -X POST "http://209.226.130.75:15734/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world this is a simple test", "exaggeration": 0.5}' \
  --output simple_speech.mp3

echo ""
echo "✅ All curl examples completed!"
echo ""
echo "Generated files:"
echo "- hello.mp3"
echo "- test_with_params.mp3"
echo "- batch_stitched.mp3"
echo "- batch_separate.mp3"
echo "- processed_file.mp3"
echo "- long_text.mp3"
echo "- simple_speech.mp3"
echo ""
echo "You can play these files with:"
echo "mpv hello.mp3"
echo "or open them in any audio player"

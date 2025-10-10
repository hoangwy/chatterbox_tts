# Chatterbox TTS API - curl Commands

## 1. Health Check
```bash
curl -X GET http://209.226.130.75:15734/
```

## 2. Single Text-to-Speech (Basic)
```bash
curl -X POST http://209.226.130.75:15734/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello there! How are you today?"}' \
  --output hello.mp3
```

## 3. Single Text-to-Speech (With Parameters)
```bash
curl -X POST http://209.226.130.75:15734/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test with different parameters.", "exaggeration": 0.7, "min_p": 0.2}' \
  --output test_with_params.mp3
```

## 4. Batch Text-to-Speech (Stitched Audio)
```bash
curl -X POST http://209.226.130.75:15734/tts-batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["Hello there!", "How are you?", "This is a batch test."], "exaggeration": 0.5, "min_p": 0.1, "stitch_audio": true}' \
  --output batch_stitched.mp3
```

## 5. Batch Text-to-Speech (Separate Files)
```bash
curl -X POST http://209.226.130.75:15734/tts-batch \
  -H "Content-Type: application/json" \
  -d '{"texts": ["First sentence.", "Second sentence."], "exaggeration": 0.6, "stitch_audio": false}' \
  --output batch_separate.mp3
```

## 6. Process Text File
```bash
curl -X POST "http://209.226.130.75:15734/process-file?file_path=docs/benchmark-text-1.txt&exaggeration=0.5&min_p=0.1" \
  --output processed_file.mp3
```

## 7. Process Long Text Directly (With Chunking) - Speech Endpoint
```bash
curl -X POST "http://209.226.130.75:15734/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Your long text here that will be automatically chunked and processed", "exaggeration": 0.5, "min_p": 0.1}' \
  --output long_text.mp3
```

## 7b. Simple Speech Test
```bash
curl -X POST "http://209.226.130.75:15734/speech" \
  -H "Content-Type: application/json" \
  -d '{"input": "Hello world this is a simple test", "exaggeration": 0.5}' \
  --output simple_speech.mp3
```

## 8. Upload New Audio Prompt (Voice Reference)
```bash
curl -X POST http://209.226.130.75:15734/set-prompt \
  -F "file=@/path/to/your/audio.mp3"
```

## Parameter Explanations

- **text**: The text to convert to speech
- **exaggeration**: Controls emotion intensity (0.0 to 1.0, default: 0.5)
- **min_p**: Minimum probability for token selection (default: 0.1)
- **stitch_audio**: For batch requests, whether to combine all audio into one file (default: true)

## Quick Test
```bash
# Test if server is running
curl -X GET http://209.226.130.75:15734/

# Generate a simple hello world
curl -X POST http://209.226.130.75:15734/tts \
  -H "Content-Type: application/json" \
  -d '{"text": "Hello world!"}' \
  --output hello_world.mp3
```

import io
import os
import time

import torch
import torchaudio as ta
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import configuration
import system_events
import utils
import api.acast as acast


def uploadToAcast(audioPath: str, showId: str, title: str, subtitle: str, text: str) -> bool:
    try:
        acast.uploadToAcast(
            audioPath=audioPath,
            showId=showId,
            title=title,
            subtitle=subtitle,
            summary=f"Generated speech from text: {text[:100]}..."
        )
        print(f"[SPEECH] Successfully uploaded to Acast: {audioPath}")
        return True
    except Exception as e:
        print(f"[SPEECH] Failed to upload to Acast: {e}")
        return False


def create_api_routes(app):
    """Create and register API routes for the FastAPI app"""
    
    @app.get("/")
    def root():
        model = system_events.get_model()
        return {
            "status": "ok", 
            "message": "Persistent Chatterbox TTS API running",
            "model_loaded": model is not None
        }

    @app.post("/speech")
    async def speech(request: dict):
        model = system_events.get_model()
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded yet")

        # Extract parameters from request
        text = request.get("input", "")
        exaggeration = request.get("exaggeration", 0.5)
        min_p = request.get("min_p", 0.1)
        showId = request.get("showId", "")
        title = request.get("title", "")
        subtitle = request.get("subtitle", "")

        if not text or not text.strip():
            raise HTTPException(status_code=400, detail="Input text cannot be empty")
        
        if not showId or not showId.strip():
            raise HTTPException(status_code=400, detail="showId cannot be empty")
        
        if not title or not title.strip():
            raise HTTPException(status_code=400, detail="title cannot be empty")

        print(f"[SPEECH] Processing text: {text[:100]}...")
        start_time = time.time()

        try:
            # Split text into chunks using the same logic as process_text_file
            # Remove lines starting with # (like process_text_file does)
            text_lines = "\n".join([line for line in text.split("\n") if not line.startswith("#")])
            
            # Chunk text by newlines
            text_lines = [i.strip() for i in text_lines.split("\n") if len(i.strip()) > 0]

            # Split text into chunks
            text_chunks = []
            for line in text_lines:
                chunks = utils.split_text_by_sentence(line)
                text_chunks.extend(chunks)
            
            print(f"[SPEECH] Text chunked into {len(text_chunks)} chunks")
            
            # Generate speech
            audios = model.generate(
                text_chunks,
                audio_prompt_path=configuration.AUDIO_PROMPT_PATH,
                exaggeration=exaggeration,
                min_p=min_p,
            )

            if not audios or len(audios) == 0:
                raise HTTPException(status_code=500, detail="Failed to generate audio")

            # Stitch audio chunks together
            full_audio = torch.cat(audios, dim=-1)
            
            # Save to output folder (mounted in Docker)
            output_dir = "output"
            try:
                os.makedirs(output_dir, exist_ok=True)
            except PermissionError:
                # Fallback to current directory if output directory is not writable
                output_dir = "."
                print(f"[SPEECH] Warning: Could not create output directory, using current directory")
            
            filename = f"speech_{int(time.time())}.mp3"
            autoPath = f"{output_dir}/{filename}"
            ta.save(autoPath, full_audio, model.sr, format="mp3")
            print(f"[SPEECH] Audio saved to: {autoPath}")
            
            # Upload to Acast
            uploadToAcast(autoPath, showId, title, subtitle, text)
            
            buf = io.BytesIO()
            ta.save(buf, full_audio, model.sr, format="mp3")
            buf.seek(0)

            generation_time = time.time() - start_time
            print(f"[SPEECH] Generated audio from {len(text_chunks)} chunks in {generation_time:.2f} seconds.")
            return StreamingResponse(buf, media_type="audio/mpeg")
        
        except Exception as e:
            print(f"[SPEECH] Error processing text: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")

#!/usr/bin/env python3

import io
import time
import re
from typing import List, Union
from pathlib import Path

import torch
import torchaudio as ta
from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
from chatterbox_tts.tts import ChatterboxTTS

# ====== Configuration ======
AUDIO_PROMPT_PATH = "docs/corey.mp3"
MAX_CHUNK_SIZE = 400
BATCH_SIZE = 60

# ====== Global FastAPI app ======
app = FastAPI(title="Persistent Chatterbox TTS API", version="1.0")
model = None  # Will be initialized at startup


# ====== Request Models ======
class TTSRequest(BaseModel):
    text: str
    exaggeration: float = 0.5
    min_p: float = 0.1


class BatchTTSRequest(BaseModel):
    texts: List[str]
    exaggeration: float = 0.5
    min_p: float = 0.1
    stitch_audio: bool = True  # Whether to return one combined audio file or separate files


# ====== Startup event (load model once) ======
@app.on_event("startup")
def load_model():
    global model
    print("[SERVER] Loading ChatterboxTTS model... This may take a while the first time.")
    start_time = time.time()
    
    try:
        model = ChatterboxTTS.from_pretrained(
            max_batch_size=BATCH_SIZE,
            max_model_len=MAX_CHUNK_SIZE * 3,
        )
        load_time = time.time() - start_time
        print(f"[SERVER] Model loaded successfully in {load_time:.2f} seconds.")
    except Exception as e:
        print(f"[SERVER] Failed to load model: {e}")
        raise


# ====== Utility functions from benchmark.py ======
def split_text_by_sentence(text: str) -> List[str]:
    """Given a line of text, split it into chunks of at most MAX_CHUNK_SIZE characters
    at sentence boundaries, forming roughly equal-sized chunks"""
    sentences = text.split(". ")
    n_chunks_needed = len(text) // MAX_CHUNK_SIZE + 1
    approx_chunk_size = len(text) // n_chunks_needed

    chunks = []
    current_chunk = []
    current_length = 0
    for sentence in sentences:
        # Remove excess whitespace like consecutive spaces, newlines, etc.
        sentence = " ".join(sentence.split())
        sentence = sentence.strip()

        if current_length + len(sentence) > approx_chunk_size:
            chunks.append(". ".join(current_chunk))
            current_chunk = [sentence]
            current_length = len(sentence)
        else:
            current_chunk.append(sentence)
            current_length += len(sentence)

    if current_chunk:
        chunks.append(". ".join(current_chunk))

    # If chunks end with a-z0-9, add a period to the end
    chunks = [chunk + "." if re.match(r"[a-zA-Z0-9]", chunk[-1]) else chunk for chunk in chunks if len(chunk) > 0]

    return chunks


def process_text_file(file_path: str) -> List[str]:
    """Process a text file like benchmark.py does"""
    with open(file_path, "r") as f:
        text = f.read()
    
    # Remove lines starting with #
    text = "\n".join([line for line in text.split("\n") if not line.startswith("#")])

    # Chunk text by newlines
    text = [i.strip() for i in text.split("\n") if len(i.strip()) > 0]

    # Split text into chunks
    text = [split_text_by_sentence(line) for line in text]

    # Flatten list
    text = [item for sublist in text for item in sublist]
    
    return text


# ====== Health check ======
@app.get("/")
def root():
    return {
        "status": "ok", 
        "message": "Persistent Chatterbox TTS API running",
        "model_loaded": model is not None
    }


# ====== Single Text-to-Speech endpoint ======
@app.post("/tts")
async def tts(req: TTSRequest):
    """
    POST /tts
    {
        "text": "Hello there!",
        "exaggeration": 0.5,
        "min_p": 0.1
    }
    Returns: audio/mp3 stream
    """
    global model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")

    print(f"[TTS] Generating speech for text: {req.text[:60]}...")
    start_time = time.time()

    try:
        # Generate speech
        audios = model.generate(
            [req.text],
            audio_prompt_path=AUDIO_PROMPT_PATH,
            exaggeration=req.exaggeration,
            min_p=req.min_p,
        )

        if not audios or len(audios) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        # Convert tensor -> bytes
        audio_tensor = audios[0]
        buf = io.BytesIO()
        ta.save(buf, audio_tensor, model.sr, format="mp3")
        buf.seek(0)

        generation_time = time.time() - start_time
        print(f"[TTS] Done in {generation_time:.2f} seconds.")
        return StreamingResponse(buf, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"[TTS] Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")


# ====== Batch Text-to-Speech endpoint ======
@app.post("/tts-batch")
async def tts_batch(req: BatchTTSRequest):
    """
    POST /tts-batch
    {
        "texts": ["Hello there!", "How are you?"],
        "exaggeration": 0.5,
        "min_p": 0.1,
        "stitch_audio": true
    }
    Returns: audio/mp3 stream (combined if stitch_audio=true)
    """
    global model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    if not req.texts or len(req.texts) == 0:
        raise HTTPException(status_code=400, detail="No texts provided")

    print(f"[BATCH-TTS] Generating speech for {len(req.texts)} texts...")
    start_time = time.time()

    try:
        # Generate speech for all texts
        audios = model.generate(
            req.texts,
            audio_prompt_path=AUDIO_PROMPT_PATH,
            exaggeration=req.exaggeration,
            min_p=req.min_p,
        )

        if not audios or len(audios) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        # Convert tensor -> bytes
        if req.stitch_audio:
            # Stitch all audio chunks together
            full_audio = torch.cat(audios, dim=-1)
            buf = io.BytesIO()
            ta.save(buf, full_audio, model.sr, format="mp3")
            buf.seek(0)
            
            generation_time = time.time() - start_time
            print(f"[BATCH-TTS] Generated {len(audios)} audio chunks and stitched together in {generation_time:.2f} seconds.")
            return StreamingResponse(buf, media_type="audio/mpeg")
        else:
            # Return first audio chunk only (for now)
            # TODO: Implement returning multiple files or zip
            audio_tensor = audios[0]
            buf = io.BytesIO()
            ta.save(buf, audio_tensor, model.sr, format="mp3")
            buf.seek(0)
            
            generation_time = time.time() - start_time
            print(f"[BATCH-TTS] Generated {len(audios)} audio chunks in {generation_time:.2f} seconds.")
            return StreamingResponse(buf, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"[BATCH-TTS] Error generating speech: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to generate speech: {str(e)}")


# ====== Process text with chunking endpoint ======
@app.post("/speech")
async def speech(request: dict):
    """
    POST /speech
    {
        "input": "Your long text here",
        "exaggeration": 0.5,
        "min_p": 0.1
    }
    Process long text directly (like process-file but with input parameter) - chunk it and generate speech
    """
    global model
    if model is None:
        raise HTTPException(status_code=503, detail="Model not loaded yet")

    # Extract parameters from request
    text = request.get("input", "")
    exaggeration = request.get("exaggeration", 0.5)
    min_p = request.get("min_p", 0.1)

    if not text or not text.strip():
        raise HTTPException(status_code=400, detail="Input text cannot be empty")

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
            chunks = split_text_by_sentence(line)
            text_chunks.extend(chunks)
        
        print(f"[SPEECH] Text chunked into {len(text_chunks)} chunks")
        
        # Generate speech
        audios = model.generate(
            text_chunks,
            audio_prompt_path=AUDIO_PROMPT_PATH,
            exaggeration=exaggeration,
            min_p=min_p,
        )

        if not audios or len(audios) == 0:
            raise HTTPException(status_code=500, detail="Failed to generate audio")

        # Stitch audio chunks together
        full_audio = torch.cat(audios, dim=-1)
        buf = io.BytesIO()
        ta.save(buf, full_audio, model.sr, format="mp3")
        buf.seek(0)

        generation_time = time.time() - start_time
        print(f"[SPEECH] Generated audio from {len(text_chunks)} chunks in {generation_time:.2f} seconds.")
        return StreamingResponse(buf, media_type="audio/mpeg")
    
    except Exception as e:
        print(f"[SPEECH] Error processing text: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")


# ====== Shutdown ======
@app.on_event("shutdown")
def shutdown_event():
    global model
    if model is not None:
        try:
            model.shutdown()
            print("[SERVER] Model shutdown successfully.")
        except Exception as e:
            print(f"[SERVER] Error during model shutdown: {e}")
    print("[SERVER] Shutdown complete.")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

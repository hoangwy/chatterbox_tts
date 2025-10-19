import io
import os
import time
import asyncio
import threading

import torch
import torchaudio as ta
from fastapi import HTTPException
from fastapi.responses import StreamingResponse
import configuration
import system_events
import utils
import api.acast as acast
import api.api as api

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


def process_queued_article(article_data):
    """Process a queued article by calling the speech function"""
    try:
        print(f"[QUEUE] Processing queued article: {article_data}")
        
        # Extract article data
        text = article_data.get("content", "")
        showId = article_data.get("podcastId", "")
        title = article_data.get("title", "")
        subtitle = article_data.get("subtitle", "")
        exaggeration = article_data.get("exaggeration", 0.5)
        min_p = article_data.get("min_p", 0.1)
        
        if not text or not showId or not title:
            print(f"[QUEUE] Missing required fields in article data")
            return False
        
        # Call speech function with article data
        model = system_events.get_model()
        if model is None:
            print(f"[QUEUE] Model not loaded, cannot process article")
            return False
        
        print(f"[QUEUE] Generating speech for article: {title}")
        start_time = time.time()
        
        # Split text into chunks using the same logic as speech endpoint
        text_lines = "\n".join([line for line in text.split("\n") if not line.startswith("#")])
        text_lines = [i.strip() for i in text_lines.split("\n") if len(i.strip()) > 0]
        
        text_chunks = []
        for line in text_lines:
            chunks = utils.split_text_by_sentence(line)
            text_chunks.extend(chunks)
        
        print(f"[QUEUE] Text chunked into {len(text_chunks)} chunks")
        
        # Generate speech
        audios = model.generate(
            text_chunks,
            audio_prompt_path=configuration.AUDIO_PROMPT_PATH,
            exaggeration=exaggeration,
            min_p=min_p,
        )
        
        if not audios or len(audios) == 0:
            print(f"[QUEUE] Failed to generate audio")
            return False
        
        # Stitch audio chunks together
        full_audio = torch.cat(audios, dim=-1)
        
        # Save to audio folder
        output_dir = "audio"
        try:
            os.makedirs(output_dir, exist_ok=True)
        except PermissionError:
            output_dir = "."
            print(f"[QUEUE] Warning: Could not create audio directory, using current directory")
        
        filename = f"{title}.mp3"
        audioPath = f"{output_dir}/{filename}"
        ta.save(audioPath, full_audio, model.sr, format="mp3")
        print(f"[QUEUE] Audio saved to: {audioPath}")
        
        # Upload to Acast
        # success = uploadToAcast(audioPath, showId, title, subtitle, text)
        
        generation_time = time.time() - start_time
        print(f"[QUEUE] Generated audio from {len(text_chunks)} chunks in {generation_time:.2f} seconds.")
        
        return True
        
    except Exception as e:
        print(f"[QUEUE] Error processing queued article: {e}")
        return False


def poll_queued_articles():
    """Poll for queued articles every 5 minutes, or immediately if upload was successful"""
    while True:
        try:
            print(f"[QUEUE] Checking for queued articles...")
            result = api.getQueuedArticle()
            
            if result and result.get("data") is not None:
                article_data = result["data"]
                print(f"[QUEUE] Found queued article, processing...")
                success = process_queued_article(article_data)
                if success:
                    print(f"[QUEUE] Successfully processed queued article, checking for next article immediately...")
                    continue  # Skip the 5-minute wait and check for next article immediately
                else:
                    print(f"[QUEUE] Failed to process queued article")
            else:
                print(f"[QUEUE] No queued articles found")
            
        except Exception as e:
            print(f"[QUEUE] Error polling for articles: {e}")
        
        # Wait 5 minutes before next poll (only if no article was processed successfully)
        print(f"[QUEUE] Waiting 5 minutes before next poll...")
        time.sleep(300)  # 5 minutes = 300 seconds


def start_polling_thread():
    """Start the polling thread for queued articles"""
    def run_polling():
        # Wait a bit for the server to fully start
        time.sleep(10)
        poll_queued_articles()
    
    polling_thread = threading.Thread(target=run_polling, daemon=True)
    polling_thread.start()
    print("[QUEUE] Started polling thread for queued articles")


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

    @app.post("/getQueuedArticle")
    async def get_queued_article():
        """Get a queued article from the external API"""
        try:
            result = api.getQueuedArticle()
            return result
        except Exception as e:
            print(f"[API] Error getting queued article: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to get queued article: {str(e)}")

    @app.post("/speech")
    async def speech(request: dict):
        model = system_events.get_model()
        if model is None:
            raise HTTPException(status_code=503, detail="Model not loaded yet")

        # Extract parameters from request
        text = request.get("content", "")
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
            
            # Save to audio folder
            output_dir = "audio"
            try:
                os.makedirs(output_dir, exist_ok=True)
            except PermissionError:
                # Fallback to current directory if audio directory is not writable
                output_dir = "."
                print(f"[SPEECH] Warning: Could not create audio directory, using current directory")
            
            filename = f"{title}.mp3"
            autoPath = f"{output_dir}/{filename}"
            ta.save(autoPath, full_audio, model.sr, format="mp3")
            print(f"[SPEECH] Audio saved to: {autoPath}")
            
            # Upload to Acast
            # uploadToAcast(autoPath, showId, title, subtitle, text)
            
            buf = io.BytesIO()
            ta.save(buf, full_audio, model.sr, format="mp3")
            buf.seek(0)

            generation_time = time.time() - start_time
            print(f"[SPEECH] Generated audio from {len(text_chunks)} chunks in {generation_time:.2f} seconds.")
            return StreamingResponse(buf, media_type="audio/mpeg")
        
        except Exception as e:
            print(f"[SPEECH] Error processing text: {e}")
            raise HTTPException(status_code=500, detail=f"Failed to process text: {str(e)}")

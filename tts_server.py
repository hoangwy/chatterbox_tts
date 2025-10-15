#!/usr/bin/env python3

from fastapi import FastAPI
import system_events
from tts_server_api import create_api_routes


# ====== Global FastAPI app ======
app = FastAPI(title="Chatterbox TTS", version="1.0")

# ====== Register API routes ======
create_api_routes(app)

# ====== Startup event (load model once) ======
@app.on_event("startup")
def startup_handler():
    system_events.load_model()


# ====== Shutdown ======
@app.on_event("shutdown")
def shutdown_handler():
    system_events.shutdown_event()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8081)

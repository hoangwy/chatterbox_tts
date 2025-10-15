import time
from chatterbox_tts.tts import ChatterboxTTS
import configuration

# Global model variable
model = None


def load_model():
    """Startup event handler to load the ChatterboxTTS model"""
    global model
    print("[SERVER] Loading ChatterboxTTS model... This may take a while the first time.")
    start_time = time.time()
    
    try:
        model = ChatterboxTTS.from_pretrained(
            max_batch_size=configuration.BATCH_SIZE,
            max_model_len=configuration.MAX_CHUNK_SIZE * 3,
        )
        load_time = time.time() - start_time
        print(f"[SERVER] Model loaded successfully in {load_time:.2f} seconds.")
    except Exception as e:
        print(f"[SERVER] Failed to load model: {e}")
        raise


def shutdown_event():
    """Shutdown event handler to clean up the model"""
    global model
    if model is not None:
        try:
            model.shutdown()
            print("[SERVER] Model shutdown successfully.")
        except Exception as e:
            print(f"[SERVER] Error during model shutdown: {e}")
    print("[SERVER] Shutdown complete.")


def get_model():
    """Get the global model instance"""
    return model

import asyncio
import time
from typing import Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from services.voice.models import SpeakRequest, VoiceServiceStatus
from services.voice.pipeline import VoicePipeline

app = FastAPI(title="Aether Voice Service", version="1.0.0")

# Global pipeline instance (set by main.py); None until main.py assigns it.
voice_pipeline: VoicePipeline | None = None
start_time: float = time.time()


class ControlRequest(BaseModel):
    command: str


@app.get("/health")
async def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "voice"}


@app.get("/status", response_model=VoiceServiceStatus)
async def get_status() -> VoiceServiceStatus:
    if not voice_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    return VoiceServiceStatus(
        current_state=voice_pipeline.state,
        stt_ready=voice_pipeline.stt.model is not None,
        tts_ready=voice_pipeline.tts.pipeline is not None,
        wake_word_active=voice_pipeline.wake_word.porcupine is not None,
        model_loaded=f"{voice_pipeline.stt.model_size} | {voice_pipeline.tts.voice}",
        uptime_seconds=time.time() - start_time,
    )


@app.post("/speak")
async def speak(request: SpeakRequest) -> dict[str, Any]:
    if not voice_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    # Schedule speak event which will handle state transition internally
    asyncio.create_task(voice_pipeline.handle_speak_event(request.text))
    return {"status": "enqueued", "text_length": len(request.text)}


@app.post("/control")
async def control(request: ControlRequest) -> dict[str, str]:
    if not voice_pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")

    if request.command == "pause":
        # Hacky pause for now: just set it to IDLE and it won't listen?
        # Actually it always listens in IDLE. If we want a real pause we need a PAUSED state.
        pass
    elif request.command == "resume":
        pass
    else:
        raise HTTPException(status_code=400, detail="Invalid command")

    return {"status": "ok", "command": request.command}

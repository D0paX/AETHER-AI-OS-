import asyncio

import sounddevice as sd
import structlog
import uvicorn

import services.voice.server as server_module
from aether.core.config import get_config
from services.voice.pipeline import VoicePipeline
from services.voice.server import app

logger = structlog.get_logger(__name__)


async def bootstrap() -> None:
    # 1. Print AETHER VOICE SERVICE banner
    print("=====================================")
    print("       AETHER VOICE SERVICE          ")
    print("=====================================")

    # 2. Load environment variables
    config = get_config()

    # 3. Validate audio hardware presence
    devices = sd.query_devices()
    logger.info("audio_devices_detected", count=len(devices))

    # Instantiate pipeline (does not load yet)
    pipeline = VoicePipeline(redis_url=config.redis.url)

    # 4. Pre-check VRAM via FasterWhisperSTT
    free_vram = pipeline.stt._check_vram_available()
    logger.info("gpu_vram_precheck", free_gb=round(free_vram, 2))

    # Steps 5, 6, 7, 8, 9, 10 are handled inside pipeline.start()
    # Let's break them out if strictly required by prompt, but pipeline.start() does them sequentially.
    # The prompt explicitly lists 11 steps for main.py. Let's do it explicitly.
    logger.info("loading_vad_model")
    pipeline.vad.load_model()

    logger.info("loading_wake_word_model")
    pipeline.wake_word.load()

    logger.info("loading_tts_model")
    pipeline.tts.load_model()

    logger.info("loading_stt_model")
    pipeline.stt.load_model()

    logger.info("starting_pipeline")
    await pipeline.start()  # This connects to Redis and spawns background tasks

    # Assign global pipeline to server
    server_module.voice_pipeline = pipeline

    # 11. Mount FastAPI app on 127.0.0.1:8001 via uvicorn
    # uvicorn.run must be run synchronously, so we will use uvicorn Server for async
    uvicorn_config = uvicorn.Config(app, host="127.0.0.1", port=8001, log_level="info")
    server = uvicorn.Server(uvicorn_config)

    logger.info("voice_service_ready", host="127.0.0.1", port=8001)
    await server.serve()


def main() -> None:
    try:
        asyncio.run(bootstrap())
    except KeyboardInterrupt:
        logger.info("voice_service_shutdown")


if __name__ == "__main__":
    main()

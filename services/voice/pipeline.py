import asyncio
from typing import Any

import numpy as np
import redis.asyncio as redis
import sounddevice as sd
import structlog

from aether.core.config import get_config
from aether.core.exceptions import VoiceError
from services.voice.models import VoicePipelineState
from services.voice.stt import FasterWhisperSTT
from services.voice.tts import KokoroTTS
from services.voice.vad import SileroVAD
from services.voice.wake_word import PorcupineWakeWord

logger = structlog.get_logger(__name__)

# Exact placeholder shipped in .env.example — keep in sync with that file's
# `AETHER_VOICE__PORCUPINE_ACCESS_KEY=` line. A configured value equal to this
# is treated as "not configured" (M2.1.10 Part 2 / DEBT-018).
PORCUPINE_KEY_PLACEHOLDER: str = "your-porcupine-key-here"

# Samples per VAD call at 16kHz. This is not a tunable — the installed Silero
# VAD model enforces it and raises otherwise, stating its own contract:
#   "Provided number of samples is N (Supported values: 256 for 8000 sample
#    rate, 512 for 16000)"
# Verified directly against the installed model (M2.1.10): at 16kHz it accepts
# 512 and rejects every other size tried (160/256/320/480 -> "chunk is too
# short"; 640/768/1024/1536 -> "Supported values..."). The pipeline previously
# sliced frames to 480 (a 30ms estimate from an older Silero release), so every
# LISTENING-state frame raised and silence detection never ran (DEBT-014).
VAD_FRAME_SAMPLES: int = 512


class VoicePipeline:
    def __init__(self, redis_url: str):
        self.redis_url = redis_url
        self.state = VoicePipelineState.IDLE
        # Any: assigned a real client in start(); typing it Optional would force
        # None-guards at every use site, which would change runtime behavior.
        self.redis: Any = None

        # Audio constants
        self.sample_rate = 16000
        self.frame_length = 512
        self.silence_threshold_ms = 800

        # Models
        self.vad = SileroVAD(threshold=0.5, sampling_rate=self.sample_rate)
        # Wake-word key comes from config (AETHER_VOICE__PORCUPINE_ACCESS_KEY via
        # env or .env), never a bare os.getenv. Validate it here, at service
        # init, and fail loudly rather than booting to a silently deaf pipeline.
        access_key = get_config().voice.porcupine_access_key
        if not access_key or access_key == PORCUPINE_KEY_PLACEHOLDER:
            # Never log or embed the configured value, even when it is the
            # known placeholder — the message says what to do, not what was set.
            raise VoiceError(
                "Porcupine access key is not configured. Wake word cannot "
                "activate. Obtain a free key from console.picovoice.ai and set "
                "AETHER_VOICE__PORCUPINE_ACCESS_KEY in .env, then restart the "
                "voice service.",
                error_code="VOICE_PORCUPINE_KEY_MISSING",
            )
        self.wake_word = PorcupineWakeWord(access_key=access_key)
        self.stt = FasterWhisperSTT(model_size="medium.en", device="cuda", compute_type="float16")
        self.tts = KokoroTTS(voice="af_sarah")

        # Buffers
        self.audio_buffer: list[np.ndarray] = []
        self.silence_frames = 0
        self._chime = self._generate_chime()

    def _generate_chime(self) -> np.ndarray:
        """Generate a 0.2s 440Hz beep as a fallback for chime.wav"""
        t = np.linspace(0, 0.2, int(16000 * 0.2), endpoint=False)
        return (np.sin(2 * np.pi * 440 * t) * 0.5).astype(np.float32)

    def _play_chime(self) -> None:
        try:
            sd.play(self._chime, 16000)
            sd.wait()
        except Exception as e:
            logger.warning("chime_failed", error=str(e))

    async def start(self) -> None:
        logger.info("initializing_voice_pipeline")

        # Initialize models sequentially
        self.vad.load_model()
        self.wake_word.load()
        self.stt.load_model()
        self.tts.load_model()

        # Connect to Redis. redis.asyncio.from_url carries no annotations
        # upstream, so --strict flags the call; the ignore is scoped to it.
        self.redis = redis.from_url(  # type: ignore[no-untyped-call]
            self.redis_url, decode_responses=True
        )

        self.state = VoicePipelineState.IDLE
        logger.info("voice_pipeline_ready", state=self.state.value)

        # Start background tasks
        asyncio.create_task(self.capture_loop())
        asyncio.create_task(self.redis_listener())

    def audio_callback(self, indata: np.ndarray, frames: int, time_info: Any, status: Any) -> None:
        """Callback for sounddevice InputStream."""
        if status:
            logger.warning("audio_input_status", status=status)

        audio_frame = indata[:, 0]

        if self.state == VoicePipelineState.IDLE:
            if self.wake_word.process(audio_frame):
                self.state = VoicePipelineState.WAKE_DETECTED

        elif self.state == VoicePipelineState.LISTENING:
            self.audio_buffer.append(audio_frame.copy())

            # Feed the VAD exactly VAD_FRAME_SAMPLES; the model accepts no other
            # size at 16kHz. The capture stream's blocksize is self.frame_length,
            # which matches, so this slice takes the whole frame.
            # We process frame by frame for simplicity in this loop
            if len(self.audio_buffer) * self.frame_length >= VAD_FRAME_SAMPLES:
                # Approximate silence tracking
                if self.vad.is_speech_threshold(audio_frame[:VAD_FRAME_SAMPLES]):
                    self.silence_frames = 0
                else:
                    self.silence_frames += 1

                silence_ms = (self.silence_frames * self.frame_length / self.sample_rate) * 1000
                if silence_ms > self.silence_threshold_ms and len(self.audio_buffer) > (
                    16000 / 512
                ):
                    self.state = VoicePipelineState.TRANSCRIBING

    async def capture_loop(self) -> None:
        logger.info("starting_capture_loop")

        stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=1,
            blocksize=self.frame_length,
            callback=self.audio_callback,
            dtype=np.float32,
        )

        with stream:
            while True:
                if self.state == VoicePipelineState.WAKE_DETECTED:
                    self._play_chime()
                    self.audio_buffer = []
                    self.silence_frames = 0
                    self.state = VoicePipelineState.LISTENING
                    logger.info("state_transition", state=self.state.value)

                elif self.state == VoicePipelineState.TRANSCRIBING:
                    logger.info("state_transition", state=self.state.value)
                    audio_data = np.concatenate(self.audio_buffer)
                    self.audio_buffer = []

                    try:
                        # Run STT synchronously in a thread (or block since it's a daemon)
                        result = await asyncio.to_thread(self.stt.transcribe, audio_data)
                        logger.info(
                            "transcription_complete", text=result.text, conf=result.confidence
                        )

                        if result.text.strip():
                            # Publish to core via Redis Streams
                            await self.redis.xadd(
                                "events:voice_in",
                                {
                                    "event_type": "transcription",
                                    "text": result.text,
                                    "confidence": str(result.confidence),
                                },
                            )

                        self.state = VoicePipelineState.TRANSCRIPT_READY
                        logger.info("state_transition", state=self.state.value)
                    except Exception as e:
                        logger.error("transcription_error", error=str(e))
                        self.state = VoicePipelineState.IDLE

                elif self.state == VoicePipelineState.SPEAKING:
                    # In speaking state, the redis_listener handles TTS
                    # We just wait here so we don't accidentally capture TTS audio or wake words
                    await asyncio.sleep(0.1)
                else:
                    await asyncio.sleep(0.01)

    async def redis_listener(self) -> None:
        logger.info("starting_redis_listener")
        last_id = "$"
        while True:
            try:
                # Block for up to 1 second waiting for events:voice_out
                messages = await self.redis.xread(
                    {"events:voice_out": last_id}, count=1, block=1000
                )
                if messages:
                    for _stream_name, stream_messages in messages:
                        for msg_id, msg_data in stream_messages:
                            last_id = msg_id
                            text = msg_data.get("text", "")
                            if text:
                                await self.handle_speak_event(text)
            except Exception as e:
                logger.error("redis_listener_error", error=str(e))
                await asyncio.sleep(1)

    async def handle_speak_event(self, text: str) -> None:
        logger.info("handle_speak_event", text=text)
        self.state = VoicePipelineState.SPEAKING

        try:
            await asyncio.to_thread(self.tts.synthesize_and_play, text)
        except Exception as e:
            logger.error("speak_event_error", error=str(e))
        finally:
            self.state = VoicePipelineState.IDLE
            logger.info("state_transition", state=self.state.value)

    async def shutdown(self) -> None:
        logger.info("shutting_down_voice_pipeline")
        if self.wake_word:
            self.wake_word.delete()
        if self.redis:
            await self.redis.aclose()

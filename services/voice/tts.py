import re
import time

import numpy as np
import sounddevice as sd
import structlog
from kokoro import KPipeline

from services.voice.models import VoiceError, VoiceSynthesisError

logger = structlog.get_logger(__name__)


class KokoroTTS:
    def __init__(self, voice: str = "af_sarah"):
        self.voice = voice
        self.pipeline = None
        self.sample_rate = 24000

    def load_model(self) -> None:
        try:
            start_time = time.time()
            # Device: CPU (preserves VRAM for STT + Ollama)
            self.pipeline = KPipeline(lang_code="a", device="cpu")
            load_time = int((time.time() - start_time) * 1000)
            logger.info("kokoro_tts_loaded", voice=self.voice, load_time_ms=load_time, device="cpu")
        except Exception as e:
            logger.error("kokoro_model_load_failed", error=str(e))
            raise VoiceError(f"Failed to load KokoroTTS: {e}") from e

    def _preprocess_text(self, text: str) -> str:
        # Strip markdown formatting
        text = re.sub(r"[\*\#\_\`]", "", text)
        # Strip leading/trailing whitespace
        text = text.strip()
        # Truncate to 500 characters maximum
        if len(text) > 500:
            text = text[:500]
        return text

    def synthesize(self, text: str) -> np.ndarray:
        if self.pipeline is None:
            raise VoiceSynthesisError("TTS model not loaded")

        clean_text = self._preprocess_text(text)
        if not clean_text:
            return np.array([], dtype=np.float32)

        try:
            generator = self.pipeline(clean_text, voice=self.voice, speed=1.0, split_pattern=r"\n+")

            audio_chunks = []
            for _gs, _ps, audio in generator:
                if audio is not None:
                    audio_chunks.append(audio)

            if not audio_chunks:
                return np.array([], dtype=np.float32)

            full_audio = np.concatenate(audio_chunks)
            # Ensure float32
            return full_audio.astype(np.float32)

        except Exception as e:
            logger.error("synthesis_failed", error=str(e))
            raise VoiceSynthesisError(f"TTS synthesis failed: {e}") from e

    def play(self, audio: np.ndarray) -> None:
        if len(audio) == 0:
            return

        try:
            sd.play(audio, self.sample_rate)
            sd.wait()
        except Exception as e:
            logger.error("playback_failed", error=str(e))
            raise VoiceSynthesisError(f"Audio playback failed: {e}") from e

    def synthesize_and_play(self, text: str) -> int:
        start_time = time.time()
        audio = self.synthesize(text)
        if len(audio) > 0:
            self.play(audio)
        return int((time.time() - start_time) * 1000)

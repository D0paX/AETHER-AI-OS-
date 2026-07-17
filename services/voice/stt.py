import math
import time

import numpy as np
import structlog
from faster_whisper import WhisperModel

from services.voice.models import TranscriptionResult, VoiceError, VoiceTranscriptionError

logger = structlog.get_logger(__name__)


class FasterWhisperSTT:
    def __init__(self, model_size: str, device: str, compute_type: str):
        self.model_size = model_size
        self.device = device
        self.compute_type = compute_type
        self.model = None

    def _check_vram_available(self) -> float:
        """Returns free VRAM in GB using nvidia-smi"""
        if self.device == "cuda":
            try:
                import subprocess

                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=memory.free", "--format=csv,noheader,nounits"],
                    encoding="utf-8",
                )
                free_mem_mb = float(output.strip().split("\n")[0])
                return free_mem_mb / 1024.0
            except Exception as e:
                logger.warning("nvidia_smi_failed", error=str(e))
                return 2.0  # Fallback optimistic assumption
        return 0.0

    def _get_vram_used(self) -> float:
        """Returns used VRAM in GB using nvidia-smi"""
        if self.device == "cuda":
            try:
                import subprocess

                output = subprocess.check_output(
                    ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
                    encoding="utf-8",
                )
                used_mem_mb = float(output.strip().split("\n")[0])
                return used_mem_mb / 1024.0
            except Exception as e:
                logger.warning("nvidia_smi_failed", error=str(e))
                return 0.0
        return 0.0

    def load_model(self) -> None:
        if self.device == "cuda":
            free_vram = self._check_vram_available()
            logger.info("stt_vram_precheck", free_vram_gb=round(free_vram, 2))
            # Medium model usually takes ~1.5GB
            if free_vram < 2.0:
                logger.warning("stt_vram_low", free_vram_gb=round(free_vram, 2))
                # We won't strictly fail on 2.0GB, but if it's super low, it will OOM on load.
                if free_vram < 1.0:
                    raise VoiceError(
                        f"Insufficient VRAM for Whisper (need ~1.5GB, have {free_vram:.2f}GB)"
                    )

        try:
            logger.info("loading_whisper_model", model_size=self.model_size, device=self.device)
            self.model = WhisperModel(
                self.model_size, device=self.device, compute_type=self.compute_type
            )

            used_vram = self._get_vram_used()
            logger.info("whisper_model_loaded", used_vram_gb=round(used_vram, 2))
        except Exception as e:
            logger.error("whisper_model_load_failed", error=str(e))
            raise VoiceError(f"Failed to load WhisperModel: {e}") from e

    def transcribe(self, audio_data: np.ndarray) -> TranscriptionResult:
        if self.model is None:
            raise VoiceTranscriptionError("STT model not loaded")

        start_time = time.time()

        # Audio duration in ms (audio_data is 16kHz float32 or int16)
        if audio_data.dtype == np.int16:
            audio_data = audio_data.astype(np.float32) / 32768.0

        duration_ms = int((len(audio_data) / 16000.0) * 1000)

        try:
            segments, info = self.model.transcribe(
                audio_data, language="en", beam_size=5, vad_filter=True
            )

            # Segments is a generator, we must consume it
            text_segments = []
            logprobs = []
            for segment in segments:
                text_segments.append(segment.text)
                logprobs.append(segment.avg_logprob)

            full_text = "".join(text_segments).strip()

            # Normalize logprob to 0.0 - 1.0 confidence
            if logprobs:
                avg_logprob = sum(logprobs) / len(logprobs)
                confidence = math.exp(avg_logprob)
            else:
                confidence = 0.0

            processing_ms = int((time.time() - start_time) * 1000)

            return TranscriptionResult(
                text=full_text,
                confidence=confidence,
                audio_duration_ms=duration_ms,
                processing_ms=processing_ms,
                model_used=f"faster-whisper-{self.model_size}",
            )

        except Exception as e:
            logger.error("transcription_failed", error=str(e))
            raise VoiceTranscriptionError(f"STT failed: {e}") from e

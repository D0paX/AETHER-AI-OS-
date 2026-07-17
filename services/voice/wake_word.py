import os
from typing import Any

import numpy as np
import pvporcupine
import structlog

from services.voice.models import VoiceError

logger = structlog.get_logger(__name__)


class PorcupineWakeWord:
    def __init__(self, access_key: str, wake_word: str = "aether"):
        self.access_key = access_key
        self.wake_word = wake_word
        # Any: pvporcupine ships no stubs, so the handle has no usable type.
        self.porcupine: Any = None
        self.frame_length = 512

    def load(self) -> None:
        if self.access_key == "dummy_key_if_not_provided":
            logger.warning("porcupine_wake_word_disabled", reason="No access key provided")
            return

        try:
            # Try to load custom keyword file
            custom_keyword_path = os.path.join(
                os.path.dirname(__file__), "models", f"{self.wake_word}_windows.ppn"
            )

            if os.path.exists(custom_keyword_path):
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key, keyword_paths=[custom_keyword_path]
                )
                active_keyword = self.wake_word
            else:
                # Fallback to built-in keyword "computer"
                logger.warning(
                    "custom_keyword_not_found", path=custom_keyword_path, fallback="computer"
                )
                self.porcupine = pvporcupine.create(
                    access_key=self.access_key, keywords=["computer"]
                )
                active_keyword = "computer"

            self.frame_length = self.porcupine.frame_length
            logger.info(
                "porcupine_wake_word_loaded",
                active_keyword=active_keyword,
                frame_length=self.frame_length,
            )

        except Exception as e:
            logger.error("porcupine_wake_word_load_failed", error=str(e))
            raise VoiceError(f"Failed to initialize Porcupine wake word: {e}") from e

    def process(self, audio_frame: np.ndarray) -> bool:
        """
        Returns True if wake word detected in this frame.
        Thread-safe (Porcupine is thread-safe internally).
        audio_frame should be 16kHz integer array of size frame_length.
        """
        if self.porcupine is None:
            # If no wake word is active, we just return False
            return False

        # Ensure it's int16 for porcupine
        if audio_frame.dtype == np.float32:
            # Convert float [-1.0, 1.0] to int16
            pcm = (audio_frame * 32767).astype(np.int16)
        else:
            pcm = audio_frame.astype(np.int16)

        keyword_index = self.porcupine.process(pcm)
        # bool(): porcupine is untyped, so the comparison is Any to mypy.
        return bool(keyword_index >= 0)

    def delete(self) -> None:
        """
        Call porcupine.delete() to release native resources.
        Called during graceful shutdown.
        """
        if self.porcupine is not None:
            self.porcupine.delete()
            self.porcupine = None
            logger.info("porcupine_resources_released")

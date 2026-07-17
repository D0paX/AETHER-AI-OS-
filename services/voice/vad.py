from typing import Any

import numpy as np
import structlog
import torch

from services.voice.models import VoiceError

logger = structlog.get_logger(__name__)


class SileroVAD:
    def __init__(self, threshold: float = 0.5, sampling_rate: int = 16000):
        self.threshold = threshold
        self.sampling_rate = sampling_rate
        # Any: the silero model is returned by torch.hub.load, which is untyped.
        self._model: Any = None

    def load_model(self) -> None:
        try:
            # VAD does not need GPU, strictly use CPU
            # torch.hub.load carries no annotations upstream, so --strict flags
            # the call itself; the ignore is scoped to that single rule.
            self._model, _ = torch.hub.load(  # type: ignore[no-untyped-call]
                repo_or_dir="snakers4/silero-vad",
                model="silero_vad",
                force_reload=False,
                trust_repo=True,
            )
            self._model.eval()
            self._model.to("cpu")
            logger.info("silero_vad_model_loaded", device="cpu", threshold=self.threshold)
        except Exception as e:
            logger.error("silero_vad_model_load_failed", error=str(e))
            raise VoiceError(f"Failed to load Silero VAD model: {e}") from e

    def is_speech(self, audio_chunk: np.ndarray) -> float:
        """
        Returns speech probability (0.0 to 1.0) for a 480-sample chunk (30ms at 16kHz).
        Thread-safe (torch inference).
        """
        if self._model is None:
            raise VoiceError("VAD model not loaded.")

        # Silero VAD expects a FloatTensor of shape (1, num_samples) in range [-1, 1]
        tensor_chunk = torch.from_numpy(audio_chunk).float().unsqueeze(0).to("cpu")

        # Get speech probability
        with torch.no_grad():
            speech_prob = self._model(tensor_chunk, self.sampling_rate).item()

        # float(): .item() already returns a Python float, but the untyped
        # torch.hub model makes it Any to mypy.
        return float(speech_prob)

    def is_speech_threshold(self, audio_chunk: np.ndarray) -> bool:
        """
        Returns True if speech probability is > threshold.
        """
        return self.is_speech(audio_chunk) > self.threshold

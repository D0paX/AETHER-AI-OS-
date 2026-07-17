from enum import Enum

from pydantic import BaseModel, Field


class VoicePipelineState(str, Enum):  # noqa: UP042
    """Voice pipeline lifecycle states.

    UP042 deliberately suppressed: this enum is the `current_state` field of
    VoiceServiceStatus, the /status endpoint's response model, and StrEnum
    changes `str()`/f-string rendering ("VoicePipelineState.IDLE" -> "IDLE").
    Every current use goes through `.value` or `==`, so a conversion would
    likely be safe — but M2.1.9 is a lint/type pass that must change no
    behavior, so the base-class change is deferred rather than bundled in.
    """

    IDLE = "IDLE"
    WAKE_DETECTED = "WAKE_DETECTED"
    LISTENING = "LISTENING"
    TRANSCRIBING = "TRANSCRIBING"
    TRANSCRIPT_READY = "TRANSCRIPT_READY"
    SPEAKING = "SPEAKING"


class TranscriptionResult(BaseModel, frozen=True):
    text: str
    confidence: float
    audio_duration_ms: int
    processing_ms: int
    model_used: str


class SpeakRequest(BaseModel, frozen=True):
    session_id: str
    text: str
    priority: int = Field(ge=1, le=10, default=5)
    interrupt_current: bool = False


class VoiceServiceStatus(BaseModel, frozen=True):
    current_state: VoicePipelineState
    stt_ready: bool
    tts_ready: bool
    wake_word_active: bool
    model_loaded: str
    uptime_seconds: float


class VoiceError(Exception):
    """Base exception for voice service errors."""

    pass


class VoiceTranscriptionError(VoiceError):
    """Raised when STT fails."""

    pass


class VoiceSynthesisError(VoiceError):
    """Raised when TTS fails."""

    pass

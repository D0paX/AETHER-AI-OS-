import os

import numpy as np
import pytest
import soundfile as sf
from fastapi.testclient import TestClient

from services.voice.server import app
from services.voice.stt import FasterWhisperSTT
from services.voice.tts import KokoroTTS

# Integration Tests for Voice Pipeline


@pytest.fixture(scope="module")
def stt_model():
    model = FasterWhisperSTT(model_size="medium.en", device="cuda", compute_type="float16")
    model.load_model()
    return model


@pytest.fixture(scope="module")
def tts_model():
    model = KokoroTTS(voice="af_sarah")
    model.load_model()
    return model


@pytest.mark.asyncio
async def test_stt_transcription(stt_model):
    """Test 1: Verify STT accurately transcribes the test utterance."""
    fixture_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)), "fixtures", "test_utterance.wav"
    )

    if not os.path.exists(fixture_path):
        pytest.skip("test_utterance.wav not found. Run record_test_audio.py first.")

    data, samplerate = sf.read(fixture_path, dtype="float32")
    # If stereo, take one channel
    if len(data.shape) > 1:
        data = data[:, 0]

    result = stt_model.transcribe(data)

    # Assert confidence and that the model captured something
    assert result.confidence > 0.1
    assert (
        "hello" in result.text.lower()
        or "time" in result.text.lower()
        or "aether" in result.text.lower()
    )
    assert result.model_used == "faster-whisper-medium.en"


def test_tts_synthesis(tts_model):
    """Test 2: Verify KokoroTTS generates audio correctly without playing it."""
    text = "This is an automated test of the speech synthesis engine."
    audio = tts_model.synthesize(text)

    # Check that audio was generated and is float32
    assert isinstance(audio, np.ndarray)
    assert audio.dtype == np.float32
    assert len(audio) > 0


def test_health_endpoint():
    """Test 3: Verify FastAPI server health endpoint."""
    # We don't need the pipeline fully loaded just to check /health
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "voice"}

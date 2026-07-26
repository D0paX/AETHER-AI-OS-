"""Loud-failure tests for wake-word key configuration (M2.1.10 Part 2 / DEBT-018).

VoicePipeline must refuse to initialize — raising VoiceError, not booting to a
silently deaf pipeline — when the Porcupine access key is missing or is the
known .env.example placeholder. The failure must never echo the configured
value. Lives in integration/ because importing the voice stack pulls in torch;
run file-by-file per DEBT-011.
"""

from types import SimpleNamespace

import pytest

import services.voice.pipeline as pipeline_mod
from aether.core.exceptions import VoiceError
from services.voice.pipeline import PORCUPINE_KEY_PLACEHOLDER, VoicePipeline

pytestmark = pytest.mark.integration

REDIS_URL = "redis://127.0.0.1:6379/1"


@pytest.mark.parametrize(
    "bad_key",
    [None, "", PORCUPINE_KEY_PLACEHOLDER],
    ids=["missing", "empty", "placeholder"],
)
def test_missing_or_placeholder_key_fails_loudly(
    bad_key: str | None, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        pipeline_mod,
        "get_config",
        lambda: SimpleNamespace(voice=SimpleNamespace(porcupine_access_key=bad_key)),
    )

    with pytest.raises(VoiceError) as exc_info:
        VoicePipeline(redis_url=REDIS_URL)

    err = exc_info.value
    assert err.error_code == "VOICE_PORCUPINE_KEY_MISSING"
    # Actionable: names the fix and the exact env var.
    assert "console.picovoice.ai" in str(err)
    assert "AETHER_VOICE__PORCUPINE_ACCESS_KEY" in str(err)


def test_failure_message_never_echoes_the_placeholder_value(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Even when the invalid value IS the placeholder, it must not appear."""
    monkeypatch.setattr(
        pipeline_mod,
        "get_config",
        lambda: SimpleNamespace(
            voice=SimpleNamespace(porcupine_access_key=PORCUPINE_KEY_PLACEHOLDER)
        ),
    )

    with pytest.raises(VoiceError) as exc_info:
        VoicePipeline(redis_url=REDIS_URL)

    assert PORCUPINE_KEY_PLACEHOLDER not in str(exc_info.value)


def test_valid_key_passes_the_wake_word_check(monkeypatch: pytest.MonkeyPatch) -> None:
    """A non-placeholder key gets past the key gate (no VoiceError from it)."""
    monkeypatch.setattr(
        pipeline_mod,
        "get_config",
        lambda: SimpleNamespace(voice=SimpleNamespace(porcupine_access_key="test-value-12345")),
    )

    # Constructs fully — the downstream model objects only store params here,
    # they do not load. The point is simply that the key check does not raise.
    pipeline = VoicePipeline(redis_url=REDIS_URL)
    assert pipeline.wake_word.access_key == "test-value-12345"

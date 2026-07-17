"""
Standalone utility script to record a test utterance for M1.10 integration tests.
Saves audio to tests/fixtures/test_utterance.wav.
"""

import os
import time

import numpy as np
import sounddevice as sd
import soundfile as sf


def record_test_utterance() -> None:
    sample_rate = 16000
    duration_sec = 5
    channels = 1
    output_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "tests", "fixtures")
    output_file = os.path.join(output_dir, "test_utterance.wav")

    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "=" * 50)
    print("M1.10 AUDIO HARDWARE VALIDATION")
    print("=" * 50)
    print("\nIn 3 seconds, say: 'hello aether what time is it'")

    for i in range(3, 0, -1):
        print(f"{i}...")
        time.sleep(1)

    print("\n🔴 RECORDING (5 seconds)...")

    # Record audio
    recording = sd.rec(
        int(duration_sec * sample_rate), samplerate=sample_rate, channels=channels, dtype=np.float32
    )
    sd.wait()  # Wait until recording is finished

    print("⏹️ Recording complete.")

    # Save as WAV file
    sf.write(output_file, recording, sample_rate)
    print(f"✅ Saved to {output_file}")
    print("\nTo test playback, we will now play it back to you.")
    time.sleep(1)
    print("🔊 PLAYING...")

    # Play back
    sd.play(recording, sample_rate)
    sd.wait()

    print("⏹️ Playback complete.")
    print("=" * 50 + "\n")


if __name__ == "__main__":
    record_test_utterance()

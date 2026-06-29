"""Audio hardware validation script."""

import sys

try:
    import numpy as np
    import sounddevice as sd
except ImportError as e:
    print(f"Audio test FAILED: Could not import required dependencies: {e}")
    sys.exit(1)


def test_audio_hardware() -> bool:
    """Test the audio hardware by recording and playing back 2 seconds of audio.

    Returns:
        bool: True if test passes, False otherwise.
    """
    samplerate = 16000
    duration = 2.0
    channels = 1

    print("Speak into your microphone now...")
    print(f"Recording for {duration} seconds at {samplerate} Hz...")

    try:
        recording = sd.rec(
            int(duration * samplerate), samplerate=samplerate, channels=channels, dtype=np.float32
        )
        sd.wait()

        print("Recording complete. Playing back...")
        sd.play(recording, samplerate)
        sd.wait()

        print("Audio test PASSED")
        return True
    except sd.PortAudioError as e:
        print(f"Audio test FAILED: PortAudioError: {e}")
        return False
    except OSError as e:
        print(f"Audio test FAILED: OSError: {e}")
        return False
    except RuntimeError as e:
        print(f"Audio test FAILED: RuntimeError: {e}")
        return False
    except Exception as e:
        print(f"Audio test FAILED: Unexpected exception: {e}")
        return False


if __name__ == "__main__":
    success = test_audio_hardware()
    if not success:
        sys.exit(1)
    sys.exit(0)

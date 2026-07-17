# Audio Hardware Configuration

**Date configured:** ___________
**System:** Windows 11, RTX 4050 Laptop GPU

## Audio Devices
Input device (microphone):
  Name: ___________
  sounddevice index: ___
  Sample rate: 16000 Hz

Output device (speaker):
  Name: ___________
  sounddevice index: ___

## VAD Calibration
Threshold setting: ___ (default 0.5)
Silence duration (ms): ___ (default 800)

## Test Results
Audio record/playback test (M0): PASS / FAIL
Whisper medium VRAM usage observed: ___ GB
Kokoro synthesis latency (1 short sentence): ___ ms
End-to-end latency (wake word confirmed → first audio byte): ___ ms
  (Measured across 10 utterances — record median and max)

## Known Issues
(document any Windows-specific audio quirks discovered)

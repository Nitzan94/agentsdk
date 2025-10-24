# Voice Recording Scripts Created

**Tags:** p, y, t, h, o, n, ,,  , v, o, i, c, e, -, r, e, c, o, r, d, i, n, g, ,,  , a, u, d, i, o, ,,  , p, r, o, d, u, c, t, i, v, i, t, y, ,,  , t, o, o, l, s

**Created:** 2025-10-24T01:01:35.166132

---

# Voice Recording Scripts

Created two Python scripts for voice-activated recording:

## 1. voice_recorder.py
- Auto-starts when you speak
- Auto-stops after silence (300ms default)
- Uses WebRTC VAD for voice detection
- Saves timestamped WAV files

## 2. voice_and_text_recorder.py
- Records voice AND captures typed text simultaneously
- Dual-threaded design (voice + text input)
- Synchronized output (audio + notes)
- Creates 3 files per recording: .wav, .txt, .json

## Dependencies Installed
- pyaudio (audio recording)
- webrtcvad (voice activity detection)

## Usage
```bash
python voice_and_text_recorder.py
```

## Output Directory
All recordings saved to: `recordings/`
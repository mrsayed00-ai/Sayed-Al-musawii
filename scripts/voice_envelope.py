"""Per-frame (30 fps) loudness envelope of the voice-over, normalised to the
98th percentile. Used later to drive the pixel character's mouth (measured
from the audio, not guessed). Usage: voice_envelope.py voice16k.wav out.json"""
import json
import sys

import numpy as np
import soundfile as sf

x, sr = sf.read(sys.argv[1], dtype="float32")
hop = sr // 30
rms = np.array([np.sqrt(np.mean(x[i : i + hop] ** 2)) for i in range(0, len(x), hop)])
env = (rms / np.percentile(rms, 98)).clip(0, 1)
json.dump({"fps": 30, "env": [round(float(v), 3) for v in env]}, open(sys.argv[2], "w"))

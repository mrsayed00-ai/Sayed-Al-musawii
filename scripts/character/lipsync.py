"""Mouth track for the pixel character, from measurements only.

- Outside the measured speech phrases (Silero VAD, transcript.json) the mouth
  is held closed: no movement during silence, breaths or room noise.
- Inside a phrase the shape follows the measured loudness envelope, updated
  at 15 fps (pairs of 30 fps frames, louder of the two) so it does not
  flicker. Dips between syllables (below 35% of the local peak within
  +-130 ms) close the mouth, so long phrases do not hold it open.
- Loudness is not articulation: this does not reproduce lip closures for
  م/ب or rounding for و; it only opens with the voice and closes with it.
"""
import json

from sprite import mouth_for_level

PAD = 0.03  # s, VAD edge tolerance


def speech_spans(transcript_path):
    return [(p["start"], p["end"]) for p in json.load(open(transcript_path))["phrases"]]


def mouth_track(env, spans, fps=30, rest="closed"):
    n = len(env)
    track = []
    for f in range(n):
        t = f / fps
        if not any(a - PAD <= t <= b + PAD for a, b in spans):
            track.append(rest)
            continue
        g = f - f % 2
        lvl = max(env[g], env[g + 1] if g + 1 < n else 0.0)
        shape = mouth_for_level(lvl)
        # dips between syllables: compare with the loudest frame within +-130 ms
        peak = max(env[max(0, g - 4): g + 6]) or 1e-6
        rel = lvl / peak
        if rel < 0.35:
            shape = "closed"
        elif rel < 0.6 and shape in ("open", "wide"):
            shape = "half"
        track.append(shape)
    return track

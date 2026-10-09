"""Per-frame timeline for the animated previews (30 fps, length = voice).

- Scene windows: scene starts at its first phrase (measured) and section
  changes sit at the cut points inside measured silences.
- Everything is derived from analysis/transcript.json (current recording):
  length, scene windows, cut points (mid-silence), gesture windows.
- V1 character per frame: expression (per scene), mouth (lipsync.mouth_track
  on the enhanced voice, gated by the measured VAD segments), blink, gesture,
  size (big/small).
- Writes renders/video/timeline.json and every character sprite the
  timeline needs to renders/storyboard/assets/charv/<key>.png (+ _tall).
Usage: build_timeline.py <repo_root>
"""
import json
import math
import os
import sys

from PIL import Image

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "scripts", "character"))
from gestures import compose_gesture  # noqa: E402
from lipsync import mouth_track  # noqa: E402

FPS = 30
tr = json.load(open(f"{root}/analysis/transcript.json"))
P = {p["id"]: p for p in tr["phrases"]}
DUR = json.load(open(f"{root}/analysis/audio_enhance_report.json"))["duration_out_s"]  # = the recording, exactly
N = math.ceil(DUR * FPS)


def cut(a):
    """mid-silence between phrase a and a+1 (section changes and pixel transitions)"""
    return round((P[a]["end"] + P[a + 1]["start"]) / 2, 2)


CUTS = [cut(3), cut(11), cut(17), cut(20), cut(22)]
for c, a in zip(CUTS, (3, 11, 17, 20, 22)):
    assert P[a]["end"] + 0.25 <= c <= P[a + 1]["start"] - 0.25, f"cut {c} too close to speech"

# (id, start, end, size, expression); a scene starts with its first phrase,
# or at the cut point when it opens a section
S = lambda n: P[n]["start"]  # noqa: E731
SCENES = [
    ("S01", 0.0, S(1), "big", "neutral"), ("S02", S(1), S(2), "big", "neutral"),
    ("S03", S(2), S(3), "big", "sly"), ("S04", S(3), CUTS[0], "big", "suspicious"),
    ("S05", CUTS[0], S(5), "small", "neutral"), ("S06", S(5), S(6), "small", "neutral"),
    ("S07", S(6), S(7), "small", "sly"), ("S08", S(7), S(8), "small", "suspicious"),
    ("S09", S(8), S(9), "small", "neutral"), ("S10", S(9), S(10), "small", "surprised"),
    ("S11", S(10), CUTS[1], "small", "laugh"), ("S12", CUTS[1], S(13), "small", "neutral"),
    ("S13", S(13), S(14), "small", "neutral"), ("S14", S(14), S(16), "small", "sly"),
    ("S15", S(16), CUTS[2], "small", "neutral"), ("S16", CUTS[2], S(20), "small", "sly"),
    ("S17", S(20), CUTS[3], "small", "neutral"), ("S18", CUTS[3], CUTS[4], "small", "neutral"),
    ("S19", CUTS[4], S(25), "big", "neutral"), ("S20", S(25), DUR + 0.1, "big", "neutral"),
]
# gestures: (start, end, kind); waves cycle a-b-a-c at 6 fps
WAVE_END = round(S(25) + 0.81, 2)  # same wave length on the end card as approved
GESTURES = [(S(11), P[11]["end"], "point_right"), (S(23), P[24]["end"], "wave"),
            (S(25), WAVE_END, "wave"), (WAVE_END, DUR + 0.1, "point_up")]

# mouth gate: the measured VAD segments of the original (timing is identical in
# the enhanced file, lag 1 sample); the envelope comes from the enhanced file
spans = [tuple(sg) for p in tr["phrases"] for sg in p["vad_segments"]]
LAST_SPEECH_END = spans[-1][1]
env = json.load(open(f"{root}/analysis/voice_env30_enhanced.json"))["env"]
env = (env + [0.0] * N)[:N]
mouths = mouth_track(env, spans, FPS)

frames = []
for i in range(N):
    t = i / FPS
    sc = next(s for s in SCENES if s[1] <= t < s[2])
    expr = sc[4]
    mouth = mouths[i]
    if t > LAST_SPEECH_END + 0.1 and mouth == "closed":
        mouth = "smile"  # final hold on the end card
    gest = None
    for a, b, k in GESTURES:
        if a <= t < b:
            gest = k if k != "wave" else ("wave_a", "wave_b", "wave_a", "wave_c")[(i // 5) % 4]
    eyes_open = expr not in ("laugh", "suspicious")
    blink = eyes_open and (i % 96) in (0, 1, 2)
    key = f"{expr}_{mouth}_{int(blink)}_{gest or 'none'}"
    frames.append({"scene": sc[0], "size": sc[3], "char": key})

out_assets = f"{root}/renders/storyboard/assets/charv"
os.makedirs(out_assets, exist_ok=True)
for key in sorted({f["char"] for f in frames}):
    expr, mouth, blink, gest = key.split("_", 3)
    im = compose_gesture(expr, mouth=mouth, blink=blink == "1", gesture=None if gest == "none" else gest)
    im.save(f"{out_assets}/{key}.png")
    tall = Image.new("RGBA", (im.width, im.height + 40), (0, 0, 0, 0))
    tall.paste(im, (0, 0))
    last = im.crop((0, im.height - 1, im.width, im.height))
    for y in range(im.height, im.height + 40):
        tall.paste(last, (0, y))
    tall.save(f"{out_assets}/{key}_tall.png")

os.makedirs(f"{root}/renders/video", exist_ok=True)
json.dump({"fps": FPS, "duration": DUR, "n": N, "cuts": CUTS,
           "scenes": [{"id": s[0], "start": s[1], "end": min(s[2], DUR)} for s in SCENES],
           "phrases": [{"id": p["id"], "start": p["start"], "end": p["end"], "segments": p["vad_segments"]} for p in tr["phrases"]],
           "gestures": GESTURES,
           "frames": frames},
          open(f"{root}/renders/video/timeline.json", "w"), ensure_ascii=False)
print("frames", N, "sprites", len({f['char'] for f in frames}))

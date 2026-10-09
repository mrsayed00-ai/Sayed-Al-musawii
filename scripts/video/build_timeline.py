"""Per-frame timeline for the animated previews (30 fps, length = voice).

- Scene windows: scene starts at its first phrase (measured) and section
  changes sit at the cut points inside measured silences.
- V1 character per frame: expression (per scene), mouth (lipsync.mouth_track
  on the enhanced voice and its VAD spans), blink, gesture, size (big/small).
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
DUR = 55.744
N = math.ceil(DUR * FPS)
CUTS = [5.8, 21.5, 36.75, 43.85, 49.45]

# (id, start, end, size, expression)
SCENES = [
    ("S01", 0.0, 1.0, "big", "neutral"), ("S02", 1.0, 2.86, "big", "neutral"),
    ("S03", 2.86, 4.62, "big", "sly"), ("S04", 4.62, 5.8, "big", "suspicious"),
    ("S05", 5.8, 8.04, "small", "neutral"), ("S06", 8.04, 11.43, "small", "neutral"),
    ("S07", 11.43, 12.52, "small", "sly"), ("S08", 12.52, 15.69, "small", "suspicious"),
    ("S09", 15.69, 17.23, "small", "neutral"), ("S10", 17.23, 18.6, "small", "surprised"),
    ("S11", 18.6, 21.5, "small", "laugh"), ("S12", 21.5, 24.55, "small", "neutral"),
    ("S13", 24.55, 27.18, "small", "neutral"), ("S14", 27.18, 31.82, "small", "sly"),
    ("S15", 31.82, 36.75, "small", "neutral"), ("S16", 36.75, 40.84, "small", "sly"),
    ("S17", 40.84, 43.85, "small", "neutral"), ("S18", 43.85, 49.45, "small", "neutral"),
    ("S19", 49.45, 52.94, "big", "neutral"), ("S20", 52.94, DUR + 0.1, "big", "neutral"),
]
# gestures: (start, end, kind); waves cycle a-b-a-c at 6 fps
GESTURES = [(20.23, 21.09, "point_right"), (49.83, 52.13, "wave"), (52.94, 53.75, "wave"), (53.75, DUR + 0.1, "point_up")]
LAST_SPEECH_END = None

tr = json.load(open(f"{root}/analysis/transcript.json"))
spans = [tuple(p.get("vad_enhanced", (p["start"], p["end"]))) for p in tr["phrases"]]
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
           "phrases": [{"id": p["id"], "start": p["start"], "end": spans[k][1]} for k, p in enumerate(tr["phrases"])],
           "frames": frames},
          open(f"{root}/renders/video/timeline.json", "w"), ensure_ascii=False)
print("frames", N, "sprites", len({f['char'] for f in frames}))

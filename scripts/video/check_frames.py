"""Post-render checks on the preview frames: no readable QR code in the scenes
that show the QR cards (every 3rd frame), using the same two readers as
qr_pixel.py. Usage: check_frames.py <repo_root>"""
import glob
import json
import os
import sys

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "scripts", "storyboard"))
from qr_pixel import qr_found  # noqa: E402

tl = json.load(open(f"{root}/renders/video/timeline.json"))
win = {s["id"]: (s["start"], s["end"]) for s in tl["scenes"]}
scenes = ("S06", "S13", "S15", "S19")
bad, checked = [], 0
for v in ("V1", "V2"):
    for sid in scenes:
        a, b = win[sid]
        for i in range(int(a * tl["fps"]), int(b * tl["fps"]), 3):
            f = f"{root}/renders/video/frames_{v}/f{i:05d}.jpg"
            if not os.path.exists(f):
                continue
            checked += 1
            r = qr_found(f)
            if r != (0, []):
                bad.append((v, i, r))
print(json.dumps({"frames_checked": checked, "qr_found": bad}, ensure_ascii=False))

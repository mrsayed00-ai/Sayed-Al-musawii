"""Prepare storyboard assets from the local (git-ignored) media folder.

- phone screenshots: crop iOS status bar (top) and Safari bar (bottom)
- host screenshots: copied as-is
- recording frames: rotated 90deg CCW (transpose=2); movies frame cropped
  above the price pills (no prices on screen, user decision)
- character sprites at scale 1 (+ a tall variant whose jacket runs to the
  bottom of the frame)
Usage: build_assets.py <repo_root>
"""
import glob
import os
import shutil
import subprocess
import sys

from PIL import Image

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "scripts", "character"))
from sprite import compose  # noqa: E402

media = os.path.join(root, "media")
out = os.path.join(root, "renders", "storyboard", "assets")
os.makedirs(out, exist_ok=True)

PHONE_TOP, PHONE_BOTTOM = 150, 1836  # Safari bar starts at y=1838 on 943x2048 shots
for f in sorted(glob.glob(f"{media}/shots/A*.jpg")):
    n = os.path.basename(f)[:-4]
    Image.open(f).convert("RGB").crop((0, PHONE_TOP, 943, PHONE_BOTTOM)).save(f"{out}/{n}.png")
for f in sorted(glob.glob(f"{media}/shots/B*.jpg")):
    Image.open(f).convert("RGB").save(f"{out}/{os.path.basename(f)[:-4]}.png")

rec = glob.glob(f"{media}/source/game_recording_*.mp4")[0]
for t in ("25.3", "26.5", "33.5", "43.5"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", rec, "-frames:v", "1",
                    "-vf", "transpose=2", f"{out}/G_{t}.png"], check=True)
# movies: keep header + posters, cut before the "1.00 KWD" pills (y >= 268)
Image.open(f"{out}/G_43.5.png").crop((0, 0, 848, 264)).save(f"{out}/G_movies_noprice.png")

for f in glob.glob(f"{media}/fonts/*.ttf") + [f"{media}/brand/fanous_wordmark_white.png"]:
    shutil.copy(f, out)

STATES = {
    "neutral_smile": ("neutral", "smile"), "neutral_half": ("neutral", "half"),
    "neutral_open": ("neutral", "open"), "sly": ("sly", None), "suspicious": ("suspicious", None),
    "surprised": ("surprised", None), "laugh": ("laugh", None), "blink": ("neutral", "smile"),
}
for name, (expr, mouth) in STATES.items():
    spr = compose(expr, mouth=mouth, blink=(name == "blink"))
    spr.save(f"{out}/char_{name}.png")
    tall = Image.new("RGBA", (spr.width, spr.height + 40), (0, 0, 0, 0))
    tall.paste(spr, (0, 0))
    last = spr.crop((0, spr.height - 1, spr.width, spr.height))
    for y in range(spr.height, spr.height + 40):
        tall.paste(last, (0, y))
    tall.save(f"{out}/char_{name}_tall.png")
print("assets ->", out)

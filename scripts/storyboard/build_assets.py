"""Prepare storyboard assets from the local (git-ignored) media folder.

- phone screenshots: crop iOS status bar (top) and Safari bar (bottom)
- host screenshots: copied as-is, except B02/B04 whose real QR codes are
  replaced by non-scannable pixel art (qr_pixel.py, verified with two readers)
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

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qr_pixel import QR_AREAS, pixelize, qr_found  # noqa: E402

media = os.path.join(root, "media")
out = os.path.join(root, "renders", "storyboard", "assets")
os.makedirs(out, exist_ok=True)

PHONE_TOP, PHONE_BOTTOM = 150, 1836  # Safari bar starts at y=1838 on 943x2048 shots
for f in sorted(glob.glob(f"{media}/shots/*.jpg")):
    n = os.path.basename(f)[:-4]
    im = Image.open(f).convert("RGB")
    if n in QR_AREAS:
        continue  # real QR codes never reach the assets; see qr_pixel.py
    if im.size == (943, 2048):  # phone (A##, C01-C02)
        im = im.crop((0, PHONE_TOP, 943, PHONE_BOTTOM))
    im.save(f"{out}/{n}.png")
for n in QR_AREAS:
    src = f"{media}/shots/{n}.jpg"
    pixelize(src, n).save(f"{out}/{n}_pxqr.png")
    found = qr_found(f"{out}/{n}_pxqr.png")
    assert found == (0, []), f"{n}: QR still readable"

rec = glob.glob(f"{media}/source/game_recording_*.mp4")[0]
for t in ("25.3", "26.5", "33.5", "43.5"):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", t, "-i", rec, "-frames:v", "1",
                    "-vf", "transpose=2", f"{out}/G_{t}.png"], check=True)
# S19 section tiles from the category pages (D01-D04, 2048x943): keep rows
# 0-900 (header, section pill, first card row; the Movies "1.00 KWD" pills
# start at y=913), crop to each tile's exact aspect (V2 430x280: centred
# 1382x900, V1 410x180: full width) and resample to 2x the tile size, so the
# browser never stretches or crops them.
TILE_SRC = {"imp": "D01", "blind": "D02", "movies": "D03", "kids": "D04"}
for key, n in TILE_SRC.items():
    page = Image.open(f"{media}/shots/{n}.jpg").convert("RGB")
    assert page.size == (2048, 943), (n, page.size)
    for v, (tw, th) in (("v2", (430, 280)), ("v1", (410, 180))):
        h = min(900, round(2048 * th / tw))
        w = round(h * tw / th)
        x0 = (2048 - w) // 2
        tile = page.crop((x0, 0, x0 + w, h)).resize((2 * tw, 2 * th), Image.LANCZOS)
        tile.save(f"{out}/S19_{key}_{v}.png")
        assert qr_found(f"{out}/S19_{key}_{v}.png") == (0, []), f"S19_{key}_{v}: QR found"

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

"""Contact sheet of frames named t<seconds>.jpg (render_video.js --test, or
frames pulled from an export) labelled with time and the phrase spoken then.
Usage: contact_sheet.py <repo_root> <frames_dir> <out.jpg> [cols]"""
import glob
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

root, fdir, out = sys.argv[1:4]
cols = int(sys.argv[4]) if len(sys.argv) > 4 else 7
tr = json.load(open(f"{root}/analysis/transcript.json"))
fs = sorted(glob.glob(f"{fdir}/t*.jpg"), key=lambda f: float(os.path.basename(f)[1:-4]))
w, h = 270, 480
rows = (len(fs) + cols - 1) // cols
sheet = Image.new("RGB", (cols * w, rows * (h + 40)), (20, 14, 46))
font = ImageFont.truetype(f"{root}/media/fonts/Cairo.ttf", 20)
d = ImageDraw.Draw(sheet)
for k, f in enumerate(fs):
    t = float(os.path.basename(f)[1:-4])
    ph = next((p["id"] for p in tr["phrases"] if p["start"] <= t <= p["end"]), None)
    im = Image.open(f).convert("RGB").resize((w, h), Image.LANCZOS)
    x, y = (k % cols) * w, (k // cols) * (h + 40)
    sheet.paste(im, (x, y + 40))
    d.text((x + w // 2, y + 20), f"{t:.2f}s  " + (f"phrase {ph}" if ph else "silence"), font=font, fill="white", anchor="mm")
sheet.save(out, quality=88)
print(out, len(fs))

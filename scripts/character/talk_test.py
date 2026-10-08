"""Lip-sync test: mouth chosen per frame from the measured loudness envelope,
blink every ~3.2 s. Writes PNG frames; ffmpeg muxes them with the original
voice (copied, not re-encoded). Usage: talk_test.py <env.json> <out_dir> <seconds>"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter

from sprite import compose, mouth_for_level

env_path, out_dir, secs = sys.argv[1], sys.argv[2], float(sys.argv[3])
env = json.load(open(env_path))
fps, levels = env["fps"], env["env"]
os.makedirs(out_dir, exist_ok=True)
S = 640
bg = Image.new("RGB", (S, S))
d = ImageDraw.Draw(bg)
for y in range(S):
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(82 * (1 - t) + 20 * t), int(48 * (1 - t) + 15 * t), int(187 * (1 - t) + 46 * t)))
glow = Image.new("L", (S, S), 0)
ImageDraw.Draw(glow).ellipse([80, 120, 560, 640], fill=160)
bg = Image.composite(Image.new("RGB", (S, S), (150, 132, 255)), bg, glow.filter(ImageFilter.GaussianBlur(80)))
cache = {}
for i in range(int(secs * fps)):
    lvl = levels[i] if i < len(levels) else 0.0
    m = mouth_for_level(lvl)
    blink = (i % 96) in (0, 1, 2)
    key = (m, blink)
    if key not in cache:
        spr = compose("neutral", mouth=m, blink=blink)
        cache[key] = spr.resize((spr.width * 10, spr.height * 10), Image.NEAREST)
    fr = bg.copy()
    spr = cache[key]
    fr.paste(spr, ((S - spr.width) // 2, S - spr.height), spr)
    fr.save(f"{out_dir}/f{i:05d}.png")
print("frames", i + 1)

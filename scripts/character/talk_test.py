"""Lip-sync test: mouth from lipsync.mouth_track (closed outside measured
speech, loudness-driven inside), blink every ~3.2 s. Writes PNG frames plus a
review chart; ffmpeg muxes the frames with the original voice (copied, not
re-encoded).
Usage: talk_test.py <env.json> <transcript.json> <out_dir> <seconds> <font.ttf>"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFilter, ImageFont

from lipsync import mouth_track, speech_spans
from sprite import compose

env_path, tr_path, out_dir, secs, font_path = sys.argv[1], sys.argv[2], sys.argv[3], float(sys.argv[4]), sys.argv[5]
env = json.load(open(env_path))
fps, levels = env["fps"], env["env"]
spans = speech_spans(tr_path)
track = mouth_track(levels, spans, fps)
nfr = int(secs * fps)
os.makedirs(f"{out_dir}/frames", exist_ok=True)

S = 640
bg = Image.new("RGB", (S, S))
d = ImageDraw.Draw(bg)
for y in range(S):
    t = y / S
    d.line([(0, y), (S, y)], fill=(int(127 * (1 - t) + 82 * t), int(113 * (1 - t) + 48 * t), int(206 * (1 - t) + 187 * t)))
glow = Image.new("L", (S, S), 0)
ImageDraw.Draw(glow).ellipse([80, 120, 560, 640], fill=150)
bg = Image.composite(Image.new("RGB", (S, S), (255, 255, 255)), bg, glow.filter(ImageFilter.GaussianBlur(90)))
cache = {}
for i in range(nfr):
    blink = (i % 96) in (0, 1, 2)
    key = (track[i], blink)
    if key not in cache:
        spr = compose("neutral", mouth=track[i], blink=blink)
        cache[key] = spr.resize((spr.width * 10, spr.height * 10), Image.NEAREST)
    fr = bg.copy()
    fr.paste(cache[key], ((S - 480) // 2, S - 600), cache[key])
    fr.save(f"{out_dir}/frames/f{i:05d}.png")

# review chart: loudness, measured speech spans, chosen mouth per frame
W, H = 2400, 520
ch = Image.new("RGB", (W, H), (18, 13, 46))
cd = ImageDraw.Draw(ch)
f = ImageFont.truetype(font_path, 26)
px = W / nfr
for a, b in spans:
    if a < secs:
        cd.rectangle([a * fps * px, 40, min(b, secs) * fps * px, 70], fill=(242, 166, 15))
cd.text((W - 10, 6), "العبارات المقاسة (VAD)", font=f, fill=(242, 166, 15), anchor="ra")
for i in range(nfr):
    v = levels[i]
    x = i * px
    cd.line([x, 260, x, 260 - v * 170], fill=(178, 164, 255))
cd.text((W - 10, 76), "شدة الصوت", font=f, fill=(178, 164, 255), anchor="ra")
COL = {"closed": (60, 52, 90), "half": (120, 200, 255), "open": (80, 140, 255), "wide": (255, 90, 120)}
for i in range(nfr):
    cd.rectangle([i * px, 300, (i + 1) * px, 360], fill=COL[track[i]])
cd.text((W - 10, 366), "شكل الفم: داكن = مغلق، سماوي = نصف، أزرق = مفتوح، وردي = واسع", font=f, fill=(255, 255, 255), anchor="ra")
for s in range(int(secs) + 1):
    x = s * fps * px
    cd.line([x, 410, x, 425], fill=(255, 255, 255))
    cd.text((x + 3, 428), f"{s}s", font=f, fill=(255, 255, 255))
outside_open = sum(1 for i in range(nfr) if track[i] != "closed"
                   and not any(a - 0.03 <= i / fps <= b + 0.03 for a, b in spans))
changes = sum(1 for i in range(1, nfr) if track[i] != track[i - 1])
cd.text((W - 10, 470), f"إطارات فم مفتوح خارج الكلام: {outside_open}   |   تغيّرات الفم: {changes} في {secs:.1f} ث",
        font=f, fill=(255, 255, 255), anchor="ra")
ch.save(f"{out_dir}/lipsync_review_chart.png")
print("frames", nfr, "outside_open", outside_open, "changes", changes)

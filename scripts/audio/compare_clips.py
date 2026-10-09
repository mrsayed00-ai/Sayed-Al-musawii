"""Before/after listening clips with on-screen labels (what is playing now).
Segments are loudness-matched to the enhanced clip so the comparison is not
biased by "louder sounds better". Also writes a clip of phrase 4 for an
optional re-record and a before/after spectrogram of «في فانوس!».
First recording only (archived: media/derived/rec1/, renders/archive_rec1/audio/);
the user re-recorded the whole voice-over afterwards.
Usage: compare_clips.py <repo_root>"""
import subprocess
import sys

import matplotlib
import numpy as np
import soundfile as sf
from PIL import Image, ImageDraw, ImageFont

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

root = sys.argv[1]
ORIG = f"{root}/renders/archive_rec1/audio/voice_orig_48k.wav"
ENH = f"{root}/media/derived/rec1/voice_enhanced_v1.wav"
OUT = f"{root}/renders/archive_rec1/audio"
FONT = f"{root}/media/fonts/Cairo.ttf"
o, sr = sf.read(ORIG, dtype="float64")
e, _ = sf.read(ENH, dtype="float64")
o, e = o[:, 0], e[:, 0]


def rms_db(a):
    return 20 * np.log10(np.sqrt(np.mean(a ** 2)) + 1e-12)


def card(lines, path, color):
    im = Image.new("RGB", (1080, 1080), (82, 48, 187))
    d = ImageDraw.Draw(im)
    d.rectangle([60, 300, 1020, 780], fill=color)
    f1 = ImageFont.truetype(FONT, 76)
    f2 = ImageFont.truetype(FONT, 42)
    d.text((540, 430), lines[0], font=f1, fill=(255, 255, 255), anchor="mm")
    for i, ln in enumerate(lines[1:]):
        d.text((540, 560 + i * 70), ln, font=f2, fill=(255, 255, 255), anchor="mm")
    im.save(path)


def build(name, segs):
    parts = []
    ref = None
    for k, (label, src, a, b, color) in enumerate(segs):
        x = (o if src == "orig" else e)[int(a * sr):int(b * sr)].copy()
        if ref is None and src == "enh":
            ref = rms_db(x)
        parts.append([label, src, x, color])
    ref = ref if ref is not None else rms_db(parts[0][2])
    files = []
    for k, (label, src, x, color) in enumerate(parts):
        if src == "orig":
            x = x * 10 ** ((ref - rms_db(x)) / 20)  # level-match for a fair comparison
        x = np.concatenate([np.zeros(int(0.5 * sr)), x, np.zeros(int(0.6 * sr))])
        x = np.clip(x, -0.95, 0.95)
        wav = f"{OUT}/_{name}_{k}.wav"
        sf.write(wav, np.stack([x, x], 1), sr)
        png = f"{OUT}/_{name}_{k}.png"
        card(label, png, color)
        mp4 = f"{OUT}/_{name}_{k}.mp4"
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-loop", "1", "-framerate", "30", "-i", png, "-i", wav,
                        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-tune", "stillimage", "-c:a", "aac", "-b:a", "256k",
                        "-shortest", mp4], check=True)
        files.append(mp4)
    lst = f"{OUT}/_{name}.txt"
    open(lst, "w").write("".join(f"file '{f}'\n" for f in files))
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy",
                    f"{OUT}/{name}.mp4"], check=True)


BEFORE, AFTER, REF = (120, 120, 140), (15, 156, 90), (229, 58, 52)
build("compare_fanous_7s", [
    (["قبل: الأصل", "«هذي لعبة الأمبوستر في فانوس!» (6.0–7.9 ث)"], "orig", 5.95, 7.85, BEFORE),
    (["بعد: معالجة موضعية + تحسين خفيف", "نفس المقطع، نفس التوقيت"], "enh", 5.95, 7.85, AFTER),
    (["للمقارنة: «فانوس Movies» من 39 ث", "الكلمة نفسها بنطق كامل (الأصل)"], "orig", 39.05, 40.55, REF),
])
build("compare_general_hook", [
    (["قبل: الأصل", "التمهيد (1–5.6 ث)"], "orig", 0.85, 5.65, BEFORE),
    (["بعد: تحسين خفيف", "نفس المقطع، نفس التوقيت"], "enh", 0.85, 5.65, AFTER),
])

# clip for an optional re-record of phrase 4 (original audio, untouched)
subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", "5.9", "-to", "7.9", "-i", f"{root}/media/source/voice_2026-10-08_2307.m4a",
                "-c:a", "aac", "-b:a", "192k", f"{OUT}/phrase4_for_rerecord.m4a"], check=True)

fig, axs = plt.subplots(2, 1, figsize=(12, 6))
for ax, (sig, t) in zip(axs, ((o, "قبل (الأصل)"), (e, "بعد"))):
    s = sig[int(6.85 * sr):int(7.85 * sr)]
    ax.specgram(s, NFFT=1024, Fs=sr, noverlap=896, cmap="magma", vmin=-130, vmax=-20)
    ax.set_ylim(0, 16000)
    ax.set_title(t[::-1] if False else t, fontsize=11)
    ticks = np.arange(0, 1.01, 0.1)
    ax.set_xticks(ticks)
    ax.set_xticklabels([f"{6.85 + v:.1f}" for v in ticks], fontsize=8)
plt.tight_layout()
plt.savefig(f"{OUT}/fanous_before_after_spectrogram.png", dpi=80)
print("ok")

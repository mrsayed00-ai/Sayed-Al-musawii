"""Final deliverables: two-pass H.264 from the lossless frames, BT.709.

- input: renders/video/frames_png_<V>/f%05d.png (render_video.js --scale 1
  --png --no-encode) and the enhanced current voice (voice2_enhanced.wav)
- video: x264 High@4.1 (ref=4 fits the level-4.1 DPB at 1080x1920 for phone
  hardware decoders), preset veryslow, aq-mode 3 (keeps the purple
  gradients clean), two-pass at the highest average bitrate that keeps the
  file under the delivery limit (the chat upload cap is 30 MiB); RGB ->
  yuv420p with the BT.709 matrix (lanczos, accurate rounding) and BT.709
  tags so HD players do not shift the brand colours; 30 fps CFR, faststart
- audio: AAC-LC 256 kb/s 48 kHz straight from the WAV (one generation),
  cut to the recording's exact length
- quality vs the lossless frames in the same YUV 4:2:0 BT.709 space (so
  the score measures compression only): PSNR and SSIM per plane
Usage: encode_final.py <repo_root> [--limit-mib 29.5] [--only V1|V2]
"""
import json
import os
import re
import subprocess
import sys

root = sys.argv[1]
args = sys.argv[2:]
LIMIT = float(args[args.index("--limit-mib") + 1]) if "--limit-mib" in args else 29.5
ONLY = args[args.index("--only") + 1] if "--only" in args else None
NAMES = {"V1": "Fanous_Ad_V1_PixelCharacter_1080x1920.mp4", "V2": "Fanous_Ad_V2_NoCharacter_1080x1920.mp4"}
TITLES = {"V1": "Fanous ad - V1 pixel character", "V2": "Fanous ad - V2 no character"}
AUDIO = f"{root}/media/derived/voice2_enhanced.wav"
OUT = f"{root}/renders/final"
tl = json.load(open(f"{root}/renders/video/timeline.json"))
DUR = tl["duration"]
A_KBPS = 256
TO_YUV = ("scale=1080:1920:flags=lanczos+accurate_rnd+full_chroma_int+full_chroma_inp:"
          "out_color_matrix=bt709:out_range=tv,format=yuv420p")
COLOR = ["-colorspace", "bt709", "-color_primaries", "bt709", "-color_trc", "bt709", "-color_range", "tv"]


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def encode(v, kbps):
    frames = f"{root}/renders/video/frames_png_{v}/f%05d.png"
    log = f"{OUT}/_pass_{v}"
    dst = f"{OUT}/{NAMES[v]}"
    venc = ["-c:v", "libx264", "-profile:v", "high", "-level:v", "4.1", "-preset", "veryslow",
            "-x264-params", "aq-mode=3:ref=4", "-b:v", f"{kbps}k", "-maxrate", "14M", "-bufsize", "28M",
            "-pix_fmt", "yuv420p", "-r", str(tl["fps"]), "-passlogfile", log] + COLOR
    src = ["-framerate", str(tl["fps"]), "-i", frames]
    run(["ffmpeg", "-v", "error", "-y", *src, "-vf", TO_YUV, *venc, "-pass", "1", "-an", "-t", f"{DUR:.6f}", "-f", "null", "-"])
    run(["ffmpeg", "-v", "error", "-y", *src, "-i", AUDIO, "-map", "0:v", "-map", "1:a", "-vf", TO_YUV, *venc, "-pass", "2",
         "-c:a", "aac", "-b:a", f"{A_KBPS}k", "-ar", "48000", "-t", f"{DUR:.6f}",
         "-metadata", f"title={TITLES[v]}", "-movflags", "+faststart", dst])
    for f in os.listdir(OUT):
        if f.startswith(f"_pass_{v}"):
            os.remove(f"{OUT}/{f}")
    return dst


def quality(v, dst):
    """PSNR/SSIM of the file against the lossless frames converted the same way."""
    frames = f"{root}/renders/video/frames_png_{v}/f%05d.png"
    r = subprocess.run(["ffmpeg", "-hide_banner", "-i", dst, "-framerate", str(tl["fps"]), "-i", frames, "-lavfi",
                        f"[0:v]split[a][b];[1:v]{TO_YUV},split[r1][r2];[a][r1]psnr;[b][r2]ssim", "-f", "null", "-"],
                       capture_output=True, text=True)
    p = re.search(r"PSNR y:([\d.inf]+) u:([\d.inf]+) v:([\d.inf]+) average:([\d.inf]+) min:([\d.inf]+)", r.stderr)
    s = re.search(r"SSIM Y:([\d.]+) .*?U:([\d.]+) .*?V:([\d.]+) .*?All:([\d.]+)", r.stderr)
    return {"psnr_db": dict(zip(("y", "u", "v", "avg", "min_frame"), map(float, p.groups()))) if p else None,
            "ssim": dict(zip(("y", "u", "v", "all"), map(float, s.groups()))) if s else None}


os.makedirs(OUT, exist_ok=True)
report = {}
limit_bytes = LIMIT * 1024 * 1024
for v in [x for x in ("V1", "V2") if not ONLY or x == ONLY]:
    # video budget = limit - audio - ~1% container/headroom
    kbps = int(((limit_bytes * 0.99) - A_KBPS * 1000 / 8 * DUR) * 8 / DUR / 1000)
    for attempt in range(4):
        dst = encode(v, kbps)
        size = os.path.getsize(dst)
        print(v, f"{kbps} kb/s ->", round(size / 2 ** 20, 2), "MiB", flush=True)
        if size <= limit_bytes:
            break
        kbps = int(kbps * limit_bytes / size * 0.985)
    report[v] = {"file": os.path.relpath(dst, root), "size_mib": round(size / 2 ** 20, 2), "video_kbps_target": kbps,
                 "audio_kbps": A_KBPS, "quality_vs_lossless_frames": quality(v, dst)}
    print(v, json.dumps(report[v]), flush=True)
rp = f"{OUT}/encode_report.json"
merged = json.load(open(rp)) if os.path.exists(rp) else {}
merged.update(report)  # --only runs in parallel add their version
json.dump(merged, open(rp, "w"), indent=1)

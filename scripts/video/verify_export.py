"""Checks on the exported ads (renders/final/fanous_ad_<V>_1080x1920.mp4).

- streams: 1080x1920, 30 fps, H.264 High, yuv420p, AAC 48 kHz, both starting at 0
- length equals the recording
- the soundtrack is the current recording only: the decoded track against the
  enhanced voice (normalised cross-correlation ~1 at lag 0, residual after
  subtracting it far below the voice) and against the first recording
  (cross-correlation ~0 at every lag)
- loudness, true peak and clipped samples of the decoded track
- no readable QR code in sampled frames (OpenCV + zxing-cpp)
- frames pulled from the file at every phrase and every cut, for a contact sheet
Usage: verify_export.py <repo_root> <silero_vad.onnx>
"""
import json
import os
import subprocess
import sys

import numpy as np
import soundfile as sf

root = sys.argv[1]
sys.path.insert(0, os.path.join(root, "scripts", "storyboard"))
from qr_pixel import qr_found  # noqa: E402

tr = json.load(open(f"{root}/analysis/transcript.json"))
tl = json.load(open(f"{root}/renders/video/timeline.json"))
NEW = f"{root}/media/derived/voice2_enhanced.wav"
OLD = f"{root}/media/source/voice_2026-10-08_2307.m4a"
SR = 16000


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def mono16(path):
    out = f"{root}/renders/final/_tmp16.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", path, "-vn", "-ac", "1", "-ar", str(SR), "-c:a", "pcm_f32le", out])
    x, _ = sf.read(out, dtype="float64")
    os.remove(out)
    return x


def xcorr(a, b):
    n = len(a) + len(b)
    nfft = 1 << (n - 1).bit_length()
    c = np.fft.irfft(np.fft.rfft(a, nfft) * np.conj(np.fft.rfft(b, nfft)), nfft)
    c = np.concatenate([c[-(len(b) - 1):], c[:len(a)]])
    c /= np.sqrt((a ** 2).sum() * (b ** 2).sum())
    k = int(np.argmax(np.abs(c)))
    return float(c[k]), k - (len(b) - 1)


def loud(path):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-vn", "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    j = json.loads(r.stderr[r.stderr.rindex("{"):])
    return float(j["input_i"]), float(j["input_tp"])


new, old = mono16(NEW), mono16(OLD)
report = {}
for v in ("V1", "V2"):
    mp4 = f"{root}/renders/final/fanous_ad_{v}_1080x1920.mp4"
    pr = json.loads(run(["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", mp4]).stdout)
    vs = next(s for s in pr["streams"] if s["codec_type"] == "video")
    as_ = next(s for s in pr["streams"] if s["codec_type"] == "audio")
    out = mono16(mp4)
    m = min(len(out), len(new))
    r_new, lag_new = xcorr(out[:m], new[:m])
    g = (out[:m] @ new[:m]) / (new[:m] @ new[:m])
    res = out[:m] - g * new[:m]
    r_old, lag_old = xcorr(out, old)
    i_lufs, tp = loud(mp4)
    full, _ = sf.read(NEW, dtype="float32")
    rep = {
        "video": f'{vs["codec_name"]} {vs.get("profile")} {vs["width"]}x{vs["height"]} {vs["pix_fmt"]} {vs["r_frame_rate"]} fps, {int(vs.get("bit_rate", 0)) / 1e6:.1f} Mb/s',
        "audio": f'{as_["codec_name"]} {as_["sample_rate"]} Hz {as_["channels"]} ch {int(as_.get("bit_rate", 0)) / 1e3:.0f} kb/s',
        "start_times": [vs.get("start_time"), as_.get("start_time")],
        "duration_s": {"file": round(float(pr["format"]["duration"]), 3), "video": round(float(vs["duration"]), 3),
                       "audio": round(float(as_["duration"]), 3), "recording": round(tl["duration"], 3)},
        "vs_new_voice": {"xcorr": round(r_new, 4), "lag_samples_16k": lag_new,
                         "residual_db_below_voice": round(10 * np.log10((new[:m] ** 2).sum() / (res ** 2).sum()), 1)},
        "vs_first_recording": {"max_abs_xcorr_any_lag": round(abs(r_old), 4), "at_lag_s": round(lag_old / SR, 2)},
        "loudness": {"I_LUFS": i_lufs, "TP_dBTP": tp, "clipped_samples": int((np.abs(out) >= 0.999).sum())},
    }
    # frames from the file itself: QR check every 10th frame, sheet at phrases and cuts
    fdir = f"{root}/renders/final/check_{v}"
    os.makedirs(fdir, exist_ok=True)
    for f in os.listdir(fdir):
        os.remove(f"{fdir}/{f}")
    times = [round((p["start"] + p["end"]) / 2, 2) for p in tr["phrases"]] + list(tl["cuts"]) + [0.3, round(tl["duration"] - 0.2, 2)]
    for t in sorted(times):
        run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.3f}", "-i", mp4, "-frames:v", "1", "-q:v", "2", f"{fdir}/t{t:.2f}.jpg"])
    qdir = f"{root}/renders/final/_qr_{v}"
    os.makedirs(qdir, exist_ok=True)
    run(["ffmpeg", "-v", "error", "-y", "-i", mp4, "-vf", "select=not(mod(n\\,10))", "-vsync", "vfr", "-q:v", "2", f"{qdir}/q%04d.jpg"])
    qs = sorted(os.listdir(qdir))
    found = [(q, qr_found(f"{qdir}/{q}")) for q in qs]
    bad = [(q, r) for q, r in found if r != (0, [])]
    for q in qs:
        os.remove(f"{qdir}/{q}")
    os.rmdir(qdir)
    rep["qr"] = {"frames_checked": len(qs), "readable_or_detected": bad}
    report[v] = rep
    print(v, json.dumps(rep, ensure_ascii=False, indent=1), flush=True)
json.dump(report, open(f"{root}/renders/final/verify_report.json", "w"), ensure_ascii=False, indent=1)

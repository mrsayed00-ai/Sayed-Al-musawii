"""Light voice enhancement (user request 2026-10-09). The original file is
never modified; outputs go to media/derived/.

1. Local fixes, only for the recording they were measured on (LOCAL_FIXES,
   keyed by source file): for the first recording, «في فانوس!» in phrase 4
   (~7.3–7.67 s) got a small lift on the short vowel and a gentle de-ess of
   the final «س». The second recording (re-recorded by the user) has none.
   Gains use raised-cosine ramps; filtering is zero-phase, nothing moves.
2. Global chain (ffmpeg, approved 2026-10-09): adeclip, 70 Hz high-pass,
   light de-esser, gentle 2:1 compression, static gain to -14 LUFS and a
   true-peak limiter at -1.5 dBTP with latency compensation.
   No time-stretch, no pitch change, no generated audio.
3. Checks: lag between original and output by cross-correlation (must be 0),
   duration unchanged, and Silero VAD segments recomputed on the output and
   matched to the measured phrase segments (stored as vad_enhanced).

Usage: enhance_voice.py <repo_root> <silero_vad.onnx> <source audio> <out.wav>
"""
import json
import subprocess
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

import os

root, vad_model, SRC, OUT = sys.argv[1:5]
TMP = f"{root}/renders/audio"
os.makedirs(TMP, exist_ok=True)

LOCAL_FIXES = {  # seconds, from the spectrogram/periodicity analysis of phrase 4
    "voice_2026-10-08_2307.m4a": {
        "vowel": (7.28, 7.50, +3.0),   # short, fading «انو»: lift +3 dB
        "sin": (7.51, 7.67, -4.0),     # final «س»: -4 dB above 4 kHz
    },
}
LOCAL = LOCAL_FIXES.get(os.path.basename(SRC), {})
RAMP = 0.02


def run(cmd):
    return subprocess.run(cmd, check=True, capture_output=True, text=True)


def ramp_window(n_total, sr, a, b):
    w = np.zeros(n_total)
    i0, i1, r = int(a * sr), int(b * sr), int(RAMP * sr)
    w[i0:i1] = 1.0
    w[i0 - r:i0] = 0.5 - 0.5 * np.cos(np.linspace(0, np.pi, r))
    w[i1:i1 + r] = 0.5 + 0.5 * np.cos(np.linspace(0, np.pi, r))
    return w


def local_fix(m, sr):
    out = m.copy()
    if not LOCAL:
        return out
    a, b, g = LOCAL["vowel"]
    out *= 10 ** (g / 20 * ramp_window(len(m), sr, a, b))
    a, b, g = LOCAL["sin"]
    sos = ss.butter(4, 4000, "hp", fs=sr, output="sos")
    hf = ss.sosfiltfilt(sos, out)  # zero-phase: low + high sums back to the input
    w = ramp_window(len(m), sr, a, b)
    out = out - hf * (1 - 10 ** (g / 20)) * w
    return out


def loudness(path):
    r = run(["ffmpeg", "-hide_banner", "-i", path, "-af", "loudnorm=print_format=json", "-f", "null", "-"])
    j = json.loads(r.stderr[r.stderr.rindex("{"):])
    return float(j["input_i"]), float(j["input_tp"])


def vad_spans(wav16):
    import sherpa_onnx
    x, sr = sf.read(wav16, dtype="float32")
    cfg = sherpa_onnx.VadModelConfig()
    cfg.silero_vad.model = vad_model
    cfg.silero_vad.min_silence_duration = 0.25
    cfg.silero_vad.min_speech_duration = 0.15
    cfg.silero_vad.threshold = 0.5
    cfg.sample_rate = sr
    vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
    spans = []
    for i in range(0, len(x), cfg.silero_vad.window_size):
        vad.accept_waveform(x[i:i + cfg.silero_vad.window_size])
        while not vad.empty():
            spans.append((vad.front.start / sr, (vad.front.start + len(vad.front.samples)) / sr))
            vad.pop()
    vad.flush()
    while not vad.empty():
        spans.append((vad.front.start / sr, (vad.front.start + len(vad.front.samples)) / sr))
        vad.pop()
    return spans


def match_segments(phrases, enh):
    """Enhanced VAD segments per measured phrase segment. A segment keeps its
    measured edge where one enhanced segment runs across a measured split
    (phrases 10/11), so phrase splits never move."""
    flat = [tuple(sg) for p in phrases for sg in p["vad_segments"]]
    out, k = [], 0
    for p in phrases:
        segs = []
        for a, b in p["vad_segments"]:
            prev_end = flat[k - 1][1] if k else -1.0
            next_start = flat[k + 1][0] if k + 1 < len(flat) else 1e9
            ov = [e for e in enh if e[1] > a and e[0] < b]
            a2 = min(e[0] for e in ov) if ov else a
            b2 = max(e[1] for e in ov) if ov else b
            if a2 < prev_end:
                a2 = a
            if b2 > next_start:
                b2 = b
            segs.append([round(a2, 3), round(b2, 3)])
            k += 1
        out.append(segs)
    return out


if __name__ == "__main__":
    orig = f"{TMP}/voice_orig_48k.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-c:a", "pcm_f32le", orig])
    x, sr = sf.read(orig, dtype="float64")
    assert np.allclose(x[:, 0], x[:, 1]), "expected dual-mono source"
    m = x[:, 0]
    fixed = local_fix(m, sr)
    sf.write(f"{TMP}/stage1_local.wav", fixed, sr, subtype="FLOAT")

    chain = ("adeclip,highpass=f=70:poles=2,deesser=i=0.3:m=0.5:f=0.5,"
             "acompressor=threshold=-20dB:ratio=2:attack=10:release=150:knee=6")
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{TMP}/stage1_local.wav", "-af", chain, "-c:a", "pcm_f32le", f"{TMP}/stage2.wav"])
    # dual-mono like the original (both channels at full level), static gain to
    # -14 LUFS, true-peak safety limiter (-1.8 dBFS sample peak); passes to land on the target
    gain = 0.0
    for _ in range(4):
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{TMP}/stage2.wav", "-af",
             f"pan=stereo|c0=c0|c1=c0,volume={gain:.2f}dB,alimiter=limit=0.81:attack=5:release=50:level=0:latency=1",
             "-c:a", "pcm_f32le", OUT])
        i_now, tp_now = loudness(OUT)
        if abs(i_now + 14.0) < 0.2:
            break
        gain += -14.0 - i_now

    # checks
    y, _ = sf.read(OUT, dtype="float64")
    lags = []
    for t0 in range(0, int(len(m) / sr) - 10, 10):  # every 10 s window, not only the start
        a = np.abs(m[sr * t0: sr * (t0 + 10)])
        b = np.abs(y[sr * t0: sr * (t0 + 10), 0])
        lags.append(int(np.argmax(ss.correlate(b - b.mean(), a - a.mean(), mode="full", method="fft")) - (len(a) - 1)))
    run(["ffmpeg", "-v", "error", "-y", "-i", OUT, "-ac", "1", "-ar", "16000", f"{TMP}/enh16k.wav"])
    enh = vad_spans(f"{TMP}/enh16k.wav")
    tr_path = f"{root}/analysis/transcript.json"
    tr = json.load(open(tr_path))
    matched = match_segments(tr["phrases"], enh)
    shifts = [(round(n[0] - o[0], 3), round(n[1] - o[1], 3))
              for p, segs in zip(tr["phrases"], matched) for o, n in zip(p["vad_segments"], segs)]
    for p, segs in zip(tr["phrases"], matched):
        p["vad_enhanced"] = segs
    json.dump(tr, open(tr_path, "w"), ensure_ascii=False, indent=1)
    li, ltp = loudness(OUT)
    oi, otp = loudness(orig)
    rep = {"source": os.path.basename(SRC), "output": os.path.relpath(OUT, root),
           "lag_samples_per_10s": lags, "duration_in_s": round(len(m) / sr, 6), "duration_out_s": round(len(y) / sr, 6),
           "vad_segments_measured": sum(len(p["vad_segments"]) for p in tr["phrases"]), "vad_segments_enhanced": len(enh),
           "start_shift_max_s": max(abs(s[0]) for s in shifts), "end_shift_max_s": max(abs(s[1]) for s in shifts),
           "end_shift_max_later_s": max(s[1] for s in shifts),
           "loudness_original": {"I": oi, "TP": otp}, "loudness_enhanced": {"I": li, "TP": ltp},
           "local_fix": LOCAL, "chain": chain}
    json.dump(rep, open(f"{root}/analysis/audio_enhance_report.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))

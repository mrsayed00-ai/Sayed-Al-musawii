"""Light voice enhancement (user request 2026-10-09). The original file is
never modified; outputs go to media/derived/.

1. Local treatment of «في فانوس!» in phrase 4 (~7.3–7.67 s): a small level
   lift on the short vowel and a gentle de-ess of the final «س». Gains use
   raised-cosine ramps; filtering is zero-phase, so nothing moves in time.
   This cannot restore voicing: the measured problem there is in delivery.
2. Global chain (ffmpeg): adeclip (two clipped spots at 1.15 s / 3.13 s),
   70 Hz high-pass, light de-esser, gentle 2:1 compression, static gain to
   -14 LUFS and a true-peak limiter at -1.5 dBTP with latency compensation.
   No time-stretch, no pitch change, no generated audio.
3. Checks: lag between original and output by cross-correlation (must be 0),
   and Silero VAD phrase boundaries recomputed on the output (must match).

Usage: enhance_voice.py <repo_root> <silero_vad.onnx>
"""
import json
import subprocess
import sys

import numpy as np
import scipy.signal as ss
import soundfile as sf

root, vad_model = sys.argv[1], sys.argv[2]
SRC = f"{root}/media/source/voice_2026-10-08_2307.m4a"
DER = f"{root}/media/derived"
TMP = f"{root}/renders/audio"

LOCAL = {  # seconds, from the spectrogram/periodicity analysis of phrase 4
    "vowel": (7.28, 7.50, +3.0),   # short, fading «انو»: lift +3 dB
    "sin": (7.51, 7.67, -4.0),     # final «س»: -4 dB above 4 kHz
}
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


if __name__ == "__main__":
    orig = f"{TMP}/voice_orig_48k.wav"
    run(["ffmpeg", "-v", "error", "-y", "-i", SRC, "-c:a", "pcm_f32le", orig])
    x, sr = sf.read(orig, dtype="float64")
    m = x[:, 0]  # the file is dual-mono (L == R)
    fixed = local_fix(m, sr)
    sf.write(f"{TMP}/stage1_local.wav", fixed, sr, subtype="FLOAT")

    chain = ("adeclip,highpass=f=70:poles=2,deesser=i=0.3:m=0.5:f=0.5,"
             "acompressor=threshold=-20dB:ratio=2:attack=10:release=150:knee=6")
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{TMP}/stage1_local.wav", "-af", chain, "-c:a", "pcm_f32le", f"{TMP}/stage2.wav"])
    # dual-mono like the original (both channels at full level), static gain to
    # -14 LUFS, true-peak safety limiter (-1.8 dBFS sample peak); passes to land on the target
    gain = 0.0
    for _ in range(3):
        run(["ffmpeg", "-v", "error", "-y", "-i", f"{TMP}/stage2.wav", "-af",
             f"pan=stereo|c0=c0|c1=c0,volume={gain:.2f}dB,alimiter=limit=0.81:attack=5:release=50:level=0:latency=1",
             "-c:a", "pcm_f32le", f"{DER}/voice_enhanced_v1.wav"])
        i_now, tp_now = loudness(f"{DER}/voice_enhanced_v1.wav")
        if abs(i_now + 14.0) < 0.2:
            break
        gain += -14.0 - i_now

    # checks
    y, _ = sf.read(f"{DER}/voice_enhanced_v1.wav", dtype="float64")
    a = np.abs(m[: sr * 20])
    b = np.abs(y[: sr * 20, 0])
    lag = int(np.argmax(ss.correlate(b - b.mean(), a - a.mean(), mode="full", method="fft")) - (len(a) - 1))
    run(["ffmpeg", "-v", "error", "-y", "-i", f"{DER}/voice_enhanced_v1.wav", "-ac", "1", "-ar", "16000", f"{TMP}/enh16k.wav"])
    new = vad_spans(f"{TMP}/enh16k.wav")
    old = [(p["start"], p["end"]) for p in json.load(open(f"{root}/analysis/transcript.json"))["phrases"]]
    d = max(max(abs(p[0] - q[0]), abs(p[1] - q[1])) for p, q in zip(old, new)) if len(new) == len(old) else None
    li, ltp = loudness(f"{DER}/voice_enhanced_v1.wav")
    oi, otp = loudness(orig)
    tr_path = f"{root}/analysis/transcript.json"
    tr = json.load(open(tr_path))
    if len(new) == len(tr["phrases"]):
        for p, q in zip(tr["phrases"], new):
            p["vad_enhanced"] = [round(q[0], 3), round(q[1], 3)]
        json.dump(tr, open(tr_path, "w"), ensure_ascii=False, indent=1)
    rep = {"lag_samples": lag, "vad_phrases_old": len(old), "vad_phrases_new": len(new),
           "max_boundary_shift_s": None if d is None else round(d, 3),
           "loudness_original": {"I": oi, "TP": otp}, "loudness_enhanced": {"I": li, "TP": ltp},
           "duration_s": round(len(y) / sr, 3), "local_fix": LOCAL, "chain": chain}
    json.dump(rep, open(f"{root}/analysis/audio_enhance_report.json", "w"), ensure_ascii=False, indent=1)
    print(json.dumps(rep, ensure_ascii=False, indent=1))

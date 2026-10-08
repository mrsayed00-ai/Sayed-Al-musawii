"""Transcribe the voice-over: Silero VAD gives measured phrase boundaries,
Whisper large-v3 (sherpa-onnx, offline) transcribes each phrase and also
larger context chunks for cross-checking. Output: JSON + printed table."""
import json
import sys

import numpy as np
import sherpa_onnx
import soundfile as sf

asr_dir, wav_path, out_path = sys.argv[1], sys.argv[2], sys.argv[3]
SR = 16000

samples, sr = sf.read(wav_path, dtype="float32")
assert sr == SR, sr
if samples.ndim > 1:
    samples = samples.mean(axis=1)

m = f"{asr_dir}/sherpa-onnx-whisper-large-v3/large-v3"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{m}-encoder.int8.onnx",
    decoder=f"{m}-decoder.int8.onnx",
    tokens=f"{m}-tokens.txt",
    language="ar",
    task="transcribe",
    num_threads=4,
)


def transcribe(x):
    s = rec.create_stream()
    s.accept_waveform(SR, x)
    rec.decode_stream(s)
    return s.result.text.strip()


cfg = sherpa_onnx.VadModelConfig()
cfg.silero_vad.model = f"{asr_dir}/silero_vad.onnx"
cfg.silero_vad.min_silence_duration = 0.25
cfg.silero_vad.min_speech_duration = 0.15
cfg.silero_vad.threshold = 0.5
cfg.sample_rate = SR
vad = sherpa_onnx.VoiceActivityDetector(cfg, buffer_size_in_seconds=120)
win = cfg.silero_vad.window_size
segs = []


def drain():
    while not vad.empty():
        f = vad.front
        segs.append((f.start / SR, (f.start + len(f.samples)) / SR))
        vad.pop()


for i in range(0, len(samples), win):
    vad.accept_waveform(samples[i : i + win])
    drain()
vad.flush()
drain()

pad = 0.12  # small context pad so word edges are not clipped
phrases = []
for a, b in segs:
    x = samples[int(max(0, a - pad) * SR) : int(min(len(samples) / SR, b + pad) * SR)]
    phrases.append({"start": round(a, 2), "end": round(b, 2), "text": transcribe(x)})
    print(f"{a:6.2f} – {b:6.2f}  {phrases[-1]['text']}", flush=True)

# context chunks (<= ~25 s, cut only at VAD gaps) for a cross-check transcript
chunks, cur = [], []
for a, b in segs:
    if cur and b - cur[0][0] > 25:
        chunks.append(cur)
        cur = []
    cur.append((a, b))
if cur:
    chunks.append(cur)
ctx = []
for c in chunks:
    a, b = c[0][0], c[-1][1]
    x = samples[int(max(0, a - pad) * SR) : int(min(len(samples) / SR, b + pad) * SR)]
    ctx.append({"start": round(a, 2), "end": round(b, 2), "text": transcribe(x)})
    print(f"\n[chunk {a:.2f}–{b:.2f}] {ctx[-1]['text']}", flush=True)

json.dump(
    {"duration": round(len(samples) / SR, 3), "vad_phrases": phrases, "context_chunks": ctx},
    open(out_path, "w"),
    ensure_ascii=False,
    indent=1,
)

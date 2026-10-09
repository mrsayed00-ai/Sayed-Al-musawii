"""Build analysis/transcript.json for a recording from its VAD segments.

Input: raw VAD/ASR json from asr_run.py (vad_phrases), a phrase map that
groups VAD segments into the 25 script phrases (splits use a finer VAD pass,
listed in the map), the script/screen texts, and the wording scores
(asr_score.py, two models). Each phrase is re-transcribed with Whisper
large-v3 and turbo (silence padded) for the audit fields.
Usage: asr_phrases.py <asr_dir> <voice16k.wav> <phrase_map.json> <out transcript.json>
"""
import json
import sys

import numpy as np
import sherpa_onnx
import soundfile as sf

asr_dir, wav, map_path, out_path = sys.argv[1:5]
SR = 16000
x, _ = sf.read(wav, dtype="float32")
pm = json.load(open(map_path))


def recognizer(model):
    m = f"{asr_dir}/sherpa-onnx-whisper-{model}/{model}"
    return sherpa_onnx.OfflineRecognizer.from_whisper(
        encoder=f"{m}-encoder.int8.onnx", decoder=f"{m}-decoder.int8.onnx", tokens=f"{m}-tokens.txt",
        language="ar", task="transcribe", num_threads=4, tail_paddings=1500)


def transcribe(rec, a, b, prev_end, next_start):
    # pad into the neighbouring silences only (never into the next phrase)
    a0 = max(prev_end, a - 0.25)
    b0 = min(next_start, b + 0.35)
    seg = x[int(a0 * SR): int(b0 * SR)]
    seg = np.concatenate([np.zeros(int(0.3 * SR), np.float32), seg, np.zeros(int(1.0 * SR), np.float32)])
    s = rec.create_stream()
    s.accept_waveform(SR, seg)
    rec.decode_stream(s)
    return s.result.text.strip()


phr = pm["phrases"]
recs = {m: recognizer(m) for m in ("large-v3", "turbo")}
out = []
for i, p in enumerate(phr):
    a, b = p["segments"][0][0], p["segments"][-1][1]
    pe = phr[i - 1]["segments"][-1][1] if i else 0.0
    ns = phr[i + 1]["segments"][0][0] if i + 1 < len(phr) else len(x) / SR
    q = {"id": p["id"], "start": a, "end": b, "section": p["section"], "vad_segments": p["segments"]}
    for m, rec in recs.items():
        q[f"whisper_{m}"] = transcribe(rec, a, b, pe, ns)
    q.update({k: v for k, v in p.items() if k not in ("id", "segments", "section")})
    out.append(q)
    print(f"{q['id']:2d} {a:6.2f}–{b:6.2f}  {q['whisper_large-v3']}  ||  {q['whisper_turbo']}", flush=True)
json.dump({**{k: v for k, v in pm.items() if k != "phrases"}, "duration": round(len(x) / SR, 3), "phrases": out},
          open(out_path, "w"), ensure_ascii=False, indent=1)

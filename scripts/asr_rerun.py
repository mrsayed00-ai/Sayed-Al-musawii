"""Re-transcribe each VAD phrase with silence appended (sherpa-onnx whisper
tends to drop the last word of short clips)."""
import json, sys
import numpy as np, sherpa_onnx, soundfile as sf
asr_dir, wav, raw, out = sys.argv[1:5]
SR = 16000
x, _ = sf.read(wav, dtype="float32")
m = f"{asr_dir}/sherpa-onnx-whisper-large-v3/large-v3"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{m}-encoder.int8.onnx", decoder=f"{m}-decoder.int8.onnx",
    tokens=f"{m}-tokens.txt", language="ar", task="transcribe",
    num_threads=4, tail_paddings=1500)
d = json.load(open(raw))
res = []
for p in d["vad_phrases"]:
    a, b = p["start"], p["end"]
    seg = x[int(max(0, a - 0.25) * SR): int(min(len(x) / SR, b + 0.35) * SR)]
    seg = np.concatenate([np.zeros(int(0.3 * SR), np.float32), seg, np.zeros(int(1.0 * SR), np.float32)])
    s = rec.create_stream(); s.accept_waveform(SR, seg); rec.decode_stream(s)
    res.append({**p, "text_padded": s.result.text.strip()})
    print(f"{a:6.2f} – {b:6.2f}  {p['text']}  ||  {res[-1]['text_padded']}", flush=True)
d["vad_phrases"] = res
json.dump(d, open(out, "w"), ensure_ascii=False, indent=1)

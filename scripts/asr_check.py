"""Independent second-model check (Whisper turbo) on selected phrases."""
import json, sys
import numpy as np, sherpa_onnx, soundfile as sf
asr_dir, wav, tj = sys.argv[1:4]; ids = [int(i) for i in sys.argv[4].split(",")]
SR = 16000
x, _ = sf.read(wav, dtype="float32")
m = f"{asr_dir}/sherpa-onnx-whisper-turbo/turbo"
rec = sherpa_onnx.OfflineRecognizer.from_whisper(
    encoder=f"{m}-encoder.int8.onnx", decoder=f"{m}-decoder.int8.onnx",
    tokens=f"{m}-tokens.txt", language="ar", task="transcribe", num_threads=4, tail_paddings=1500)
for p in json.load(open(tj))["phrases"]:
    if p["id"] not in ids: continue
    a, b = p["start"], p["end"]
    seg = x[int(max(0, a - 0.25) * SR): int(min(len(x) / SR, b + 0.35) * SR)]
    seg = np.concatenate([np.zeros(int(0.3 * SR), np.float32), seg, np.zeros(int(1.0 * SR), np.float32)])
    s = rec.create_stream(); s.accept_waveform(SR, seg); rec.decode_stream(s)
    print(f"{p['id']:2d} {a:6.2f}-{b:6.2f} turbo: {s.result.text.strip()}  ||  script: {p['script_text']}", flush=True)

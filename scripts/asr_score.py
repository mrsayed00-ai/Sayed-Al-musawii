"""Forced-choice check: score candidate wordings of a phrase against the audio.

For each phrase, Whisper (sherpa-onnx ONNX export) is run teacher-forced on
every candidate text and returns log P(text | audio). The candidate the
acoustic+language model finds more likely wins; a small margin means the
audio does not settle it. Spelling variants of the same wording are scored
separately and the best one stands for that wording.

Candidates file: {"<phrase id>": {"window": [start, end], "cands": {label: [spellings]}}}
(analysis/asr_candidates_rec1.json, asr_candidates_rec2.json).
Usage: asr_score.py <asr_dir> <voice16k.wav> <candidates.json> <model: large-v3|turbo> <out.json>
"""
import base64
import json
import sys

import librosa
import numpy as np
import onnxruntime as ort
import soundfile as sf
import tiktoken

asr_dir, wav, cj, model, out_path = sys.argv[1:6]
d = f"{asr_dir}/sherpa-onnx-whisper-{model}/{model}"
SR = 16000

ranks = {}
for line in open(f"{d}-tokens.txt", encoding="utf-8"):
    b64, idx = line.split()
    ranks[base64.b64decode(b64)] = int(idx)
enc = tiktoken.Encoding(
    name="whisper-multilingual",
    pat_str=r"""'s|'t|'re|'ve|'m|'ll|'d| ?\p{L}+| ?\p{N}+| ?[^\s\p{L}\p{N}]+|\s+(?!\S)|\s+""",
    mergeable_ranks=ranks,
    special_tokens={},
)

so = ort.SessionOptions()
so.intra_op_num_threads = 4
encs = ort.InferenceSession(f"{d}-encoder.int8.onnx", so, providers=["CPUExecutionProvider"])
decs = ort.InferenceSession(f"{d}-decoder.int8.onnx", so, providers=["CPUExecutionProvider"])
meta = encs.get_modelmeta().custom_metadata_map
codes = meta["all_language_codes"].split(",")
langs = [int(t) for t in meta["all_language_tokens"].split(",")]
AR = langs[codes.index("ar")]
PREFIX = [int(meta["sot"]), AR, int(meta["transcribe"]), int(meta["no_timestamps"])]
EOT = int(meta["eot"])
n_layer = int(meta["n_text_layer"])
n_state = int(meta["n_text_state"])
n_ctx = int(meta["n_text_ctx"])
n_mels = int(meta["n_mels"])
mel_fb = librosa.filters.mel(sr=SR, n_fft=400, n_mels=n_mels)


def log_mel(x):
    x = np.concatenate([x, np.zeros(SR * 30 - len(x), np.float32)])[: SR * 30]
    st = librosa.stft(x, n_fft=400, hop_length=160, window="hann", center=True, pad_mode="reflect")
    mag = np.abs(st[:, :-1]) ** 2
    m = np.log10(np.clip(mel_fb @ mag, 1e-10, None))
    m = np.maximum(m, m.max() - 8.0)
    return ((m + 4.0) / 4.0).astype(np.float32)[None]


def score(cross_k, cross_v, text):
    toks = enc.encode(" " + text)
    seq = PREFIX + toks + [EOT]
    zeros = np.zeros((n_layer, 1, n_ctx, n_state), np.float32)
    logits = decs.run(
        ["logits"],
        {
            "tokens": np.array([seq[:-1]], np.int64),
            "in_n_layer_self_k_cache": zeros,
            "in_n_layer_self_v_cache": zeros,
            "n_layer_cross_k": cross_k,
            "n_layer_cross_v": cross_v,
            "offset": np.array([0], np.int64),
        },
    )[0][0]
    lp = logits - np.logaddexp.reduce(logits, axis=-1, keepdims=True)
    tgt = seq[1:]
    s = sum(lp[i, t] for i, t in enumerate(tgt) if i >= len(PREFIX) - 1)
    n = len(tgt) - (len(PREFIX) - 1)
    return float(s), n


x, _ = sf.read(wav, dtype="float32")
cand = {k: v for k, v in json.load(open(cj)).items() if not k.startswith("_")}
out = {}
for pid, c in cand.items():
    a, b = c["window"]
    seg = x[int(max(0, a - 0.25) * SR) : int((b + 0.35) * SR)]
    seg = np.concatenate([np.zeros(int(0.3 * SR), np.float32), seg])
    ck, cv = encs.run(None, {"mel": log_mel(seg)})
    res = {}
    for label, texts in c["cands"].items():
        best = max((score(ck, cv, t) + (t,) for t in texts), key=lambda r: r[0])
        res[label] = {"logp": round(best[0], 2), "tokens": best[1], "per_token": round(best[0] / best[1], 3), "text": best[2]}
    order = sorted(res, key=lambda k: -res[k]["logp"])
    margin = res[order[0]]["logp"] - res[order[1]]["logp"]
    out[pid] = {"window": c["window"], "cands": res, "best": order[0], "margin_over_next": round(margin, 2)}
    print(pid, order[0], f"+{margin:.2f}", json.dumps(res, ensure_ascii=False), flush=True)
json.dump(out, open(out_path, "w"), ensure_ascii=False, indent=1)

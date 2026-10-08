"""Replace the real (scannable) QR codes in host screenshots with a pixel-art
illustration that cannot be scanned (user decision 2026-10-09).

The illustration is an 11x11 grid of coarse pixels with no finder patterns:
a QR code needs at least 21x21 modules plus three finder squares, so this is
not decodable by construction. The Fanous badge in the middle and the frame
around the code are kept from the original screenshot. qr_found() checks
with two readers (OpenCV detector/decoder and zxing-cpp); the originals are
read first as a positive control, and the script fails if anything is still
detected or decoded after replacement.
"""
import random

import cv2
import numpy as np
import zxingcpp
from PIL import Image, ImageDraw

# inner white area of each QR (x0, y0, x1, y1) on the 2048x943 screenshots
QR_AREAS = {
    "B02": [(873, 475, 1174, 777)],
    "B04": [(388, 470, 690, 773), (1360, 470, 1663, 773)],
}
GRID = 11
PURPLE = (88, 66, 200)
PURPLE_LT = (127, 113, 206)


def pixelize(src, name, seed=11):
    im = Image.open(src).convert("RGB")
    d = ImageDraw.Draw(im)
    for k, (x0, y0, x1, y1) in enumerate(QR_AREAS[name]):
        w, h = x1 - x0, y1 - y0
        cx, cy, r = x0 + w // 2, y0 + h // 2, int(w * 0.17)
        badge = im.crop((cx - r, cy - r, cx + r, cy + r))
        d.rectangle([x0, y0, x1, y1], fill=(255, 255, 255))
        rnd = random.Random(seed + k)
        m = w * 0.06
        cell = (w - 2 * m) / GRID
        for i in range(GRID):
            for j in range(GRID):
                if abs(i - GRID // 2) <= 1 and abs(j - GRID // 2) <= 1:
                    continue  # centre kept for the Fanous badge
                if rnd.random() < 0.5:
                    a, b = x0 + m + j * cell, y0 + m + i * cell
                    d.rectangle([a + 2, b + 2, a + cell - 2, b + cell - 2],
                                fill=PURPLE if rnd.random() < 0.75 else PURPLE_LT)
        mask = Image.new("L", badge.size, 0)
        ImageDraw.Draw(mask).ellipse([0, 0, 2 * r - 1, 2 * r - 1], fill=255)
        im.paste(badge, (cx - r, cy - r), mask)
    return im


def qr_found(path_or_img):
    img = cv2.imread(path_or_img) if isinstance(path_or_img, str) else cv2.cvtColor(np.asarray(path_or_img), cv2.COLOR_RGB2BGR)
    det = cv2.QRCodeDetector()
    ok, pts = det.detectMulti(img)
    dec, texts, _, _ = det.detectAndDecodeMulti(img)
    decoded = [t for t in (texts or []) if t]
    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    decoded += [r.text for r in zxingcpp.read_barcodes(rgb) if r.format.name.startswith("QR") or "QR" in str(r.format)]
    return (int(len(pts)) if ok and pts is not None else 0), decoded


if __name__ == "__main__":
    import sys
    shots, out = sys.argv[1], sys.argv[2]
    for name in QR_AREAS:
        src = f"{shots}/{name}.jpg"
        before = qr_found(src)
        im = pixelize(src, name)
        im.save(f"{out}/{name}_pxqr.png")
        after = qr_found(f"{out}/{name}_pxqr.png")
        print(f"{name}: before detected={before[0]} decoded={len(before[1])} | after detected={after[0]} decoded={len(after[1])}")
        assert after == (0, []), f"{name}: QR still readable after replacement"

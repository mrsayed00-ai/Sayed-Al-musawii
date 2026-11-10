"""Build the playful «صفحة واحد» logo as a fully-outlined SVG.

Text is shaped with HarfBuzz and converted to vector paths with fontTools, so
the SVG needs no fonts to display. The letter dots of «صفحة» are pulled out as
separate gold shapes and nudged upward to make them "bounce".

Font: Baloo Bhaijaan 2 ExtraBold (Google Fonts, SIL Open Font License).
Download BalooBhaijaan2-ExtraBold.ttf into ./fonts next to this script, then:

    pip install fonttools uharfbuzz
    python build_logo.py            # writes ../safha-wahed-logo*.svg
"""

from pathlib import Path

import uharfbuzz as hb
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.recordingPen import DecomposingRecordingPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont

HERE = Path(__file__).resolve().parent
FONT = HERE / "fonts" / "BalooBhaijaan2-ExtraBold.ttf"
OUT = HERE.parent

CREAM = "#F5EBDA"
GOLD = "#F6B73C"
INK = "#141414"

_tt = TTFont(FONT)
_glyphs = _tt.getGlyphSet()
_order = _tt.getGlyphOrder()
_upem = _tt["head"].unitsPerEm
_hbfont = hb.Font(hb.Face(hb.Blob.from_file_path(str(FONT))))


def contours(text, size, cx, baseline):
    """Shape `text`, centre it on `cx`, and return its contours as
    (svg_path_d, (xmin, ymin, xmax, ymax)) in SVG user space."""
    buf = hb.Buffer()
    buf.add_str(text)
    buf.guess_segment_properties()
    hb.shape(_hbfont, buf, {})
    s = size / _upem
    total = sum(p.x_advance for p in buf.glyph_positions) * s
    pen_x = cx - total / 2
    out = []
    # HarfBuzz returns RTL runs in left-to-right visual order.
    for info, pos in zip(buf.glyph_infos, buf.glyph_positions):
        rec = DecomposingRecordingPen(_glyphs)
        _glyphs[_order[info.codepoint]].draw(rec)
        tx = pen_x + pos.x_offset * s
        ty = baseline - pos.y_offset * s
        affine = (s, 0, 0, -s, tx, ty)
        cur = []
        for op, args in rec.value:
            cur.append((op, args))
            if op in ("closePath", "endPath"):
                sp, bp = SVGPathPen(None), BoundsPen(None)
                for o, a in cur:
                    getattr(TransformPen(sp, affine), o)(*a)
                    getattr(TransformPen(bp, affine), o)(*a)
                out.append((sp.getCommands(), bp.bounds))
                cur = []
        pen_x += pos.x_advance * s
    return out


def path(cs, **attrs):
    d = "".join(c for c, _ in cs)
    extra = "".join(f' {k.replace("_", "-")}="{v}"' for k, v in attrs.items())
    return f'<path d="{d}"{extra}/>'


def build(background):
    # «صفحة» — split the letter dots (everything sitting fully above the
    # letter bodies) from the bodies so they can be gold and bounce.
    w1 = contours("صفحة", 330, 600, 370)
    body_top = 370 - 186
    body = [c for c in w1 if c[1][3] > body_top]
    dots = sorted((c for c in w1 if c[1][3] <= body_top), key=lambda c: c[1][0])
    assert len(dots) == 3, f"expected 3 dots, found {len(dots)}"
    bounce = [(-2, -14), (2, -4), (0, -10)]  # left ة dot, right ة dot, ف dot
    dots_svg = "\n    ".join(
        f'<g transform="translate({dx} {dy})">{path([c], fill=GOLD)}</g>'
        for c, (dx, dy) in zip(dots, bounce)
    )

    waw = contours("و", 330, 898, 650)
    hd = contours("حد", 330, 442, 650)
    one = contours("1", 140, 2, 140)
    tag = contours("بداية كل شي", 92, 600, 1080)

    bg = f'<rect width="1200" height="1200" fill="{INK}"/>' if background else ""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="1200" viewBox="0 0 1200 1200">
  <title>صفحة واحد — بداية كل شي</title>
  <defs>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFD36B"/>
      <stop offset="1" stop-color="#EFA526"/>
    </linearGradient>
    <path id="spark" d="M0-1C.13-.13.13-.13 1 0C.13.13.13.13 0 1C-.13.13-.13.13-1 0C-.13-.13-.13-.13 0-1Z"/>
  </defs>
  {bg}

  <!-- صفحة -->
  <g transform="rotate(-4 600 260)">
    {path(body, fill=CREAM)}
    {dots_svg}
  </g>

  <!-- و [bookmark-1] حد -->
  <g transform="rotate(2.5 600 560)">
    {path(waw, fill=CREAM)}
    <g transform="translate(728 425) rotate(7)">
      <path d="M-32 0H32Q50 0 50 18V280Q50 290 41 284L0 250L-41 284Q-50 290 -50 280V18Q-50 0 -32 0Z" fill="url(#gold)"/>
      <rect x="-37" y="16" width="10" height="200" rx="5" fill="#FFFFFF" fill-opacity=".3"/>
      {path(one, fill=INK)}
    </g>
    <g fill="none" stroke="{GOLD}" stroke-width="7" stroke-linecap="round">
      <path d="M662 432L640 416"/>
      <path d="M654 466L628 466"/>
      <path d="M676 404L666 382"/>
    </g>
    {path(hd, fill=CREAM)}
  </g>

  <!-- open book with fluttering pages -->
  <g transform="translate(280 770)">
    <g fill="none" stroke="{CREAM}" stroke-linecap="round" stroke-linejoin="round">
      <path d="M320 196C250 164 130 162 18 182" stroke-width="11"/>
      <path d="M320 196C390 164 510 162 622 182" stroke-width="11"/>
      <path d="M320 176C255 142 145 140 42 156" stroke-width="7"/>
      <path d="M320 176C385 142 495 140 598 156" stroke-width="7"/>
      <path d="M320 158C262 120 160 116 66 130" stroke-width="6"/>
      <path d="M320 158C378 120 480 116 574 130" stroke-width="6"/>
      <path d="M320 196V156" stroke-width="8"/>
    </g>
    <g fill="{CREAM}" stroke="{CREAM}" stroke-width="4" stroke-linejoin="round">
      <path d="M320 156C298 106 252 76 190 66L180 88C240 98 288 124 320 156Z"/>
      <path d="M320 156C318 102 330 62 356 30L374 44C348 74 330 110 320 156Z"/>
      <path d="M320 156C350 104 400 76 462 70L468 92C410 100 360 124 320 156Z"/>
    </g>
    <g fill="{GOLD}">
      <use href="#spark" transform="translate(126 60) scale(22)"/>
      <use href="#spark" transform="translate(536 74) scale(16)"/>
      <use href="#spark" transform="translate(410 6) scale(12)"/>
      <circle cx="232" cy="20" r="6"/>
      <circle cx="80" cy="104" r="5"/>
      <circle cx="590" cy="30" r="7"/>
      <circle cx="270" cy="0" r="4"/>
    </g>
  </g>

  <!-- بداية كل شي -->
  {path(tag, fill=GOLD)}
  <g fill="none" stroke="{GOLD}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round">
    <path d="M286 1052q10-12 20 0t20 0t20 0"/>
    <path d="M854 1052q10-12 20 0t20 0t20 0"/>
  </g>
</svg>
"""


if __name__ == "__main__":
    (OUT / "safha-wahed-logo.svg").write_text(build(background=True), encoding="utf-8")
    (OUT / "safha-wahed-logo-transparent.svg").write_text(build(background=False), encoding="utf-8")
    print("wrote", OUT / "safha-wahed-logo.svg")

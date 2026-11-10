"""Build the playful «صفحة واحد» YouTube logo as a fully-outlined SVG.

Layout: a big swinging gold bookmark with «1» on top, the name «صفحة واحد» on one
line underneath. Everything sits inside the circle YouTube crops profile
pictures to.

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
GOLD_DARK = "#B8760F"
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


def bbox(cs):
    return (min(b[0] for _, b in cs), min(b[1] for _, b in cs),
            max(b[2] for _, b in cs), max(b[3] for _, b in cs))


# Bookmark ribbon, 140 x 330, origin at its top centre.
RIBBON = ("M-48 0H48Q70 0 70 22V318Q70 332 58 324L0 278"
          "L-58 324Q-70 332 -70 318V22Q-70 0 -48 0Z")


def build(background):
    # Name on one line. Split the letter dots (contours sitting entirely
    # above the letter bodies) so they can be gold and bounce.
    size, baseline = 116, 628
    name = contours("صفحة واحد", size, 400, baseline)
    dot_line = baseline - 186 / 330 * size
    body = [c for c in name if c[1][3] > dot_line]
    dots = sorted((c for c in name if c[1][3] <= dot_line), key=lambda c: c[1][0])
    assert len(dots) == 3, f"expected 3 dots, found {len(dots)}"
    bounce = [(-1, -8), (1, -3), (0, -6)]  # left ة dot, right ة dot, ف dot
    dots_svg = "\n    ".join(
        f'<g transform="translate({dx} {dy})">{path([c], fill=GOLD)}</g>'
        for c, (dx, dy) in zip(dots, bounce)
    )

    # «1» centred in the upper part of the ribbon.
    one = contours("1", 190, 0, 0)
    x0, y0, x1, y1 = bbox(one)
    one_tf = f"translate({-(x0 + x1) / 2 + 3:.1f} {135 - (y0 + y1) / 2:.1f})"

    if background:
        bg = """<rect width="800" height="800" fill="url(#bg)"/>
  <circle cx="410" cy="300" r="250" fill="url(#glow)"/>"""
    else:
        bg = ""

    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" viewBox="0 0 800 800">
  <title>صفحة واحد</title>
  <defs>
    <radialGradient id="bg" cx="400" cy="380" r="480" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#211E1A"/>
      <stop offset="1" stop-color="{INK}"/>
    </radialGradient>
    <radialGradient id="glow">
      <stop offset="0" stop-color="{GOLD}" stop-opacity=".22"/>
      <stop offset="1" stop-color="{GOLD}" stop-opacity="0"/>
    </radialGradient>
    <linearGradient id="gold" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#FFD66E"/>
      <stop offset="1" stop-color="#F0A322"/>
    </linearGradient>
    <path id="spark" d="M0-1C.13-.13.13-.13 1 0C.13.13.13.13 0 1C-.13.13-.13.13-1 0C-.13-.13-.13-.13 0-1Z"/>
  </defs>
  {bg}
  <g transform="translate(0 10)">

  <!-- swinging bookmark «1» -->
  <g transform="translate(418 130) rotate(8)">
    <path d="{RIBBON}" fill="{GOLD_DARK}" transform="translate(10 10)"/>
    <path d="{RIBBON}" fill="url(#gold)"/>
    <rect x="-54" y="24" width="13" height="226" rx="6.5" fill="#FFFFFF" fill-opacity=".3"/>
    <g transform="{one_tf}">{path(one, fill=INK)}</g>
  </g>

  <!-- pop lines + sparkles -->
  <g fill="none" stroke="{GOLD}" stroke-width="9" stroke-linecap="round">
    <path d="M508 112L530 86"/>
    <path d="M520 140L552 134"/>
    <path d="M488 98L494 66"/>
  </g>
  <g fill="{GOLD}">
    <use href="#spark" transform="translate(286 236) scale(32)"/>
    <use href="#spark" transform="translate(566 318) scale(20)"/>
    <use href="#spark" transform="translate(300 400) scale(13)"/>
    <circle cx="330" cy="150" r="8"/>
    <circle cx="560" cy="226" r="7"/>
    <circle cx="246" cy="330" r="6"/>
    <circle cx="540" cy="420" r="6"/>
  </g>

  <!-- صفحة واحد -->
  <g transform="rotate(-2 400 590)">
    {path(body, fill=CREAM)}
    {dots_svg}
  </g>
  </g>
</svg>
"""


if __name__ == "__main__":
    (OUT / "safha-wahed-logo.svg").write_text(build(background=True), encoding="utf-8")
    (OUT / "safha-wahed-logo-transparent.svg").write_text(build(background=False), encoding="utf-8")
    print("wrote", OUT / "safha-wahed-logo.svg")

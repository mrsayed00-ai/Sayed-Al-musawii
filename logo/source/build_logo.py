"""Build the playful «صفحة واحد» YouTube logo as a fully-outlined SVG.

Layout: a big swinging gold bookmark shaped like the number 1 on top, the name «صفحة واحد» on one
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


# The number 1 drawn as a bookmark: a slim ribbon is the upright stroke (with
# the notched bottom) and the 1's flag is a straight stroke slanting down-left
# from its top at 33 degrees, with a clean, softly rounded cut end.
# Origin at the top centre of the stem.
ONE_RIBBON = ("M0 0Q-10 0 -18.4 5.5L-112.3 66.4Q-119 70.8 -114.6 77.5"
              "L-98.3 102.7Q-93.9 109.4 -87.2 105L-56.4 85.1Q-48 79.6 -48 89.6"
              "V346Q-48 360 -37 352L0 312L37 352Q48 360 48 346V16Q48 0 32 0Z")
# Dashed stitching just inside the ribbon's edges.
STITCH = "M-35 104V334L0 296L35 334V20"


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
    <linearGradient id="gold" x1="-150" y1="0" x2="60" y2="360" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFE7A4"/>
      <stop offset=".38" stop-color="#F7BD45"/>
      <stop offset=".72" stop-color="#E2961C"/>
      <stop offset="1" stop-color="#FBCB62"/>
    </linearGradient>
    <linearGradient id="rim" x1="-150" y1="0" x2="60" y2="360" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#FFF8E6" stop-opacity=".95"/>
      <stop offset=".55" stop-color="#FFF1CC" stop-opacity=".25"/>
      <stop offset="1" stop-color="#FFF1CC" stop-opacity=".6"/>
    </linearGradient>
    <clipPath id="oneClip"><path d="{ONE_RIBBON}"/></clipPath>
    <filter id="lift" x="-50%" y="-50%" width="200%" height="200%">
      <feDropShadow dx="4" dy="16" stdDeviation="12" flood-color="#000000" flood-opacity=".55"/>
    </filter>
    <path id="spark" d="M0-1C.13-.13.13-.13 1 0C.13.13.13.13 0 1C-.13.13-.13.13-1 0C-.13-.13-.13-.13 0-1Z"/>
  </defs>
  {bg}
  <g transform="translate(0 10)">

  <!-- swinging bookmark shaped as «1» -->
  <g transform="translate(440 116) rotate(7)">
    <g filter="url(#lift)">
      <path d="{ONE_RIBBON}" fill="{GOLD_DARK}" transform="translate(6 7)"/>
      <path d="{ONE_RIBBON}" fill="url(#gold)"/>
    </g>
    <!-- polished bevel: the outline stroked, kept only on the inside -->
    <path d="{ONE_RIBBON}" fill="none" stroke="url(#rim)" stroke-width="9" clip-path="url(#oneClip)"/>
    <path d="{STITCH}" fill="none" stroke="#FFF4D6" stroke-opacity=".75" stroke-width="3.5"
          stroke-dasharray="11 8" stroke-linecap="round" stroke-linejoin="round"/>
  </g>

  <!-- pop lines + sparkles -->
  <g fill="none" stroke="{GOLD}" stroke-width="9" stroke-linecap="round">
    <path d="M520 112L542 86"/>
    <path d="M532 140L564 134"/>
    <path d="M500 98L506 66"/>
  </g>
  <g fill="{GOLD}">
    <use href="#spark" transform="translate(262 330) scale(32)"/>
    <use href="#spark" transform="translate(572 318) scale(20)"/>
    <use href="#spark" transform="translate(298 418) scale(13)"/>
    <circle cx="300" cy="136" r="8"/>
    <circle cx="566" cy="226" r="7"/>
    <circle cx="232" cy="250" r="6"/>
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

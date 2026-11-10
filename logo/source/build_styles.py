"""Alternative style explorations of the «صفحة واحد» YouTube logo.

Same concept as build_logo.py (the bookmark shaped as «1» above the name),
drawn in three different styles:

  neon     glowing neon tubes on a dark wall
  retro    vintage two-tone print on cream paper, with a sunburst and banner
  sticker  bold die-cut sticker on gold

    python build_styles.py          # writes ../styles/safha-wahed-<style>.svg
"""

from build_logo import ONE_RIBBON, STITCH, OUT, contours, path, rays

STYLES = OUT / "styles"

SPARK = "M0-1C.13-.13.13-.13 1 0C.13.13.13.13 0 1C-.13.13-.13.13-1 0C-.13-.13-.13-.13 0-1Z"
FOLD = "M-48 92L-13 0H-140V140Z"     # flag region of the «1», for fold shading
CREASE = "M-47 88L-15 4"


def name_parts(size, baseline, cx=400):
    """The name's letter bodies and its three dots (left-to-right), with the
    dots' playful bounce offsets scaled to the text size."""
    cs = contours("صفحة واحد", size, cx, baseline)
    dot_line = baseline - 186 / 330 * size
    body = [c for c in cs if c[1][3] > dot_line]
    dots = sorted((c for c in cs if c[1][3] <= dot_line), key=lambda c: c[1][0])
    assert len(dots) == 3
    k = size / 106
    bounce = [(-1 * k, -8 * k), (1 * k, -3 * k), (0, -6 * k)]
    return body, list(zip(dots, bounce))


def svg(body):
    return ('<svg xmlns="http://www.w3.org/2000/svg" width="800" height="800" '
            f'viewBox="0 0 800 800">\n  <title>صفحة واحد</title>\n{body}\n</svg>\n')


# --------------------------------------------------------------------------
# 1. Neon
# --------------------------------------------------------------------------
def neon():
    AMBER, PINK, CYAN, CORE = "#FFB83D", "#FF4F9A", "#3FE0FF", "#FFF4DC"
    body, dots = name_parts(106, 622)
    dots_svg = "".join(
        f'<g transform="translate({dx:.1f} {dy:.1f})">{path([c], fill=AMBER)}</g>'
        for c, (dx, dy) in dots)

    def glow(fid, colour, a, b):
        return f"""
    <filter id="{fid}" x="-50%" y="-50%" width="200%" height="200%">
      <feGaussianBlur in="SourceAlpha" stdDeviation="{a}" result="a"/>
      <feGaussianBlur in="SourceAlpha" stdDeviation="{b}" result="b"/>
      <feMerge result="m"><feMergeNode in="b"/><feMergeNode in="a"/></feMerge>
      <feFlood flood-color="{colour}"/>
      <feComposite in2="m" operator="in" result="g"/>
      <feMerge><feMergeNode in="g"/><feMergeNode in="g"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>"""

    return svg(f"""  <defs>
    <radialGradient id="wall" cx="400" cy="360" r="480" gradientUnits="userSpaceOnUse">
      <stop offset="0" stop-color="#1E1233"/>
      <stop offset="1" stop-color="#07050E"/>
    </radialGradient>
    <pattern id="bricks" width="80" height="40" patternUnits="userSpaceOnUse">
      <path d="M0 .5H80M0 20.5H80M40 0V20M0 20V40M80 20V40" stroke="#FFFFFF" stroke-opacity=".035" stroke-width="2" fill="none"/>
    </pattern>
    <path id="spark" d="{SPARK}"/>{glow("gAmber", AMBER, 5, 16)}{glow("gPink", PINK, 5, 16)}{glow("gCyan", CYAN, 4, 12)}
  </defs>
  <rect width="800" height="800" fill="url(#wall)"/>
  <rect width="800" height="800" fill="url(#bricks)"/>

  <!-- neon ring with a few breaks, like bent glass tube -->
  <g filter="url(#gCyan)" fill="none" stroke-linecap="round">
    <circle cx="400" cy="400" r="362" stroke="{CYAN}" stroke-width="6" stroke-dasharray="620 26 380 26 760 26 400 26"
            transform="rotate(-80 400 400)"/>
    <circle cx="400" cy="400" r="362" stroke="#E9FCFF" stroke-width="2" stroke-dasharray="620 26 380 26 760 26 400 26"
            transform="rotate(-80 400 400)"/>
  </g>

  <!-- the «1» bookmark as an amber tube with pink stitching -->
  <g transform="translate(440 126) rotate(7)" fill="none" stroke-linecap="round" stroke-linejoin="round">
    <g filter="url(#gAmber)">
      <path d="{ONE_RIBBON}" stroke="{AMBER}" stroke-width="11"/>
      <path d="{ONE_RIBBON}" stroke="{CORE}" stroke-width="3.5"/>
      <path d="{CREASE}" stroke="{AMBER}" stroke-width="6"/>
    </g>
    <g filter="url(#gPink)">
      <path d="{STITCH}" stroke="{PINK}" stroke-width="6" stroke-dasharray="12 12"/>
      <path d="{STITCH}" stroke="#FFE3F0" stroke-width="2" stroke-dasharray="12 12"/>
    </g>
  </g>

  <!-- pop lines + twinkles -->
  <g filter="url(#gAmber)" stroke="{AMBER}" stroke-width="7" stroke-linecap="round" fill="none">
    <path d="M520 122L542 96"/><path d="M532 150L564 144"/><path d="M500 108L506 76"/>
  </g>
  <g filter="url(#gCyan)" fill="{CYAN}">
    <use href="#spark" transform="translate(262 340) scale(28)"/>
    <use href="#spark" transform="translate(576 330) scale(18)"/>
    <circle cx="300" cy="146" r="6"/><circle cx="566" cy="236" r="6"/>
  </g>
  <g filter="url(#gPink)" fill="{PINK}">
    <use href="#spark" transform="translate(298 428) scale(12)"/>
    <circle cx="232" cy="260" r="5"/><circle cx="540" cy="430" r="5"/>
  </g>

  <!-- the name in glowing pink-white with amber dots -->
  <g transform="rotate(-2 400 600)">
    <g filter="url(#gPink)">{path(body, fill="#FFEAF4")}</g>
    <g filter="url(#gAmber)">{dots_svg}</g>
  </g>""")


# --------------------------------------------------------------------------
# 2. Retro print
# --------------------------------------------------------------------------
def retro():
    PAPER, PAPER2, INK2 = "#F2E3C6", "#E9D3A8", "#2A1F17"
    MUSTARD, MUSTARD_D, BRICK, BRICK_D = "#E5A11E", "#C4830E", "#C9472E", "#93301D"
    body, dots = name_parts(70, 586)
    dots_svg = "".join(
        f'<g transform="translate({dx:.1f} {dy:.1f})">'
        f'{path([c], fill=INK2, transform="translate(3 3)")}{path([c], fill=MUSTARD)}</g>'
        for c, (dx, dy) in dots)

    # ribbon banner: tails sit behind and lower than the main band
    tail_l = "M214 548H138L158 590L138 632H214Z"
    tail_r = "M586 548H662L642 590L662 632H586Z"
    fold_l = "M188 610L214 610L214 632Z"
    fold_r = "M612 610L586 610L586 632Z"
    band = "M188 512Q400 498 612 512V616Q400 602 188 616Z"

    return svg(f"""  <defs>
    <path id="spark" d="{SPARK}"/>
    <clipPath id="inside"><circle cx="400" cy="400" r="356"/></clipPath>
    <clipPath id="oneClip"><path d="{ONE_RIBBON}"/></clipPath>
    <filter id="grain" x="0" y="0" width="100%" height="100%">
      <feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="7" stitchTiles="stitch"/>
      <feColorMatrix values="0 0 0 0 .16  0 0 0 0 .12  0 0 0 0 .09  0 0 0 .55 -.18"/>
    </filter>
  </defs>
  <rect width="800" height="800" fill="{PAPER}"/>
  <path d="{rays(400, 320, 620, 24)}" fill="{PAPER2}" clip-path="url(#inside)"/>

  <!-- double ink ring with little stars -->
  <circle cx="400" cy="400" r="374" fill="none" stroke="{INK2}" stroke-width="7"/>
  <circle cx="400" cy="400" r="358" fill="none" stroke="{INK2}" stroke-width="2.5"/>
  <g fill="{INK2}">
    <use href="#spark" transform="translate(26 400) scale(14)"/>
    <use href="#spark" transform="translate(774 400) scale(14)"/>
  </g>

  <!-- the «1» bookmark: mustard with an ink outline and an off-register brick print -->
  <g transform="translate(445 132) rotate(7) scale(.95)">
    <path d="{ONE_RIBBON}" fill="{BRICK}" transform="translate(11 10)"/>
    <path d="{ONE_RIBBON}" fill="{MUSTARD}"/>
    <path d="{FOLD}" fill="{MUSTARD_D}" clip-path="url(#oneClip)"/>
    <path d="{CREASE}" stroke="{INK2}" stroke-width="3" stroke-linecap="round"/>
    <path d="{STITCH}" fill="none" stroke="{INK2}" stroke-width="3.5" stroke-dasharray="11 8"
          stroke-linecap="round" stroke-linejoin="round"/>
    <path d="{ONE_RIBBON}" fill="none" stroke="{INK2}" stroke-width="6" stroke-linejoin="round"/>
  </g>

  <!-- action lines + stars -->
  <g stroke="{INK2}" stroke-width="7" stroke-linecap="round" fill="none">
    <path d="M520 128L542 102"/><path d="M532 156L564 150"/><path d="M500 114L506 82"/>
  </g>
  <g fill="{INK2}">
    <use href="#spark" transform="translate(266 330) scale(28)"/>
    <use href="#spark" transform="translate(580 320) scale(18)"/>
  </g>
  <g fill="{BRICK}">
    <use href="#spark" transform="translate(300 430) scale(12)"/>
    <circle cx="300" cy="150" r="7"/><circle cx="570" cy="236" r="6"/>
    <circle cx="236" cy="252" r="5"/><circle cx="548" cy="430" r="5"/>
  </g>

  <!-- ribbon banner carrying the name -->
  <g stroke="{INK2}" stroke-width="5" stroke-linejoin="round">
    <path d="{tail_l}" fill="{BRICK_D}"/><path d="{tail_r}" fill="{BRICK_D}"/>
    <path d="{fold_l}" fill="{INK2}"/><path d="{fold_r}" fill="{INK2}"/>
    <path d="{band}" fill="{BRICK}"/>
  </g>
  {path(body, fill=INK2, transform="translate(3 3)")}
  {path(body, fill=PAPER)}
  {dots_svg}

  <rect width="800" height="800" filter="url(#grain)" opacity=".7"/>""")


# --------------------------------------------------------------------------
# 3. Sticker pop
# --------------------------------------------------------------------------
def sticker():
    BG, BG_D, INK3, WHITE, CREAM3 = "#F6B73C", "#E39A1F", "#17140F", "#FFFFFF", "#F5EBDA"
    body, dots = name_parts(104, 626)
    dots_svg = "".join(
        f'<g transform="translate({dx:.1f} {dy:.1f})">{path([c], fill=INK3)}</g>'
        for c, (dx, dy) in dots)
    dots_outline = "".join(
        f'<g transform="translate({dx:.1f} {dy:.1f})">'
        f'{path([c], fill=WHITE, stroke=WHITE, stroke_width=16, stroke_linejoin="round")}</g>'
        for c, (dx, dy) in dots)

    return svg(f"""  <defs>
    <path id="spark" d="{SPARK}"/>
    <clipPath id="oneClip"><path d="{ONE_RIBBON}"/></clipPath>
    <pattern id="halftone" width="22" height="22" patternUnits="userSpaceOnUse">
      <circle cx="11" cy="11" r="4.2" fill="{BG_D}"/>
    </pattern>
    <radialGradient id="edgeFade" cx="400" cy="400" r="420" gradientUnits="userSpaceOnUse">
      <stop offset=".55" stop-color="#000000"/>
      <stop offset="1" stop-color="#FFFFFF"/>
    </radialGradient>
    <mask id="edges" maskUnits="userSpaceOnUse" x="0" y="0" width="800" height="800">
      <rect width="800" height="800" fill="url(#edgeFade)"/>
    </mask>
    <filter id="drop" x="-30%" y="-30%" width="160%" height="160%">
      <feDropShadow dx="6" dy="12" stdDeviation="8" flood-color="#5A3500" flood-opacity=".45"/>
    </filter>
  </defs>
  <rect width="800" height="800" fill="{BG}"/>
  <rect width="800" height="800" fill="url(#halftone)" mask="url(#edges)"/>
  <path d="{rays(400, 300, 520, 20)}" fill="#FFFFFF" fill-opacity=".12"/>

  <!-- the «1» bookmark as a die-cut sticker -->
  <g transform="translate(440 128) rotate(7)">
    <path d="{ONE_RIBBON}" fill="{WHITE}" stroke="{WHITE}" stroke-width="30" stroke-linejoin="round" filter="url(#drop)"/>
    <path d="{ONE_RIBBON}" fill="{INK3}"/>
    <path d="{FOLD}" fill="#FFFFFF" fill-opacity=".12" clip-path="url(#oneClip)"/>
    <path d="{CREASE}" stroke="{CREAM3}" stroke-opacity=".7" stroke-width="2.5" stroke-linecap="round"/>
    <path d="{STITCH}" fill="none" stroke="{BG}" stroke-width="4" stroke-dasharray="11 8"
          stroke-linecap="round" stroke-linejoin="round"/>
    <rect x="14" y="26" width="10" height="150" rx="5" fill="#FFFFFF" fill-opacity=".18"/>
  </g>

  <!-- pop lines + sparkles -->
  <g stroke="{INK3}" stroke-width="9" stroke-linecap="round" fill="none">
    <path d="M530 116L552 90"/><path d="M544 146L576 140"/><path d="M508 100L514 68"/>
  </g>
  <g fill="{WHITE}" stroke="{INK3}" stroke-width="4" stroke-linejoin="round">
    <use href="#spark" transform="translate(258 336) scale(34)" stroke-width=".12"/>
    <use href="#spark" transform="translate(582 324) scale(22)" stroke-width=".18"/>
  </g>
  <g fill="{INK3}">
    <use href="#spark" transform="translate(300 432) scale(13)"/>
    <circle cx="300" cy="146" r="8"/><circle cx="568" cy="236" r="7"/>
    <circle cx="232" cy="256" r="6"/><circle cx="546" cy="432" r="6"/>
  </g>

  <!-- the name as a sticker too -->
  <g transform="rotate(-3 400 600)">
    <g filter="url(#drop)">
      {path(body, fill=WHITE, stroke=WHITE, stroke_width=22, stroke_linejoin="round")}
      {dots_outline}
    </g>
    {path(body, fill=INK3)}
    {dots_svg}
  </g>""")


if __name__ == "__main__":
    STYLES.mkdir(exist_ok=True)
    for name, fn in (("neon", neon), ("retro", retro), ("sticker", sticker)):
        (STYLES / f"safha-wahed-{name}.svg").write_text(fn(), encoding="utf-8")
        print("wrote", STYLES / f"safha-wahed-{name}.svg")

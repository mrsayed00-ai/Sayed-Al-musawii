"""Hand gestures for the pixel character (drawn in code, like the bust).

The bust (48x60) is placed on a wider 72x60 canvas (offset 12) so a hand can
sit beside the head. Gestures:
  wave_a / wave_b / wave_c  right hand raised beside the head, open palm,
                            three tilts for a waving cycle
  point_up                  same arm, index finger up (towards the link above)
  point_right               left arm, index finger to the right (towards the
                            phone screen beside the small character)
compose_gesture() returns an RGBA image; scale with NEAREST only.
"""
from PIL import Image

import sprite as S

OFF, GW = 12, 72


def _blank():
    return [[None] * GW for _ in range(S.H)]


def _put(g, x, y, c):
    if 0 <= x < GW and 0 <= y < S.H:
        g[y][x] = c


def _sleeve(g, path):
    """path: list of (y, x_left, x_right) rows of the forearm sleeve."""
    for y, a, b in path:
        for x in range(a, b + 1):
            _put(g, x, y, "jacket")
        _put(g, a, y, "jacket_sh")
        _put(g, b, y, "zip")
        if (a + y) % 4 == 0:
            _put(g, (a + b) // 2, y, "jacket_hi")


def _right_arm(g):  # viewer's left side
    rows = [(y, 9 - (59 - y) // 10, 16 - (59 - y) // 10) for y in range(40, 60)]
    _sleeve(g, rows)
    for x in range(6, 15):
        _put(g, x, 38, "collar")
        _put(g, x, 39, "collar")


def _open_hand(g, tilt=0):
    for y in range(32, 38):  # palm
        for x in range(6, 14):
            _put(g, x, y, "skin")
    for x in range(6, 14):
        _put(g, x, 37, "skin_sh")
    for y in range(32, 37):
        _put(g, 13, y, "skin_sh")
    fingers = [(6, 29), (8, 28), (10, 27), (12, 28)]  # pinky .. index: (x, top row)
    for fx, top in fingers:
        for y in range(top, 32):
            dx = tilt if y < top + 2 else 0
            _put(g, fx + dx, y, "skin")
        _put(g, fx + 1, 31, "skin_sh")
    for x, y in ((14, 33), (15, 32), (15, 33), (14, 34)):  # thumb towards the face
        _put(g, x, y, "skin")


def _fist_up(g):
    for y in range(32, 38):
        for x in range(6, 13):
            _put(g, x, y, "skin")
    for x in range(6, 13):
        _put(g, x, 33, "skin_sh")
        _put(g, x, 37, "skin_sh")
    for y in range(25, 32):  # index finger up
        _put(g, 11, y, "skin")
        _put(g, 12, y, "skin_sh")
    for x in range(7, 11):  # thumb across the fist
        _put(g, x, 35, "skin_sh")


def _left_arm_point_right(g):  # viewer's right side
    rows = [(y, 54 + (59 - y) // 3, 61 + (59 - y) // 3) for y in range(46, 60)]
    _sleeve(g, rows)
    for x in range(58, 66):
        _put(g, x, 45, "collar")
        _put(g, x, 44, "collar")
    for y in range(38, 44):  # fist
        for x in range(60, 66):
            _put(g, x, y, "skin")
    for y in range(38, 44):
        _put(g, 60, y, "skin_sh")
    for x in range(66, 71):  # index finger to the right
        _put(g, x, 39, "skin")
        _put(g, x, 40, "skin_sh")
    for x in range(61, 65):  # curled fingers
        _put(g, x, 42, "skin_sh")


def _rim(g, max_row=47):
    pts = []
    for y in range(S.H):
        for x in range(GW):
            if g[y][x] is None and y <= max_row and any(
                    0 <= x + dx < GW and 0 <= y + dy < S.H and g[y + dy][x + dx] not in (None, "rim")
                    for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                pts.append((x, y))
    for x, y in pts:
        g[y][x] = "rim"


def compose_gesture(expression="neutral", mouth=None, blink=False, gesture=None):
    brows, eyes, look, m = S.EXPRESSIONS[expression]
    b = S.build_base()
    S.draw_brows(b, brows)
    S.draw_eyes(b, "blink" if blink else eyes, look)
    S.draw_mouth(b, mouth or m)
    g = _blank()
    for y in range(S.H):
        for x in range(S.W):
            if b[y][x]:
                g[y][x + OFF] = b[y][x]
    if gesture in ("wave_a", "wave_b", "wave_c"):
        _right_arm(g)
        _open_hand(g, {"wave_a": 0, "wave_b": -1, "wave_c": 1}[gesture])
    elif gesture == "point_up":
        _right_arm(g)
        _fist_up(g)
    elif gesture == "point_right":
        _left_arm_point_right(g)
    _rim(g)
    im = Image.new("RGBA", (GW, S.H), (0, 0, 0, 0))
    px = im.load()
    for y in range(S.H):
        for x in range(GW):
            if g[y][x]:
                px[x, y] = S.PAL[g[y][x]] + (255,)
    return im

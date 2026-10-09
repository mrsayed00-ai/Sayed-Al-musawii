"""Pixel illustration for «بدون لا أشوف» (S14): two small players standing
face to face, each holding a phone up in front of the face with the dark back
towards themselves and the lit screen (with a picture) towards the other
player. Dotted sight lines go from each player's eye to the OTHER player's
screen and cross in the middle. Illustration only, not app UI.

Layers (64x36 cells, scale with NEAREST): playerA.png, playerB.png (each
with its phone and arm), fx_0..7.png (screen glow, marching sight lines, «؟»
bubbles alternating), static.png (composite, for the storyboard).
Usage: blind_illus.py <out_dir>
"""
import os
import sys

from PIL import Image

W, H = 64, 40
PAL = {
    "hair": (28, 24, 32), "skinA": (201, 139, 99), "skinA_sh": (170, 110, 76),
    "skinB": (218, 160, 120), "skinB_sh": (186, 128, 92),
    "eye": (26, 20, 24),
    "shirtA": (102, 85, 194), "shirtA_sh": (82, 48, 187),
    "shirtB": (242, 166, 15), "shirtB_sh": (201, 132, 8),
    "pants": (42, 36, 64), "shoe": (26, 20, 64),
    "ph_back": (26, 20, 64), "ph_edge": (60, 52, 96), "screen": (255, 248, 214),
    "apple": (229, 58, 52), "leaf": (74, 164, 76), "banana": (242, 196, 40), "banana_sh": (201, 150, 20),
    "rim": (178, 164, 255),
}


def grid():
    return [[None] * W for _ in range(H)]


def put(g, x, y, c):
    if 0 <= x < W and 0 <= y < H:
        g[y][x] = c


def player(g, skin, skin_sh, shirt, shirt_sh, icon):
    """Player facing right, drawn on the left half; mirror for player B.
    The phone is held up at forehead height, above the eye line, so the
    player looks under their own phone at the other player's screen."""
    for y in range(10, 13):                    # hair
        for x in range(8, 15):
            put(g, x, y, "hair")
    for y in range(13, 16):
        put(g, 8, y, "hair")
    for y in range(13, 19):                    # face (profile)
        for x in range(9, 15):
            put(g, x, y, skin)
    put(g, 15, 15, skin)                       # nose
    put(g, 10, 15, skin_sh)                    # ear
    put(g, 13, 14, "eye")                      # eye, looking right and up
    put(g, 14, 17, skin_sh)                    # mouth line
    for x in (11, 12):
        put(g, x, 19, skin_sh)                 # neck
    for y in range(20, 30):                    # torso
        for x in range(8, 15):
            put(g, x, y, shirt)
        put(g, 8, y, shirt_sh)
    for x, y in ((14, 21), (15, 20), (15, 19), (15, 18), (16, 17), (16, 16), (16, 15), (16, 14), (16, 13)):
        put(g, x, y, shirt)                    # raised front arm
    for x, y in ((17, 12), (17, 11), (16, 12)):  # hand holding the phone
        put(g, x, y, skin)
    for y in range(30, 38):                    # legs
        for x in (9, 10, 12, 13):
            put(g, x, y, "pants")
    for x in (9, 10, 11, 12, 13, 14):
        put(g, x, 38, "shoe")
    # phone: back towards the holder (x 18), screen towards the other player
    for y in range(3, 12):
        put(g, 18, y, "ph_back")
    for x in (19, 20, 21):
        put(g, x, 3, "ph_edge")
        put(g, x, 11, "ph_edge")
        for y in range(4, 11):
            put(g, x, y, "screen")
    for x, y, c in icon:
        put(g, x, y, c)


APPLE = [(19, 7, "apple"), (20, 7, "apple"), (19, 8, "apple"), (20, 8, "apple"), (20, 6, "leaf"), (21, 7, "apple")]
BANANA = [(19, 8, "banana"), (20, 8, "banana"), (21, 7, "banana"), (21, 6, "banana_sh"), (19, 7, "banana_sh")]


def mirror(g):
    return [list(reversed(row)) for row in g]


def rim(g, max_row=39):
    pts = [(x, y) for y in range(H) for x in range(W) if g[y][x] is None and y <= max_row and any(
        0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] not in (None, "rim")
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)))]
    for x, y in pts:
        g[y][x] = "rim"


def to_img(g, alpha=None):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        for x in range(W):
            c = g[y][x]
            if c:
                px[x, y] = PAL[c] + (255,)
    return im


def line_points(x0, y0, x1, y1):
    n = max(abs(x1 - x0), abs(y1 - y0))
    return [(round(x0 + (x1 - x0) * i / n), round(y0 + (y1 - y0) * i / n)) for i in range(n + 1)]


QMARK_AR = ["01110", "10001", "10000", "01000", "00100", "00000", "00100"]  # «؟» (mirrored)


def fx_frame(k):
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()
    white, lav, purple = (255, 255, 255, 235), (178, 164, 255, 255), (82, 48, 187, 255)
    # sight lines: each eye (below its own phone) -> the OTHER player's screen.
    # Coloured like the looker's shirt so the crossing reads at a glance.
    gaze = {"A": (214, 206, 255, 240), "B": (255, 214, 74, 240)}
    for who, (x0, y0, x1, y1) in (("A", (14, 14, 41, 8)), ("B", (49, 14, 22, 8))):
        pts = line_points(x0, y0, x1, y1)
        for i, (x, y) in enumerate(pts):
            if (i - k) % 4 in (0, 1):
                px[x, y] = gaze[who]
        ex, ey = pts[-1]
        d = 1 if x1 > x0 else -1
        for dx, dy in ((-d, -1), (-d, 1)):
            px[ex + dx, ey + dy] = gaze[who]
    # the lit screens pulse softly (light on the screen, not rays)
    glow = (0, 60, 110, 60)[k % 4]
    for x in (19, 20, 21, 42, 43, 44):
        for y in range(4, 11):
            px[x, y] = (255, 255, 255, glow)
    # «؟» bubbles above the heads, alternating (they guess with yes/no questions)
    side = (k // 4) % 2
    bx = 7 if side == 0 else 63 - 7 - 8
    for y in range(0, 9):
        for x in range(bx, bx + 9):
            edge = y in (0, 8) or x in (bx, bx + 8)
            px[x, y] = lav if edge else (255, 255, 255, 255)
    for r, row in enumerate(QMARK_AR):
        for c, v in enumerate(row):
            if v == "1":
                px[bx + 2 + c, 1 + r] = purple
    px[bx + 4, 9] = lav
    return im


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    a = grid()
    player(a, "skinA", "skinA_sh", "shirtA", "shirtA_sh", APPLE)
    rim(a)
    b = grid()
    player(b, "skinB", "skinB_sh", "shirtB", "shirtB_sh", BANANA)
    b = mirror(b)
    rim(b)
    A, B = to_img(a), to_img(b)
    A.save(f"{out}/playerA.png")
    B.save(f"{out}/playerB.png")
    for k in range(8):
        fx_frame(k).save(f"{out}/fx_{k}.png")
    comp = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    for layer in (fx_frame(0), A, B):
        comp.alpha_composite(layer)
    comp.save(f"{out}/static.png")
    print("ok", out)

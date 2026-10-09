"""Pixel-art bust of the presenter, drawn in code (no photo pixels are used).

Reference: the user's portrait (short dark hair, short trimmed beard that
is light on the cheeks and fuller on the jaw and chin, full moustache, wide smile with upper teeth, charcoal textured jacket with a big
open collar over a black crew-neck tee). No headset. Skin uses a natural warm
tone, not the photo's blue lighting. The rim light is Fanous purple.

The sprite is 48x60 cells. compose() returns an RGBA PIL image at scale 1;
scale up with NEAREST only.
"""
from PIL import Image

W, H = 48, 60

PAL = {
    "hair": (28, 24, 32), "hair_hi": (58, 52, 64),
    "skin": (201, 139, 99), "skin_hi": (222, 166, 124), "skin_sh": (170, 110, 76), "skin_dk": (138, 86, 58),
    "beard": (38, 30, 33), "beard_md": (66, 50, 50), "stubble": (112, 79, 63), "stub_lt": (152, 105, 80),
    "brow": (26, 20, 24), "lash": (20, 14, 16),
    "eye_w": (241, 232, 224), "iris": (52, 30, 22),
    "teeth": (248, 244, 238), "mouth": (74, 26, 32), "tongue": (166, 70, 76), "lip": (120, 60, 58),
    "tee": (22, 20, 27), "rib": (44, 41, 51), "logo": (214, 214, 224),
    "jacket": (75, 74, 85), "jacket_sh": (58, 57, 67), "jacket_hi": (98, 95, 110), "collar": (104, 101, 116),
    "zip": (44, 43, 52),
    "rim": (178, 164, 255),
}


def sym(x):
    return W - 1 - x


# head silhouette (hair + face + beard), inclusive spans per row
HEAD = {4: (18, 29), 5: (15, 32), 6: (14, 33), 7: (13, 34), 8: (12, 35), 9: (12, 35), 10: (12, 35)}
for y in range(11, 30):
    HEAD[y] = (11, 36)
HEAD.update({30: (12, 35), 31: (12, 35), 32: (13, 34), 33: (14, 33), 34: (15, 32), 35: (16, 31),
             36: (18, 29), 37: (20, 27)})

# beard starts at this row for each left-side column (mirrored on the right)
CHEEK = {11: 18, 12: 20, 13: 25, 14: 27, 15: 28, 16: 28, 17: 28}

HAIR_TEX = [(16, 5), (17, 5), (22, 5), (23, 5), (27, 6), (28, 6), (14, 7), (15, 7), (19, 7), (20, 7),
            (31, 7), (32, 7), (24, 8), (25, 8), (13, 9), (14, 9), (29, 9), (30, 9), (18, 9), (19, 9)]


def body_span(y):
    spans = {40: (15, 32), 41: (12, 35), 42: (9, 38), 43: (6, 41), 44: (4, 43), 45: (3, 44)}
    return spans.get(y, (2, 45) if y >= 46 else None)


def tee_left(y):
    return 17 - (y - 42) // 4


def build_base():
    g = [[None] * W for _ in range(H)]

    def put(x, y, c):
        if 0 <= x < W and 0 <= y < H:
            g[y][x] = c

    def put2(x, y, c):  # mirrored pair
        put(x, y, c)
        put(sym(x), y, c)

    # body: jacket, collar, tee
    for y in range(40, H):
        l, r = body_span(y)
        for x in range(l, r + 1):
            put(x, y, "jacket")
        for x in (l, l + 1):
            put2(x, y, "jacket_sh")
        if y >= 42:
            tl = tee_left(y)
            for x in range(tl, sym(tl) + 1):
                put(x, y, "rib" if y <= 43 else "tee")
            put2(tl - 1, y, "zip")
            # big open collar beside the tee, widest around the chest
            w = min(6, 2 + (y - 40) // 2) if y <= 48 else max(0, 6 - (y - 48))
            for k in range(1, w + 1):
                put2(tl - 1 - k, y, "collar" if (k + y) % 3 else "jacket_hi")
    for y in range(44, H):  # sparse fleece texture
        for x in range(3, 45):
            if g[y][x] == "jacket" and (x * 7 + y * 13) % 11 == 0:
                g[y][x] = "jacket_hi"
    for x, y in ((30, 55), (31, 54), (32, 55), (33, 54)):  # small print on the tee
        put(x, y, "logo")

    # neck
    for y in range(36, 44):
        for x in range(18, 30):
            put(x, y, "skin_sh")
    for x in range(19, 29):  # shadow under the chin
        put(x, 38, "skin_dk")

    # head mass
    for y, (l, r) in HEAD.items():
        for x in range(l, r + 1):
            put(x, y, "skin")
    # ears
    for y in range(18, 26):
        a = 9 if y in (18, 25) else 8
        for x in range(a, 11):
            put2(x, y, "skin")
    for y in range(20, 24):
        put2(9, y, "skin_sh")
    # face shading
    for y in range(12, 30):
        put(35, y, "skin_sh")
        put(36, y, "skin_sh")
    for y in (11, 12):
        for x in range(20, 28):
            put(x, y, "skin_hi")

    # hair cap + hairline + sideburns
    for y in range(4, 11):
        l, r = HEAD[y]
        for x in range(l, r + 1):
            put(x, y, "hair")
    for x in range(11, 37):
        put(x, 10, "hair" if not 16 <= x <= 31 else "skin")
    for x in (13, 14, 15):
        put2(x, 11, "hair")
    put2(13, 12, "hair")
    for y in range(10, 19):
        put2(11, y, "hair")
        put2(12, y, "hair")
    for x, y in HAIR_TEX:
        put(x, y, "hair_hi")

    # beard: graded density, light on the cheeks, fuller along the jaw and
    # chin, ordered-dither transitions (photo reference: short, trimmed,
    # skin visible through it on the cheeks); moustache stays full
    bayer = ((0.0, 0.5), (0.75, 0.25))
    edge = {(x, y) for y, (l, r) in HEAD.items() if 28 <= y <= 34 for x in (l, l + 1, r - 1, r)}
    chin = {(x, y) for y in (35, 36, 37) for x in range(HEAD[y][0], HEAD[y][1] + 1)}
    for y, (l, r) in HEAD.items():
        for x in range(l, r + 1):
            xl = min(x, sym(x))
            start = CHEEK.get(xl, 27)
            if y < start:
                continue
            k = y - start
            dens = min(0.74, 0.15 + 0.13 * k)       # fade in below the cheek line
            if 17 <= x <= 30 and y >= 31:
                dens = max(dens, 0.62)               # under the lip and chin
            if (x, y) in edge:
                dens = max(dens, 0.8)                # jaw outline
            if (x, y) in chin:
                dens = 0.74                          # chin underside: one even tone
            q = dens + (bayer[y % 2][x % 2] - 0.375) * 0.22
            c = ("skin" if q < 0.27 else "stub_lt" if q < 0.45 else "stubble" if q < 0.62
                 else "beard_md" if q < 0.86 else "beard")
            if c != "skin":
                put(x, y, c)
    for x in range(18, 30):                          # moustache: full, softer ends
        put(x, 27, "beard" if 19 <= x <= 28 else "beard_md")
    for x in range(17, 31):
        put(x, 28, "beard" if 18 <= x <= 29 else "beard_md")
    for x in (19, 22, 25, 28):
        put(x, 27, "beard_md")                       # hair texture in the moustache
    # nose
    for y in range(18, 26):
        put(24, y, "skin_hi")
    for y in range(21, 26):
        put(22, y, "skin_sh")
    for x in (21, 26):
        put(x, 25, "skin_sh")
        put(x, 26, "skin_sh")
    for x in range(22, 26):
        put(x, 26, "skin_sh")
    put(22, 26, "skin_dk")
    put(25, 26, "skin_dk")
    return g


def draw_brows(g, kind):
    rows = {"normal": (14, 15), "raised": (13, 14), "up": (12, 13)}
    if kind == "frown":
        for x in range(15, 19):
            g[14][x] = "brow"; g[14][sym(x)] = "brow"
        for x in (19, 20):
            g[15][x] = "brow"; g[15][sym(x)] = "brow"
        g[15][14] = "brow"; g[15][sym(14)] = "brow"
        return
    if kind == "sly":  # viewer-left brow raised, the other normal
        _brow(g, 13, 14, left=True)
        _brow(g, 14, 15, left=False)
        return
    a, b = rows[kind]
    _brow(g, a, b, True)
    _brow(g, a, b, False)


def _brow(g, a, b, left):
    xs_top = range(15, 21)
    xs_tail = range(14, 17)
    f = (lambda x: x) if left else sym
    for x in xs_top:
        g[a][f(x)] = "brow"
    for x in xs_tail:
        g[b][f(x)] = "brow"


def draw_eyes(g, kind, look=0):
    """Eyes occupy rows 17 (upper lid) to 20 (lower lid); iris is 2x2."""
    sides = ((lambda x: x), False), (sym, True)
    for f, mirror in sides:
        if kind == "blink":
            for x in range(16, 20):
                g[19][f(x)] = "lash"
            continue
        if kind == "happy":  # closed, laughing arcs
            g[17][f(17)] = g[17][f(18)] = "lash"
            g[18][f(16)] = g[18][f(19)] = "lash"
            continue
        for x in range(15, 21):
            g[17][f(x)] = "lash"
        rows = (18, 19) if kind != "squint" else (19,)
        if kind == "squint":
            for x in range(15, 21):
                g[18][f(x)] = "lash"
        for y in rows:
            for x in range(16, 20):
                g[y][f(x)] = "eye_w"
        i0 = 17 - look if mirror else 17 + look  # look: -1 screen-left, +1 screen-right
        for y in rows:
            for x in (i0, i0 + 1):
                g[y][f(x)] = "iris"
        for x in range(16, 20):
            g[20][f(x)] = "skin_sh"


MOUTHS = {
    # (row, x0, x1, colour); moustache sits on rows 27-28
    "closed": [(29, 19, 28, "lip"), (28, 18, 18, "lip"), (28, 29, 29, "lip")],
    "smile": [(29, 19, 28, "teeth"), (30, 19, 28, "teeth"), (29, 18, 18, "mouth"), (29, 29, 29, "mouth"),
              (31, 20, 27, "mouth")],
    "half": [(29, 20, 27, "teeth"), (30, 20, 27, "mouth"), (31, 21, 26, "mouth")],
    "open": [(29, 19, 28, "teeth"), (30, 19, 28, "mouth"), (31, 19, 28, "mouth"), (32, 20, 27, "mouth"),
             (32, 22, 25, "tongue")],
    "wide": [(29, 18, 29, "teeth"), (30, 18, 29, "teeth"), (31, 18, 29, "mouth"), (32, 18, 29, "mouth"),
             (33, 19, 28, "mouth"), (33, 21, 26, "tongue"), (34, 21, 26, "tongue")],
    "smirk": [(29, 20, 27, "lip"), (28, 28, 29, "lip")],
}


def draw_mouth(g, kind):
    for row, x0, x1, c in MOUTHS[kind]:
        for x in range(x0, x1 + 1):
            g[row][x] = c


def add_rim(g, max_row=47):
    rim = []
    for y in range(H):
        for x in range(W):
            if g[y][x] is None and y <= max_row:
                if any(0 <= x + dx < W and 0 <= y + dy < H and g[y + dy][x + dx] is not None
                       for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1))):
                    rim.append((x, y))
    for x, y in rim:
        g[y][x] = "rim"


EXPRESSIONS = {
    # name: (brows, eyes, look, default mouth)
    "neutral": ("normal", "open", 0, "smile"),
    "sly": ("sly", "open", 1, "smirk"),
    "suspicious": ("frown", "squint", -1, "closed"),
    "surprised": ("up", "open", 0, "open"),
    "laugh": ("raised", "happy", 0, "wide"),
}


def compose(expression="neutral", mouth=None, blink=False, rim=True):
    brows, eyes, look, m = EXPRESSIONS[expression]
    g = build_base()
    draw_brows(g, brows)
    draw_eyes(g, "blink" if blink else eyes, look)
    draw_mouth(g, mouth or m)
    if rim:
        add_rim(g)
    im = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    px = im.load()
    for y in range(H):
        for x in range(W):
            if g[y][x]:
                px[x, y] = PAL[g[y][x]] + (255,)
    return im


def mouth_for_level(level):
    """Mouth shape from the measured loudness envelope (0..1) of one frame."""
    if level < 0.12:
        return "closed"
    if level < 0.35:
        return "half"
    if level < 0.7:
        return "open"
    return "wide"

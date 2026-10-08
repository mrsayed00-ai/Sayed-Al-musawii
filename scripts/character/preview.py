"""Character preview sheet: big neutral bust, expressions, mouth set, blink,
and a side-by-side with the reference photo (photo stays local).
Usage: preview.py <photo> <font.ttf> <out.png>"""
import sys

from PIL import Image, ImageDraw, ImageFont

from sprite import EXPRESSIONS, MOUTHS, compose

photo_path, font_path, out = sys.argv[1:4]
BG_TOP, BG_BOT = (82, 48, 187), (20, 15, 46)


def stage(w, h, glow=True):
    im = Image.new("RGB", (w, h))
    d = ImageDraw.Draw(im)
    for y in range(h):
        t = y / h
        d.line([(0, y), (w, y)], fill=tuple(int(BG_TOP[i] * (1 - t) + BG_BOT[i] * t) for i in range(3)))
    if glow:
        g = Image.new("L", (w, h), 0)
        ImageDraw.Draw(g).ellipse([w * 0.12, h * 0.15, w * 0.88, h * 0.95], fill=150)
        from PIL import ImageFilter
        g = g.filter(ImageFilter.GaussianBlur(w // 8))
        im = Image.composite(Image.new("RGB", (w, h), (150, 132, 255)), im, g)
    return im


def big(sprite, scale):
    return sprite.resize((sprite.width * scale, sprite.height * scale), Image.NEAREST)


f_big = ImageFont.truetype(font_path, 54)
f_sm = ImageFont.truetype(font_path, 34)
sheet = Image.new("RGB", (2200, 2050), (16, 12, 36))
d = ImageDraw.Draw(sheet)
d.text((2140, 30), "معاينة شخصية البكسل — بدون سماعة", font=f_big, fill=(255, 255, 255), anchor="ra")

# reference photo vs sprite
ph = Image.open(photo_path).convert("RGB")
ph = ph.crop((150, 250, 874, 1336)).resize((482, 723))
sheet.paste(ph, (60, 130))
d.text((542, 860), "المرجع (محلي فقط)", font=f_sm, fill=(190, 180, 255), anchor="ra")
st = stage(720, 900)
spr = big(compose("neutral"), 15)
st.paste(spr, ((720 - spr.width) // 2, 900 - spr.height), spr)
sheet.paste(st, (580, 130))
d.text((1300, 1040), "الوضع الأساسي ×15", font=f_sm, fill=(190, 180, 255), anchor="ra")

# expressions
x = 1340
AR = {"sly": "تمثيل / خبث", "suspicious": "شك", "surprised": "مفاجأة", "laugh": "ضحك"}
for i, name in enumerate(["sly", "suspicious", "surprised", "laugh"]):
    cx, cy = x + (i % 2) * 420, 130 + (i // 2) * 490
    st = stage(400, 430)
    spr = big(compose(name), 7)
    st.paste(spr, ((400 - spr.width) // 2, 430 - spr.height), spr)
    sheet.paste(st, (cx, cy))
    d.text((cx + 400, cy + 432), AR[name], font=f_sm, fill=(190, 180, 255), anchor="ra")

# mouth set + blink (crops of the face)
d.text((2140, 1110), "أشكال الفم: تُختار إطارًا بإطار من شدة الصوت المقاسة (مغلق، نصف، مفتوح، واسع)", font=f_sm, fill=(255, 255, 255), anchor="ra")
names = ["closed", "half", "open", "wide", "smile", "smirk"]
for i, m in enumerate(names + ["blink"]):
    spr = compose("neutral", mouth=m if m != "blink" else "smile", blink=(m == "blink"), rim=False)
    face = big(spr.crop((8, 10, 40, 42)), 9)
    bx = 60 + i * 300
    tile = stage(288, 288, glow=False)
    tile.paste(face, (0, 0), face)
    sheet.paste(tile, (bx, 1170))
    d.text((bx + 288, 1462), {"closed": "مغلق", "half": "نصف", "open": "مفتوح", "wide": "واسع", "smile": "ابتسامة", "smirk": "ابتسامة جانبية", "blink": "رمشة"}[m], font=f_sm, fill=(190, 180, 255), anchor="ra")

# small corner size, as used during the gameplay sections
d.text((2140, 1540), "الحجم الصغير في زاوية الشاشة أثناء الأقسام، ودورة كلام", font=f_sm, fill=(255, 255, 255), anchor="ra")
for i, m in enumerate(["closed", "half", "open", "wide", "half", "closed"]):
    st = stage(340, 440)
    spr = big(compose("neutral", mouth=m), 7)
    st.paste(spr, ((340 - spr.width) // 2, 440 - spr.height), spr)
    st = st.resize((280, 362))
    sheet.paste(st, (60 + i * 300, 1600))
sheet.save(out)
print(out, sheet.size)

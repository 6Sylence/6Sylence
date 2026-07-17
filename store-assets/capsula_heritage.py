#!/usr/bin/env python3
# Cápsula Heritage — flat-lay garment renders for sparse apparel/footwear categories.
# Editorial illustration style: studio-gray backdrop, soft shadow, shaded fabric,
# stitch details, unique prints per piece (none reused from the poster line).
import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

S = 1600  # square canvas
NEGRO   = (24, 24, 27)
CREMA   = (238, 230, 212)
ORO     = (191, 154, 70)
ORO_HI  = (222, 192, 112)
BURDEOS = (94, 30, 42)
NAVY    = (30, 38, 60)
BLANCO  = (245, 244, 241)

SANS_B = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS   = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B= "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO   = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p, s): return ImageFont.truetype(p, s)

# ---------------------------------------------------------------- studio + fabric
def studio():
    ys = np.linspace(0, 1, S)
    top, bot = np.array((233, 231, 227)), np.array((209, 206, 201))
    col = top[None, :] + (bot - top)[None, :] * ys[:, None]
    img = Image.fromarray(np.repeat(col[:, None, :], S, axis=1).astype(np.uint8))
    return img

def drop_shadow(img, mask, dy=26, blur=30, opacity=90):
    sh = Image.new("L", (S, S), 0)
    sh.paste(mask, (0, dy))
    sh = sh.filter(ImageFilter.GaussianBlur(blur)).point(lambda v: v * opacity // 255)
    black = Image.new("RGB", (S, S), (60, 58, 55))
    img.paste(black, (0, 0), sh)
    return img

def fabric(img, mask, base, grad=0.10, noise=3.5, edge=0.18, seed=5):
    """Shade a garment region: vertical gradient + fabric noise + inner edge shadow."""
    m = np.asarray(mask).astype(np.float32) / 255.0
    ys = np.linspace(-1, 1, S)[:, None]
    shade = 1 - grad * 0.5 * (ys + 0.4)
    rng = np.random.default_rng(seed)
    tex = rng.normal(0, noise, (S, S))
    # inner shadow from edge distance
    er = mask.filter(ImageFilter.MinFilter(9)).filter(ImageFilter.GaussianBlur(14))
    inner = 1 - edge * (1 - np.asarray(er).astype(np.float32) / 255.0)
    col = np.zeros((S, S, 3), dtype=np.float32)
    for c in range(3):
        col[:, :, c] = base[c] * shade * inner + tex
    out = np.asarray(img).astype(np.float32)
    out = out * (1 - m[:, :, None]) + np.clip(col, 0, 255) * m[:, :, None]
    return Image.fromarray(out.astype(np.uint8))

def poly_mask(polys):
    mask = Image.new("L", (S, S), 0)
    d = ImageDraw.Draw(mask)
    for p in polys:
        d.polygon(p, fill=255)
    return mask.filter(ImageFilter.GaussianBlur(1.2))

def outline(draw, poly, color, w=3):
    draw.line(list(poly) + [poly[0]], fill=color, width=w, joint="curve")

def dashed(draw, p1, p2, color, w=2, dash=10, gap=8):
    x1, y1 = p1; x2, y2 = p2
    L = math.hypot(x2 - x1, y2 - y1)
    n = max(1, int(L / (dash + gap)))
    for i in range(n):
        t0 = i * (dash + gap) / L
        t1 = min(1, t0 + dash / L)
        draw.line([x1 + (x2 - x1) * t0, y1 + (y2 - y1) * t0,
                   x1 + (x2 - x1) * t1, y1 + (y2 - y1) * t1], fill=color, width=w)

def darker(c, f=0.78): return tuple(int(v * f) for v in c)
def lighter(c, f=1.18): return tuple(min(255, int(v * f)) for v in c)

def crown_mini(draw, cx, cy, w, h, color, width=0, fill=True):
    l, r, t, b = cx - w / 2, cx + w / 2, cy - h / 2, cy + h / 2
    dip = b - h * 0.45
    pts = [(l, b), (l, t + h * 0.3), (l + w * 0.19, dip), (cx - w * 0.15, t + h * 0.1),
           (cx, dip - h * 0.05), (cx + w * 0.15, t + h * 0.1), (r - w * 0.19, dip),
           (r, t + h * 0.3), (r, b)]
    band = [l, b + h * 0.10, r, b + h * 0.26]
    if fill:
        draw.polygon(pts, fill=color)
        draw.rectangle(band, fill=color)
    else:
        draw.line(pts + [pts[0]], fill=color, width=width, joint="curve")
        draw.rectangle(band, outline=color, width=width)

def mirror(pts, cx=S / 2):
    return [(2 * cx - x, y) for (x, y) in reversed(pts)]

def sym(right_half, cx=S / 2):
    """right_half from top-center going down the right side; returns closed sym poly."""
    return right_half + mirror(right_half, cx)

# ---------------------------------------------------------------- garments
def render_polo():
    img = studio()
    cx = S / 2
    body = sym([(cx + 10, 300), (cx + 235, 330), (cx + 330, 395), (cx + 300, 585),
                (cx + 262, 570), (cx + 268, 1210), (cx + 10, 1230)])
    sleeveR = [(cx + 235, 330), (cx + 330, 395), (cx + 452, 560), (cx + 372, 646),
               (cx + 262, 570), (cx + 300, 585)]
    sleeveL = mirror(sleeveR)
    mask = poly_mask([body, sleeveR, sleeveL])
    img = drop_shadow(img, mask)
    img = fabric(img, mask, NAVY, seed=21)
    draw = ImageDraw.Draw(img)
    nc = darker(NAVY, 0.6)
    # sleeve cuffs with gold+burgundy tipping
    for sgn in (1, -1):
        p1 = (cx + sgn * 452, 560); p2 = (cx + sgn * 372, 646)
        draw.line([p1, p2], fill=darker(NAVY, 0.7), width=26)
        off = 16
        draw.line([(p1[0] - sgn * off, p1[1] + 10), (p2[0] - sgn * off, p2[1] + 10)], fill=ORO, width=5)
        draw.line([(p1[0] - sgn * off * 2, p1[1] + 22), (p2[0] - sgn * off * 2, p2[1] + 22)], fill=BURDEOS, width=5)
        dashed(draw, (cx + sgn * 262, 570), (cx + sgn * 300, 585), nc)
    # placket + buttons (drawn first so collar overlaps its top)
    draw.rectangle([cx - 26, 400, cx + 26, 640], fill=darker(NAVY, 0.86), outline=nc, width=2)
    for by in (470, 545, 618):
        draw.ellipse([cx - 9, by - 9, cx + 9, by + 9], fill=(200, 196, 186), outline=nc, width=2)
    # classic polo collar: band + two pointed flaps
    cc = darker(NAVY, 0.80)
    draw.chord([cx - 175, 258, cx + 175, 380], 180, 360, fill=cc)
    flapR = [(cx + 8, 318), (cx + 168, 318), (cx + 120, 452), (cx + 30, 418)]
    flapL = [(cx - 8, 318), (cx - 168, 318), (cx - 120, 452), (cx - 30, 418)]
    for flap in (flapR, flapL):
        draw.polygon(flap, fill=cc)
    # tipping along flap lower edges
    for sgn in (1, -1):
        draw.line([(cx + sgn * 162, 330), (cx + sgn * 120, 446)], fill=ORO, width=5)
        draw.line([(cx + sgn * 146, 328), (cx + sgn * 108, 434)], fill=BURDEOS, width=4)
        draw.line([(cx + sgn * 120, 452), (cx + sgn * 32, 420)], fill=ORO, width=5)
    # hem stitching
    dashed(draw, (cx - 262, 1196), (cx + 262, 1196), nc)
    # gold crown embroidery left chest
    crown_mini(draw, cx - 150, 520, 76, 46, ORO_HI, width=6, fill=False)
    # embroidery texture: tiny stitch ticks
    for i in range(-4, 5):
        draw.line([cx - 150 + i * 8, 552, cx - 150 + i * 8, 558], fill=ORO, width=2)
    return img

def render_longsleeve():
    img = studio()
    cx = S / 2
    body = sym([(cx + 10, 315), (cx + 250, 345), (cx + 345, 410), (cx + 315, 600),
                (cx + 278, 585), (cx + 282, 1215), (cx + 10, 1235)])
    slvR = [(cx + 250, 345), (cx + 345, 410), (cx + 420, 700), (cx + 470, 1120),
            (cx + 330, 1140), (cx + 292, 760), (cx + 278, 585), (cx + 315, 600)]
    mask = poly_mask([body, slvR, mirror(slvR)])
    img = drop_shadow(img, mask)
    img = fabric(img, mask, NEGRO, seed=22, edge=0.24)
    draw = ImageDraw.Draw(img)
    oc = (58, 58, 62)
    # neck rib
    draw.arc([cx - 120, 288, cx + 120, 375], 0, 180, fill=oc, width=16)
    # cuffs
    for sgn in (1, -1):
        draw.line([(cx + sgn * 466, 1122), (cx + sgn * 332, 1140)], fill=(48, 48, 52), width=30)
    # seams
    for sgn in (1, -1):
        dashed(draw, (cx + sgn * 278, 585), (cx + sgn * 315, 600), oc)
        dashed(draw, (cx + sgn * 282, 760), (cx + sgn * 296, 1120), oc)
    dashed(draw, (cx - 276, 1200), (cx + 276, 1200), oc)
    # chest print: coordinates lockup (unique concept "Coordenadas")
    text = "40.4168° N"
    text2 = "3.7038° W"
    f1 = F(MONO, 44)
    draw.text((cx, 560), text, font=f1, fill=CREMA, anchor="mm")
    draw.text((cx, 615), text2, font=f1, fill=CREMA, anchor="mm")
    draw.line([cx - 130, 585, cx - 60, 585], fill=ORO, width=3)
    draw.line([cx + 60, 585, cx + 130, 585], fill=ORO, width=3)
    crown_mini(draw, cx, 480, 70, 42, ORO, width=5, fill=False)
    text_v = "STREET ROYALTY HOOD"
    fv = F(SANS_B, 34)
    # vertical print down right sleeve
    tmp = Image.new("RGBA", (620, 60), (0, 0, 0, 0))
    td = ImageDraw.Draw(tmp)
    td.text((0, 30), text_v, font=fv, fill=ORO_HI, anchor="lm")
    tmp = tmp.rotate(-83, expand=True, resample=Image.BICUBIC)
    img.paste(tmp, (int(cx + 320), 470), tmp)
    return img

def render_tank_front():
    img = studio()
    cx = S / 2
    body = sym([(cx + 105, 330), (cx + 130, 340), (cx + 200, 500), (cx + 300, 585),
                (cx + 272, 640), (cx + 282, 1215), (cx + 10, 1235)])
    mask = poly_mask([body])
    img = drop_shadow(img, mask)
    img = fabric(img, mask, NEGRO, seed=23, edge=0.24)
    draw = ImageDraw.Draw(img)
    oc = (58, 58, 62)
    # neckline scoop
    draw.arc([cx - 105, 300, cx + 105, 430], 0, 180, fill=oc, width=12)
    for sgn in (1, -1):
        draw.line([(cx + sgn * 105, 332), (cx + sgn * 130, 342)], fill=oc, width=10)
        dashed(draw, (cx + sgn * 200, 505), (cx + sgn * 296, 588), oc)
    dashed(draw, (cx - 276, 1200), (cx + 276, 1200), oc)
    # small chest mark
    crown_mini(draw, cx - 150, 520, 66, 40, ORO, width=5, fill=False)
    return img

def render_tank_back():
    img = render_tank_front()
    draw = ImageDraw.Draw(img)
    cx = S / 2
    # cover chest mark area is fine (back view identical silhouette); spine print
    draw.rectangle([cx - 190, 470, cx - 106, 575], fill=(24, 24, 27))
    f = F(SANS_B, 52)
    word = "ROYALTY"
    y = 560
    for ch in word:
        draw.text((cx, y), ch, font=f, fill=CREMA, anchor="mm")
        y += 66
    y += 10
    crown_mini(draw, cx, y + 10, 56, 34, ORO, width=4, fill=False)
    draw.text((cx, y + 80), "EST. MMXXVI", font=F(SANS, 26), fill=(150, 145, 135), anchor="mm")
    return img

def render_cropped():
    img = studio()
    cx = S / 2
    body = sym([(cx + 10, 330), (cx + 250, 360), (cx + 350, 430), (cx + 318, 620),
                (cx + 280, 600), (cx + 285, 960), (cx + 10, 975)])
    slvR = [(cx + 250, 360), (cx + 350, 430), (cx + 430, 700), (cx + 470, 1000),
            (cx + 335, 1020), (cx + 295, 780), (cx + 280, 600), (cx + 318, 620)]
    hood = [(cx - 185, 360), (cx - 150, 268), (cx - 70, 222), (cx + 70, 222), (cx + 150, 268),
            (cx + 185, 360), (cx + 120, 400), (cx, 412), (cx - 120, 400)]
    mask = poly_mask([body, slvR, mirror(slvR), hood])
    img = drop_shadow(img, mask)
    img = fabric(img, mask, CREMA, grad=0.13, seed=24, edge=0.14)
    draw = ImageDraw.Draw(img)
    oc = (188, 178, 158)
    # hood: rolled rim + shaded interior opening + center seam
    draw.ellipse([cx - 152, 268, cx + 152, 396], fill=(206, 196, 176))
    draw.ellipse([cx - 118, 286, cx + 118, 384], fill=(174, 164, 145))
    draw.arc([cx - 152, 268, cx + 152, 396], 0, 360, fill=(192, 182, 162), width=6)
    draw.line([(cx, 226), (cx, 268)], fill=(200, 190, 170), width=4)
    # drawcords
    for sgn in (1, -1):
        draw.line([(cx + sgn * 60, 390), (cx + sgn * 66, 470)], fill=(196, 186, 166), width=8)
        draw.ellipse([cx + sgn * 66 - 7, 470 - 4, cx + sgn * 66 + 7, 470 + 10], fill=darker(CREMA, 0.7))
    # ribbed hem band + cuffs
    draw.rectangle([cx - 285, 930, cx + 285, 985], fill=darker(CREMA, 0.9))
    for x in range(int(cx - 280), int(cx + 280), 12):
        draw.line([(x, 934), (x, 981)], fill=darker(CREMA, 0.82), width=2)
    for sgn in (1, -1):
        draw.line([(cx + sgn * 466, 1002), (cx + sgn * 337, 1020)], fill=darker(CREMA, 0.88), width=30)
    for sgn in (1, -1):
        dashed(draw, (cx + sgn * 280, 600), (cx + sgn * 318, 620), oc)
    # print: laurel wreath + crown tonal burdeos (unique "Láurea")
    lc = BURDEOS
    ccx, ccy, R = cx, 640, 155
    for sgn in (1, -1):
        for i in range(9):
            phi = math.radians(25 + i * 17.5)  # side arc, top → bottom
            lx = ccx + sgn * R * math.sin(phi)
            ly = ccy - R * math.cos(phi)
            leaf = Image.new("RGBA", (44, 17), (0, 0, 0, 0))
            ld = ImageDraw.Draw(leaf)
            ld.ellipse([1, 1, 43, 16], fill=lc + (255,))
            dx = sgn * R * math.cos(phi); dy = R * math.sin(phi)
            rot = -math.degrees(math.atan2(dy, dx))
            leaf = leaf.rotate(rot, expand=True, resample=Image.BICUBIC)
            img.paste(leaf, (int(lx - leaf.width / 2), int(ly - leaf.height / 2)), leaf)
    draw = ImageDraw.Draw(img)
    crown_mini(draw, ccx, ccy - 34, 104, 64, lc, width=8, fill=False)
    draw.text((ccx, ccy + 52), "HERITAGE", font=F(SANS_B, 32), fill=lc, anchor="mm")
    draw.text((ccx, ccy + 96), "MMXXVI", font=F(SANS, 22), fill=(170, 120, 118), anchor="mm")
    return img

def render_leggings():
    img = studio()
    cx = S / 2
    waist_y, crotch_y, ankle_y = 260, 610, 1400
    legR = [(cx + 10, crotch_y - 40), (cx + 232, 300), (cx + 232, waist_y + 130),
            (cx + 205, 900), (cx + 175, ankle_y), (cx + 62, ankle_y), (cx + 60, 900), (cx + 10, crotch_y)]
    # build as: waist block + two legs
    waist = [(cx - 232, waist_y), (cx + 232, waist_y), (cx + 232, waist_y + 150),
             (cx - 232, waist_y + 150)]
    legR = [(cx + 232, waist_y + 140), (cx + 210, 900), (cx + 178, ankle_y),
            (cx + 58, ankle_y), (cx + 55, 880), (cx + 8, crotch_y), (cx + 8, waist_y + 140)]
    mask = poly_mask([waist, legR, mirror(legR)])
    img = drop_shadow(img, mask)
    img = fabric(img, mask, NEGRO, seed=25, edge=0.26, grad=0.08)
    draw = ImageDraw.Draw(img)
    oc = (58, 58, 62)
    # high waistband
    draw.rectangle([cx - 232, waist_y, cx + 232, waist_y + 78], fill=(38, 38, 42))
    dashed(draw, (cx - 232, waist_y + 80), (cx + 232, waist_y + 80), oc)
    # center seam
    dashed(draw, (cx, waist_y + 150), (cx, crotch_y), oc)
    for sgn in (1, -1):
        dashed(draw, (cx + sgn * 8, crotch_y), (cx + sgn * 56, 880), oc)
        dashed(draw, (cx + sgn * 56, 880), (cx + sgn * 60, ankle_y - 6), oc)
    # gold monogram pinstripe down right leg (unique "Pinstripe SRH")
    f = F(SANS_B, 26)
    x0, x1 = cx + 218, cx + 118
    n = 14
    for i in range(n):
        t = i / (n - 1)
        y = waist_y + 165 + t * (ankle_y - waist_y - 190)
        x = cx + 218 - t * 52
        tmp = Image.new("RGBA", (80, 34), (0, 0, 0, 0))
        td = ImageDraw.Draw(tmp)
        td.text((40, 17), "SRH", font=f, fill=(ORO_HI + (255,)), anchor="mm")
        tmp = tmp.rotate(87, expand=True, resample=Image.BICUBIC)
        img.paste(tmp, (int(x - 17), int(y - 40)), tmp)
    draw = ImageDraw.Draw(img)
    # waistband crown
    crown_mini(draw, cx, waist_y + 40, 54, 30, ORO, width=4, fill=False)
    return img

def render_socks():
    img = studio()
    def sock(rot):
        layer = Image.new("RGBA", (720, 900), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        # one-piece sock silhouette: cuff top, leg, round heel, foot to rounded toe
        outline_pts = [(250, 70), (450, 70), (450, 540), (462, 620), (440, 700),
                       (380, 748), (240, 760), (140, 745), (78, 690), (62, 615),
                       (92, 560), (170, 535), (232, 528), (250, 470)]
        d.polygon(outline_pts, fill=BLANCO + (255,))
        # smooth corners
        d.ellipse([62, 560, 200, 758], fill=BLANCO + (255,))      # toe round
        d.ellipse([370, 590, 470, 756], fill=BLANCO + (255,))     # heel round
        d.rectangle([150, 560, 420, 758], fill=BLANCO + (255,))   # foot body
        # heel patch (burgundy) — quarter circle at back of foot
        d.pieslice([352, 560, 486, 720], 300, 80, fill=(226, 222, 214, 255))
        # toe patch
        d.pieslice([40, 560, 190, 760], 90, 270, fill=BURDEOS + (255,))
        # ribbed cuff
        d.rectangle([250, 70, 450, 160], fill=(238, 235, 229, 255))
        for x in range(258, 450, 14):
            d.line([(x, 76), (x, 156)], fill=(216, 212, 204, 255), width=3)
        # stripes
        d.rectangle([250, 180, 450, 204], fill=BURDEOS + (255,))
        d.rectangle([250, 218, 450, 234], fill=ORO + (255,))
        # crown + SRH at calf
        crown_mini(d, 350, 310, 84, 52, BURDEOS, fill=True)
        d.text((350, 385), "SRH", font=F(SANS_B, 40), fill=ORO + (255,), anchor="mm")
        return layer.rotate(rot, expand=True, resample=Image.BICUBIC)
    positions = [(sock(10), (700, 320)), (sock(-6), (330, 300))]
    for layer, pos in positions:
        sh = Image.new("L", (S, S), 0)
        sh.paste(layer.split()[3], (pos[0], pos[1] + 26))
        sh = sh.filter(ImageFilter.GaussianBlur(24)).point(lambda v: v * 75 // 255)
        img.paste(Image.new("RGB", (S, S), (72, 70, 66)), (0, 0), sh)
        img.paste(layer, pos, layer)
    return img

def render_slipon():
    img = studio()
    LW, LH = 1200, 760
    shoe = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    d = ImageDraw.Draw(shoe)
    # sole with foxing stripe
    d.rounded_rectangle([56, 600, 1150, 694], radius=46, fill=(250, 248, 244, 255))
    d.rounded_rectangle([56, 600, 1150, 634], radius=16, fill=(238, 235, 229, 255))
    d.line([78, 654, 1128, 654], fill=(225, 222, 216, 255), width=3)
    # upper: toe spring, vamp, throat, gore, heel counter
    upper = [(150, 612), (126, 560), (136, 505), (200, 468), (300, 440), (420, 424),
             (540, 416), (612, 430), (648, 414), (760, 396), (900, 382), (1010, 394),
             (1080, 424), (1112, 488), (1120, 612)]
    d.polygon(upper, fill=(32, 32, 36, 255))
    up_col = (32, 32, 36, 255)
    # collar opening shadow (suggests footbed)
    d.polygon([(660, 416), (1000, 394), (1044, 408), (668, 428)], fill=(14, 14, 16, 255))
    d.line([(648, 416), (1010, 394)], fill=(58, 58, 64, 255), width=5)
    # elastic gore
    gore = [(600, 432), (664, 418), (700, 502), (632, 512)]
    d.polygon(gore, fill=(74, 74, 82, 255))
    for i in range(4):
        d.line([(614 + i * 17, 428), (650 + i * 16, 506)], fill=(50, 50, 56, 255), width=3)
    # toe cap stitch
    d.arc([140, 500, 400, 700], 215, 320, fill=(76, 76, 84, 255), width=3)
    # all-over micro crown pattern (unique "Micro-Corona")
    pat_mask = Image.new("L", (LW, LH), 0)
    pd = ImageDraw.Draw(pat_mask)
    pd.polygon(upper, fill=255)
    pd.polygon(gore, fill=0)
    pd.polygon([(660, 416), (1000, 394), (1044, 408), (668, 428)], fill=0)
    pat = Image.new("RGBA", (LW, LH), (0, 0, 0, 0))
    pdd = ImageDraw.Draw(pat)
    step = 74
    for row, y in enumerate(range(430, 600, 42)):
        off = (row % 2) * step // 2
        for x in range(70 + off, 1140, step):
            crown_mini(pdd, x, y, 30, 18, (196, 162, 84, 255), width=3, fill=False)
    shoe.paste(pat, (0, 0), Image.composite(pat.split()[3], Image.new("L", (LW, LH), 0), pat_mask))
    d = ImageDraw.Draw(shoe)
    # heel tab
    d.rectangle([1030, 430, 1086, 480], fill=BURDEOS + (255,))
    d.text((1058, 455), "SR", font=F(SERIF_B, 26), fill=(230, 205, 190, 255), anchor="mm")
    # place with corrected shadow
    mask_full = shoe.split()[3]
    sh = Image.new("L", (S, S), 0)
    sh.paste(mask_full, (200, 452))
    sh = sh.filter(ImageFilter.GaussianBlur(26)).point(lambda v: v * 85 // 255)
    img.paste(Image.new("RGB", (S, S), (66, 64, 60)), (0, 0), sh)
    img.paste(shoe, (200, 420), shoe)
    return img

def brand_tag(img, label):
    """small brand caption bottom-left like a catalog shot"""
    draw = ImageDraw.Draw(img)
    draw.text((70, S - 96), "STREET ROYALTY HOOD", font=F(SANS_B, 26), fill=(120, 116, 110))
    draw.text((70, S - 60), label, font=F(SANS, 24), fill=(150, 146, 140))
    return img

def print_card(title, subtitle, render_fn, bg=NEGRO):
    """close-up card of the print artwork itself (second image)."""
    img = Image.new("RGB", (S, S), bg)
    render_fn(img)
    draw = ImageDraw.Draw(img)
    draw.text((S / 2, S - 170), title, font=F(SANS_B, 40), fill=CREMA, anchor="mm")
    draw.text((S / 2, S - 115), subtitle, font=F(SANS, 26), fill=(150, 144, 132), anchor="mm")
    return img

if __name__ == "__main__":
    jobs = {
        "heritage-polo": (render_polo, "Polo Piqué Tipping — Navy"),
        "heritage-manga-larga": (render_longsleeve, "Manga Larga Coordenadas — Negro"),
        "heritage-tank-front": (render_tank_front, "Tirantes Spine — Negro (frontal)"),
        "heritage-tank-back": (render_tank_back, "Tirantes Spine — Negro (espalda)"),
        "heritage-cropped": (render_cropped, "Cropped Hoodie Láurea — Crema"),
        "heritage-leggings": (render_leggings, "Leggings Pinstripe SRH — Negro"),
        "heritage-calcetines": (render_socks, "Calcetines Crown Stripe — Blanco"),
        "heritage-slipon": (render_slipon, "Slip-On Micro-Corona — Negro"),
    }
    for name, (fn, label) in jobs.items():
        im = brand_tag(fn(), label)
        im.save(f"{OUT}/{name}.jpg", quality=92)
        print("done", name)

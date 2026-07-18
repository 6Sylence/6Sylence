#!/usr/bin/env python3
# Cápsula Laurel — Victoria Real: 6 print files for Street Royalty Hood
# Tee / sweat / hoodie DTG prints + AOP patterns for hi-tops, athletic shoes, socks.
import math, os, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

SS = 2  # supersample factor

NEGRO    = (13, 13, 15)
CREMA    = (242, 234, 217)
ORO_HI   = (236, 205, 130)
ORO      = (206, 166, 88)
ORO_DK   = (162, 122, 50)
BURDEOS  = (116, 38, 50)
VERDE    = (36, 56, 44)
VERDE_HI = (96, 124, 96)
MARFIL   = (243, 238, 226)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SERIF   = "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def gold_gradient(size, top=ORO_HI, bottom=ORO_DK):
    w, h = size
    g = Image.new("RGB", (1, h))
    px = g.load()
    for y in range(h):
        t = y / max(1, h - 1)
        px[0, y] = tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3))
    return g.resize((w, h))

def paste_gradient(canvas, mask, top=ORO_HI, bottom=ORO_DK):
    grad = gold_gradient(canvas.size, top, bottom)
    canvas.paste(grad, (0, 0), mask)

# ---------------------------------------------------------------- leaves
def leaf_poly(x, y, ang, L, W):
    """Almond leaf polygon centred on its base at (x,y), pointing along ang."""
    pts = []
    n = 16
    for i in range(n + 1):           # one side
        t = i / n
        along = t * L
        wide = W * math.sin(math.pi * t) ** 0.85
        pts.append((along, -wide / 2))
    for i in range(n + 1):           # back the other side
        t = 1 - i / n
        along = t * L
        wide = W * math.sin(math.pi * t) ** 0.85
        pts.append((along, wide / 2))
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + a * ca - b * sa, y + a * sa + b * ca) for a, b in pts]

def leaf_vein(x, y, ang, L):
    ca, sa = math.cos(ang), math.sin(ang)
    return [(x + 0.12 * L * ca, y + 0.12 * L * sa),
            (x + 0.82 * L * ca, y + 0.82 * L * sa)]

def bezier(p0, p1, p2, t):
    x = (1 - t) ** 2 * p0[0] + 2 * (1 - t) * t * p1[0] + t ** 2 * p2[0]
    y = (1 - t) ** 2 * p0[1] + 2 * (1 - t) * t * p1[1] + t ** 2 * p2[1]
    return x, y

def draw_branch(mask_d, vein_d, p0, p1, p2, n_pairs=9, L0=150, W0=62,
                stem_w=9, spread=0.62, taper=0.42, berries=None, flip=1):
    """Laurel branch along a quadratic bezier on a greyscale mask.
    berries: optional list collecting (x, y, r) berry circles."""
    # stem
    pts = [bezier(p0, p1, p2, t / 60) for t in range(61)]
    mask_d.line(pts, fill=255, width=stem_w)
    for k in range(n_pairs):
        t = 0.08 + 0.9 * k / max(1, n_pairs - 1)
        x, y = bezier(p0, p1, p2, t)
        # tangent
        x2, y2 = bezier(p0, p1, p2, min(1, t + 0.02))
        ang = math.atan2(y2 - y, x2 - x)
        fade = 1 - taper * (k / max(1, n_pairs - 1))
        L, W = L0 * fade, W0 * fade
        for side in (-1, 1):
            a = ang + side * flip * spread
            mask_d.polygon(leaf_poly(x, y, a, L, W), fill=255)
            v = leaf_vein(x, y, a, L)
            vein_d.line(v, fill=255, width=max(3, int(W * 0.09)))
        if berries is not None and k % 2 == 1:
            bx, by = bezier(p0, p1, p2, min(1, t + 0.045))
            nx, ny = math.cos(ang - flip * math.pi / 2), math.sin(ang - flip * math.pi / 2)
            off = W0 * 0.55 * fade
            berries.append((bx + nx * off, by + ny * off, W0 * 0.26 * fade))
    return pts

# ---------------------------------------------------------------- crown
def crown_poly(cx, cy, w, h):
    l, r, b, t = cx - w / 2, cx + w / 2, cy + h / 2, cy - h / 2
    dip = b - h * 0.42
    return [(l, b), (l, t + h * 0.30), (l + w * 0.185, dip),
            (cx - w * 0.155, t + h * 0.12), (cx, dip - h * 0.02),
            (cx + w * 0.155, t + h * 0.12), (r - w * 0.185, dip),
            (r, t + h * 0.30), (r, b)]

def draw_crown(d, cx, cy, w, h, fill, band=True, jewels=None):
    d.polygon(crown_poly(cx, cy, w, h), fill=fill)
    if band:
        bh = h * 0.16
        d.rectangle([cx - w / 2, cy + h / 2 + h * 0.06,
                     cx + w / 2, cy + h / 2 + h * 0.06 + bh], fill=fill)
    if jewels:
        r = w * 0.032
        for jx, jy in [(cx - w * 0.5, cy - h * 0.20), (cx, cy - h * 0.40),
                       (cx + w * 0.5, cy - h * 0.20)]:
            d.ellipse([jx - r, jy - r - h * 0.16, jx + r, jy + r - h * 0.16], fill=jewels)

# ---------------------------------------------------------------- text helpers
def tracked(d, xy, text, font, fill, tracking=0.0, anchor="mm"):
    """Letterspaced text centred on xy (anchor mm) or left (lm)."""
    widths = [d.textlength(c, font=font) for c in text]
    tr = tracking * font.size
    total = sum(widths) + tr * (len(text) - 1)
    x, y = xy
    if anchor == "mm":
        x -= total / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill, anchor="lm")
        x += w + tr

def arc_text(img_d, cx, cy, radius, text, font, fill, a0, a1, tracking=1.0):
    """Draw text along an arc (angles in degrees, 0=right, CCW negative up)."""
    widths = [img_d.textlength(c, font=font) for c in text]
    tr = tracking * font.size * 0.1
    total = sum(widths) + tr * (len(text) - 1)
    arc_len = math.radians(abs(a1 - a0)) * radius
    # scale spacing to requested arc
    scale = min(1.0, arc_len / total) if total > 0 else 1
    ang = math.radians(a0)
    direction = 1 if a1 > a0 else -1
    for c, w in zip(text, widths):
        step = (w + tr) * scale / radius * direction
        mid = ang + step / 2
        x = cx + radius * math.cos(mid)
        y = cy + radius * math.sin(mid)
        deg = math.degrees(mid) + (90 if direction > 0 else -90)
        tile = Image.new("RGBA", (int(w) + 8, font.size + 12), (0, 0, 0, 0))
        td = ImageDraw.Draw(tile)
        td.text((4, 4), c, font=font, fill=fill)
        tile = tile.rotate(-deg, expand=True, resample=Image.BICUBIC)
        # paste centred
        px, py = int(x - tile.width / 2), int(y - tile.height / 2)
        base = img_d._image
        base.paste(tile, (px, py), tile)
        ang += step

def grain(img, blend=0.05, seed=11):
    noise = Image.effect_noise(img.size, 14).convert("L")
    n = Image.merge("RGB", (noise, noise, noise))
    return Image.blend(img.convert("RGB"), n, blend)

# ================================================================ 1. TEE
def tee():
    W, H = 2400 * SS, 3200 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gold_m = Image.new("L", (W, H), 0); gm = ImageDraw.Draw(gold_m)
    vein_m = Image.new("L", (W, H), 0); vm = ImageDraw.Draw(vein_m)
    crema_m = Image.new("L", (W, H), 0); cm = ImageDraw.Draw(crema_m)
    burd_m = Image.new("L", (W, H), 0); bm = ImageDraw.Draw(burd_m)

    cx, cy = W / 2, H * 0.38
    R = W * 0.355
    berries = []
    # two mirrored branches: start at bottom centre, sweep up the sides
    for side in (-1, 1):
        p0 = (cx + side * R * 0.28, cy + R * 1.02)
        p1 = (cx + side * R * 1.42, cy + R * 0.72)
        p2 = (cx + side * R * 0.42, cy - R * 1.02)
        draw_branch(gm, vm, p0, p1, p2, n_pairs=11,
                    L0=R * 0.205, W0=R * 0.082, stem_w=int(R * 0.024),
                    spread=0.66, taper=0.46, berries=berries, flip=side)
    for bx, by, r in berries:
        cm.ellipse([bx - r, by - r, bx + r, by + r], fill=255)

    # crown in the middle
    ccy = cy - R * 0.36
    cw, ch = R * 0.66, R * 0.42
    draw_crown(cm, cx, ccy, cw, ch, 255, jewels=None)
    jr = cw * 0.042
    for jx, jy in [(cx - cw * 0.5, ccy - ch * 0.46),
                   (cx, ccy - ch * 0.66),
                   (cx + cw * 0.5, ccy - ch * 0.46)]:
        bm.ellipse([jx - jr, jy - jr, jx + jr, jy + jr], fill=255)

    # typography inside wreath
    d = ImageDraw.Draw(img)
    tmp = ImageDraw.Draw(Image.new("L", (10, 10)))
    f_disp = F(SERIF_B, int(R * 0.225))
    f_sub  = F(SANS_B, int(R * 0.058))
    f_bot  = F(SANS_B, int(R * 0.085))
    # measure with a real draw context
    md = ImageDraw.Draw(img)
    tracked(md, (cx, cy + R * 0.16), "LAUREL", f_disp, CREMA + (255,), tracking=0.10)
    tracked(md, (cx, cy + R * 0.42), "REAL", f_disp, CREMA + (255,), tracking=0.30)
    tracked(md, (cx, cy + R * 0.64), "VICTORIA · EST. MMXXVI", f_sub, ORO + (255,), tracking=0.26)
    # bottom lockup outside wreath
    tracked(md, (cx, cy + R * 1.42), "STREET ROYALTY HOOD", f_bot, ORO + (255,), tracking=0.42)
    rule_y = cy + R * 1.28
    md.line([cx - R * 0.50, rule_y, cx - R * 0.10, rule_y], fill=ORO + (255,), width=SS * 3)
    md.line([cx + R * 0.10, rule_y, cx + R * 0.50, rule_y], fill=ORO + (255,), width=SS * 3)
    dr = R * 0.028
    md.ellipse([cx - dr, rule_y - dr, cx + dr, rule_y + dr], fill=BURDEOS + (255,))

    # composite gold with gradient, veins carved in darker gold, crema, burdeos
    gold_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_gradient(gold_layer, gold_m)
    gold_rgba = Image.composite(gold_layer, Image.new("RGBA", (W, H), (0, 0, 0, 0)),
                                gold_m)
    img_base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    img_base.paste(gold_rgba, (0, 0), gold_m)
    # veins: darker gold cut into leaves
    vein_col = Image.new("RGBA", (W, H), (120, 88, 34, 255))
    img_base.paste(vein_col, (0, 0), vein_m)
    img_base.paste(Image.new("RGBA", (W, H), CREMA + (255,)), (0, 0), crema_m)
    img_base.paste(Image.new("RGBA", (W, H), BURDEOS + (255,)), (0, 0), burd_m)
    out = Image.alpha_composite(img_base, img)
    out = out.resize((2400, 3200), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_tee_print.png"))

# ================================================================ 2. SWEAT
def sweat():
    W, H = 2400 * SS, 3000 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d._image = img
    cx = W / 2
    # arched STREET ROYALTY
    f_arc = F(SERIF_B, int(W * 0.062))
    arc_r = W * 0.72
    arc_cy = H * 0.245 + arc_r
    arc_text(d, cx, arc_cy, arc_r, "STREET ROYALTY", f_arc, CREMA + (255,),
             a0=-121, a1=-59, tracking=1.4)
    # big HOOD
    f_big = F(SERIF_B, int(W * 0.145))
    tracked(d, (cx, H * 0.435), "HOOD", f_big, CREMA + (255,), tracking=0.30)
    # crossed branches under
    gold_m = Image.new("L", (W, H), 0); gm = ImageDraw.Draw(gold_m)
    vein_m = Image.new("L", (W, H), 0); vm = ImageDraw.Draw(vein_m)
    crema_m = Image.new("L", (W, H), 0); cm = ImageDraw.Draw(crema_m)
    by0 = H * 0.615
    R = W * 0.27
    berries = []
    for side in (-1, 1):
        p0 = (cx + side * R * 0.26, by0 + R * 0.30)
        p1 = (cx + side * R * 0.85, by0 + R * 0.24)
        p2 = (cx + side * R * 1.20, by0 - R * 0.38)
        draw_branch(gm, vm, p0, p1, p2, n_pairs=8,
                    L0=R * 0.20, W0=R * 0.085, stem_w=int(R * 0.030),
                    spread=0.62, taper=0.44, berries=berries, flip=side)
    for bx, byy, r in berries:
        cm.ellipse([bx - r, byy - r, bx + r, byy + r], fill=255)
    # small crown cradled between branch bases
    draw_crown(cm, cx, by0 + R * 0.02, R * 0.34, R * 0.22, 255)
    f_est = F(SANS_B, int(W * 0.026))
    tracked(d, (cx, by0 + R * 0.62), "VICTORIA REAL · EST. MMXXVI", f_est,
            ORO_HI + (255,), tracking=0.38)

    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_gradient(gl, gold_m, top=(238, 208, 138), bottom=(186, 144, 66))
    base.paste(gl, (0, 0), gold_m)
    base.paste(Image.new("RGBA", (W, H), (122, 92, 40, 255)), (0, 0), vein_m)
    base.paste(Image.new("RGBA", (W, H), CREMA + (255,)), (0, 0), crema_m)
    out = Image.alpha_composite(base, img)
    out = out.resize((2400, 3000), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_sweat_print.png"))

# ================================================================ 3. HOODIE
def hoodie():
    W, H = 1800 * SS, 1800 * SS
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img); d._image = img
    cx, cy = W / 2, H * 0.46
    R = W * 0.36
    gold_m = Image.new("L", (W, H), 0); gm = ImageDraw.Draw(gold_m)
    vein_m = Image.new("L", (W, H), 0); vm = ImageDraw.Draw(vein_m)
    crema_m = Image.new("L", (W, H), 0); cm = ImageDraw.Draw(crema_m)
    burd_m = Image.new("L", (W, H), 0); bm = ImageDraw.Draw(burd_m)
    berries = []
    # closed-ish vertical wreath
    for side in (-1, 1):
        p0 = (cx + side * R * 0.34, cy + R * 0.92)
        p1 = (cx + side * R * 1.30, cy + R * 0.30)
        p2 = (cx + side * R * 0.30, cy - R * 0.96)
        draw_branch(gm, vm, p0, p1, p2, n_pairs=10,
                    L0=R * 0.20, W0=R * 0.082, stem_w=int(R * 0.026),
                    spread=0.64, taper=0.46, berries=berries, flip=side)
    for bx, by, r in berries:
        cm.ellipse([bx - r, by - r, bx + r, by + r], fill=255)
    # crown on top
    ccy = cy - R * 0.56
    ch = R * 0.32
    draw_crown(cm, cx, ccy, R * 0.50, ch, 255)
    jr = R * 0.024
    for jx, jy in [(cx - R * 0.25, ccy - ch * 0.44),
                   (cx, ccy - ch * 0.64),
                   (cx + R * 0.25, ccy - ch * 0.44)]:
        bm.ellipse([jx - jr, jy - jr, jx + jr, jy + jr], fill=255)
    # monogram
    f_mono = F(SERIF_B, int(R * 0.52))
    tracked(d, (cx, cy + R * 0.14), "SRH", f_mono, CREMA + (255,), tracking=0.10)
    # ribbon banner
    ry = cy + R * 0.60
    rw, rh = R * 0.88, R * 0.19
    # side tails behind the band, slightly lower, with swallow-tail notch
    for side in (-1, 1):
        x0 = cx + side * (rw / 2 - rh * 0.10)
        ty = ry + rh * 0.22
        tail = [(x0, ty - rh / 2), (x0 + side * rh * 1.15, ty - rh / 2),
                (x0 + side * (rh * 1.15 - rh * 0.50), ty),
                (x0 + side * rh * 1.15, ty + rh / 2),
                (x0, ty + rh / 2)]
        d.polygon(tail, fill=(86, 26, 36, 255))
    # centre band
    d.rectangle([cx - rw / 2, ry - rh / 2, cx + rw / 2, ry + rh / 2],
                fill=BURDEOS + (255,))
    f_ban = F(SANS_B, int(rh * 0.50))
    tracked(d, (cx, ry + rh * 0.02), "STAY ROYAL", f_ban, CREMA + (255,), tracking=0.32)

    base = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gl = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    paste_gradient(gl, gold_m)
    base.paste(gl, (0, 0), gold_m)
    base.paste(Image.new("RGBA", (W, H), (118, 86, 34, 255)), (0, 0), vein_m)
    base.paste(Image.new("RGBA", (W, H), CREMA + (255,)), (0, 0), crema_m)
    base.paste(Image.new("RGBA", (W, H), BURDEOS + (255,)), (0, 0), burd_m)
    out = Image.alpha_composite(base, img)
    out = out.resize((1800, 1800), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_hoodie_print.png"))

# ================================================================ sprig motif
def sprig_tile(size, stem_col, leaf_top, leaf_bot, vein_col, n_pairs=5):
    """A small laurel sprig on transparent tile, pointing up."""
    s = size
    tile = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    m = Image.new("L", (s, s), 0); md = ImageDraw.Draw(m)
    vm = Image.new("L", (s, s), 0); vd = ImageDraw.Draw(vm)
    p0 = (s * 0.5, s * 0.92)
    p1 = (s * 0.56, s * 0.5)
    p2 = (s * 0.46, s * 0.10)
    draw_branch(md, vd, p0, p1, p2, n_pairs=n_pairs,
                L0=s * 0.22, W0=s * 0.10, stem_w=max(3, int(s * 0.028)),
                spread=0.72, taper=0.40)
    gl = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    paste_gradient(gl, m, top=leaf_top, bottom=leaf_bot)
    tile.paste(gl, (0, 0), m)
    tile.paste(Image.new("RGBA", (s, s), vein_col + (255,)), (0, 0), vm)
    return tile

def crown_tile(size, col, jewel=None):
    s = size
    tile = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    draw_crown(d, s / 2, s / 2, s * 0.72, s * 0.44, col + (255,))
    if jewel:
        jr = s * 0.035
        for jx, jy in [(s / 2 - s * 0.36, s / 2 - s * 0.135),
                       (s / 2, s / 2 - s * 0.20),
                       (s / 2 + s * 0.36, s / 2 - s * 0.135)]:
            d.ellipse([jx - jr, jy - jr, jx + jr, jy + jr], fill=jewel + (255,))
    return tile

def paste_wrapped(canvas, tile, x, y):
    """Paste with wraparound so the pattern tiles seamlessly."""
    W, H = canvas.size
    tw, th = tile.size
    for dx in (-W, 0, W):
        for dy in (-H, 0, H):
            px, py = int(x + dx), int(y + dy)
            if -tw < px < W and -th < py < H:
                canvas.paste(tile, (px, py), tile)

def scatter_pattern(W, H, bg, motifs, cols, rows, jitter=0.16, seed=7,
                    dotgrid=None):
    """Half-drop scatter of rotated motifs. motifs: list of (tile_img, weight)."""
    rnd = random.Random(seed)
    img = Image.new("RGBA", (W, H), bg + (255,))
    if dotgrid:
        dd = ImageDraw.Draw(img)
        step, r, col = dotgrid
        yy = 0
        while yy < H:
            xx = (yy // step % 2) * step // 2
            while xx < W:
                dd.ellipse([xx - r, yy - r, xx + r, yy + r], fill=col + (255,))
                xx += step
            yy += step
    cw, chh = W / cols, H / rows
    tiles = [m[0] for m in motifs]
    weights = [m[1] for m in motifs]
    rots = [m[2] if len(m) > 2 else (-30, -15, 0, 15, 30, 180, 160, 200)
            for m in motifs]
    for j in range(rows):
        for i in range(cols):
            x = (i + 0.5) * cw + (0.5 * cw if j % 2 else 0)
            y = (j + 0.5) * chh
            x += rnd.uniform(-jitter, jitter) * cw
            y += rnd.uniform(-jitter, jitter) * chh
            idx = rnd.choices(range(len(tiles)), weights=weights)[0]
            t = tiles[idx]
            ang = rnd.choice(list(rots[idx])) + rnd.uniform(-8, 8)
            rt = t.rotate(ang, expand=True, resample=Image.BICUBIC)
            paste_wrapped(img, rt, x - rt.width / 2, y - rt.height / 2)
    return img

# ================================================================ 4. HI-TOPS
def hitops():
    W = H = 2400 * SS
    s = int(430 * SS)
    sp_gold = sprig_tile(s, ORO, ORO_HI, ORO_DK, (122, 90, 38))
    sp_verde = sprig_tile(s, VERDE_HI, (128, 152, 124), (70, 96, 72), (46, 66, 50))
    cr = crown_tile(int(s * 0.42), CREMA, jewel=BURDEOS)
    img = scatter_pattern(W, H, NEGRO,
                          [(sp_gold, 5), (sp_verde, 2), (cr, 2, (-18, -9, 0, 9, 18))],
                          cols=6, rows=6, jitter=0.14, seed=17,
                          dotgrid=(int(120 * SS), int(2.2 * SS), (38, 38, 42)))
    out = grain(img, 0.035).resize((2400, 2400), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_hitops_print.png"))

# ================================================================ 5. ATHLETIC
def athletic():
    W, H = 1950 * SS, 3300 * SS
    s = int(400 * SS)
    sp_verde = sprig_tile(s, VERDE, (86, 112, 88), (40, 62, 48), (28, 44, 34))
    sp_gold = sprig_tile(s, ORO, (222, 186, 108), (176, 134, 58), (130, 96, 42))
    cr = crown_tile(int(s * 0.40), ORO_DK, jewel=BURDEOS)
    img = scatter_pattern(W, H, MARFIL,
                          [(sp_verde, 5), (sp_gold, 3), (cr, 2, (-18, -9, 0, 9, 18))],
                          cols=5, rows=9, jitter=0.13, seed=23,
                          dotgrid=(int(110 * SS), int(2.0 * SS), (226, 218, 202)))
    out = grain(img, 0.03).resize((1950, 3300), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_athletic_print.png"))

# ================================================================ 6. SOCKS
def socks():
    W, H = 1400 * SS, 2400 * SS
    s = int(330 * SS)
    sp_gold = sprig_tile(s, ORO, ORO_HI, ORO_DK, (122, 90, 38))
    cr = crown_tile(int(s * 0.44), CREMA, jewel=BURDEOS)
    img = scatter_pattern(W, H, NEGRO,
                          [(sp_gold, 5), (cr, 2, (-18, -9, 0, 9, 18))],
                          cols=4, rows=8, jitter=0.12, seed=31,
                          dotgrid=(int(100 * SS), int(2.0 * SS), (38, 38, 42)))
    out = grain(img, 0.035).resize((1400, 2400), Image.LANCZOS)
    out.save(os.path.join(OUT, "lrl_socks_print.png"))

if __name__ == "__main__":
    tee(); print("tee ok")
    sweat(); print("sweat ok")
    hoodie(); print("hoodie ok")
    hitops(); print("hitops ok")
    athletic(); print("athletic ok")
    socks(); print("socks ok")

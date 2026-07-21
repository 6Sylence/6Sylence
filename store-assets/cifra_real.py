#!/usr/bin/env python3
# Cifra Real — Royal Cipher capsule for Street Royalty Hood
# Fresh motif (not used before): interlaced mirrored SR monogram = a monarch's cipher,
# minimal crown + fine laurel arc. Cream line-art on transparent, print-ready DTG file.
import math, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs")
os.makedirs(OUT, exist_ok=True)

CREMA   = (239, 231, 214, 255)
CREMA_S = (239, 231, 214, 140)   # secondary, softer stroke
NEGRO   = (12, 12, 14)

SERIF_B = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
SANS    = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SANS_B  = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

def F(p, s): return ImageFont.truetype(p, s)

def text_tracked(draw, xy, text, font, fill, tracking=0, center=True):
    x, y = xy
    widths = [draw.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    if center: x -= total / 2
    for c, cw in zip(text, widths):
        draw.text((x, y), c, font=font, fill=fill)
        x += cw + tracking
    return total

def crown_line(draw, cx, cy, w, h, fill, width):
    """Minimal 3-point crown outline."""
    l = cx - w/2; r = cx + w/2; b = cy + h/2; t = cy - h/2
    dip = b - h*0.34
    pts = [(l, b), (l, b - h*0.30), (l + w*0.22, dip),
           (cx - w*0.19, t + h*0.10), (cx, dip - h*0.05),
           (cx + w*0.19, t + h*0.10), (r - w*0.22, dip),
           (r, b - h*0.30), (r, b)]
    draw.line(pts, fill=fill, width=width, joint="curve")
    draw.line([(l, b), (r, b)], fill=fill, width=width)
    # jewels
    for jx in (cx - w*0.28, cx, cx + w*0.28):
        rr = width*1.4
        draw.ellipse([jx-rr, t + h*0.02 - rr, jx+rr, t + h*0.02 + rr], outline=fill, width=max(2,width-1))

def laurel_branch(draw, cx, cy, radius, a_start, a_end, fill, leaves=8, leaf=44, width=5):
    """One laurel branch following the ring; leaves point outward along the arc.
    Angles in degrees, PIL convention (0=east, +=clockwise as y grows down)."""
    n = leaves
    for i in range(n):
        t = i/(n-1)
        a = math.radians(a_start + (a_end - a_start)*t)
        bx, by = cx + radius*math.cos(a), cy + radius*math.sin(a)
        # outward normal
        ox, oy = math.cos(a), math.sin(a)
        # tangent (direction of travel)
        tx, ty = -math.sin(a), math.cos(a)
        sgn = 1 if a_end > a_start else -1
        # leaf tip: mostly outward, angled with the branch
        tipx = bx + ox*leaf*0.9 + tx*sgn*leaf*0.45
        tipy = by + oy*leaf*0.9 + ty*sgn*leaf*0.45
        # almond leaf via two curved sides (polygon)
        midx = bx + ox*leaf*0.5 + tx*sgn*leaf*0.22
        midy = by + oy*leaf*0.5 + ty*sgn*leaf*0.22
        perp = leaf*0.20
        p1 = (midx + tx*perp, midy + ty*perp)
        p2 = (midx - tx*perp, midy - ty*perp)
        draw.polygon([(bx,by), p1, (tipx,tipy), p2], fill=fill)

def cipher_layer(size, scale=1.0):
    """Royal cipher emblem: crown + double ring + serif SR monogram + laurel branches."""
    S = size
    img = Image.new("RGBA", (S, S), (0,0,0,0))
    cx, cy = S/2, S*0.50
    R = S*0.27

    d = ImageDraw.Draw(img)
    # double ring
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=CREMA, width=max(4,int(S*0.006)))
    d.ellipse([cx-R*0.90, cy-R*0.90, cx+R*0.90, cy+R*0.90], outline=CREMA_S, width=max(2,int(S*0.003)))

    # serif SR monogram fully inside ring
    fsize = int(S*0.26*scale)
    f = F(SERIF_B, fsize)
    d.text((cx, cy), "SR", font=f, fill=CREMA, anchor="mm")
    # subtle interlace bar between letters (a hairline vertical) for the "cipher" feel
    d.line([(cx, cy - fsize*0.34), (cx, cy + fsize*0.34)], fill=CREMA_S, width=max(2,int(S*0.0025)))

    # crown above ring
    crown_line(d, cx, cy - R - S*0.075, S*0.185, S*0.10, CREMA, max(5,int(S*0.007)))

    # two mirrored laurel branches sweeping up the lower sides, meeting at bottom
    lr = R*1.06
    leaf = S*0.030
    laurel_branch(d, cx, cy, lr, 100, 168, CREMA, leaves=8, leaf=leaf, width=max(4,int(S*0.005)))  # left
    laurel_branch(d, cx, cy, lr,  80,  12, CREMA, leaves=8, leaf=leaf, width=max(4,int(S*0.005)))  # right
    # small tie dot at bottom where branches meet
    bx, by = cx, cy + lr
    rr = S*0.012
    d.ellipse([bx-rr, by-rr, bx+rr, by+rr], fill=CREMA)
    return img

def print_file():
    """Transparent DTG print file, portrait, emblem sized for chest placement."""
    W, H = 3600, 4800
    img = Image.new("RGBA", (W, H), (0,0,0,0))
    emb = cipher_layer(2000, scale=1.0)
    # place centered horizontally, upper-chest vertically
    x = (W - emb.width)//2
    y = int(H*0.16)
    img.alpha_composite(emb, (x, y))
    # microtext beneath
    d = ImageDraw.Draw(img)
    text_tracked(d, (W/2, y + int(emb.height*0.86)), "STREET ROYALTY · MADRID · MMXXVI",
                 F(SANS_B, 60), CREMA, tracking=16)
    img.save(f"{OUT}/cifra-real-print.png")
    return img

def print_file_square():
    """Square DTG print file (for hoodie / square print areas), emblem centered."""
    S = 3600
    img = Image.new("RGBA", (S, S), (0,0,0,0))
    emb = cipher_layer(2200, scale=1.0)
    x = (S - emb.width)//2
    y = int(S*0.16)
    img.alpha_composite(emb, (x, y))
    d = ImageDraw.Draw(img)
    text_tracked(d, (S/2, y + int(emb.height*0.86)), "STREET ROYALTY · MADRID · MMXXVI",
                 F(SANS_B, 62), CREMA, tracking=16)
    img.save(f"{OUT}/cifra-real-print-square.png")
    return img

def hero_preview():
    """QA + a clean brand hero on near-black (secondary product image)."""
    W, H = 1600, 1600
    img = Image.new("RGBA", (W, H), (16,16,18,255))
    emb = cipher_layer(1300, scale=1.0)
    img.alpha_composite(emb, ((W-emb.width)//2, int(H*0.06)))
    d = ImageDraw.Draw(img)
    text_tracked(d, (W/2, int(H*0.90)), "CIFRA REAL · CAPSULE Nº01", F(SANS_B, 40), CREMA, tracking=14)
    img.convert("RGB").save(f"{OUT}/cifra-real-hero.jpg", quality=92)
    return img

print_file()
print_file_square()
hero_preview()
print("OK — files:", os.listdir(OUT))

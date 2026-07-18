# Forja Real — wrought-iron scrollwork drop for SRHOOD
# Generates 6 print files + poster-quality composition helpers (PIL only).
import math, os
from PIL import Image, ImageDraw, ImageFilter, ImageFont

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'forja')
os.makedirs(OUT, exist_ok=True)

# Palette
IRON   = (240, 234, 219, 255)   # ivory "polished iron" reads on black garments
IRON2  = (214, 205, 186, 255)   # darker ivory for depth
GOLD   = (201, 163, 74, 255)
GOLD2  = (226, 190, 110, 255)
WINE   = (94, 31, 42, 255)
BLACK  = (13, 12, 11, 255)

def font(sz, bold=True):
    path = '/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf' if bold else '/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf'
    try: return ImageFont.truetype(path, sz)
    except Exception: return ImageFont.load_default()

def font_sans(sz):
    try: return ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', sz)
    except Exception: return ImageFont.load_default()

def rot(px, py, cx, cy, a):
    s, c = math.sin(a), math.cos(a)
    return (cx + (px-cx)*c - (py-cy)*s, cy + (px-cx)*s + (py-cy)*c)

def draw_spiral(d, cx, cy, r0, r1, a0, turns, width, color, ccw=1, steps=140):
    """Archimedean spiral from radius r0 to r1 starting at angle a0."""
    pts = []
    for i in range(steps+1):
        t = i/steps
        r = r0 + (r1-r0)*t
        a = a0 + ccw * turns * 2*math.pi * t
        pts.append((cx + r*math.cos(a), cy + r*math.sin(a)))
    d.line(pts, fill=color, width=width, joint='curve')
    # rounded tip
    x, y = pts[-1]
    d.ellipse([x-width*0.75, y-width*0.75, x+width*0.75, y+width*0.75], fill=color)
    return pts

def c_scroll(d, cx, cy, R, width, color, flip=False, a_base=0.0):
    """C-scroll: big curve with an inward volute at each end."""
    ccw = -1 if flip else 1
    # main arc
    pts=[]
    for i in range(121):
        t=i/120
        a = a_base + ccw*(math.pi*0.15 + t*math.pi*0.7)
        pts.append((cx + R*math.cos(a), cy + R*math.sin(a)))
    d.line(pts, fill=color, width=width, joint='curve')
    for end,sgn in ((pts[0],1),(pts[-1],-1)):
        ex,ey = end
        ang = math.atan2(ey-cy, ex-cx)
        vx, vy = ex + R*0.22*math.cos(ang), ey + R*0.22*math.sin(ang)
        draw_spiral(d, vx, vy, R*0.22, R*0.045, ang+math.pi, 1.35, width, color, ccw=sgn*ccw)

def volute_pair(d, cx, cy, R, width, color):
    """Two mirrored volutes forming a heart/lyre motif (classic reja element)."""
    draw_spiral(d, cx-R*0.52, cy, R*0.5, R*0.09, math.pi*0.5, 1.4, width, color, ccw=-1)
    draw_spiral(d, cx+R*0.52, cy, R*0.5, R*0.09, math.pi*0.5, 1.4, width, color, ccw=1)

def spear_finial(d, cx, cy, h, color):
    w = h*0.42
    d.polygon([(cx, cy-h), (cx-w/2, cy-h*0.35), (cx-w*0.16, cy-h*0.42), (cx-w*0.16, cy),
               (cx+w*0.16, cy), (cx+w*0.16, cy-h*0.42), (cx+w/2, cy-h*0.35)], fill=color)

def crown(d, cx, cy, w, color, jewel=None):
    h = w*0.62
    base_h = h*0.18
    pts = [(cx-w/2, cy), (cx-w/2, cy-h*0.55), (cx-w*0.25, cy-h*0.28), (cx, cy-h),
           (cx+w*0.25, cy-h*0.28), (cx+w/2, cy-h*0.55), (cx+w/2, cy)]
    d.polygon(pts, fill=color)
    d.rectangle([cx-w/2, cy+h*0.08, cx+w/2, cy+h*0.08+base_h], fill=color)
    if jewel:
        for jx, jy in [(cx-w/2, cy-h*0.62), (cx, cy-h*1.08), (cx+w/2, cy-h*0.62)]:
            r = w*0.045
            d.ellipse([jx-r, jy-r, jx+r, jy+r], fill=jewel)

def twisted_bar(d, x, y0, y1, width, color, pitch=90):
    """Vertical bar with barley-twist hatching."""
    d.line([(x, y0), (x, y1)], fill=color, width=width)
    y = y0 + pitch*0.5
    while y < y1 - pitch*0.2:
        d.line([(x-width*0.55, y-pitch*0.30), (x+width*0.55, y+pitch*0.30)], fill=BLACK[:3]+(90,), width=max(3, width//5))
        y += pitch

def quatrefoil(d, cx, cy, r, width, color):
    for a in (0, math.pi/2, math.pi, 3*math.pi/2):
        x, y = cx + r*0.62*math.cos(a), cy + r*0.62*math.sin(a)
        d.arc([x-r*0.55, y-r*0.55, x+r*0.55, y+r*0.55], 0, 360, fill=color, width=width)
    d.ellipse([cx-width*0.9, cy-width*0.9, cx+width*0.9, cy+width*0.9], fill=color)

def rosette(d, cx, cy, R, width, color, gold):
    n = 8
    for i in range(n):
        a = i*2*math.pi/n
        x, y = cx + R*0.62*math.cos(a), cy + R*0.62*math.sin(a)
        ang = a + math.pi
        draw_spiral(d, x, y, R*0.34, R*0.06, ang, 1.25, width, color, ccw=1 if i%2==0 else -1)
    d.ellipse([cx-R*0.16, cy-R*0.16, cx+R*0.16, cy+R*0.16], outline=gold, width=width)
    d.ellipse([cx-R*0.05, cy-R*0.05, cx+R*0.05, cy+R*0.05], fill=gold)

def letterspace(d, cx, y, text, f, color, ls):
    widths = [d.textlength(ch, font=f) for ch in text]
    total = sum(widths) + ls*(len(text)-1)
    x = cx - total/2
    for ch, w in zip(text, widths):
        d.text((x, y), ch, font=f, fill=color)
        x += w + ls

# ---------------------------------------------------------------- TEE FRONT
def tee(path, W=2400, H=3200):
    im = Image.new('RGBA', (W, H), (0,0,0,0))
    d = ImageDraw.Draw(im)
    cx = W//2
    top, bot = 420, 2260
    gl, gr = cx-780, cx+780       # gate frame
    bw = 26                        # bar width
    # frame
    d.rounded_rectangle([gl, top, gr, bot], radius=40, outline=IRON, width=bw)
    d.rounded_rectangle([gl+70, top+70, gr-70, bot-70], radius=24, outline=IRON2, width=int(bw*0.55))
    # vertical bars with spear finials above frame
    xs = [gl + 170 + i*(gr-gl-340)//4 for i in range(5)]
    for i, x in enumerate(xs):
        if i == 2:   # center: leave room for medallion
            twisted_bar(d, x, top+90, top+330, bw-6, IRON)
            twisted_bar(d, x, bot-330, bot-90, bw-6, IRON)
        else:
            twisted_bar(d, x, top+90, bot-90, bw-6, IRON)
        spear_finial(d, x, top-30, 150, GOLD if i % 2 else IRON)
    # scroll bands
    for y in (top+430, bot-430):
        for x in (cx-395, cx+395):
            volute_pair(d, x, y, 300, bw-8, IRON)
    # center medallion (solid black backing so ring reads as a plate)
    my = (top+bot)//2 - 60
    d.ellipse([cx-330, my-330, cx+330, my+330], fill=BLACK, outline=GOLD, width=bw-6)
    d.ellipse([cx-296, my-296, cx+296, my+296], outline=IRON2, width=12)
    rosette(d, cx, my, 300, bw-10, IRON, GOLD)
    d.ellipse([cx-160, my-160, cx+160, my+160], fill=BLACK)
    crown(d, cx, my+30, 230, GOLD2, jewel=WINE)
    # corner quarter-arcs inside the frame
    r = 260
    for sx, sy, a0 in ((-1, -1, 0), (1, -1, 90), (1, 1, 180), (-1, 1, 270)):
        ccx = gl if sx < 0 else gr
        ccy = top if sy < 0 else bot
        d.arc([ccx-r, ccy-r, ccx+r, ccy+r], a0, a0+90, fill=GOLD, width=12)
    quatrefoil(d, cx, bot-190, 120, bw-12, GOLD)
    # typography
    letterspace(d, cx, bot+150, 'FORJA REAL', font(190), IRON, 26)
    letterspace(d, cx, bot+420, 'HIERRO Y ORO · STREET ROYALTY HOOD', font_sans(52), GOLD, 16)
    d.line([(cx-560, bot+380), (cx-180, bot+380)], fill=GOLD, width=6)
    d.line([(cx+180, bot+380), (cx+560, bot+380)], fill=GOLD, width=6)
    d.ellipse([cx-14, bot+366, cx+14, bot+394], fill=WINE)
    im.save(path)

# ---------------------------------------------------------------- TANK FRONT
def tank(path, W=2400, H=3000):
    im = Image.new('RGBA', (W, H), (0,0,0,0))
    d = ImageDraw.Draw(im)
    cx = W//2
    # tall narrow reja column
    top, bot = 330, 2280
    gl, gr = cx-430, cx+430
    bw = 24
    d.rounded_rectangle([gl, top, gr, bot], radius=30, outline=IRON, width=bw)
    xs = [gl+120, cx, gr-120]
    for i, x in enumerate(xs):
        if i == 1:
            twisted_bar(d, x, top+70, top+430, bw-6, IRON)
            twisted_bar(d, x, bot-430, bot-70, bw-6, IRON)
        else:
            twisted_bar(d, x, top+70, bot-70, bw-6, IRON)
        spear_finial(d, x, top-26, 130, GOLD if i == 1 else IRON)
    my = (top+bot)//2
    volute_pair(d, cx, my-560, 240, bw-8, IRON)
    volute_pair(d, cx, my+560, 240, bw-8, IRON)
    d.ellipse([cx-250, my-250, cx+250, my+250], fill=BLACK, outline=GOLD, width=bw-6)
    rosette(d, cx, my, 225, bw-10, IRON, GOLD)
    d.ellipse([cx-118, my-118, cx+118, my+118], fill=BLACK)
    crown(d, cx, my+24, 185, GOLD2, jewel=WINE)
    letterspace(d, cx, bot+120, 'FORJA REAL', font(150), IRON, 20)
    letterspace(d, cx, bot+330, 'SRHOOD · MMXXVI', font_sans(48), GOLD, 14)
    im.save(path)

# ---------------------------------------------------------------- HOODIE FRONT
def hoodie(path, W=1800, H=1800):
    im = Image.new('RGBA', (W, H), (0,0,0,0))
    d = ImageDraw.Draw(im)
    cx, cy = W//2, H//2 - 60
    bw = 20
    R = 610
    d.ellipse([cx-R, cy-R, cx+R, cy+R], outline=IRON, width=bw)
    d.ellipse([cx-R+42, cy-R+42, cx+R-42, cy+R-42], outline=GOLD, width=10)
    # ring of scroll volutes
    n = 10
    for i in range(n):
        a = i*2*math.pi/n
        x, y = cx + (R-135)*math.cos(a), cy + (R-135)*math.sin(a)
        draw_spiral(d, x, y, 92, 18, a+math.pi/2, 1.3, bw-6, IRON, ccw=1 if i%2==0 else -1)
    # spear points around outside
    for i in range(n):
        a = i*2*math.pi/n + math.pi/n
        x, y = cx + (R+58)*math.cos(a), cy + (R+58)*math.sin(a)
        px, py = rot(x, y+64, x, y, a+math.pi/2)
        poly = [(x, y-64), (x-26, y-8), (x-9, y-14), (x-9, y+64), (x+9, y+64), (x+9, y-14), (x+26, y-8)]
        poly = [rot(px_, py_, x, y, a+math.pi/2) for px_, py_ in poly]
        d.polygon(poly, fill=GOLD if i % 2 else IRON2)
    crown(d, cx, cy-120, 300, GOLD2, jewel=WINE)
    letterspace(d, cx, cy+8, 'FORJA', font(180), IRON, 22)
    letterspace(d, cx, cy+230, 'REAL', font(150), IRON2, 34)
    letterspace(d, cx, H-236, 'PUERTA DEL REINO · SRHOOD', font_sans(44), GOLD, 12)
    im.save(path)

# ---------------------------------------------------------------- LATTICE (shoes)
def lattice_tile(W, H, scale=1.0, density=1.0):
    """Wrought-iron lattice: S-scroll columns + quatrefoils + gold studs on black."""
    im = Image.new('RGBA', (W, H), BLACK)
    d = ImageDraw.Draw(im)
    cell = int(300*scale)
    bw = max(10, int(16*scale))
    cols = W//cell + 2
    rows = H//cell + 2
    for r in range(rows):
        for c in range(cols):
            x = c*cell + (cell//2 if r % 2 else 0)
            y = r*cell
            flip = (r+c) % 2 == 0
            draw_spiral(d, x, y+cell*0.28, cell*0.30, cell*0.055, math.pi*0.5, 1.35, bw, IRON, ccw=1 if flip else -1)
            draw_spiral(d, x, y+cell*0.78, cell*0.30, cell*0.055, math.pi*1.5, 1.35, bw, IRON2, ccw=-1 if flip else 1)
            if (r + c) % 3 == 0:
                gr = cell*0.055
                d.ellipse([x-gr, y+cell*0.53-gr, x+gr, y+cell*0.53+gr], fill=GOLD)
    # sparse quatrefoils + crowns
    step = cell*2
    for yy in range(0, H+step, step):
        for xx in range(0, W+step, step):
            if (xx//step + yy//step) % 2 == 0:
                quatrefoil(d, xx+cell*0.5, yy+cell*0.5, cell*0.30, max(8, bw-6), GOLD)
    return im

def hightop(path):
    lattice_tile(2400, 2400, scale=1.0).convert('RGB').save(path)

def chanclas(path):
    lattice_tile(2000, 2000, scale=1.35).convert('RGB').save(path)

# ---------------------------------------------------------------- RIÑONERA
def rinonera(path, W=2850, H=1050):
    im = Image.new('RGBA', (W, H), BLACK)
    d = ImageDraw.Draw(im)
    cy = H//2
    bw = 18
    # horizontal scroll frieze
    cell = 330
    for i in range(-1, W//cell + 2):
        x = i*cell
        draw_spiral(d, x, cy-105, 100, 20, math.pi, 1.3, bw, IRON, ccw=1)
        draw_spiral(d, x+cell//2, cy+105, 100, 20, 0, 1.3, bw, IRON2, ccw=-1)
        d.ellipse([x+cell//2-16, cy-16, x+cell//2+16, cy+16], fill=GOLD)
    # gold rails
    d.line([(0, 84), (W, 84)], fill=GOLD, width=10)
    d.line([(0, H-84), (W, H-84)], fill=GOLD, width=10)
    # center crown medallion
    cx = W//2
    d.ellipse([cx-190, cy-190, cx+190, cy+190], fill=BLACK, outline=GOLD, width=14)
    crown(d, cx, cy+26, 200, GOLD2, jewel=WINE)
    im.save(path)

if __name__ == '__main__':
    tee(OUT+'/frj01_tee_front.png')
    tank(OUT+'/frj02_tank_front.png')
    hoodie(OUT+'/frj03_hoodie_front.png')
    hightop(OUT+'/frj04_hightop.png')
    chanclas(OUT+'/frj05_chanclas.png')
    rinonera(OUT+'/frj06_fanny.png')
    print('done')

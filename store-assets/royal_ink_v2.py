#!/usr/bin/env python3
# Royal Ink Vol. II — 3 elevated original poster designs for SRHOOD
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs2")
os.makedirs(OUT, exist_ok=True)

W, H = 1600, 2400
NEGRO=(12,12,14); CREMA=(242,234,217); ARENA=(214,196,158)
ORO=(201,164,76); ORO_HI=(234,204,126); BURDEOS=(74,22,32); NAVY=(20,27,45)
OLIVA=(78,84,58); AZUL=(28,52,74)

SANS_B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
MONO="/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
def F(p,s): return ImageFont.truetype(p,s)

def grain(img, seed=5):
    n=Image.effect_noise(img.size,10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB",(n,n,n)), 0.045)

def vgrad(size, top, bot):
    w,h=size; base=Image.new("RGB",(1,h)); px=base.load()
    for y in range(h):
        t=y/(h-1); px[0,y]=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))
    return base.resize((w,h))

def tracked(draw,xy,text,font,fill,tr=0,center=False,stroke=0,sfill=None):
    x,y=xy; ws=[draw.textlength(c,font=font) for c in text]
    tot=sum(ws)+tr*(len(text)-1)
    if center: x-=tot/2
    for c,cw in zip(text,ws):
        draw.text((x,y),c,font=font,fill=fill,stroke_width=stroke,stroke_fill=sfill); x+=cw+tr
    return tot

def crown(cx,cy,w,h):
    l=cx-w/2;r=cx+w/2;b=cy+h/2;t=cy-h/2;dipy=b-h*0.42
    pts=[(l,b),(l,t+h*0.30),(l+w*0.185,dipy),(cx-w*0.155,t+h*0.12),(cx,dipy-h*0.02),
         (cx+w*0.155,t+h*0.12),(r-w*0.185,dipy),(r,t+h*0.30),(r,b)]
    band=(l,b+h*0.06,r,b+h*0.16)
    return pts,band

def footer(draw,txt,csub,color=ORO,y=H-150):
    tracked(draw,(W/2,y),txt,F(SANS_B,34),color,tr=14,center=True)
    tracked(draw,(W/2,y+52),"STREET ROYALTY HOOD — VOL. II",F(SANS,24),csub,tr=8,center=True)

# ---- 7. Sol Naciente Royal — sunburst rays + crown medallion, olive/gold
def d7():
    img=vgrad((W,H),(66,72,50),(40,44,30)); draw=ImageDraw.Draw(img)
    cx,cy=W/2,H*0.40
    # radiant triangle rays
    N=48
    for i in range(N):
        a0=2*math.pi*i/N; a1=2*math.pi*(i+0.5)/N
        R=H*0.9
        p=[(cx,cy),(cx+math.cos(a0)*R,cy+math.sin(a0)*R),(cx+math.cos(a1)*R,cy+math.sin(a1)*R)]
        draw.polygon(p, fill=(ORO if i%2==0 else (150,124,60)))
    # dark disc over rays
    for rr,c in [(W*0.40,(46,50,34)),(W*0.35,(52,58,40))]:
        draw.ellipse([cx-rr,cy-rr,cx+rr,cy+rr],fill=c)
    draw.ellipse([cx-W*0.355,cy-W*0.355,cx+W*0.355,cy+W*0.355],outline=ORO_HI,width=4)
    # crown medallion
    pts,band=crown(cx,cy,W*0.30,H*0.135)
    draw.polygon(pts,fill=ORO_HI); draw.rectangle(band,fill=ORO_HI)
    for px_,py_ in [(cx-W*0.15,cy-H*0.135*0.60),(cx,cy-H*0.135*0.84),(cx+W*0.15,cy-H*0.135*0.60)]:
        draw.ellipse([px_-12,py_-12,px_+12,py_+12],fill=CREMA)
    # bottom shade so text is legible over the rays
    shade=Image.new("RGBA",(W,H),(0,0,0,0)); sp=shade.load()
    y0=int(H*0.66)
    for y in range(y0,H):
        t=(y-y0)/(H-y0); a=int(215*t)
        for x in range(W): sp[x,y]=(30,34,22,a)
    img=Image.alpha_composite(img.convert("RGBA"),shade).convert("RGB"); draw=ImageDraw.Draw(img)
    draw.rectangle([W*0.30,H*0.705,W*0.70,H*0.707],fill=ORO_HI)
    draw.text((W/2,H*0.755),"SOL REAL",font=F(SERIF_B,116),fill=CREMA,anchor="mm")
    tracked(draw,(W/2,H*0.808),"AMANECE LA CORONA",F(SANS,32),ORO_HI,tr=16,center=True)
    footer(draw,"ROYAL INK · Nº 07",(200,200,170),color=ORO_HI)
    return grain(img)

# ---- 8. Blueprint Corona — technical draft of the crown, navy
def d8():
    img=vgrad((W,H),(24,34,58),(14,20,36)); draw=ImageDraw.Draw(img)
    # grid
    for x in range(0,W,54): draw.line([(x,0),(x,H)],fill=(38,50,78),width=1)
    for y in range(0,H,54): draw.line([(0,y),(W,y)],fill=(38,50,78),width=1)
    for x in range(0,W,270): draw.line([(x,0),(x,H)],fill=(52,68,104),width=1)
    for y in range(0,H,270): draw.line([(0,y),(W,y)],fill=(52,68,104),width=1)
    cx,cy=W/2,H*0.40
    pts,band=crown(cx,cy,W*0.44,H*0.20)
    # construction circles at crown tips
    tips=[(cx-W*0.22*0.85,cy-H*0.20*0.30),(cx-W*0.155*1.0,cy-H*0.20*0.38),(cx,cy-H*0.20*0.60),
          (cx+W*0.155*1.0,cy-H*0.20*0.38),(cx+W*0.22*0.85,cy-H*0.20*0.30)]
    # outline crown in cyan-white
    line=(150,196,232)
    draw.line(pts+[pts[0]],fill=line,width=5,joint="curve")
    draw.rectangle(band,outline=line,width=5)
    # dimension ticks
    for px_,py_ in [(cx,cy-H*0.20*0.62),(cx-W*0.155,cy-H*0.20*0.40),(cx+W*0.155,cy-H*0.20*0.40)]:
        for rr in (26,10):
            draw.ellipse([px_-rr,py_-rr,px_+rr,py_+rr],outline=ORO_HI,width=2)
    # dimension line
    draw.line([(cx-W*0.22,cy+H*0.135),(cx+W*0.22,cy+H*0.135)],fill=ORO_HI,width=2)
    for ex in (cx-W*0.22,cx+W*0.22):
        draw.line([(ex,cy+H*0.125),(ex,cy+H*0.145)],fill=ORO_HI,width=2)
    tracked(draw,(cx,cy+H*0.150),"CORONA SRH · ESC. 1:1",F(MONO,26),(150,196,232),tr=4,center=True)
    draw.text((W/2,H*0.745),"BLUEPRINT",font=F(SANS_B,108),fill=CREMA,anchor="mm")
    tracked(draw,(W/2,H*0.795)," diseñado para durar",F(SANS,32),ORO_HI,tr=12,center=True)
    footer(draw,"ROYAL INK · Nº 08",(110,130,170))
    return grain(img)

# ---- 9. Retrato Fragmentado — geometric low-poly crown bust, burdeos+cream
def d9():
    img=Image.new("RGB",(W,H),(238,230,214)); draw=ImageDraw.Draw(img)
    cx,cy=W/2,H*0.42
    rnd=random.Random(9)
    # low-poly shard field radiating, burdeos tones
    pal=[(74,22,32),(104,36,48),(140,52,64),(190,150,110),(201,164,76),(232,204,126)]
    R=W*0.46
    prev=None
    pts_ring=[]
    for i in range(19):
        a=2*math.pi*i/18
        rad=R*(0.72+0.28*rnd.random())
        pts_ring.append((cx+math.cos(a)*rad, cy+math.sin(a)*rad*1.18))
    for i in range(18):
        p1=pts_ring[i]; p2=pts_ring[i+1]
        mid=(cx+(p1[0]-cx)*0.4+(p2[0]-cx)*0.1, cy+(p1[1]-cy)*0.4+(p2[1]-cy)*0.1)
        draw.polygon([ (cx,cy), p1, p2], fill=pal[(i)%len(pal)])
        draw.polygon([ (cx,cy), p1, p2], outline=(238,230,214))
    # inner facets
    for _ in range(60):
        a=rnd.uniform(0,2*math.pi); rr=rnd.uniform(0,R*0.55)
        x=cx+math.cos(a)*rr; y=cy+math.sin(a)*rr*1.15
        s=rnd.uniform(20,60)
        tri=[(x,y),(x+s,y+rnd.uniform(-s,s)),(x+rnd.uniform(-s,s),y+s)]
        draw.polygon(tri,fill=pal[rnd.randrange(len(pal))])
    # crown silhouette knocked out in cream on top
    pts,band=crown(cx,cy-H*0.02,W*0.34,H*0.15)
    draw.polygon(pts,fill=(238,230,214)); draw.rectangle(band,fill=(238,230,214))
    draw.line(pts+[pts[0]],fill=BURDEOS,width=6,joint="curve")
    draw.rectangle(band,outline=BURDEOS,width=6)
    draw.rectangle([W*0.26,H*0.66,W*0.74,H*0.663],fill=BURDEOS)
    draw.text((W/2,H*0.745),"MOSAICO",font=F(SERIF_B,112),fill=BURDEOS,anchor="mm")
    tracked(draw,(W/2,H*0.80),"MIL PIEZAS · UNA CORONA",F(SANS,32),(120,60,70),tr=13,center=True)
    footer(draw,"ROYAL INK · Nº 09",(150,110,118),color=BURDEOS)
    return grain(img)

def mockup(poster, wall=(224,220,212)):
    MW,MH=1600,2000
    img=vgrad((MW,MH),tuple(min(255,c+12) for c in wall),tuple(max(0,c-18) for c in wall))
    ph=int(MH*0.72); pw=int(ph*W/H); px,py=(MW-pw)//2,int(MH*0.10)
    fp=26; mt=46
    sh=Image.new("RGBA",(MW,MH),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rectangle([px-fp-mt+14,py-fp-mt+26,px+pw+fp+mt+30,py+ph+fp+mt+44],fill=(0,0,0,110))
    sh=sh.filter(ImageFilter.GaussianBlur(28))
    img=Image.alpha_composite(img.convert("RGBA"),sh).convert("RGB"); draw=ImageDraw.Draw(img)
    draw.rectangle([px-fp-mt,py-fp-mt,px+pw+fp+mt,py+ph+fp+mt],fill=(24,22,20))
    draw.rectangle([px-mt,py-mt,px+pw+mt,py+ph+mt],fill=(248,246,240))
    img.paste(poster.resize((pw,ph),Image.LANCZOS),(px,py))
    draw.rectangle([0,int(MH*0.94),MW,MH],fill=tuple(max(0,c-34) for c in wall))
    return img

designs={"royal-ink-07-sol-real":d7,"royal-ink-08-blueprint":d8,"royal-ink-09-mosaico":d9}
for name,fn in designs.items():
    art=fn(); art.save(f"{OUT}/{name}.jpg",quality=92)
    mockup(art).save(f"{OUT}/{name}-wall.jpg",quality=90)
    print("done",name)

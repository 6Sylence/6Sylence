#!/usr/bin/env python3
# MANIFIESTO — typographic poster series for SRHOOD (distinct from Royal Ink)
import math, random, os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "designs3")
os.makedirs(OUT, exist_ok=True)
W, H = 1600, 2400
NEGRO=(14,14,16); CREMA=(240,232,215); ARENA=(210,192,152)
ORO=(201,164,76); ORO_HI=(234,204,126); BURDEOS=(78,24,34); BURDEOS_HI=(150,52,66); NAVY=(20,27,45)
SANS_B="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
SANS="/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
SERIF_B="/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"
def F(p,s): return ImageFont.truetype(p,s)

def grain(img):
    n=Image.effect_noise(img.size,10).convert("L")
    return Image.blend(img.convert("RGB"), Image.merge("RGB",(n,n,n)), 0.04)

def vgrad(size, top, bot):
    w,h=size; base=Image.new("RGB",(1,h)); px=base.load()
    for y in range(h):
        t=y/(h-1); px[0,y]=tuple(int(top[i]+(bot[i]-top[i])*t) for i in range(3))
    return base.resize((w,h))

def tracked(draw,xy,text,font,fill,tr=0,anchor_left=True,stroke=0,sfill=None):
    x,y=xy
    ws=[draw.textlength(c,font=font) for c in text]
    tot=sum(ws)+tr*(len(text)-1)
    if not anchor_left: x-=tot
    for c,cw in zip(text,ws):
        draw.text((x,y),c,font=font,fill=fill,stroke_width=stroke,stroke_fill=sfill); x+=cw+tr
    return tot

def fit_font(draw, text, path, target_w, start=300, tr=0):
    s=start
    while s>20:
        f=F(path,s)
        w=sum(draw.textlength(c,font=f) for c in text)+tr*(len(text)-1)
        if w<=target_w: return f,w
        s-=4
    return F(path,20),0

def crown_mark(draw, cx, cy, w, col):
    h=w*0.62; l=cx-w/2; r=cx+w/2; b=cy+h/2; t=cy-h/2; dip=b-h*0.42
    pts=[(l,b),(l,t+h*0.30),(l+w*0.185,dip),(cx-w*0.155,t+h*0.12),(cx,dip-h*0.02),
         (cx+w*0.155,t+h*0.12),(r-w*0.185,dip),(r,t+h*0.30),(r,b)]
    draw.polygon(pts,fill=col); draw.rectangle((l,b+h*0.10,r,b+h*0.24),fill=col)

def footer(draw, num, color, sub_color):
    tracked(draw,(W/2,H-150),"SRHOOD · MANIFIESTO",F(SANS_B,32),color,tr=12,anchor_left=False) if False else None
    f1=F(SANS_B,32); f2=F(SANS,23)
    t1="MANIFIESTO · "+num
    w1=sum(draw.textlength(c,font=f1) for c in t1)+12*(len(t1)-1)
    tracked(draw,(W/2-w1/2,H-150),t1,f1,color,tr=12)
    t2="STREET ROYALTY HOOD — MMXXVI"
    w2=sum(draw.textlength(c,font=f2) for c in t2)+8*(len(t2)-1)
    tracked(draw,(W/2-w2/2,H-102),t2,f2,sub_color,tr=8)

# ---- Nº01 "LA CORONA NO SE PIDE" — black / gold, left-aligned stacked
def d1():
    img=vgrad((W,H),(18,18,22),(10,10,12)); draw=ImageDraw.Draw(img)
    mL=150
    # small top label
    tracked(draw,(mL,190),"EL CÓDIGO DE LA CASA",F(SANS_B,30),ORO,tr=10)
    draw.rectangle([mL,250,mL+250,254],fill=ORO)
    # stacked words
    f_la,_=fit_font(draw,"LA",SANS_B,360,start=170)
    draw.text((mL,300),"LA",font=f_la,fill=(70,68,64))
    f_cor,_=fit_font(draw,"CORONA",SANS_B,W-2*mL,start=320)
    draw.text((mL,430),"CORONA",font=f_cor,fill=ORO_HI)
    f_no,_=fit_font(draw,"NO SE",SANS_B,W-2*mL,start=300)
    draw.text((mL,690),"NO SE",font=f_no,fill=CREMA)
    f_pi,_=fit_font(draw,"PIDE.",SANS_B,W-2*mL,start=340)
    draw.text((mL,930),"PIDE.",font=f_pi,fill=CREMA)
    # rule + subline
    draw.rectangle([mL,H*0.62,W-mL,H*0.622],fill=(60,58,54))
    tracked(draw,(mL,H*0.645),"SE LLEVA PUESTA",F(SANS_B,54),ORO,tr=8)
    crown_mark(draw,W-mL-70,H*0.655+30,120,ORO)
    footer(draw,"Nº 01",ORO,(120,112,96))
    return grain(img)

# ---- Nº02 "MANDA EN SILENCIO" — cream / burgundy, framed editorial
def d2():
    img=vgrad((W,H),(244,238,224),(232,224,206)); draw=ImageDraw.Draw(img)
    m=100
    draw.rectangle([m,m,W-m,H-m],outline=BURDEOS,width=4)
    draw.rectangle([m+16,m+16,W-m-16,H-m-16],outline=(190,150,110),width=1)
    tracked(draw,(W/2,m+90),"SRHOOD",F(SANS_B,34),BURDEOS,tr=22,anchor_left=False)
    # big statement, centered stacked
    def cline(text,y,col,path=SANS_B,pad=260):
        f,w=fit_font(draw,text,path,W-2*m-pad,start=260)
        draw.text((W/2,y),text,font=f,fill=col,anchor="mm")
        return f
    cline("LA CALLE",H*0.30,NEGRO)
    cline("NO GRITA.",H*0.40,NEGRO)
    draw.line([(W*0.32,H*0.475),(W*0.68,H*0.475)],fill=BURDEOS,width=3)
    cline("MANDA",H*0.56,BURDEOS)
    cline("EN SILENCIO",H*0.655,BURDEOS,pad=120)
    crown_mark(draw,W/2,H*0.745,120,(150,110,70))
    footer(draw,"Nº 02",BURDEOS,(150,110,90))
    return grain(img)

# ---- Nº03 "STREET ROYALTY" — navy / gold, oversized monogram behind
def d3():
    img=vgrad((W,H),(24,32,54),(14,19,34)); draw=ImageDraw.Draw(img)
    # giant faint SR monogram behind
    fbig=F(SERIF_B,900)
    draw.text((W/2,H*0.42),"SR",font=fbig,fill=(32,42,68),anchor="mm")
    # thin gold frame ticks
    for x in (140,W-140):
        draw.line([(x,H*0.12),(x,H*0.72)],fill=(52,66,100),width=2)
    # overlaid wordmark, two lines, gold + cream
    f1,w1=fit_font(draw,"STREET",SANS_B,W-300,start=260)
    draw.text((W/2,H*0.33),"STREET",font=f1,fill=CREMA,anchor="mm")
    f2,w2=fit_font(draw,"ROYALTY",SANS_B,W-260,start=260)
    draw.text((W/2,H*0.44),"ROYALTY",font=f2,fill=ORO_HI,anchor="mm")
    # baseline bar + tagline
    draw.rectangle([W*0.2,H*0.53,W*0.8,H*0.533],fill=ORO)
    draw.text((W/2,H*0.567),"LA CORONA NO SE PIDE · SE LLEVA PUESTA",font=F(SANS,26),fill=ARENA,anchor="mm")
    crown_mark(draw,W/2,H*0.66,150,ORO)
    tracked(draw,(W/2,H*0.72),"EST. MMXXVI · MADRID",F(SANS_B,30),(120,140,180),tr=12,anchor_left=False)
    footer(draw,"Nº 03",ORO,(110,128,168))
    return grain(img)

def mockup(poster, wall=(226,222,214)):
    MW,MH=1600,2000
    img=vgrad((MW,MH),tuple(min(255,c+12) for c in wall),tuple(max(0,c-18) for c in wall))
    ph=int(MH*0.72); pw=int(ph*W/H); px,py=(MW-pw)//2,int(MH*0.10); fp=26; mt=46
    sh=Image.new("RGBA",(MW,MH),(0,0,0,0)); sd=ImageDraw.Draw(sh)
    sd.rectangle([px-fp-mt+14,py-fp-mt+26,px+pw+fp+mt+30,py+ph+fp+mt+44],fill=(0,0,0,110))
    sh=sh.filter(ImageFilter.GaussianBlur(28))
    img=Image.alpha_composite(img.convert("RGBA"),sh).convert("RGB"); draw=ImageDraw.Draw(img)
    draw.rectangle([px-fp-mt,py-fp-mt,px+pw+fp+mt,py+ph+fp+mt],fill=(24,22,20))
    draw.rectangle([px-mt,py-mt,px+pw+mt,py+ph+mt],fill=(248,246,240))
    img.paste(poster.resize((pw,ph),Image.LANCZOS),(px,py))
    draw.rectangle([0,int(MH*0.94),MW,MH],fill=tuple(max(0,c-34) for c in wall))
    return img

designs={"manifiesto-01-corona-no-se-pide":d1,"manifiesto-02-manda-en-silencio":d2,"manifiesto-03-street-royalty":d3}
for name,fn in designs.items():
    art=fn(); art.save(f"{OUT}/{name}.jpg",quality=92)
    mockup(art).save(f"{OUT}/{name}-wall.jpg",quality=90)
    print("done",name)

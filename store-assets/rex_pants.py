# -*- coding: utf-8 -*-
# SRHOOD — pantalones all-over: patrones densos por aspect-ratio de prenda
import math, os, random
from PIL import Image, ImageDraw, ImageFont
OUT=os.path.dirname(os.path.abspath(__file__))+"/prints"; os.makedirs(OUT,exist_ok=True)
ORO=(201,162,75,255); CREMA=(242,234,216,255); BURDEOS=(107,34,49,255); NAVY=(30,42,68,255); NEGRO=(20,21,26,255); OLIVA=(90,95,69,255)
def crown(d,cx,cy,w,color,lw):
    h=w*0.52
    pts=[(cx-w/2,cy+h/2),(cx-w/2,cy-h*0.1),(cx-w*0.25,cy+h*0.05),(cx,cy-h/2),(cx+w*0.25,cy+h*0.05),(cx+w/2,cy-h*0.1),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)]
    d.line(pts,fill=color,width=lw,joint="curve")
    for i in range(6):
        x=cx-w/2+(i+0.5)*w/6; y=cy+h/2+h*0.22; r=max(1,w*0.035); d.ellipse([x-r,y-r,x+r,y+r],fill=color)
def meander(d,x0,y0,s,color,lw,flip=False):
    u=s/8.0; pts=[(1,7),(1,1),(7,1),(7,7),(3,7),(3,3),(5,3),(5,5)]
    if flip: pts=[(px,8-py) for px,py in pts]
    d.line([(x0+px*u,y0+py*u) for px,py in pts],fill=color,width=lw,joint="curve")

# 1) Greca track pants 4200x4050 (base negro)
W,H=4200,4050
img=Image.new("RGBA",(W,H),NEGRO); d=ImageDraw.Draw(img)
tile=420
for r in range(-1,H//tile+2):
    for c in range(-1,W//tile+2):
        meander(d,c*tile,r*tile,tile,ORO,16,flip=(r%2==1))
for r in range(0,H//tile+1,2):
    for c in range(0,W//tile+1):
        crown(d,c*tile+tile*0.5,r*tile+tile*0.5,110,(201,162,75,150),7)
img.convert("RGB").save(f"{OUT}/pant-greca.png"); print("ok pant-greca")

# 2) Terrazo wide-leg 5100x3750 (base crema)
W,H=5100,3750
img=Image.new("RGBA",(W,H),CREMA); d=ImageDraw.Draw(img); rnd=random.Random(31)
cols=[BURDEOS,NAVY,OLIVA,(201,162,75,255),(60,60,66,255)]
for _ in range(1600):
    cx,cy=rnd.randint(0,W),rnd.randint(0,H); r=rnd.randint(20,64); k=rnd.randint(3,6)
    pts=[(cx+r*(0.6+rnd.random()*0.7)*math.cos(2*math.pi*i/k+rnd.random()),cy+r*(0.6+rnd.random()*0.7)*math.sin(2*math.pi*i/k+rnd.random())) for i in range(k)]
    d.polygon(pts,fill=rnd.choice(cols))
for _ in range(40): crown(d,rnd.randint(120,W-120),rnd.randint(120,H-120),130,(201,162,75,230),9)
img.convert("RGB").save(f"{OUT}/pant-terrazo.png"); print("ok pant-terrazo")

# 3) Corona Scatter leggings 3600x3113 (base negro)
W,H=3600,3113
img=Image.new("RGBA",(W,H),NEGRO); d=ImageDraw.Draw(img); rnd=random.Random(41); placed=[]
for _ in range(120):
    for _t in range(20):
        cx,cy=rnd.randint(80,W-80),rnd.randint(80,H-80); w=rnd.choice([150,190,240])
        if all((cx-px)**2+(cy-py)**2>(w*0.8)**2 for px,py,pw in placed):
            placed.append((cx,cy,w)); col=ORO if rnd.random()<0.72 else CREMA; crown(d,cx,cy,w,col,max(7,int(w*0.05))); break
img.convert("RGB").save(f"{OUT}/pant-scatter.png"); print("ok pant-scatter")

# 4) Camuflaje shorts 4200x1650 (base crema)
W,H=4200,1650
img=Image.new("RGBA",(W,H),CREMA); d=ImageDraw.Draw(img); rnd=random.Random(51)
def blob(cx,cy,rad,col):
    pts=[(cx+rad*(0.68+rnd.random()*0.5)*math.cos(2*math.pi*i/14),cy+rad*(0.68+rnd.random()*0.5)*math.sin(2*math.pi*i/14)) for i in range(14)]
    d.polygon(pts,fill=col)
for col in (OLIVA,NAVY,BURDEOS):
    for _ in range(20): blob(rnd.randint(0,W),rnd.randint(0,H),rnd.randint(220,420),col)
for _ in range(28): crown(d,rnd.randint(120,W-120),rnd.randint(120,H-120),120,(201,162,75,210),8)
img.convert("RGB").save(f"{OUT}/pant-camo.png"); print("ok pant-camo")

sheet=Image.new("RGB",(4*380,380),(245,245,245))
for i,n in enumerate(["pant-greca.png","pant-terrazo.png","pant-scatter.png","pant-camo.png"]):
    im=Image.open(f"{OUT}/{n}"); im.thumbnail((370,370)); sheet.paste(im,(i*380+5,5))
sheet.save(f"{OUT}/_pants.jpg",quality=85); print("done")

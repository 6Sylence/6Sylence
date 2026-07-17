# -*- coding: utf-8 -*-
# SRHOOD — calcetines: patrones verticales para calcetín sublimado
import math, os
from PIL import Image, ImageDraw, ImageFont
OUT = os.path.dirname(os.path.abspath(__file__)) + "/prints"
os.makedirs(OUT, exist_ok=True)
ORO=(201,162,75,255); CREMA=(242,234,216,255); BURDEOS=(107,34,49,255); NAVY=(30,42,68,255); NEGRO=(20,21,26,255)
FB="/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
def crown(d,cx,cy,w,color,lw):
    h=w*0.52
    pts=[(cx-w/2,cy+h/2),(cx-w/2,cy-h*0.1),(cx-w*0.25,cy+h*0.05),(cx,cy-h/2),(cx+w*0.25,cy+h*0.05),(cx+w/2,cy-h*0.1),(cx+w/2,cy+h/2),(cx-w/2,cy+h/2)]
    d.line(pts,fill=color,width=lw,joint="curve")
    for i in range(6):
        x=cx-w/2+(i+0.5)*w/6; y=cy+h/2+h*0.22; r=max(1,w*0.035)
        d.ellipse([x-r,y-r,x+r,y+r],fill=color)

# 1) Corona Navy — sublimation sock 1348x5595. Columnas de coronas oro + bandas
W,H=1348,5595
img=Image.new("RGBA",(W,H),NAVY); d=ImageDraw.Draw(img)
# banda superior (caña) burdeos con oro
d.rectangle([0,0,W,520],fill=BURDEOS)
d.line([(0,540),(W,540)],fill=ORO,width=18)
d.line([(0,585),(W,585)],fill=CREMA,width=8)
for c in range(4):
    crown(d, 170+c*340, 260, 220, ORO, 16)
# columnas de coronas
for row in range(6, H//360+1):
    y=row*360
    for c in range(3):
        x=225+c*450
        off=225 if row%2 else 0
        crown(d, x-off*0 + (0 if row%2==0 else 225), y, 180, (201,162,75,235), 13)
# talón/puntera oro
d.rectangle([0,H-360,W,H],fill=ORO)
img.convert("RGB").save(f"{OUT}/sock-corona-navy.png"); print("ok corona-navy")

# 2) Wordmark Burdeos — sublimation sock. SRHOOD vertical repetido en crema
W,H=1348,5595
img=Image.new("RGBA",(W,H),BURDEOS); d=ImageDraw.Draw(img)
d.rectangle([0,0,W,520],fill=NAVY)
d.line([(0,540),(W,540)],fill=ORO,width=18)
f=ImageFont.truetype(FB,300)
d.text((W//2,260),"SRH",font=f,fill=ORO,anchor="mm")
fw=ImageFont.truetype(FB,210)
y=680
while y<H-420:
    d.text((W//2,y),"SRHOOD",font=fw,fill=CREMA,anchor="mm")
    crown(d,W//2,y+230,120,ORO,10)
    y+=520
d.rectangle([0,H-360,W,H],fill=NAVY)
img.convert("RGB").save(f"{OUT}/sock-wordmark-burdeos.png"); print("ok wordmark-burdeos")

# 3) Black Foot Crown — sock 186 700x1200 (x2). Caña crema + banda burdeos coronas; pie va negro
W,H=1400,2400
img=Image.new("RGBA",(W,H),CREMA); d=ImageDraw.Draw(img)
d.rectangle([0,0,W,300],fill=BURDEOS)
for c in range(3): crown(d,235+c*465,150,240,ORO,17)
d.line([(0,330),(W,330)],fill=ORO,width=16)
# columnas de coronas tonales en la caña (parte superior visible)
for row in range(1,5):
    for c in range(3):
        x=235+c*465; off=235 if row%2 else 0
        crown(d,(x if row%2==0 else x-235),430+row*300,150,(107,34,49,180),11)
img.convert("RGB").save(f"{OUT}/sock-blackfoot-crown.png"); print("ok blackfoot")

# hoja de revisión (miniaturas verticales)
sheet=Image.new("RGB",(3*260,760),(245,245,245))
for i,n in enumerate(["sock-corona-navy.png","sock-wordmark-burdeos.png","sock-blackfoot-crown.png"]):
    im=Image.open(f"{OUT}/{n}")
    im.thumbnail((240,740))
    sheet.paste(im,(i*260+10,10))
sheet.save(f"{OUT}/_socks.jpg",quality=88); print("done")

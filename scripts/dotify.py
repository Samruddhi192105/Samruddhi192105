import argparse
from pathlib import Path
from PIL import Image,ImageOps,ImageEnhance
ap=argparse.ArgumentParser(); ap.add_argument("image"); ap.add_argument("-o","--out",required=True); ap.add_argument("--cols",type=int,default=100); ap.add_argument("--equalize",action="store_true"); ap.add_argument("--detail",type=float,default=.5); ap.add_argument("--color",action="store_true"); ap.add_argument("--circle",action="store_true"); a=ap.parse_args()
im=Image.open(a.image).convert("RGBA")
if a.circle:
 side=min(im.size); im=im.crop(((im.width-side)//2,(im.height-side)//2,(im.width+side)//2,(im.height+side)//2))
rows=max(1,round(a.cols*im.height/im.width*.62)); small=im.resize((a.cols,rows),Image.Resampling.LANCZOS); rgb=small.convert("RGB")
if a.equalize: rgb=ImageOps.equalize(rgb)
rgb=ImageEnhance.Contrast(rgb).enhance(1+a.detail*.25); px=rgb.load(); al=small.getchannel("A").load(); W=900; H=round(900*rows/a.cols); dots=[]
for y in range(rows):
 for x in range(a.cols):
  if al[x,y]<20: continue
  r,g,b=px[x,y]; bright=(r+g+b)/765; rad=max(.7,min(W/a.cols*.48,W/a.cols*(.10+.42*(1-bright)))); fill=f"rgb({r},{g},{b})" if a.color else "#39D353"; dots.append(f'<circle cx="{(x+.5)*W/a.cols:.1f}" cy="{(y+.5)*H/rows:.1f}" r="{rad:.2f}" fill="{fill}"/>')
svg=f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}">{"".join(dots)}</svg>'; p=Path(a.out); p.parent.mkdir(parents=True,exist_ok=True); p.with_suffix(".svg").write_text(svg,encoding="utf-8")

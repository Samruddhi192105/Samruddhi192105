import argparse,json,math,urllib.request,html
from pathlib import Path
GREEN="#39D353"; DARK="#0d1117"; LIGHT="#ffffff"; DT="#f0f6fc"; LT="#24292f"
def svg(labels,vals,dark,title):
    bg,fg=(DARK,DT) if dark else (LIGHT,LT); cx=250; cy=250; R=160; n=len(labels)
    def p(r,i):
        a=-math.pi/2+2*math.pi*i/n; return cx+r*math.cos(a),cy+r*math.sin(a)
    def poly(r): return " ".join(f"{p(r,i)[0]:.1f},{p(r,i)[1]:.1f}" for i in range(n))
    rings="".join(f'<polygon points="{poly(R*k/5)}" fill="none" stroke="#57606a" stroke-opacity=".45"/>' for k in range(1,6))
    spokes=""; labels_svg=""
    for i,l in enumerate(labels):
        x,y=p(R,i); x2,y2=p(R+30,i)
        spokes+=f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="#57606a" stroke-opacity=".5"/>'
        anchor="middle" if abs(x2-cx)<15 else ("start" if x2>cx else "end")
        labels_svg+=f'<text x="{x2:.1f}" y="{y2:.1f}" text-anchor="{anchor}" dominant-baseline="middle" font-family="Arial" font-size="13" fill="{fg}">{html.escape(l)}</text>'
    data=" ".join(f"{p(R*v/100,i)[0]:.1f},{p(R*v/100,i)[1]:.1f}" for i,v in enumerate(vals))
    nums="".join(f'<circle cx="{p(R*v/100,i)[0]:.1f}" cy="{p(R*v/100,i)[1]:.1f}" r="4" fill="{GREEN}"/><text x="{p(R*v/100,i)[0]:.1f}" y="{p(R*v/100,i)[1]-9:.1f}" text-anchor="middle" font-family="Arial" font-size="10" fill="{fg}">{v}</text>' for i,v in enumerate(vals))
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="500" height="500"><rect width="500" height="500" rx="18" fill="{bg}"/><text x="250" y="30" text-anchor="middle" font-family="Arial" font-size="18" font-weight="700" fill="{fg}">{html.escape(title)}</text>{rings}{spokes}<polygon points="{data}" fill="{GREEN}" fill-opacity=".18" stroke="{GREEN}" stroke-width="2"/>{nums}{labels_svg}</svg>'
def langs(user,limit):
    q=urllib.request.Request(f"https://api.github.com/users/{user}/repos?per_page=100&type=owner",headers={"User-Agent":"profile-generator"})
    with urllib.request.urlopen(q,timeout=20) as r: repos=json.load(r)
    t={}
    for repo in repos:
        if repo.get("fork"): continue
        try:
            q=urllib.request.Request(repo["languages_url"],headers={"User-Agent":"profile-generator"})
            with urllib.request.urlopen(q,timeout=20) as r: d=json.load(r)
            for k,v in d.items(): t[k]=t.get(k,0)+v
        except: pass
    return sorted(t.items(),key=lambda x:x[1],reverse=True)[:limit]
ap=argparse.ArgumentParser(); ap.add_argument("--data"); ap.add_argument("--github"); ap.add_argument("-o","--out",required=True); ap.add_argument("--limit",type=int,default=7); ap.add_argument("--curve",type=float,default=.4); ap.add_argument("--exclude",default=""); a=ap.parse_args()
out=Path(a.out); out.parent.mkdir(parents=True,exist_ok=True)
if a.data:
    d=json.load(open(a.data,encoding="utf-8")); labels=[x["label"] for x in d["axes"]]; vals=[x["value"] for x in d["axes"]]; title=d["title"]
else:
    try:
        ex={x.strip().lower() for x in a.exclude.split(",")}; items=[x for x in langs(a.github,a.limit) if x[0].lower() not in ex]; m=max(v for _,v in items); labels=[x[0] for x in items]; vals=[round(100*(x[1]/m)**a.curve) for x in items]; title="Repository Languages"
    except:
        labels=["Java","JavaScript","Python","HTML/CSS","SQL"]; vals=[90,80,45,60,55]; title="Repository Languages"
for dark in (True,False):
    (out.parent/(out.name+("-dark.svg" if dark else "-light.svg"))).write_text(svg(labels,vals,dark,title),encoding="utf-8")

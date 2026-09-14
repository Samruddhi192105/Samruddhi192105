import argparse,json,urllib.request,html
from pathlib import Path
GREEN="#39D353"; DARK="#0d1117"; LIGHT="#ffffff"; DT="#f0f6fc"; LT="#24292f"
def api(u):
 q=urllib.request.Request(u,headers={"User-Agent":"profile-generator"}); 
 with urllib.request.urlopen(q,timeout=20) as r:return json.load(r)
def card(title,desc,meta,dark):
 bg,fg=(DARK,DT) if dark else (LIGHT,LT)
 return f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="210"><rect x="2" y="2" width="516" height="206" rx="18" fill="{bg}" stroke="{GREEN}" stroke-width="2"/><text x="28" y="48" font-family="Arial" font-size="23" font-weight="700" fill="{fg}">{html.escape(title)}</text><text x="28" y="84" font-family="Arial" font-size="14" fill="{fg}">{html.escape(desc[:62])}</text><text x="28" y="108" font-family="Arial" font-size="14" fill="{fg}">{html.escape(desc[62:124])}</text><text x="28" y="172" font-family="Arial" font-size="12" fill="{GREEN}">{html.escape(meta)}</text></svg>'
ap=argparse.ArgumentParser(); ap.add_argument("--user",required=True); ap.add_argument("--out",required=True); a=ap.parse_args()
out=Path(a.out); out.mkdir(parents=True,exist_ok=True)
try: repos=api(f"https://api.github.com/users/{a.user}/repos?per_page=100&type=owner")
except: repos=[]
wanted=json.load(open(out/"projects.json",encoding="utf-8"))["projects"]
for p in wanted:
 r=next((x for x in repos if x["name"].lower()==p["repo"].lower()),{})
 meta=f'{r.get("language") or "Project"} | stars {r.get("stargazers_count",0)} | forks {r.get("forks_count",0)}'
 safe=p["repo"].replace("/","-").lower()
 for dark in (True,False):
  (out/f"card-{safe}-{'dark' if dark else 'light'}.svg").write_text(card(p["repo"],p["description"],meta,dark),encoding="utf-8")
try: user=api(f"https://api.github.com/users/{a.user}")
except: user={}
stats=f'{user.get("public_repos",0)} public repos | {user.get("followers",0)} followers'
for dark in (True,False):
 bg,fg=(DARK,DT) if dark else (LIGHT,LT)
 s=f'<svg xmlns="http://www.w3.org/2000/svg" width="520" height="210"><rect x="2" y="2" width="516" height="206" rx="18" fill="{bg}" stroke="{GREEN}" stroke-width="2"/><text x="30" y="52" font-family="Arial" font-size="24" font-weight="700" fill="{fg}">GitHub Activity</text><text x="30" y="96" font-family="Arial" font-size="15" fill="{fg}">{html.escape(stats)}</text><text x="30" y="136" font-family="Arial" font-size="14" fill="{fg}">Generated automatically by GitHub Actions.</text><text x="30" y="174" font-family="Arial" font-size="13" fill="{GREEN}">Self-hosted profile assets</text></svg>'
 (out/f"stats-{'dark' if dark else 'light'}.svg").write_text(s,encoding="utf-8")

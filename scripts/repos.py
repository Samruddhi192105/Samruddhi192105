import argparse,json,urllib.request
from pathlib import Path
def api(url):
    req=urllib.request.Request(url,headers={"User-Agent":"Samruddhi192105-profile"})
    with urllib.request.urlopen(req,timeout=20) as r:return json.load(r)
p=argparse.ArgumentParser();p.add_argument("--user",required=True);p.add_argument("--out",required=True);a=p.parse_args()
repos=api(f"https://api.github.com/users/{a.user}/repos?per_page=100&type=owner&sort=updated")
repos=[r for r in repos if not r.get("fork")]
rows=["| Repository | Language | Stars | Description |","|---|---|---:|---|"]
for r in repos:
    desc=(r.get("description") or "No description").replace("|","-").replace("\n"," ")
    rows.append(f'| [{r["name"]}](https://github.com/{a.user}/{r["name"]}) | {r.get("language") or "—"} | {r.get("stargazers_count",0)} | {desc[:120]} |')
Path(a.out).write_text("\n".join(rows)+"\n",encoding="utf-8")

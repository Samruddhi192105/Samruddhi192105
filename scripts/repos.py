```python
import argparse
import json
import os
from pathlib import Path
import urllib.error
import urllib.request


def api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    req = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.load(r)

    except urllib.error.HTTPError as e:
        if e.code == 403:
            print("GitHub API request was rejected (403).")
            print("Check GITHUB_TOKEN and GitHub API rate limits.")
            return []

        raise


p = argparse.ArgumentParser()
p.add_argument("--user", required=True)
p.add_argument("--out", required=True)
a = p.parse_args()

repos = api(
    f"https://api.github.com/users/{a.user}/repos"
    "?per_page=100&type=owner&sort=updated"
)

repos = [r for r in repos if not r.get("fork")]

rows = [
    "| Repository | Language | Stars | Description |",
    "|---|---|---:|---|"
]

for r in repos:
    desc = (
        (r.get("description") or "No description")
        .replace("|", "-")
        .replace("\n", " ")
    )

    rows.append(
        f'| [{r["name"]}](https://github.com/{a.user}/{r["name"]}) '
        f'| {r.get("language") or "—"} '
        f'| {r.get("stargazers_count", 0)} '
        f'| {desc[:120]} |'
    )

Path(a.out).write_text(
    "\n".join(rows) + "\n",
    encoding="utf-8"
)
```

import argparse
import json
import os
import urllib.error
import urllib.request
from pathlib import Path

GITHUB_API_VERSION = "2022-11-28"
USER_AGENT = "profile-generator"


def api(url):
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(url, headers=headers)

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.load(response)

    except urllib.error.HTTPError as error:
        print(f"GitHub API error: HTTP {error.code}")

        if error.code == 401:
            print("GitHub token is invalid or unauthorized.")
        elif error.code == 403:
            print("GitHub API access was forbidden or the API rate limit was exceeded.")
        elif error.code == 404:
            print("GitHub user or resource was not found.")

        raise


def main():
    parser = argparse.ArgumentParser(
        description="Generate a Markdown table of GitHub repositories."
    )

    parser.add_argument("--user", required=True, help="GitHub username")
    parser.add_argument("--out", required=True, help="Output Markdown file")

    args = parser.parse_args()

    url = (
        f"https://api.github.com/users/{args.user}/repos"
        "?per_page=100"
        "&type=owner"
        "&sort=updated"
    )

    repos = api(url)

    repos = [repo for repo in repos if not repo.get("fork")]

    rows = [
        "| Repository | Language | Stars | Description |",
        "|---|---|---:|---|",
    ]

    for repo in repos:
        name = repo.get("name", "")
        description = repo.get("description") or "No description"

        description = (
            description
            .replace("|", "-")
            .replace("\n", " ")
            .replace("\r", " ")
        )

        language = repo.get("language") or "—"
        stars = repo.get("stargazers_count", 0)

        rows.append(
            f'| [{name}](https://github.com/{args.user}/{name}) '
            f'| {language} '
            f'| {stars} '
            f'| {description[:120]} |'
        )

    output = Path(args.out)

    output.parent.mkdir(parents=True, exist_ok=True)

    output.write_text(
        "\n".join(rows) + "\n",
        encoding="utf-8"
    )

    print(f"Generated {output} with {len(repos)} repositories.")


if __name__ == "__main__":
    main()

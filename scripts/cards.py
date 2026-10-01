```python
import argparse
import html
import json
import os
import urllib.error
import urllib.request
from pathlib import Path


GREEN = "#F5C542"
DARK = "#1A160B"
LIGHT = "#FFFDF5"
DARK_TEXT = "#FFF7D6"
LIGHT_TEXT = "#3B2F14"

GITHUB_API_VERSION = "2022-11-28"
USER_AGENT = "profile-generator"


def api(url):
    """
    Make an authenticated GitHub API request.
    """

    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": GITHUB_API_VERSION,
    }

    token = os.getenv("GITHUB_TOKEN")

    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        headers=headers,
    )

    try:
        with urllib.request.urlopen(
            request,
            timeout=20,
        ) as response:
            return json.load(response)

    except urllib.error.HTTPError as error:
        print(
            f"GitHub API error while requesting {url}: "
            f"HTTP {error.code}"
        )
        raise


def card(title, description, metadata, dark):
    """
    Generate a project card SVG.
    """

    background, foreground = (
        (DARK, DARK_TEXT)
        if dark
        else (LIGHT, LIGHT_TEXT)
    )

    return (
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'width="520" '
        'height="210">'

        f'<rect '
        f'x="2" '
        f'y="2" '
        f'width="516" '
        f'height="206" '
        f'rx="18" '
        f'fill="{background}" '
        f'stroke="{GREEN}" '
        f'stroke-width="2"/>'

        f'<text '
        f'x="28" '
        f'y="48" '
        f'font-family="Arial" '
        f'font-size="23" '
        f'font-weight="700" '
        f'fill="{foreground}">'
        f'{html.escape(title)}'
        f'</text>'

        f'<text '
        f'x="28" '
        f'y="84" '
        f'font-family="Arial" '
        f'font-size="14" '
        f'fill="{foreground}">'
        f'{html.escape(description[:62])}'
        f'</text>'

        f'<text '
        f'x="28" '
        f'y="108" '
        f'font-family="Arial" '
        f'font-size="14" '
        f'fill="{foreground}">'
        f'{html.escape(description[62:124])}'
        f'</text>'

        f'<text '
        f'x="28" '
        f'y="172" '
        f'font-family="Arial" '
        f'font-size="12" '
        f'fill="{GREEN}">'
        f'{html.escape(metadata)}'
        f'</text>'

        '</svg>'
    )


def main():
    parser = argparse.ArgumentParser(
        description="Generate project card SVGs."
    )

    parser.add_argument(
        "--user",
        required=True,
        help="GitHub username.",
    )

    parser.add_argument(
        "--out",
        required=True,
        help="Output directory.",
    )

    args = parser.parse_args()

    output = Path(args.out)

    output.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Get repositories.
    try:
        repos = api(
            f"https://api.github.com/users/{args.user}/repos"
            "?per_page=100"
            "&type=owner"
        )

    except Exception as error:
        print(
            f"Could not fetch repositories: {error}"
        )
        repos = []

    # Load manually selected projects.
    projects_file = output / "projects.json"

    if not projects_file.exists():
        raise FileNotFoundError(
            f"Missing {projects_file}"
        )

    with open(
        projects_file,
        encoding="utf-8",
    ) as file:
        wanted = json.load(file)["projects"]

    # Generate project cards.
    for project in wanted:
        repository = next(
            (
                repo
                for repo in repos
                if repo.get("name", "").lower()
                == project["repo"].lower()
            ),
            {},
        )

        metadata = (
            f'{repository.get("language") or "Project"} '
            f'| stars {repository.get("stargazers_count", 0)} '
            f'| forks {repository.get("forks_count", 0)}'
        )

        safe_name = (
            project["repo"]
            .replace("/", "-")
            .lower()
        )

        for dark in (True, False):
            theme = (
                "dark"
                if dark
                else "light"
            )

            output_file = (
                output
                / f"card-{safe_name}-{theme}.svg"
            )

            output_file.write_text(
                card(
                    project["repo"],
                    project["description"],
                    metadata,
                    dark,
                ),
                encoding="utf-8",
            )

            print(
                f"Generated {output_file}"
            )

    # Generate GitHub activity cards.
    try:
        user = api(
            f"https://api.github.com/users/{args.user}"
        )

    except Exception as error:
        print(
            f"Could not fetch GitHub user information: "
            f"{error}"
        )
        user = {}

    stats = (
        f'{user.get("public_repos", 0)} public repos '
        f'| {user.get("followers", 0)} followers'
    )

    for dark in (True, False):
        background, foreground = (
            (DARK, DARK_TEXT)
            if dark
            else (LIGHT, LIGHT_TEXT)
        )

        theme = (
            "dark"
            if dark
            else "light"
        )

        svg = (
            '<svg '
            'xmlns="http://www.w3.org/2000/svg" '
            'width="520" '
            'height="210">'

            f'<rect '
            f'x="2" '
            f'y="2" '
            f'width="516" '
            f'height="206" '
            f'rx="18" '
            f'fill="{background}" '
            f'stroke="{GREEN}" '
            f'stroke-width="2"/>'

            f'<text '
            f'x="30" '
            f'y="52" '
            f'font-family="Arial" '
            f'font-size="24" '
            f'font-weight="700" '
            f'fill="{foreground}">'
            f'GitHub Activity'
            f'</text>'

            f'<text '
            f'x="30" '
            f'y="96" '
            f'font-family="Arial" '
            f'font-size="15" '
            f'fill="{foreground}">'
            f'{html.escape(stats)}'
            f'</text>'

            f'<text '
            f'x="30" '
            f'y="136" '
            f'font-family="Arial" '
            f'font-size="14" '
            f'fill="{foreground}">'
            f'Generated automatically by GitHub Actions.'
            f'</text>'

            f'<text '
            f'x="30" '
            f'y="174" '
            f'font-family="Arial" '
            f'font-size="13" '
            f'fill="{GREEN}">'
            f'Self-hosted profile assets'
            f'</text>'

            '</svg>'
        )

        output_file = (
            output
            / f"stats-{theme}.svg"
        )

        output_file.write_text(
            svg,
            encoding="utf-8",
        )

        print(
            f"Generated {output_file}"
        )


if __name__ == "__main__":
    main()
```

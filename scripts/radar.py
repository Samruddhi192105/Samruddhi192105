import argparse
import html
import json
import math
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


def github_api(url):
    """
    Make an authenticated GitHub API request.

    In GitHub Actions, GITHUB_TOKEN is provided automatically
    by the workflow.
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


def point(radius, index, count, cx=250, cy=250):
    """
    Calculate the x/y position of a radar point.
    """

    angle = (
        -math.pi / 2
        + 2 * math.pi * index / count
    )

    return (
        cx + radius * math.cos(angle),
        cy + radius * math.sin(angle),
    )


def polygon_points(radius, count):
    """
    Generate the points for one radar polygon.
    """

    points = []

    for index in range(count):
        x, y = point(
            radius,
            index,
            count,
        )

        points.append(
            f"{x:.1f},{y:.1f}"
        )

    return " ".join(points)


def svg(labels, values, dark, title):
    """
    Generate the complete radar chart SVG.
    """

    background, foreground = (
        (DARK, DARK_TEXT)
        if dark
        else (LIGHT, LIGHT_TEXT)
    )

    center_x = 250
    center_y = 250
    radius = 160
    count = len(labels)

    if count == 0:
        raise ValueError(
            "Radar chart requires at least one label."
        )

    # Radar rings.
    rings = "".join(
        f'<polygon '
        f'points="{polygon_points(radius * level / 5, count)}" '
        f'fill="none" '
        f'stroke="#8A7A5A" '
        f'stroke-opacity=".45"/>'
        for level in range(1, 6)
    )

    spokes = ""
    labels_svg = ""

    for index, label in enumerate(labels):
        x, y = point(
            radius,
            index,
            count,
            center_x,
            center_y,
        )

        x2, y2 = point(
            radius + 30,
            index,
            count,
            center_x,
            center_y,
        )

        spokes += (
            f'<line '
            f'x1="{center_x}" '
            f'y1="{center_y}" '
            f'x2="{x:.1f}" '
            f'y2="{y:.1f}" '
            f'stroke="#8A7A5A" '
            f'stroke-opacity=".5"/>'
        )

        if abs(x2 - center_x) < 15:
            anchor = "middle"
        elif x2 > center_x:
            anchor = "start"
        else:
            anchor = "end"

        labels_svg += (
            f'<text '
            f'x="{x2:.1f}" '
            f'y="{y2:.1f}" '
            f'text-anchor="{anchor}" '
            f'dominant-baseline="middle" '
            f'font-family="Arial" '
            f'font-size="13" '
            f'fill="{foreground}">'
            f'{html.escape(str(label))}'
            f'</text>'
        )

    # Main data polygon.
    data_points = []

    for index, value in enumerate(values):
        x, y = point(
            radius * value / 100,
            index,
            count,
            center_x,
            center_y,
        )

        data_points.append(
            f"{x:.1f},{y:.1f}"
        )

    data = " ".join(data_points)

    # Value markers.
    numbers = []

    for index, value in enumerate(values):
        x, y = point(
            radius * value / 100,
            index,
            count,
            center_x,
            center_y,
        )

        numbers.append(
            f'<circle '
            f'cx="{x:.1f}" '
            f'cy="{y:.1f}" '
            f'r="4" '
            f'fill="{GREEN}"/>'
        )

        numbers.append(
            f'<text '
            f'x="{x:.1f}" '
            f'y="{y - 9:.1f}" '
            f'text-anchor="middle" '
            f'font-family="Arial" '
            f'font-size="10" '
            f'fill="{foreground}">'
            f'{value}'
            f'</text>'
        )

    nums = "".join(numbers)

    return (
        '<svg '
        'xmlns="http://www.w3.org/2000/svg" '
        'width="500" '
        'height="500">'
        f'<rect '
        f'width="500" '
        f'height="500" '
        f'rx="18" '
        f'fill="{background}"/>'
        f'<text '
        f'x="250" '
        f'y="30" '
        f'text-anchor="middle" '
        f'font-family="Arial" '
        f'font-size="18" '
        f'font-weight="700" '
        f'fill="{foreground}">'
        f'{html.escape(title)}'
        f'</text>'
        f'{rings}'
        f'{spokes}'
        f'<polygon '
        f'points="{data}" '
        f'fill="{GREEN}" '
        f'fill-opacity=".18" '
        f'stroke="{GREEN}" '
        f'stroke-width="2"/>'
        f'{nums}'
        f'{labels_svg}'
        '</svg>'
    )


def langs(user, limit):
    """
    Calculate repository language usage.

    GitHub reports language usage as bytes per repository.
    We aggregate those values across non-fork repositories.
    """

    repos_url = (
        f"https://api.github.com/users/{user}/repos"
        "?per_page=100"
        "&type=owner"
    )

    repos = github_api(repos_url)

    totals = {}

    for repo in repos:
        if repo.get("fork"):
            continue

        languages_url = repo.get("languages_url")

        if not languages_url:
            continue

        try:
            language_data = github_api(
                languages_url
            )

            for language, byte_count in language_data.items():
                totals[language] = (
                    totals.get(language, 0)
                    + byte_count
                )

        except Exception as error:
            print(
                f"Could not read languages for "
                f"{repo.get('name', 'unknown')}: {error}"
            )

    return sorted(
        totals.items(),
        key=lambda item: item[1],
        reverse=True,
    )[:limit]


def load_data_file(path):
    """
    Load manually defined skill radar data.
    """

    with open(
        path,
        encoding="utf-8",
    ) as file:
        data = json.load(file)

    labels = [
        item["label"]
        for item in data["axes"]
    ]

    values = [
        item["value"]
        for item in data["axes"]
    ]

    title = data["title"]

    return labels, values, title


def generate_repository_radar(
    user,
    limit,
    curve,
    exclude,
):
    """
    Generate the repository language radar.
    """

    excluded = {
        item.strip().lower()
        for item in exclude.split(",")
        if item.strip()
    }

    items = [
        item
        for item in langs(user, limit)
        if item[0].lower() not in excluded
    ]

    if not items:
        raise RuntimeError(
            "No repository language data was returned."
        )

    maximum = max(
        value
        for _, value in items
    )

    labels = [
        language
        for language, _ in items
    ]

    values = [
        round(
            100 * (value / maximum) ** curve
        )
        for _, value in items
    ]

    return labels, values, "Repository Languages"


def main():
    parser = argparse.ArgumentParser(
        description="Generate profile radar SVG assets."
    )

    parser.add_argument(
        "--data",
        help="JSON file containing skill radar data.",
    )

    parser.add_argument(
        "--github",
        help="GitHub username for repository language radar.",
    )

    parser.add_argument(
        "-o",
        "--out",
        required=True,
        help="Output directory/base path.",
    )

    parser.add_argument(
        "--limit",
        type=int,
        default=7,
        help="Number of languages to display.",
    )

    parser.add_argument(
        "--curve",
        type=float,
        default=0.4,
        help="Radar scaling curve.",
    )

    parser.add_argument(
        "--exclude",
        default="",
        help="Comma-separated languages to exclude.",
    )

    args = parser.parse_args()

    output = Path(args.out)

    output.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    # Static skill radar.
    if args.data:
        labels, values, title = load_data_file(
            args.data
        )

    # GitHub repository language radar.
    else:
        try:
            labels, values, title = (
                generate_repository_radar(
                    args.github,
                    args.limit,
                    args.curve,
                    args.exclude,
                )
            )

        except Exception as error:
            print(
                f"Could not generate repository "
                f"language radar: {error}"
            )

            print(
                "Using fallback language values."
            )

            labels = [
                "Java",
                "JavaScript",
                "Python",
                "HTML/CSS",
                "SQL",
            ]

            values = [
                90,
                80,
                45,
                60,
                55,
            ]

            title = "Repository Languages"

    for dark in (True, False):
        suffix = (
            "-dark.svg"
            if dark
            else "-light.svg"
        )

        output_path = (
            output.parent
            / f"{output.name}{suffix}"
        )

        output_path.write_text(
            svg(
                labels,
                values,
                dark,
                title,
            ),
            encoding="utf-8",
        )

        print(
            f"Generated {output_path}"
        )


if __name__ == "__main__":
    main()

import json
import os
import sys
import urllib.request
from datetime import date

from geass import CRIMSON, INK, MUTED, PAPER, VIOLET, esc, gradient_defs, sigil

QUERY = """
query($login: String!) {
  user(login: $login) {
    createdAt
    pullRequests { totalCount }
    contributionsCollection {
      restrictedContributionsCount
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount } }
      }
    }
    repositories(first: 100, ownerAffiliations: OWNER, isFork: false) {
      totalCount
      nodes {
        stargazerCount
        languages(first: 8, orderBy: {field: SIZE, direction: DESC}) {
          edges { size node { name color } }
        }
      }
    }
  }
}
"""


def fetch(login, token):
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=body,
        headers={"Authorization": f"bearer {token}", "Content-Type": "application/json"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if "errors" in payload:
        raise SystemExit(payload["errors"])
    return payload["data"]["user"]


def streaks(days):
    longest = current = run = 0
    for day in days:
        run = run + 1 if day["contributionCount"] > 0 else 0
        longest = max(longest, run)
    for day in reversed(days):
        if day["contributionCount"] > 0:
            current += 1
        elif day["date"] != date.today().isoformat() or current:
            break
    return current, longest


def languages(repos, limit=5):
    totals = {}
    colors = {}
    for repo in repos:
        for edge in repo["languages"]["edges"]:
            name = edge["node"]["name"]
            totals[name] = totals.get(name, 0) + edge["size"]
            colors[name] = edge["node"]["color"] or MUTED
    ranked = sorted(totals.items(), key=lambda item: item[1], reverse=True)
    whole = sum(totals.values()) or 1
    top = [(name, size / whole, colors[name]) for name, size in ranked[:limit]]
    rest = 1 - sum(share for _, share, _ in top)
    if rest > 0.005:
        top.append(("Other", rest, "#4a3d5c"))
    return top


def render(login, user):
    collection = user["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    days = [day for week in calendar["weeks"] for day in week["contributionDays"]]
    current, longest = streaks(days)
    repos = user["repositories"]["nodes"]
    stars = sum(repo["stargazerCount"] for repo in repos)
    langs = languages(repos)
    since = user["createdAt"][:4]

    articles = [
        ("I", "Contributions sworn this year", calendar["totalContributions"]),
        ("II", "Cast in the shadows", collection["restrictedContributionsCount"]),
        ("III", "Pull requests that obeyed", user["pullRequests"]["totalCount"]),
        ("IV", "Repositories under command", user["repositories"]["totalCount"]),
        ("V", "Longest unbroken streak", f"{longest} days"),
        ("VI", "Days bound by the contract", (date.today() - date.fromisoformat(user["createdAt"][:10])).days),
    ]

    width, height = 900, 470
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">',
        "<defs>",
        gradient_defs(),
        '<linearGradient id="paper" x1="0" y1="0" x2="1" y2="1">'
        '<stop offset="0" stop-color="#140a1f"/><stop offset="1" stop-color="#0b0610"/></linearGradient>',
        '<radialGradient id="aura" cx="0.5" cy="0.5" r="0.5">'
        f'<stop offset="0" stop-color="{CRIMSON}" stop-opacity="0.35"/>'
        f'<stop offset="1" stop-color="{CRIMSON}" stop-opacity="0"/></radialGradient>',
        "<style>"
        ".serif{font-family:'Cormorant Garamond','Palatino Linotype','Book Antiqua',Georgia,serif}"
        ".mono{font-family:'JetBrains Mono','Fira Code',Consolas,monospace}"
        ".sans{font-family:'Segoe UI','Helvetica Neue',Arial,sans-serif}"
        ".pulse{animation:pulse 3.6s ease-in-out infinite;transform-origin:760px 150px}"
        ".spin{animation:spin 50s linear infinite;transform-origin:760px 150px}"
        "@keyframes pulse{0%,100%{opacity:.75}50%{opacity:1}}"
        "@keyframes spin{to{transform:rotate(360deg)}}"
        "@media (prefers-reduced-motion:reduce){.pulse,.spin{animation:none}}"
        "</style>",
        "</defs>",
        f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="14" fill="url(#paper)" stroke="{VIOLET}" stroke-opacity=".55"/>',
        f'<rect x="12" y="12" width="{width - 24}" height="{height - 24}" rx="9" fill="none" stroke="{CRIMSON}" stroke-opacity=".35" stroke-dasharray="2 6"/>',
        f'<text x="44" y="64" class="mono" font-size="13" letter-spacing="5" fill="{CRIMSON}">GEASS CONTRACT · 契約</text>',
        f'<text x="44" y="104" class="serif" font-size="36" font-style="italic" fill="{PAPER}">The power of the King</text>',
        f'<text x="44" y="140" class="serif" font-size="36" font-style="italic" fill="{PAPER}">will make you lonely.</text>',
        f'<text x="46" y="166" class="sans" font-size="13" fill="{MUTED}">— C.C., to the one who accepted the contract</text>',
        '<circle class="pulse" cx="760" cy="150" r="120" fill="url(#aura)"/>',
        f'<circle class="spin" cx="760" cy="150" r="92" fill="none" stroke="{CRIMSON}" stroke-opacity=".5" stroke-dasharray="3 9"/>',
        '<g class="pulse">' + sigil(760, 150, 0.9, extra='filter="url(#glow)"') + "</g>",
    ]

    y = 214
    for numeral, label, value in articles:
        parts.append(
            "<g>"
            f'<text x="44" y="{y}" class="mono" font-size="12" fill="{CRIMSON}">ART. {numeral}</text>'
            f'<text x="120" y="{y}" class="sans" font-size="15" fill="{PAPER}">{esc(label)}</text>'
            f'<line x1="120" y1="{y + 8}" x2="520" y2="{y + 8}" stroke="{MUTED}" stroke-opacity=".18"/>'
            f'<text x="520" y="{y}" text-anchor="end" class="mono" font-size="16" font-weight="700" fill="{PAPER}">{esc(value)}</text>'
            "</g>"
        )
        y += 34

    bar_x, bar_y, bar_w = 600, 300, 256
    parts.append(f'<text x="{bar_x}" y="{bar_y - 22}" class="mono" font-size="12" letter-spacing="3" fill="{CRIMSON}">LANGUAGES OF POWER</text>')
    offset = bar_x
    for name, share, color in langs:
        segment = max(bar_w * share, 2)
        parts.append(f'<rect x="{offset:.1f}" y="{bar_y}" width="{segment:.1f}" height="10" fill="{color}"/>')
        offset += segment
    legend_y = bar_y + 34
    for index, (name, share, color) in enumerate(langs):
        column = index % 2
        row = index // 2
        lx = bar_x + column * 132
        ly = legend_y + row * 24
        parts.append(
            f'<circle cx="{lx + 5}" cy="{ly - 4}" r="5" fill="{color}"/>'
            f'<text x="{lx + 16}" y="{ly}" class="sans" font-size="13" fill="{PAPER}">{esc(name)}'
            f'<tspan fill="{MUTED}"> {share * 100:.1f}%</tspan></text>'
        )

    parts += [
        f'<line x1="44" y1="{height - 54}" x2="{width - 44}" y2="{height - 54}" stroke="{VIOLET}" stroke-opacity=".35"/>',
        f'<text x="44" y="{height - 26}" class="serif" font-size="22" font-style="italic" fill="{PAPER}">{esc(login)}</text>',
        f'<text x="{44 + len(login) * 11 + 14}" y="{height - 27}" class="mono" font-size="12" fill="{MUTED}">contract holder since {since}</text>',
        f'<text x="{width - 44}" y="{height - 27}" text-anchor="end" class="mono" font-size="12" fill="{MUTED}">'
        f'streak {current}d · ★ {stars} · renewed {date.today().isoformat()}</text>',
        "</svg>",
    ]
    return "\n".join(parts)


def main():
    login = os.environ.get("GITHUB_USER", "Sotonush")
    token = os.environ.get("PROFILE_TOKEN") or os.environ["GITHUB_TOKEN"]
    output = sys.argv[1] if len(sys.argv) > 1 else "assets/contract.svg"
    svg = render(login, fetch(login, token))
    with open(output, "w", encoding="utf-8") as file:
        file.write(svg)


if __name__ == "__main__":
    main()

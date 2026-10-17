"""Generate assets/stats.svg and assets/commit-langs.svg from the GitHub API.

Usage:
  python scripts/generate_stats.py USERNAME          (needs GH_TOKEN or GITHUB_TOKEN)
  python scripts/generate_stats.py USERNAME --demo   (sample numbers, for a layout preview only)
  python scripts/generate_stats.py USERNAME --placeholder   (empty state, no network)

Only the Python standard library is used.
"""
import argparse
import collections
import datetime
import json
import os
import sys
import urllib.error
import urllib.request
from xml.sax.saxutils import escape

OUT = "assets"
C = dict(
    bg="#041C38", panel="#0C3B57", red="#DE0202", maroon="#810D10",
    gold="#DCB318", silver="#C4CBCB", qsilver="#AEA4A2", gray="#989A9B",
)
FONT = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"

EXT = {
    ".py": "Python", ".js": "JavaScript", ".jsx": "JavaScript", ".mjs": "JavaScript",
    ".ts": "TypeScript", ".tsx": "TypeScript", ".php": "PHP", ".html": "HTML",
    ".css": "CSS", ".scss": "CSS", ".java": "Java", ".c": "C", ".cpp": "C++",
    ".sql": "SQL", ".prisma": "Prisma", ".sh": "Shell", ".md": "Markdown",
    ".json": "JSON", ".yml": "YAML", ".yaml": "YAML", ".vue": "Vue", ".go": "Go",
}
SKIP = {"JSON", "YAML", "Markdown"}


def api(path, token, data=None):
    req = urllib.request.Request(
        "https://api.github.com" + path,
        data=json.dumps(data).encode() if data else None,
        headers={
            "Authorization": f"bearer {token}",
            "User-Agent": "profile-readme-stats",
            "Accept": "application/vnd.github+json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", "replace")[:500]
        raise RuntimeError(f"GitHub API {e.code} on {path}: {body}") from None


def fetch_stats(user, token):
    q = """query($login:String!){user(login:$login){
      repositories(ownerAffiliation:OWNER,isFork:false,privacy:PUBLIC,first:100){totalCount nodes{stargazerCount}}
      contributionsCollection{totalCommitContributions totalPullRequestContributions
        totalIssueContributions contributionCalendar{totalContributions}}}}"""
    d = api("/graphql", token, {"query": q, "variables": {"login": user}})["data"]["user"]
    cc = d["contributionsCollection"]
    return {
        "Contributions (12 mo)": cc["contributionCalendar"]["totalContributions"],
        "Commits": cc["totalCommitContributions"],
        "Pull requests": cc["totalPullRequestContributions"],
        "Issues": cc["totalIssueContributions"],
        "Stars earned": sum(n["stargazerCount"] for n in d["repositories"]["nodes"]),
        "Public repos": d["repositories"]["totalCount"],
    }


def fetch_langs(user, token, days=30, max_commits=60):
    since = (datetime.datetime.now(datetime.timezone.utc) -datetime.timedelta(days=days)).strftime("%Y-%m-%dT%H:%M:%SZ")
    repos = api(f"/users/{user}/repos?type=owner&sort=pushed&per_page=15", token)
    added, removed = collections.Counter(), collections.Counter()
    seen = 0
    for r in repos:
        if r.get("fork"):
            continue
        try:
            commits = api(f"/repos/{user}/{r['name']}/commits?author={user}&since={since}&per_page=30", token)
        except Exception:
            continue
        for c in commits:
            if seen >= max_commits:
                break
            seen += 1
            try:
                detail = api(f"/repos/{user}/{r['name']}/commits/{c['sha']}", token)
            except Exception:
                continue
            for f in detail.get("files", []):
                ext = os.path.splitext(f["filename"])[1].lower()
                lang = EXT.get(ext)
                if not lang or lang in SKIP:
                    continue
                added[lang] += f.get("additions", 0)
                removed[lang] += f.get("deletions", 0)
    return added, removed


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.join(OUT, name))


def fmt(n):
    return "-" if n is None else f"{n:,}"


def stats_svg(stats, note=None):
    w, h = 900, 250
    tiles = []
    items = list(stats.items())
    tw, th, gap = 276, 88, 22
    for i, (label, val) in enumerate(items):
        col, row = i % 3, i // 3
        x, y = 0 + col * (tw + gap), 16 + row * (th + 14)
        tiles.append(
            f'<g transform="translate({x},{y})">'
            f'<rect width="{tw}" height="{th}" rx="12" fill="{C["panel"]}"/>'
            f'<rect width="6" height="{th}" rx="3" fill="{C["red"] if (i % 2 == 0) else C["gold"]}"/>'
            f'<text x="28" y="40" font-family="{MONO}" font-size="14" fill="{C["qsilver"]}">{escape(label)}</text>'
            f'<text x="28" y="72" font-family="{FONT}" font-size="30" font-weight="800" fill="{C["silver"]}">{fmt(val)}</text>'
            f'</g>'
        )
    foot = escape(note) if note else "Updated daily by GitHub Actions"
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="GitHub stats">
  <rect width="{w}" height="{h}" rx="14" fill="{C['bg']}"/>
  <g transform="translate(16,0)">{''.join(tiles)}</g>
  <text x="{w - 16}" y="{h - 10}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{C['gray']}">{foot}</text>
</svg>
"""


def langs_svg(added, removed, note=None):
    langs = sorted(added.keys() | removed.keys(), key=lambda k: -(added[k] + removed[k]))[:6]
    w = 900
    row_h = 42
    h = 70 + max(len(langs), 1) * row_h + 34
    parts = [
        f'<rect width="{w}" height="{h}" rx="14" fill="{C["bg"]}"/>',
        f'<text x="24" y="36" font-family="{MONO}" font-size="15" fill="{C["silver"]}">Lines changed per language, last 30 days</text>',
        f'<rect x="{w - 250}" y="24" width="12" height="12" rx="2" fill="{C["gold"]}"/>'
        f'<text x="{w - 232}" y="35" font-family="{MONO}" font-size="13" fill="{C["qsilver"]}">added</text>'
        f'<rect x="{w - 160}" y="24" width="12" height="12" rx="2" fill="{C["red"]}"/>'
        f'<text x="{w - 142}" y="35" font-family="{MONO}" font-size="13" fill="{C["qsilver"]}">removed</text>',
    ]
    if not langs:
        parts.append(
            f'<text x="{w // 2}" y="{h // 2 + 8}" text-anchor="middle" font-family="{MONO}" font-size="15" fill="{C["gray"]}">'
            f'{escape(note or "No commits in the last 30 days")}</text>'
        )
    else:
        mx = max(max(added[k], removed[k]) for k in langs) or 1
        bar_x, bar_w = 170, 560
        for i, k in enumerate(langs):
            y = 64 + i * row_h
            a = max(int(bar_w * added[k] / mx), 2)
            r = max(int(bar_w * removed[k] / mx), 2) if removed[k] else 0
            parts.append(
                f'<text x="24" y="{y + 22}" font-family="{MONO}" font-size="15" fill="{C["silver"]}">{escape(k)}</text>'
                f'<rect x="{bar_x}" y="{y + 4}" width="{a}" height="12" rx="6" fill="{C["gold"]}"/>'
                f'<rect x="{bar_x}" y="{y + 20}" width="{r}" height="12" rx="6" fill="{C["red"]}"/>'
                f'<text x="{bar_x + bar_w + 20}" y="{y + 16}" font-family="{MONO}" font-size="13" fill="{C["gold"]}">+{added[k]:,}</text>'
                f'<text x="{bar_x + bar_w + 20}" y="{y + 32}" font-family="{MONO}" font-size="13" fill="{C["red"]}">-{removed[k]:,}</text>'
            )
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Lines changed per language">'
        + "".join(parts)
        + f'<text x="{w - 16}" y="{h - 10}" text-anchor="end" font-family="{MONO}" font-size="12" fill="{C["gray"]}">Updated daily by GitHub Actions</text></svg>\n'
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("user")
    ap.add_argument("--demo", action="store_true")
    ap.add_argument("--placeholder", action="store_true")
    a = ap.parse_args()

    if a.placeholder:
        empty = {k: None for k in ["Contributions (12 mo)", "Commits", "Pull requests", "Issues", "Stars earned", "Public repos"]}
        write("stats.svg", stats_svg(empty, "Fills in after the first workflow run"))
        write("commit-langs.svg", langs_svg(collections.Counter(), collections.Counter(), "Fills in after the first workflow run"))
        return
    if a.demo:
        s = {"Contributions (12 mo)": 412, "Commits": 361, "Pull requests": 9, "Issues": 4, "Stars earned": 7, "Public repos": 12}
        add = collections.Counter({"TypeScript": 5200, "PHP": 2100, "Python": 1500, "CSS": 900, "HTML": 600})
        rem = collections.Counter({"TypeScript": 1800, "PHP": 700, "Python": 300, "CSS": 350, "HTML": 90})
        write("stats-demo.svg", stats_svg(s, "DEMO DATA, not real"))
        write("commit-langs-demo.svg", langs_svg(add, rem))
        return

    token = os.environ.get("GH_TOKEN") or os.environ.get("GITHUB_TOKEN")
    if not token:
        sys.exit("Set GH_TOKEN or GITHUB_TOKEN")
    failed = False
    try:
        write("stats.svg", stats_svg(fetch_stats(a.user, token)))
    except Exception as e:
        failed = True
        print(f"ERROR stats: {e}", file=sys.stderr)
    try:
        add, rem = fetch_langs(a.user, token)
        write("commit-langs.svg", langs_svg(add, rem))
    except Exception as e:
        failed = True
        print(f"ERROR commit-langs: {e}", file=sys.stderr)
    if failed:
        sys.exit(1)


if __name__ == "__main__":
    main()

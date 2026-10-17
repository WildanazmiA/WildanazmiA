"""Build the static SVG assets for the profile README.

Run from the repo root:  python scripts/build_assets.py
Output goes to ./assets
Palette: Maastricht/Prussian blue base, Electric Red and Urobilin gold accents, Chinese Silver text.
"""
import os
from xml.sax.saxutils import escape

OUT = "assets"
C = dict(
    bg="#041C38", panel="#0C3B57", deep="#0A2A46",
    red="#DE0202", maroon="#810D10", blood="#5A111D",
    gold="#DCB318", silver="#C4CBCB", qsilver="#AEA4A2",
    gray="#989A9B", olive="#383736",
)
FONT = "'Segoe UI','Helvetica Neue',Helvetica,Arial,sans-serif"
MONO = "'SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"


def write(name, svg):
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, name), "w", encoding="utf-8") as f:
        f.write(svg)
    print("wrote", os.path.join(OUT, name))


def header():
    w, h = 1200, 320
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="Wildan, Cybersecurity Enthusiast">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="{C['bg']}"/><stop offset="1" stop-color="{C['panel']}"/>
    </linearGradient>
    <linearGradient id="red" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{C['maroon']}"/><stop offset="1" stop-color="{C['red']}"/>
    </linearGradient>
    <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
      <path d="M40 0H0V40" fill="none" stroke="{C['silver']}" stroke-opacity="0.05"/>
    </pattern>
    <clipPath id="card"><rect width="{w}" height="{h}" rx="18"/></clipPath>
  </defs>
  <g clip-path="url(#card)">
    <rect width="{w}" height="{h}" fill="url(#bg)"/>
    <rect width="{w}" height="{h}" fill="url(#grid)"/>
    <polygon points="900,0 1060,0 860,320 700,320" fill="url(#red)">
      <animate attributeName="opacity" values="0;0.95" dur="0.9s" fill="freeze"/>
    </polygon>
    <polygon points="1075,0 1105,0 905,320 875,320" fill="{C['gold']}">
      <animate attributeName="opacity" values="0;1" dur="1.1s" fill="freeze"/>
    </polygon>
    <polygon points="1120,0 1135,0 935,320 920,320" fill="{C['silver']}" opacity="0.8">
      <animate attributeName="opacity" values="0;0.8" dur="1.3s" fill="freeze"/>
    </polygon>
    <rect x="0" y="312" width="{w}" height="8" fill="{C['red']}"/>
    <rect x="0" y="312" width="260" height="8" fill="{C['gold']}"/>

    <text x="60" y="62" font-family="{MONO}" font-size="20" fill="{C['gold']}">root@wildan:~$ whoami<tspan fill="{C['red']}">_<animate attributeName="opacity" values="1;0;1" dur="1.2s" repeatCount="indefinite"/></tspan></text>

    <text x="66" y="196" font-family="{FONT}" font-size="118" font-weight="900" letter-spacing="10" fill="{C['red']}" opacity="0.9">WILDAN
      <animate attributeName="opacity" values="0;0.9" dur="0.8s" fill="freeze"/></text>
    <text x="60" y="190" font-family="{FONT}" font-size="118" font-weight="900" letter-spacing="10" fill="{C['silver']}">WILDAN
      <animate attributeName="opacity" values="0;1" dur="0.8s" fill="freeze"/></text>

    <text x="62" y="240" font-family="{FONT}" font-size="28" font-weight="600" fill="{C['silver']}">Moh. Wildan Azmi Abdullah
      <animate attributeName="opacity" values="0;1" dur="0.6s" begin="0.5s" fill="freeze"/></text>
    <text x="62" y="272" font-family="{FONT}" font-size="19" fill="{C['gold']}">Informatics Engineering Student  ·  Cybersecurity Enthusiast
      <animate attributeName="opacity" values="0;1" dur="0.6s" begin="0.9s" fill="freeze"/></text>
    <text x="62" y="297" font-family="{FONT}" font-size="19" fill="{C['qsilver']}">Aspiring Junior Pentester
      <animate attributeName="opacity" values="0;1" dur="0.6s" begin="1.2s" fill="freeze"/></text>

    <circle cx="1130" cy="36" r="6" fill="{C['red']}"/>
    <circle cx="1152" cy="36" r="6" fill="{C['gold']}"/>
    <circle cx="1174" cy="36" r="6" fill="{C['gray']}"/>
  </g>
</svg>
"""
    write("header.svg", svg)


def section(name, number, title):
    w, h = 900, 60
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">
  <defs>
    <linearGradient id="line" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="{C['red']}"/><stop offset="1" stop-color="{C['red']}" stop-opacity="0"/>
    </linearGradient>
  </defs>
  <rect width="{w}" height="{h}" rx="10" fill="{C['bg']}"/>
  <rect x="16" y="13" width="6" height="34" rx="3" fill="{C['red']}"/>
  <text x="38" y="38" font-family="{MONO}" font-size="16" fill="{C['gold']}">{number}</text>
  <text x="76" y="39" font-family="{FONT}" font-size="24" font-weight="800" letter-spacing="3" fill="{C['silver']}">{escape(title.upper())}</text>
  <rect x="0" y="56" width="{w}" height="2" fill="url(#line)"/>
</svg>
"""
    write(name, svg)


def about():
    rows = [
        ("campus", "Informatics Engineering, UMKT (semester 3)"),
        ("focus", "Cybersecurity, aiming for Junior Pentester"),
        ("learning", "TryHackMe, Cisco Ethical Hacker, Linux"),
        ("building", "EventSpace, local event discovery in Samarinda"),
        ("background", "SMK TKJ, networking fundamentals"),
        ("lab", "Kali Linux in VirtualBox, cyber range"),
        ("off the clock", "Piano and songwriting"),
    ]
    w = 900
    top = 62
    step = 34
    h = top + step * len(rows) + 26
    lines = []
    for i, (k, v) in enumerate(rows):
        y = top + 16 + i * step
        lines.append(
            f'<g opacity="0"><animate attributeName="opacity" values="0;1" dur="0.4s" begin="{0.3 + i * 0.25:.2f}s" fill="freeze"/>'
            f'<text x="36" y="{y}" font-family="{MONO}" font-size="17" fill="{C["gold"]}">{escape(k)}</text>'
            f'<text x="220" y="{y}" font-family="{MONO}" font-size="17" fill="{C["red"]}">:</text>'
            f'<text x="240" y="{y}" font-family="{MONO}" font-size="17" fill="{C["silver"]}">{escape(v)}</text></g>'
        )
    body = "\n  ".join(lines)
    svg = f"""<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="About Wildan">
  <rect width="{w}" height="{h}" rx="14" fill="{C['bg']}" stroke="{C['panel']}" stroke-width="2"/>
  <rect x="1" y="1" width="{w - 2}" height="40" rx="13" fill="{C['panel']}"/>
  <rect x="1" y="26" width="{w - 2}" height="15" fill="{C['panel']}"/>
  <circle cx="26" cy="21" r="6" fill="{C['red']}"/><circle cx="48" cy="21" r="6" fill="{C['gold']}"/><circle cx="70" cy="21" r="6" fill="{C['gray']}"/>
  <text x="96" y="26" font-family="{MONO}" font-size="14" fill="{C['qsilver']}">wildan@github: ~/about</text>
  {body}
</svg>
"""
    write("about.svg", svg)


if __name__ == "__main__":
    header()
    about()
    section("title-about.svg", "01", "About me")
    section("title-stats.svg", "02", "Stats")
    section("title-stack.svg", "03", "Tech stack")
    section("title-commits.svg", "04", "What I actually commit")
    section("title-contrib.svg", "05", "Contributions")
    section("title-music.svg", "06", "Now playing")
    section("title-connect.svg", "07", "Let's connect")

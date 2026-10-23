import sys, os
OUT = sys.argv[1] if len(sys.argv) > 1 else "assets"
MONO = "ui-monospace,'SFMono-Regular','JetBrains Mono',Menlo,Consolas,monospace"
SANS = "'Helvetica Neue',Helvetica,Arial,sans-serif"

def common_defs(w, h):
    return f'''<defs>
<pattern id="scan" width="4" height="4" patternUnits="userSpaceOnUse"><rect width="4" height="1" fill="#000" opacity=".4"/></pattern>
<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" seed="7"/><feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  0 0 0 .9 0"/></filter>
<radialGradient id="vig" cx="50%" cy="50%" r="75%"><stop offset="55%" stop-color="#000" stop-opacity="0"/><stop offset="100%" stop-color="#000" stop-opacity=".85"/></radialGradient>
<linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#5a0c0c"/><stop offset=".55" stop-color="#2a0606"/><stop offset="1" stop-color="#0a0a0a"/></linearGradient>
</defs>'''

def overlay(w, h):
    return f'''<rect width="{w}" height="{h}" filter="url(#noise)" opacity=".07"/>
<g class="roll"><rect y="-8" width="{w}" height="{h+16}" fill="url(#scan)"/></g>
<rect width="{w}" height="{h}" fill="url(#vig)"/>
<rect class="flick" width="{w}" height="{h}" fill="#fff" opacity="0"/>'''

CSS_BASE = '''
.roll{animation:roll 1.6s linear infinite}
@keyframes roll{to{transform:translateY(4px)}}
.flick{animation:flick 7s steps(1) infinite}
@keyframes flick{0%,100%{opacity:0}61%{opacity:.04}62%{opacity:0}63%{opacity:.06}64%{opacity:0}}
.blink{animation:blink 1.1s steps(1) infinite}
@keyframes blink{50%{opacity:0}}
.in{animation:in 5s infinite steps(1)}
@keyframes in{0%,100%{opacity:1}47%{opacity:.35}48%{opacity:1}83%{opacity:.5}84%{opacity:1}}
'''

def pole(x, base, top, s=1.0):
    p = [f'<rect x="{x-3*s}" y="{top}" width="{6*s}" height="{base-top}" fill="#000"/>']
    for i, (dy, half) in enumerate([(14, 46), (34, 34)]):
        y = top + dy*s
        p.append(f'<rect x="{x-half*s}" y="{y}" width="{2*half*s}" height="{4*s}" fill="#000"/>')
        for k in (-1, 0, 1):
            p.append(f'<rect x="{x + k*half*s*0.85 - 2*s}" y="{y-7*s}" width="{4*s}" height="{7*s}" fill="#000"/>')
    return "\n".join(p)

def hero():
    w, h = 900, 380
    name = "AMIR SULEIMANOV"
    wires = []
    for i, (ya, yb, sag) in enumerate([(92, 120, 38), (100, 128, 44), (112, 140, 50), (132, 150, 40)]):
        wires.append(f'<path d="M -10 {ya} Q 330 {ya+sag} 640 {yb-30} T 905 {yb}" stroke="#000" stroke-width="1.6" fill="none"/>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{common_defs(w, h)}
<style>{CSS_BASE}
.r{{animation:gr 3.2s infinite steps(1)}} .c{{animation:gc 3.2s infinite steps(1)}} .m{{animation:gm 3.2s infinite steps(1)}}
@keyframes gr{{0%,100%{{transform:translate(-2px,0)}}20%{{transform:translate(-6px,1px)}}22%{{transform:translate(3px,-1px)}}24%{{transform:translate(-2px,0)}}71%{{transform:translate(-9px,0)}}73%{{transform:translate(-2px,0)}}}}
@keyframes gc{{0%,100%{{transform:translate(2px,0)}}20%{{transform:translate(6px,-1px)}}22%{{transform:translate(-3px,1px)}}24%{{transform:translate(2px,0)}}71%{{transform:translate(9px,0)}}73%{{transform:translate(2px,0)}}}}
@keyframes gm{{0%,100%{{transform:none}}20%{{transform:skewX(-8deg)}}21%{{transform:none}}71%{{transform:translateX(4px)}}72%{{transform:none}}}}
.t1{{animation-delay:.3s}} .t2{{animation-delay:1.1s}} .t3{{animation-delay:1.9s}} .t4{{animation-delay:2.6s}}
</style>
<rect width="{w}" height="{h}" fill="#0a0a0a"/>
<rect width="{w}" height="210" fill="url(#sky)"/>
{"".join(wires)}
{pole(700, 230, 60, 1.25)}
{pole(860, 230, 84, 0.9)}
<rect y="205" width="{w}" height="{h-205}" fill="#0a0a0a"/>
<text x="40" y="58" font-family="{MONO}" font-size="13" letter-spacing="4" fill="#e9e4dc" class="in t1">PRESENT DAY</text>
<text x="40" y="80" font-family="{MONO}" font-size="13" letter-spacing="4" fill="#e9e4dc" class="in t2">PRESENT TIME.</text>
<text x="40" y="102" font-family="{MONO}" font-size="12" letter-spacing="2" fill="#ff4d4d" class="in t3">hahahaha<tspan class="blink">_</tspan></text>
<g font-family="{SANS}" font-weight="900" font-size="66" letter-spacing="2">
<text x="40" y="280" fill="#ff2a3d" opacity=".85" class="r">{name}</text>
<text x="40" y="280" fill="#2ee6ff" opacity=".75" class="c">{name}</text>
<text x="40" y="280" fill="#f2efe9" class="m">{name}</text>
</g>
<text x="42" y="314" font-family="{MONO}" font-size="15" letter-spacing="2" fill="#b9b2a8">full-stack developer · tech lead · bishkek, kg</text>
<text x="42" y="350" font-family="{MONO}" font-size="13" fill="#ff4d4d" class="in t4">&gt; <tspan fill="#e9e4dc">connection established</tspan><tspan class="blink" fill="#e9e4dc">█</tspan></text>
<text x="858" y="350" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="3" fill="#6b6259">LAYER:00 · 接続中</text>
{overlay(w, h)}
</svg>'''
    open(os.path.join(OUT, "hero.svg"), "w", encoding="utf-8").write(svg)

def nodes():
    w, h = 900, 440
    cx, cy = 450, 210
    items = [
        (150, 110, "node:01", "e-commerce ecosystem", "crm · store · delivery · payments", "ONLINE", "tech lead · launching soon"),
        (750, 110, "node:02", "medtech saas", "rbac · keycloak · inpatient · cashier", "ARCHIVED", "2025.07 — 2026.05"),
        (150, 310, "node:03", "clinic messaging", "whatsapp · ai assistant", "OFFLINE", "freelance · 2025"),
        (750, 310, "node:04", "own multi-tenant saas", "tenant isolation · 220+ tests · ci/cd", "RUNNING", "in development"),
    ]
    parts = []
    for i, (x, y, nid, title, sub, st, note) in enumerate(items):
        pid = f"w{i}"
        mx = (cx + x) / 2
        d = f"M {cx} {cy} C {mx} {cy} {mx} {y} {x} {y}"
        parts.append(f'<path id="{pid}" d="{d}" stroke="#3a2a2a" stroke-width="1.4" fill="none" stroke-dasharray="3 4"/>')
        dur = 2.4 + i * 0.5
        parts.append(f'<circle r="3" fill="#ff3347"><animateMotion dur="{dur}s" repeatCount="indefinite" begin="{i*0.4}s"><mpath href="#{pid}"/></animateMotion></circle>')
        live = st in ("ONLINE", "RUNNING")
        col = "#ff3347" if live else "#6b6259"
        anchor = "start" if x < cx else "end"
        tx = x + 16 if x < cx else x - 16
        parts.append(f'<rect x="{x-7}" y="{y-7}" width="14" height="14" fill="#0a0a0a" stroke="#e9e4dc" stroke-width="1.4"/>')
        parts.append(f'<rect x="{x-3}" y="{y-3}" width="6" height="6" fill="{col}" class="{"blink" if live else ""}"/>')
        ty = y - 34 if y < cy else y + 30
        parts.append(f'<text x="{tx}" y="{ty}" text-anchor="{anchor}" font-family="{MONO}" font-size="11" letter-spacing="2" fill="#6b6259">{nid} · <tspan fill="{col}">{st}</tspan></text>')
        parts.append(f'<text x="{tx}" y="{ty+20}" text-anchor="{anchor}" font-family="{SANS}" font-weight="800" font-size="19" fill="#f2efe9">{title}</text>')
        parts.append(f'<text x="{tx}" y="{ty+38}" text-anchor="{anchor}" font-family="{MONO}" font-size="12" fill="#b9b2a8">{sub}</text>')
        parts.append(f'<text x="{tx}" y="{ty+54}" text-anchor="{anchor}" font-family="{MONO}" font-size="11" fill="#6b6259">{note}</text>')
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{common_defs(w, h)}
<style>{CSS_BASE}
.pulse{{animation:pulse 2.4s ease-out infinite;transform-origin:{cx}px {cy}px}}
@keyframes pulse{{0%{{transform:scale(.6);opacity:.9}}100%{{transform:scale(2.4);opacity:0}}}}
</style>
<rect width="{w}" height="{h}" fill="#0a0a0a"/>
<text x="30" y="34" font-family="{MONO}" font-size="11" letter-spacing="3" fill="#6b6259">THE WIRED · NODE MAP</text>
<text x="870" y="34" text-anchor="end" font-family="{MONO}" font-size="11" letter-spacing="3" fill="#6b6259">4 NODES · 2 LIVE</text>
{"".join(parts)}
<circle cx="{cx}" cy="{cy}" r="26" fill="none" stroke="#ff3347" stroke-width="1.2" class="pulse"/>
<circle cx="{cx}" cy="{cy}" r="24" fill="#0a0a0a" stroke="#e9e4dc" stroke-width="1.6"/>
<text x="{cx}" y="{cy+5}" text-anchor="middle" font-family="{MONO}" font-weight="700" font-size="13" letter-spacing="2" fill="#f2efe9">AMIR</text>
<text x="{cx}" y="{cy+48}" text-anchor="middle" font-family="{MONO}" font-size="10" letter-spacing="2" fill="#6b6259">you are here</text>
{overlay(w, h)}
</svg>'''
    open(os.path.join(OUT, "nodes.svg"), "w", encoding="utf-8").write(svg)

def footer():
    w, h = 900, 120
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}">
{common_defs(w, h)}
<style>{CSS_BASE}
.g{{animation:g 4s infinite steps(1)}}
@keyframes g{{0%,100%{{transform:none}}40%{{transform:translateX(-5px)}}41%{{transform:translateX(3px)}}42%{{transform:none}}}}
</style>
<rect width="{w}" height="{h}" fill="#0a0a0a"/>
<g font-family="{SANS}" font-weight="900" font-size="30" letter-spacing="6" text-anchor="middle">
<text x="{w/2-2}" y="62" fill="#ff2a3d" opacity=".8" class="g">CLOSE THE WORLD, OPEN THE nExt</text>
<text x="{w/2}" y="62" fill="#f2efe9">CLOSE THE WORLD, OPEN THE nExt</text>
</g>
<text x="{w/2}" y="94" text-anchor="middle" font-family="{MONO}" font-size="12" letter-spacing="3" fill="#6b6259">no matter where you go, everyone's connected<tspan class="blink" fill="#ff3347">_</tspan></text>
{overlay(w, h)}
</svg>'''
    open(os.path.join(OUT, "footer.svg"), "w", encoding="utf-8").write(svg)

hero(); nodes(); footer()

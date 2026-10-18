# Eye-catching animated SVG (SMIL only, works inside <img>) of the agentic demand adaptation in the JSAC paper.
# A LEO satellite serves 4 users; a demand surge hits; an AI agent loops ACT -> OBSERVE -> DECIDE with the
# BT-NWS-GPI solver as its tool and raises the worst-user satisfaction (paper, tau = 1.8: rule 0.597 -> agent 0.617).
# Usage: python tools/figures/make_agent_anim.py   (writes assets/img/research/ai-agent-anim.svg)
import math

T = 14.0                                      # loop (s)
# timeline: 0-2 calm, 2-3.5 SURGE, then 3 agent rounds of 3 s (3.5-12.5), 12.5-14 result hold
ST = [0, 2, 3.5, 6.5, 9.5, 12.5, 14]
users = ["UE 1", "UE 2", "UE 3", "MC"]
ux = [110, 210, 310, 410]
calm = [0.45, 0.38, 0.42, 0.40]               # normal demands
d = [1.00, 0.80, 0.90, 1.00]                  # surged demands
offer = {                                     # offered rate per phase
    "calm": calm,
    "surge": [0.62, 0.50, 0.55, 0.56],        # passive solver right after the surge
    "r1": [0.600, 0.480, 0.540, 0.597],       # rule-based beta = 0.600
    "r2": [0.640, 0.520, 0.550, 0.600],       # beta 0.648
    "r3": [0.622, 0.500, 0.557, 0.617],       # beta 0.624
}
phases = ["calm", "surge", "r1", "r2", "r3", "r3"]
thought = ["", "",
           "β = 0.600 (rule) → all targets met ✓ → raise β 8%",
           "β = 0.648 → MC at 93% ✗ → β ← midpoint",
           "β = 0.624 → all targets met ✓ → keep best",
           ""]
gauge = [None, None, 0.597, 0.600, 0.617, 0.617]


def keys(vals, ease=0.4):
    t, v = [0.0], [vals[0]]
    for i in range(1, len(vals)):
        a = ST[i] / T
        t += [a, min(a + ease / T, ST[i + 1] / T - 1e-4)]
        v += [vals[i - 1], vals[i]]
    t.append(1.0); v.append(vals[-1])
    return ";".join(f"{x:.4f}" for x in t), ";".join(f"{x:.2f}" for x in v)


def window(i, j=None):
    """discrete opacity 1 only during phases i..j"""
    j = i if j is None else j
    a, b = ST[i] / T, ST[j + 1] / T
    ks, vs = ["0"], ["1" if a == 0 else "0"]
    if a > 0: ks.append(f"{a:.4f}"); vs.append("1")
    if b < 1: ks.append(f"{b:.4f}"); vs.append("0")
    ks.append("1"); vs.append(vs[-1])
    return ";".join(ks), ";".join(vs)


o = []
add = o.append
add('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 520" font-family="Inter, Helvetica, Arial, sans-serif">')
add('''<defs>
  <radialGradient id="sky" cx="30%" cy="10%" r="100%"><stop offset="0" stop-color="#16204a"/><stop offset="1" stop-color="#04060e"/></radialGradient>
  <radialGradient id="earth" cx="50%" cy="0%" r="80%"><stop offset="0" stop-color="#3a7bd5"/><stop offset=".6" stop-color="#173a7a"/><stop offset="1" stop-color="#0a1836"/></radialGradient>
  <linearGradient id="beam" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#4cc9f0" stop-opacity=".9"/><stop offset="1" stop-color="#4cc9f0" stop-opacity=".15"/></linearGradient>
  <linearGradient id="beamMC" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#c77dff" stop-opacity=".9"/><stop offset="1" stop-color="#c77dff" stop-opacity=".15"/></linearGradient>
  <linearGradient id="core" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#4cc9f0"/><stop offset="1" stop-color="#7b61ff"/></linearGradient>
  <linearGradient id="gaugeG" x1="0" y1="0" x2="1" y2="0"><stop offset="0" stop-color="#f72585"/><stop offset=".5" stop-color="#fbbf24"/><stop offset="1" stop-color="#4ade80"/></linearGradient>
  <filter id="glow" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="4" result="b"/><feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge></filter>
  <g id="user"><circle cy="-15" r="7" fill="#e8ecf6"/><path d="M-11 6 Q-11 -6 0 -6 Q11 -6 11 6 Z" fill="#e8ecf6"/></g>
</defs>''')
add('<rect width="820" height="520" rx="18" fill="url(#sky)"/>')
for (x, y, r) in [(40, 40, 1.2), (150, 22, 1), (300, 60, 1.4), (470, 30, 1), (520, 120, 1.2), (780, 50, 1.4), (700, 140, 1), (60, 160, 1), (380, 150, .9)]:
    add(f'<circle cx="{x}" cy="{y}" r="{r}" fill="#fff" opacity=".7"><animate attributeName="opacity" values=".2;.9;.2" dur="{2 + x % 3}s" repeatCount="indefinite"/></circle>')

# ---------------- Earth + users + demand bars
add('<ellipse cx="260" cy="760" rx="420" ry="330" fill="url(#earth)"/>')
add('<ellipse cx="260" cy="760" rx="420" ry="330" fill="none" stroke="#7fd3ff" stroke-opacity=".45" stroke-width="3"/>')
UY = 452
for i, x in enumerate(ux):
    add(f'<g transform="translate({x} {UY})"><use href="#user"/></g>')
    add(f'<text x="{x}" y="{UY + 28}" font-size="13" fill="#c3cbe0" text-anchor="middle">{users[i]}</text>')
    # demand bar (outline) and offered bar
    BX, BW, BB, SC = x + 16, 12, UY + 6, 110
    dk, dv = keys([calm[i] * SC, d[i] * SC, d[i] * SC, d[i] * SC, d[i] * SC, d[i] * SC])
    _, dy = keys([BB - calm[i] * SC, BB - d[i] * SC, BB - d[i] * SC, BB - d[i] * SC, BB - d[i] * SC, BB - d[i] * SC])
    add(f'<rect x="{BX}" width="{BW}" y="{BB - calm[i] * SC:.1f}" height="{calm[i] * SC:.1f}" fill="none" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="3 2">'
        f'<animate attributeName="height" dur="{T}s" repeatCount="indefinite" keyTimes="{dk}" values="{dv}"/>'
        f'<animate attributeName="y" dur="{T}s" repeatCount="indefinite" keyTimes="{dk}" values="{dy}"/></rect>')
    ov = [offer[p][i] * SC for p in phases]
    ok, oh = keys(ov)
    _, oy = keys([BB - v for v in ov])
    col = "#c77dff" if users[i] == "MC" else "#4cc9f0"
    add(f'<rect x="{BX + 1.5}" width="{BW - 3}" y="{BB - ov[0]:.1f}" height="{ov[0]:.1f}" fill="{col}" filter="url(#glow)">'
        f'<animate attributeName="height" dur="{T}s" repeatCount="indefinite" keyTimes="{ok}" values="{oh}"/>'
        f'<animate attributeName="y" dur="{T}s" repeatCount="indefinite" keyTimes="{ok}" values="{oy}"/></rect>')
add('<text x="96" y="502" font-size="11" fill="#8f9bb6"><tspan fill="#fbbf24">┄ demand</tspan>   <tspan fill="#4cc9f0">█ offered rate</tspan>   (MC = multicast)</text>')

# ---------------- satellite + beams (beam width follows offered rate)
SX, SY = 260, 120
for i, x in enumerate(ux):
    ws = [offer[p][i] * 26 for p in phases]
    k, wv = keys(ws)
    grad = "beamMC" if users[i] == "MC" else "beam"
    add(f'<path d="M{SX} {SY + 18} L{x} {UY - 30}" stroke="url(#{grad})" stroke-linecap="round" fill="none" stroke-width="{ws[0]:.1f}" opacity=".55">'
        f'<animate attributeName="stroke-width" dur="{T}s" repeatCount="indefinite" keyTimes="{k}" values="{wv}"/></path>')
    add(f'<circle r="3.2" fill="#fff" filter="url(#glow)"><animateMotion dur="{1.1 + i * .17:.2f}s" repeatCount="indefinite" path="M{SX} {SY + 18} L{x} {UY - 30}"/></circle>')
add(f'''<g transform="translate({SX} {SY})" filter="url(#glow)">
  <rect x="-62" y="-10" width="42" height="20" fill="#2b4a9b" stroke="#9fb6ff"/><rect x="20" y="-10" width="42" height="20" fill="#2b4a9b" stroke="#9fb6ff"/>
  <path d="M-48 -10V10M-34 -10V10M34 -10V10M48 -10V10" stroke="#9fb6ff" stroke-width=".8"/>
  <rect x="-16" y="-16" width="32" height="32" rx="5" fill="#e6e8ec"/><path d="M-10 16 A10 7 0 0 0 10 16" fill="#e6e8ec"/>
  <animateTransform attributeName="transform" type="translate" values="{SX - 6} {SY};{SX + 6} {SY + 2};{SX - 6} {SY}" dur="6s" repeatCount="indefinite"/>
</g>''')
add(f'<text x="{SX}" y="{SY - 28}" font-size="12" fill="#8f9bb6" text-anchor="middle">LEO satellite · RSMA</text>')

# SURGE banner
k, v = window(1)
add(f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/>'
    '<rect x="150" y="190" width="220" height="44" rx="10" fill="#f72585" fill-opacity=".18" stroke="#f72585" stroke-width="2"/>'
    '<text x="260" y="220" font-size="22" font-weight="800" fill="#ff6fae" text-anchor="middle">⚠ DEMAND SURGE ×1.8</text>'
    '</g>')

# ---------------- AI agent
AX, AY, R = 650, 215, 92
add(f'<circle cx="{AX}" cy="{AY}" r="{R}" fill="none" stroke="#7b61ff" stroke-opacity=".35" stroke-width="2" stroke-dasharray="4 7">'
    f'<animateTransform attributeName="transform" type="rotate" from="0 {AX} {AY}" to="360 {AX} {AY}" dur="20s" repeatCount="indefinite"/></circle>')
add(f'<circle cx="{AX}" cy="{AY}" r="46" fill="#120f33" stroke="url(#core)" stroke-width="3" filter="url(#glow)"/>')
add(f'<g stroke="#4cc9f0" stroke-width="2" opacity=".8">' + ''.join(
    f'<path d="M{AX - 22 + 11 * k} {AY - 46} v-8 M{AX - 22 + 11 * k} {AY + 46} v8 M{AX - 46} {AY - 22 + 11 * k} h-8 M{AX + 46} {AY - 22 + 11 * k} h8"/>' for k in range(5)) + '</g>')
add(f'<text x="{AX}" y="{AY - 2}" font-size="22" font-weight="800" fill="#fff" text-anchor="middle">AI</text>')
add(f'<text x="{AX}" y="{AY + 18}" font-size="12" fill="#c4b8ff" text-anchor="middle">agent</text>')
steps = [("ACT", "call solver", -90), ("OBSERVE", "satisfaction", 30), ("DECIDE", "update β", 150)]
for j, (nm, sub, ang) in enumerate(steps):
    nx, ny = AX + R * math.cos(math.radians(ang)), AY + R * math.sin(math.radians(ang))
    tms, op = ["0"], ["0.25"]
    for r in range(3):
        a = (ST[2 + r] + j) / T; b = (ST[2 + r] + j + 1) / T
        tms += [f"{a:.4f}", f"{b:.4f}"]; op += ["1", "0.25"]
    tms.append("1"); op.append("0.25")
    add(f'<g opacity=".25"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{";".join(tms)}" values="{";".join(op)}"/>'
        f'<rect x="{nx - 50:.1f}" y="{ny - 20:.1f}" width="100" height="40" rx="20" fill="#0b1430" stroke="#4cc9f0" stroke-width="2" filter="url(#glow)"/>'
        f'<text x="{nx:.1f}" y="{ny - 1:.1f}" font-size="14" font-weight="800" fill="#4cc9f0" text-anchor="middle">{nm}</text>'
        f'<text x="{nx:.1f}" y="{ny + 13:.1f}" font-size="10" fill="#c3cbe0" text-anchor="middle">{sub}</text></g>')
# packet from agent to satellite during ACT (solver call)
for r in range(3):
    a = ST[2 + r]
    add(f'<circle r="5" fill="#4ade80" filter="url(#glow)" opacity="0">'
        f'<animateMotion begin="{a}s;{a}s+{T}s" dur="1s" fill="freeze" path="M{AX - 40} {AY - R + 6} Q{(AX + SX) / 2} 40 {SX + 40} {SY}" repeatCount="1"/>'
        f'<set attributeName="opacity" to="1" begin="{a}s" dur="1s"/></circle>')
add(f'<text x="{AX}" y="{AY - R - 34}" font-size="11" fill="#4ade80" text-anchor="middle">tool: BT-NWS-GPI solver</text>')
# thought bubble
for p in range(2, 5):
    k, v = window(p)
    add(f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/>'
        f'<rect x="470" y="336" width="330" height="34" rx="17" fill="#0b1430" stroke="#7b61ff" stroke-opacity=".7"/>'
        f'<text x="635" y="358" font-size="13" fill="#e8ecf6" text-anchor="middle">💭 {thought[p]}</text></g>')

# ---------------- worst-user satisfaction gauge
GX, GY, GR = 635, 470, 62
add(f'<path d="M{GX - GR} {GY} A{GR} {GR} 0 0 1 {GX + GR} {GY}" fill="none" stroke="url(#gaugeG)" stroke-width="10" stroke-linecap="round" opacity=".9"/>')
add(f'<text x="{GX}" y="{GY - GR - 10}" font-size="12" fill="#c3cbe0" text-anchor="middle">worst-user satisfaction</text>')
def ang_of(vv):                        # map 0.5..0.7 to -90..+90 deg (needle pointing up = 0.6)
    return -90 + (vv - 0.5) / 0.2 * 180
gv = [0.55, 0.55] + [g for g in gauge[2:]]
k, av = keys([ang_of(x) for x in gv], ease=0.8)
add(f'<g transform="translate({GX} {GY})"><g><line x1="0" y1="0" x2="0" y2="{-GR + 8}" stroke="#fff" stroke-width="4" stroke-linecap="round"/>'
    f'<circle r="6" fill="#fff"/>'
    f'<animateTransform attributeName="transform" type="rotate" dur="{T}s" repeatCount="indefinite" keyTimes="{k}" '
    f'values="{av}"/></g></g>')
for p in range(2, 6):
    k, v = window(p) if p < 5 else window(5)
    big = gauge[p]
    add(f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/>'
        f'<text x="{GX}" y="{GY + 24}" font-size="20" font-weight="800" fill="#fff" text-anchor="middle">{big:.3f}</text></g>')
k, v = window(5)
add(f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/>'
    '<rect x="470" y="336" width="330" height="34" rx="17" fill="#4ade80" fill-opacity=".15" stroke="#4ade80"/>'
    '<text x="635" y="358" font-size="14" font-weight="800" fill="#4ade80" text-anchor="middle">rule 0.597 → AI agent 0.617 ↑</text></g>')
add('<text x="24" y="34" font-size="20" font-weight="800" fill="#fff">When demand explodes, an <tspan fill="#4cc9f0">AI agent</tspan> keeps every user served</text>')
add('</svg>')
open("assets/img/research/ai-agent-anim.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")

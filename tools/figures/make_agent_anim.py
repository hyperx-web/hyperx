# Animated SVG (SMIL only, so it also animates inside <img>) of the solver agent in the JSAC paper:
# demand surge -> the agent repeats Act (call BT-NWS-GPI) / Observe (satisfaction) / Decide (update beta).
# Usage: python tools/figures/make_agent_anim.py   (writes assets/img/research/ai-agent-anim.svg)
import math

T = 12.0                                    # loop length (s); 4 stages of 3 s
stages = [0, 3, 6, 9, 12]
msgs = ["UE 1", "UE 2", "UE 3", "MC"]
d = [1.00, 0.80, 0.90, 1.00]                # surged requested demands (normalised)
beta = [0.600, 0.648, 0.624, 0.624]         # rule -> raise 8% -> midpoint -> return best
offered = [                                 # offered rates per stage (offered / demand = satisfaction)
    [0.600, 0.480, 0.540, 0.597],           # rule: every scaled target met (min sat 0.597 as in the paper)
    [0.640, 0.520, 0.550, 0.600],           # beta 0.648: MC stays at 0.600 -> min sat 0.600 < 0.98 beta
    [0.622, 0.500, 0.557, 0.617],           # beta 0.624: min sat 0.617 (>= 0.98 beta)
    [0.622, 0.500, 0.557, 0.617],
]
SPL = ';'.join(['0 0 1 1', '.4 0 .2 1'] * 3 + ['0 0 1 1'])
minsat = [min(x / dd for x, dd in zip(off, d)) for off in offered]
X0, BASE, SC, BW, GAP = 60, 400, 250 / 0.62, 46, 34
V0 = 0.40                                   # y-axis starts at 0.4 (zoomed so target changes are visible)


def kt(vals, ease=0.35):
    """Hold each stage value; change quickly right after each stage starts."""
    times, vs = [0.0], [vals[0]]
    for i in range(1, len(vals)):
        t0 = stages[i] / T
        times += [t0, t0 + ease / T]
        vs += [vals[i - 1], vals[i]]
    times += [1.0]
    vs += [vals[-1]]
    return ";".join(f"{t:.4f}" for t in times), ";".join(f"{v:.2f}" for v in vs)


def stage_visibility(s):
    a, b = stages[s] / T, stages[s + 1] / T
    if a == 0:
        return f"0;{b - 0.0005:.4f};1", "1;0;0"
    if s == len(stages) - 2:
        return f"0;{a:.4f};1", "0;1;1"
    return f"0;{a:.4f};{b - 0.0005:.4f};1", "0;1;0;0"


o = []
o.append('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 500" font-family="Helvetica, Arial, sans-serif">')
o.append('<defs><marker id="ar" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
         '<path d="M0 0L10 5L0 10z" fill="#5a7d3a"/></marker></defs>')
o.append('<rect width="820" height="500" fill="#fff"/>')
o.append('<text x="40" y="34" font-size="19" font-weight="bold">Demand surge (τ = 1.8): fair scaling of all targets by β</text>')

# ---------------- bar chart: requested demand / target beta*d / offered rate
o.append(f'<line x1="{X0 - 10}" y1="{BASE}" x2="{X0 + 4 * (BW + GAP)}" y2="{BASE}" stroke="#222" stroke-width="1.4"/>')
for i, m in enumerate(msgs):
    x = X0 + i * (BW + GAP)
    h = (d[i] - V0) * SC
    o.append(f'<rect x="{x}" y="{BASE - h:.1f}" width="{BW}" height="{h:.1f}" fill="none" stroke="#9aa1ab" '
             f'stroke-width="1.6" stroke-dasharray="5 4"/>')
    hs = [(off[i] - V0) * SC for off in offered]
    k, hv = kt(hs)
    _, yv = kt([BASE - hh for hh in hs])
    col = "#7a3e8e" if m == "MC" else "#2f5aa8"
    o.append(f'<rect x="{x}" y="{BASE - hs[0]:.1f}" width="{BW}" height="{hs[0]:.1f}" fill="{col}" opacity=".85">'
             f'<animate attributeName="height" dur="{T}s" repeatCount="indefinite" keyTimes="{k}" values="{hv}"/>'
             f'<animate attributeName="y" dur="{T}s" repeatCount="indefinite" keyTimes="{k}" values="{yv}"/></rect>')
    k2, y2 = kt(ease=1.0, vals=[BASE - (beta[s] * d[i] - V0) * SC for s in range(4)])
    y0 = BASE - (beta[0] * d[i] - V0) * SC
    for s in (1, 2):                         # ghost of the previous target
        k, v = stage_visibility(s)
        yp = BASE - (beta[s - 1] * d[i] - V0) * SC
        o.append(f'<line x1="{x - 6}" x2="{x + BW + 6}" y1="{yp:.1f}" y2="{yp:.1f}" stroke="#d9480f" stroke-width="1.5" stroke-dasharray="4 3" opacity="0">'
                 f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/></line>')
    o.append(f'<line x1="{x - 6}" x2="{x + BW + 6}" y1="{y0:.1f}" y2="{y0:.1f}" stroke="#d9480f" stroke-width="3">'
             f'<animate attributeName="y1" dur="{T}s" repeatCount="indefinite" keyTimes="{k2}" values="{y2}" calcMode="spline" keySplines="{SPL}"/>'
             f'<animate attributeName="y2" dur="{T}s" repeatCount="indefinite" keyTimes="{k2}" values="{y2}" calcMode="spline" keySplines="{SPL}"/></line>')
    o.append(f'<text x="{x + BW / 2}" y="{BASE + 22}" font-size="15" text-anchor="middle">{m}</text>')
for v in (0.4, 0.6, 0.8, 1.0):
    yy = BASE - (v - V0) * SC
    o.append(f'<text x="{X0 - 16}" y="{yy + 4:.1f}" font-size="11" fill="#777" text-anchor="end">{v:.1f}</text>')
o.append(f'<path d="M{X0 - 14} {BASE + 2} l6 -6 M{X0 - 9} {BASE + 2} l6 -6" stroke="#222" stroke-width="1.3"/>')
for s_, lab in ((1, "target ↑ +8%"), (2, "target ↓ −3.7%")):
    k, v = stage_visibility(s_)
    o.append(f'<g opacity="0"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/>'
             f'<rect x="250" y="96" width="120" height="28" rx="14" fill="#d9480f"/>'
             f'<text x="310" y="115" font-size="14" font-weight="bold" fill="#fff" text-anchor="middle">{lab}</text></g>')
ly = 72
o.append(f'<rect x="60" y="{ly - 11}" width="16" height="12" fill="none" stroke="#9aa1ab" stroke-dasharray="4 3"/>'
         f'<text x="82" y="{ly}" font-size="13">requested demand d</text>')
o.append(f'<line x1="214" y1="{ly - 5}" x2="232" y2="{ly - 5}" stroke="#d9480f" stroke-width="3"/>'
         f'<text x="238" y="{ly}" font-size="13">target β·d</text>')
o.append(f'<rect x="60" y="{ly + 9}" width="16" height="12" fill="#2f5aa8"/>'
         f'<text x="82" y="{ly + 20}" font-size="13">offered rate</text>')

# ---------------- agent loop: Act -> Observe -> Decide
cx, cy, R = 600, 255, 112
nodes = [("Act", "call BT-NWS-GPI", -90), ("Observe", "satisfaction ratios", 30), ("Decide", "update β", 150)]
o.append(f'<circle cx="{cx}" cy="{cy}" r="{R}" fill="none" stroke="#cbd5e1" stroke-width="2" stroke-dasharray="6 6"/>')
o.append(f'<text x="{cx}" y="{cy - 6}" font-size="18" font-weight="bold" text-anchor="middle">Solver</text>')
o.append(f'<text x="{cx}" y="{cy + 16}" font-size="18" font-weight="bold" text-anchor="middle">agent</text>')
for j, (nm, sub, ang) in enumerate(nodes):
    nx = cx + R * math.cos(math.radians(ang))
    ny = cy + R * math.sin(math.radians(ang))
    tms, vals = [0.0], ["#ffffff"]
    for s in range(3):                       # node j is active during second j of stages 0..2
        a = (stages[s] + j) / T
        b = (stages[s] + j + 1) / T
        tms += [a, b]
        vals += ["#dbe6f6", "#ffffff"]
    tms += [1.0]
    vals += ["#ffffff"]
    o.append(f'<rect x="{nx - 64:.1f}" y="{ny - 24:.1f}" width="128" height="48" rx="8" stroke="#2f5aa8" stroke-width="1.8" fill="#fff">'
             f'<animate attributeName="fill" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{";".join(f"{t:.4f}" for t in tms)}" values="{";".join(vals)}"/></rect>')
    o.append(f'<text x="{nx:.1f}" y="{ny - 3:.1f}" font-size="16" font-weight="bold" text-anchor="middle">{nm}</text>')
    o.append(f'<text x="{nx:.1f}" y="{ny + 15:.1f}" font-size="12" fill="#555" text-anchor="middle">{sub}</text>')
loop = f"M{cx} {cy - R} A{R} {R} 0 1 1 {cx - 0.01} {cy - R}"
o.append(f'<circle r="7" fill="#d9480f"><animateMotion dur="3s" repeatCount="indefinite" path="{loop}"/>'
         f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="0;0.75;1" values="1;0;0"/></circle>')
o.append(f'<rect x="{cx + 70}" y="70" width="130" height="40" rx="8" fill="#e3edd9" stroke="#5a7d3a" stroke-width="1.6"/>')
o.append(f'<text x="{cx + 135}" y="88" font-size="13" font-weight="bold" text-anchor="middle">Tool: BT-NWS-GPI</text>')
o.append(f'<text x="{cx + 135}" y="103" font-size="11" fill="#555" text-anchor="middle">few GPI updates</text>')
o.append(f'<path d="M{cx + 70} 98 L{cx + 48} {cy - R + 6}" stroke="#5a7d3a" stroke-width="1.6" fill="none" marker-end="url(#ar)"/>')

# ---------------- per-stage status
caps = ["Rule-based β: every scaled target met → raise β by 8%",
        "A message falls below 98% of its target → β ← midpoint(β, min ratio)",
        "All scaled targets met with the corrected β",
        "Return the best solution: higher worst-case satisfaction than the rule"]
for s in range(4):
    k, v = stage_visibility(s)
    init = "1" if s == 0 else "0"
    o.append(f'<g opacity="{init}"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" '
             f'keyTimes="{k}" values="{v}"/>'
             f'<text x="40" y="462" font-size="15" fill="#d9480f" font-weight="bold">{caps[s]}</text>'
             f'<text x="440" y="412" font-size="17">β = <tspan font-weight="bold">{beta[s]:.3f}</tspan></text>'
             f'<text x="565" y="412" font-size="17">min satisfaction = <tspan font-weight="bold">{minsat[s]:.3f}</tspan></text></g>')
o.append('<text x="40" y="488" font-size="12" fill="#777">Paper result at τ = 1.8: minimum satisfaction 0.597 (rule) → 0.617 (agent with BT-NWS-GPI)</text>')
o.append('</svg>')
open("assets/img/research/ai-agent-anim.svg", "w", encoding="utf-8").write("\n".join(o))
print("written; min satisfaction per stage", [round(x, 3) for x in minsat])

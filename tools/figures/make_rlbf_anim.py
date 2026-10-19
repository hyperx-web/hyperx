# Animated SVG (SMIL only, works inside <img>) for the TWC paper "Reinforcement Learning-Based Secure Beamforming
# Against Satellite Eavesdroppers": beam-gain maps (azimuth tau x zenith zeta) of the ground terminal's 4x4 UPA during
# one LEO pass (paper test scenario), next to a diagram of the primal-dual SAC agent that outputs the beamformer.
# Orbits, angles and array response come from the paper's simulation code (read-only: configs/submitted/config_loader.py,
# src/envs/satellite_core.py, constants_eve_3_M16.yaml / constants_eve_5_M16.yaml).
# Beam: null-space projection toward the visible eavesdroppers (illustrative, not the trained actor).
# Usage: python tools/figures/make_rlbf_anim.py   (writes assets/img/research/ai-rlbf-anim.svg)
import base64, io, sys, types, importlib.util
import numpy as np
import torch
from PIL import Image

SIM = r"C:\Users\dhjun\Dropbox\04_연구\2602_RL_BF\03_Simulation codes\MBPDAC"
sys.path.insert(0, SIM + r"\configs\submitted")
from config_loader import Config                     # noqa: E402
sys.modules.setdefault("einops", types.ModuleType("einops"))   # satellite_core imports einops; the functions used here do not need it
_spec = importlib.util.spec_from_file_location("satellite_core", SIM + r"\src\envs\satellite_core.py")
sc = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(sc)

T, NF = 14.0, 140                                     # loop (s), frames (uniform in time -> constant orbital speed)
PW, PH, PY = 478, 206, 28                            # beam-pattern panel size / top (Configuration A)
PX = [432]                                           # beam-pattern panels' left edge (right column)
PY2 = PY + PH + 14                                   # top of the Configuration B panel
DR = 30.0
AZ = np.linspace(-180, 180, 181)
ZE = np.linspace(0, 90, 46)
f64 = lambda x: torch.tensor(x, dtype=torch.float64)

# diverging colour map (low gain -> high gain): indigo / blue -> near white -> coral / crimson-rose
PAL = np.array([[25, 45, 175], [70, 120, 225], [160, 195, 240], [245, 245, 245],     # -30 dB blue -> 0 dB red
                [245, 170, 140], [225, 80, 60], [200, 20, 30]], float)


def cmap(x):
    p = np.clip(x, 0, 1) * (len(PAL) - 1)
    i = np.minimum(p.astype(int), len(PAL) - 2)
    f = (p - i)[..., None]
    return (PAL[i] * (1 - f) + PAL[i + 1] * f).astype(np.uint8)


class Scenario:
    def __init__(self, path, orbit=None):
        self.c = Config(path, mode="test")
        if orbit:                                    # different orbits (degrees), applied in memory; the original config is untouched
            c = self.c
            c.i_s, c.omega_s = np.radians(orbit["i_s"]), np.radians(orbit["omega_s"])
            c.i_e = list(np.radians(orbit["i_e"])); c.omega_e = list(np.radians(orbit["omega_e"]))
            c.u_e_0_offset = list(np.radians(orbit["u_off"]))
            c._calculate_pass_interval()
        self.rE = f64(self.c.r_E)
        TT, ZZ = np.meshgrid(AZ, ZE)
        self.A = self.resp(TT, ZZ)
        self.M = self.A.shape[-1]
        self.dur = self.c.max_time_slots * self.c.time_interval

    def resp(self, tau, zeta):
        return sc.array_response_vector_sat_2d(f64(np.radians(zeta)), f64(np.radians(tau)),
                                               self.c.num_tx_ant_ue_x, self.c.num_tx_ant_ue_y).numpy()

    def geometry(self, t):
        c = self.c
        psi = f64(c.psi + c.omega_earth * t)
        phi_t = sc.get_phi_t(self.rE, f64(c.phi), psi).reshape(1, 3)
        sats = [sc.calculate_phi_k_n(f64(c.omega_s), f64(c.i_s), f64(c.delta_s * t + c.u_s_0), self.rE, f64(c.a_s))]
        for j in range(len(c.a_e)):
            de = np.sqrt(c.G * c.M_E / (c.r_E + c.a_e[j]) ** 3) * c.time_interval
            sats.append(sc.calculate_phi_k_n(f64(c.omega_e[j]), f64(c.i_e[j]), f64(de * t + c.u_e_0[j]), self.rE, f64(c.a_e[j])))
        out = []
        for p in sats:
            p = p.reshape(1, 3)
            z = sc.get_zeta_k_n(phi_t, p).item()
            tau = sc.get_tau_k_n(phi_t, p, f64(c.phi), psi, self.rE).item()
            out.append((np.degrees(tau), np.degrees(z), float(torch.dot((p - phi_t)[0], phi_t[0])) > 0))
        return out

    def weights(self, g):
        (ts, zs, _), eves = g[0], [e for e in g[1:] if e[2]]
        w = self.resp(ts, zs)
        if eves:
            E = np.stack([self.resp(e[0], e[1]) for e in eves], 1)
            w = (np.eye(self.M) - E @ np.linalg.pinv(E)) @ w
        return w / np.linalg.norm(w)

    def gain_db(self, g):
        w = self.weights(g)
        return 10 * np.log10(np.maximum(np.abs(self.A.conj() @ w) ** 2 / self.M, 1e-6))


def jpg(G):
    big = np.array(Image.fromarray(G.astype(np.float32)).resize((PW, PH), Image.BICUBIC))[::-1]
    lev = (np.clip(big, -DR, 0) + DR) / DR                                          # continuous gradient
    b = io.BytesIO(); Image.fromarray(cmap(lev)).save(b, "JPEG", quality=64)
    return base64.b64encode(b.getvalue()).decode()


star = '<path d="M0 -10 L2.7 -3.2 L10 -3.2 L4.1 1.4 L6.4 8.6 L0 4.1 L-6.4 8.6 L-4.1 1.4 L-10 -3.2 L-2.7 -3.2 Z" fill="#ffd43b" stroke="#333" stroke-width="1.2"/>'
tri = '<path d="M0 -8 L7 5.5 L-7 5.5 Z" fill="#fff" stroke="#222" stroke-width="1.6"/>'
kt = ";".join(f"{f / NF:.4f}" for f in range(NF)) + ";1"


# ---------------- LaTeX labels: latex + dvisvgm (MiKTeX) -> glyph outlines embedded as nested <svg>
import os, re, subprocess, tempfile
_TEXN = [0]
TEXDIR = os.path.join(tempfile.gettempdir(), "rlbf_tex")


def tex(body, x, y, px=17, col="#212529", anchor="start", rotate=False):
    """Render LaTeX `body` (text mode) with its baseline at y; px = height of 10 pt text in pixels.
    A 0.4 pt strut from -4 pt to +10 pt pins the bounding box to the baseline; it is removed from the output."""
    os.makedirs(TEXDIR, exist_ok=True)
    _TEXN[0] += 1
    n = _TEXN[0]
    open(os.path.join(TEXDIR, f"t{n}.tex"), "w", encoding="utf-8").write(
        "\\documentclass[10pt]{article}\\usepackage{amsmath,bm}\\pagestyle{empty}\\begin{document}\\noindent\\rule[-4pt]{0.4pt}{14pt}" + body + "\\end{document}")
    subprocess.run(["latex", "-interaction=batchmode", f"t{n}.tex"], cwd=TEXDIR, check=True, capture_output=True)
    subprocess.run(["dvisvgm", "--no-fonts", "--exact-bbox", "-o", f"t{n}.svg", f"t{n}.dvi"], cwd=TEXDIR, check=True, capture_output=True)
    svg = open(os.path.join(TEXDIR, f"t{n}.svg"), encoding="utf-8").read()
    vb = [float(v) for v in re.search(r"viewBox=['\"]([^'\"]+)['\"]", svg).group(1).split()]
    inner = svg[svg.index(">", svg.index("<svg")) + 1:svg.rindex("</svg>")]
    inner = re.sub(r"<rect[^>]*/>", "", inner, count=1)                                   # drop the strut
    inner = re.sub(r"id=['\"]([^'\"]+)['\"]", lambda m: f'id="t{n}{m.group(1)}"', inner)
    inner = re.sub(r"href=['\"]#([^'\"]+)['\"]", lambda m: f'href="#t{n}{m.group(1)}"', inner)
    k = px / 10.0                                    # 10 pt -> px pixels
    vb[0] += 0.4; vb[2] -= 0.4                       # strip the strut width
    w, h = vb[2] * k, vb[3] * k
    ox = {"start": 0, "middle": -w / 2, "end": -w}[anchor]
    g = (f'<svg x="{ox:.2f}" y="{-10 * k:.2f}" width="{w:.2f}" height="{h:.2f}" viewBox="{" ".join(map(str, vb))}" overflow="visible">'
         f'<g fill="{col}" stroke="none">{inner}</g></svg>')
    rot = " rotate(-90)" if rotate else ""
    return f'<g transform="translate({x:.2f} {y:.2f}){rot}">{g}</g>', w


from PIL import ImageFont                            # noqa: E402
_FONTS = {}


def arial_w(text, px, bold):
    key = (px, bold)
    if key not in _FONTS:
        _FONTS[key] = ImageFont.truetype("arialbd.ttf" if bold else "arial.ttf", px)
    return _FONTS[key].getlength(text)


def mixed(parts, x, y, px=17, col="#212529", bold=False, anchor="start", rotate=False):
    """Arial text with LaTeX math pieces; parts = [("t", "text") | ("m", r"$...$")], vertically centred on y."""
    items, cur = [], 0.0
    for kind, val in parts:
        if kind == "t":
            w = arial_w(val, px, bold)
            items.append(f'<text x="{cur:.2f}" y="{px * 0.36:.2f}" font-family="Arial, Helvetica, sans-serif" font-size="{px}"'
                         f'{" font-weight=\"bold\"" if bold else ""} fill="{col}" xml:space="preserve">{val}</text>')
        else:
            g, w = tex(val, cur, px * 0.36, px * 1.05, col)      # same baseline as the Arial text
            items.append(g)
        cur += w
    ox = {"start": 0, "middle": -cur / 2, "end": -cur}[anchor]
    rot = " rotate(-90)" if rotate else ""
    return f'<g transform="translate({x:.2f} {y:.2f}){rot} translate({ox:.2f} 0)">{"".join(items)}</g>', cur



def panel(sco, X0, title, xaxis=True):
    sx = lambda a: X0 + (a + 180) / 360 * PW
    sy = lambda z: PY + PH - z / 90 * PH
    geo = [sco.geometry(sco.dur * (TW[0] + (TW[1] - TW[0]) * f / NF)) for f in range(NF)]
    o = [
         f'<clipPath id="cp{X0}_{PY}"><rect x="{X0}" y="{PY}" width="{PW}" height="{PH}" rx="6"/></clipPath>',
         f'<g clip-path="url(#cp{X0}_{PY})">']
    for f, g in enumerate(geo):
        a, z = f / NF, (f + 1) / NF
        k, v = (f"0;{z:.4f};1", "1;0;0") if f == 0 else (f"0;{a:.4f};{z:.4f};1", "0;1;0;0")
        o.append(f'<image x="{X0}" y="{PY}" width="{PW}" height="{PH}" preserveAspectRatio="none" opacity="{1 if f == 0 else 0}" '
                 f'href="data:image/jpeg;base64,{jpg(sco.gain_db(g))}">'
                 f'<animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{k}" values="{v}"/></image>')
    fine = [sco.geometry(sco.dur * f / 300) for f in range(301)]
    for k in range(len(fine[0])):
        seg, segs = [], []
        for g in fine:
            a, z, vis = g[k]
            if not vis or (seg and abs(a - seg[-1][0]) > 90):
                if len(seg) > 1: segs.append(seg)
                seg = []
            if vis: seg.append((a, z))
        if len(seg) > 1: segs.append(seg)
        for s_ in segs:
            o.append(f'<polyline points="{" ".join(f"{sx(a):.1f},{sy(z):.1f}" for a, z in s_)}" fill="none" stroke="#5c6070" '
                     f'stroke-width="1" stroke-dasharray="{"0" if k == 0 else "4 3"}" opacity=".55"/>')
    for k in range(len(geo[0])):
        xs = [f"{sx(g[k][0]):.1f} {sy(g[k][1]):.1f}" for g in geo]; xs.append(xs[0])
        op = ["1" if g[k][2] else "0" for g in geo]; op.append(op[0])
        o.append(f'<g opacity="{op[0]}"><animate attributeName="opacity" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{";".join(op)}"/>'
                 f'<g transform="translate({xs[0]})">{star if k == 0 else tri}'
                 f'<animateTransform attributeName="transform" type="translate" dur="{T}s" repeatCount="indefinite" calcMode="discrete" keyTimes="{kt}" values="{";".join(xs)}"/></g></g>')
    o.append('</g>')
    o.append(f'<rect x="{X0}" y="{PY}" width="{PW}" height="{PH}" rx="6" fill="none" stroke="#6b7080"/>')
    tw = arial_w(title, 15, True) + 16                 # title label inside the plot (top-left)
    if title: o.append(f'<rect x="{X0 + 8}" y="{PY + 8}" width="{tw:.0f}" height="25" rx="5" fill="#fff" fill-opacity=".88" stroke="#888"/>'
             f'<text x="{X0 + 16}" y="{PY + 26}" font-family="Arial, Helvetica, sans-serif" font-size="15" font-weight="bold">{title}</text>')
    for a in (range(-150, 181, 50) if xaxis else ()):
        o.append(f'<text x="{sx(a):.1f}" y="{PY + PH + 20}" font-size="15" fill="#444" text-anchor="middle">{a}</text>')
    for z in (range(0, 91, 15) if X0 == PX[0] else ()):   # y tick labels only on the left panel
        o.append(f'<text x="{X0 - 6}" y="{sy(z) + 5:.1f}" font-size="15" fill="#444" text-anchor="end">{z}</text>')
    o.append(mixed([("t", "Azimuth "), ("m", r"$\tau$"), ("t", " [deg]")], X0 + PW / 2, PY + PH + 38, 17, anchor="middle")[0])
    return o


base = SIM + r"\configs\submitted\constants_eve_"
sA = Scenario(base + "3_M16.yaml")                   # paper test scenario (Configuration A)
sB = Scenario(base + "5_M16.yaml", orbit=dict(i_s=88.0, omega_s=0.0, i_e=[87.0, 87.0, 96.0, 96.0, 96.0],
                                              omega_e=[20.0, 20.0, -45.0, -45.0, -45.0], u_off=[3.0, 7.0, -6.0, -2.0, 2.0]))

# time window: only the part of the pass where the set of visible satellites stays the same in both configurations,
# so the pattern evolves smoothly (no jumps when a satellite rises or sets); the window then loops
_N = 400
_vis = [tuple(g[2] for g in sA.geometry(sA.dur * i / _N)) + tuple(g[2] for g in sB.geometry(sB.dur * i / _N)) for i in range(_N + 1)]
_best, _i0 = (0, 0), 0
for i in range(1, _N + 2):
    if i == _N + 1 or _vis[i] != _vis[_i0]:
        if i - _i0 > _best[1] - _best[0]:
            _best = (_i0, i - 1)
        _i0 = i
TW = (_best[0] / _N + 0.01, _best[1] / _N - 0.01)
print("time window (fraction of pass):", TW)
geoA = [sA.geometry(sA.dur * (TW[0] + (TW[1] - TW[0]) * f / NF)) for f in range(NF)]
o = ['<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 1000 {HTOT}" font-family="Helvetica, Arial, sans-serif">',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0 0L10 5L0 10z" fill="#222"/></marker>'
     '<marker id="ahr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0 0L10 5L0 10z" fill="#c2255c"/></marker></defs>',
     '<rect width="1000" height="{HTOT}" fill="#fff"/>']
o += panel(sA, PX[0], "", xaxis=False)
o.append(mixed([("t", "Zenith "), ("m", r"$\zeta$"), ("t", " [deg]")], PX[0] - 42, PY + PH / 2, 17, anchor="middle", rotate=True)[0])
HB = PY2 + PH - PY                                   # shared colour bar for A and B
bar = np.repeat(cmap(np.linspace(1, 0, HB))[:, None, :], 14, 1)
b = io.BytesIO(); Image.fromarray(bar).save(b, "PNG")
CBX = PX[0] + PW + 12
o.append(f'<image x="{CBX}" y="{PY}" width="12" height="{HB}" preserveAspectRatio="none" href="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}"/>'
         f'<rect x="{CBX}" y="{PY}" width="12" height="{HB}" fill="none" stroke="#6b7080"/>')
for db in (0, -10, -20, -30):
    o.append(f'<text x="{CBX + 16}" y="{PY + (-db) / DR * HB + 5:.1f}" font-size="15">{db} dB</text>')

# ---------------- left: primal-dual SAC agent of the paper (actor, reward critics, multi-head cost critics, dual update)
def rbox(x, y, w, h, lines, fill, px=14):
    """lines: list of mixed() part lists, centred in the box"""
    o = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="#333" stroke-width="1.6"/>']
    for i, parts in enumerate(lines):
        o.append(mixed(parts, x + w / 2, y + h / 2 + (i - (len(lines) - 1) / 2) * (px + 6), px, anchor="middle")[0])
    return "".join(o)


def pulse(path, col, dur=1.6, begin=0.0):
    return (f'<circle r="3.6" fill="{col}"><animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{path}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>')


def arrow(path, col="#222", w=1.7):
    return f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}" marker-end="url(#ah)"/>'


T_ = lambda t: ("t", t)
M_ = lambda m: ("m", m)
AX0, AY0, AX1, AY1 = 58, PY + 22, 340, PY + 318       # agent region
o.append(f'<rect x="{AX0}" y="{AY0}" width="{AX1 - AX0}" height="{AY1 - AY0}" rx="22" fill="#f8d7da" fill-opacity=".45" '
         f'stroke="#222" stroke-width="1.6" stroke-dasharray="7 5"/>')
o.append(f'<text x="{(AX0 + AX1) / 2}" y="{AY0 - 10}" font-family="Arial, Helvetica, sans-serif" font-size="19" font-weight="bold" fill="#212529" text-anchor="middle">Agent (primal–dual SAC)</text>')
ACx, ACy, ACw, ACh = 100, AY0 + 46, 112, 62          # actor
LMx, LMy, LMw, LMh = 258, AY0 + 46, 70, 62           # dual variables
RCx, RCy, RCw, RCh = 64, AY0 + 184, 132, 96          # reward critics
CCx, CCy, CCw, CCh = 204, AY0 + 184, 132, 96         # multi-head cost critics
o.append(rbox(ACx, ACy, ACw, ACh, [[T_("Actor "), M_(r"$\pi_{\bm{\theta}}$")]], "#f1aeb5", 19))
o.append(rbox(LMx, LMy, LMw, LMh, [[M_(r"$\bm{\lambda}$")], [T_("dual")]], "#ffe8cc", 17))
o.append(rbox(RCx, RCy, RCw, RCh, [[T_("Reward")], [T_("critics "), M_(r"$Q^{\mathrm{R}}_{1,2}$")]], "#cfe2ff", 17))
o.append(rbox(CCx, CCy, CCw, CCh, [[T_("Cost critics")], [M_(r"$\bm{Q}^{\mathrm{C}}_{1,2}$")], [T_("co / so heads")]], "#e5dbff", 17))
EX, EY, EW, EH = 86, PY + 384, 240, 66               # environment
o.append(rbox(EX, EY, EW, EH, [[T_("Environment")], [T_("LEO pass, eavesdroppers")]], "#e2f0d9", 18))
# internal updates
inner = [f"M{RCx + RCw / 2} {RCy} L{RCx + RCw / 2} {ACy + ACh + 2}",                           # reward critic -> actor
         f"M{CCx + 30} {CCy} C{CCx + 30} {CCy - 30} {ACx + ACw - 20} {ACy + ACh + 30} {ACx + ACw - 20} {ACy + ACh + 2}",  # cost critic -> actor
         f"M{CCx + CCw - 30} {CCy} L{CCx + CCw - 30} {LMy + LMh + 2}",                        # cost critic -> dual update
         f"M{LMx} {LMy + LMh / 2} L{ACx + ACw + 2} {ACy + ACh / 2}"]                          # lambda -> actor
for pth, col in zip(inner, ["#1971c2", "#7048e8", "#e8590c", "#e8590c"]):
    o.append(arrow(pth))
    o.append(pulse(pth, col, 1.2, 0.3))
# outer loop
LXs, RXa = 34, 352
sy_ = EY + EH / 2
paths = {
    "state": f"M{EX} {sy_} L{LXs} {sy_} L{LXs} {ACy + ACh / 2} L{ACx - 2} {ACy + ACh / 2}",
    "state2": f"M{LXs} {RCy + RCh / 2} L{RCx - 2} {RCy + RCh / 2}",
    "action": f"M{RXa} {ACy - 18} L{RXa} {sy_} L{EX + EW + 2} {sy_}",
    "action0": f"M{ACx + ACw / 2} {ACy} L{ACx + ACw / 2} {ACy - 18} L{RXa} {ACy - 18}",
    "reward": f"M{RCx + RCw / 2} {EY} L{RCx + RCw / 2} {RCy + RCh + 2}",
    "cost": f"M{CCx + CCw / 2} {EY} L{CCx + CCw / 2} {CCy + CCh + 2}",
}
for k, pth in paths.items():
    o.append(f'<path d="{pth}" fill="none" stroke="#222" stroke-width="1.7"'
             + ('' if k in ("action0",) else ' marker-end="url(#ah)"') + '/>')
o.append(pulse(paths["state"], "#1971c2", 2.2, 0.0))
o.append(pulse(paths["action0"] + paths["action"].replace("M", " L", 1), "#0c8599", 2.4, 0.6))
o.append(pulse(paths["reward"], "#2f9e44", 1.2, 1.2))
o.append(pulse(paths["cost"], "#c2255c", 1.2, 1.5))
o.append(mixed([M_(r"$s_n$"), T_(": state")], LXs + 6, RCy + RCh + 34, 18)[0])
o.append(mixed([M_(r"$r_n$")], RCx + RCw / 2 + 6, EY - 22, 18)[0])
o.append(mixed([M_(r"$c_{\mathrm{co},n},\,c_{\mathrm{so},n}$")], CCx + CCw / 2 + 6, EY - 22, 18)[0])
o.append(mixed([M_(r"$\bm{w}_n$"), T_(": action")], AX1 - 12, ACy - 32, 18, anchor="end")[0])
# the action is the beamformer -> beam pattern

# ---------------- Configuration B (two eavesdropper trains), stacked under A in the right column
_PY = PY
PY = PY2
o += panel(sB, PX[0], "")
o.append(mixed([("t", "Zenith "), ("m", r"$\zeta$"), ("t", " [deg]")], PX[0] - 42, PY + PH / 2, 17, anchor="middle", rotate=True)[0])
LX, LY = PX[0] + 8, PY2 + PH - 96
o.append(f'<rect x="{LX}" y="{LY}" width="162" height="88" rx="5" fill="#fff" fill-opacity=".88" stroke="#888"/>'
         f'<g transform="translate({LX + 16} {LY + 19}) scale(1.05)">{star}</g><text x="{LX + 33}" y="{LY + 25}" font-size="15">Serving satellite</text>'
         f'<g transform="translate({LX + 16} {LY + 45}) scale(1.05)">{tri}</g><text x="{LX + 33}" y="{LY + 51}" font-size="15">Eavesdropper</text>'
         f'<line x1="{LX + 6}" y1="{LY + 71}" x2="{LX + 26}" y2="{LY + 71}" stroke="#5c6070"/><text x="{LX + 33}" y="{LY + 77}" font-size="15">Orbit trace</text>')
PY = _PY
HTOT = 512
o.append('</svg>')
o[0] = o[0].replace('{HTOT}', str(int(HTOT))); o = [x.replace('{HTOT}', str(int(HTOT))) for x in o]
open("assets/img/research/ai-rlbf-anim.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")

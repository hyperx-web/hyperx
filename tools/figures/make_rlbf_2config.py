# Animated SVG (SMIL only, works inside <img>) for the TWC paper "Reinforcement Learning-Based Secure Beamforming
# Against Satellite Eavesdroppers": beam-gain maps (azimuth tau x zenith zeta) of the ground terminal's 4x4 UPA during
# one LEO pass, side by side for two test configurations (3 and 5 satellite eavesdroppers).
# Orbits, angles and array response come from the paper's simulation code (read-only: configs/submitted/config_loader.py,
# src/envs/satellite_core.py, constants_eve_3_M16.yaml / constants_eve_5_M16.yaml).
# Beam: null-space projection toward the visible eavesdroppers (illustrative, not the trained actor).
# Usage: python tools/figures/make_rlbf_anim.py   (writes assets/img/research/ai-rlbf-2config-anim.svg; saved two-configuration version)
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
PW, PH, PY = 340, 410, 38                            # panel size / top
PX = [52, 410]                                       # panel left edges
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

    def gain_db(self, g):
        (ts, zs, _), eves = g[0], [e for e in g[1:] if e[2]]
        w = self.resp(ts, zs)
        if eves:
            E = np.stack([self.resp(e[0], e[1]) for e in eves], 1)
            w = (np.eye(self.M) - E @ np.linalg.pinv(E)) @ w
        w /= np.linalg.norm(w)
        return 10 * np.log10(np.maximum(np.abs(self.A.conj() @ w) ** 2 / self.M, 1e-6))


def jpg(G):
    big = np.array(Image.fromarray(G.astype(np.float32)).resize((PW, PH), Image.BICUBIC))[::-1]
    lev = (np.clip(big, -DR, 0) + DR) / DR                                          # continuous gradient
    b = io.BytesIO(); Image.fromarray(cmap(lev)).save(b, "JPEG", quality=64)
    return base64.b64encode(b.getvalue()).decode()


star = '<path d="M0 -10 L2.7 -3.2 L10 -3.2 L4.1 1.4 L6.4 8.6 L0 4.1 L-6.4 8.6 L-4.1 1.4 L-10 -3.2 L-2.7 -3.2 Z" fill="#ffd43b" stroke="#333" stroke-width="1.2"/>'
tri = '<path d="M0 -8 L7 5.5 L-7 5.5 Z" fill="#fff" stroke="#222" stroke-width="1.6"/>'
kt = ";".join(f"{f / NF:.4f}" for f in range(NF)) + ";1"


def panel(sco, X0, title):
    sx = lambda a: X0 + (a + 180) / 360 * PW
    sy = lambda z: PY + PH - z / 90 * PH
    geo = [sco.geometry(sco.dur * f / NF) for f in range(NF)]
    o = [f'<text x="{X0 + PW / 2}" y="{PY - 12}" font-size="15" font-weight="bold" text-anchor="middle">{title}</text>',
         f'<clipPath id="cp{X0}"><rect x="{X0}" y="{PY}" width="{PW}" height="{PH}" rx="6"/></clipPath>',
         f'<g clip-path="url(#cp{X0})">']
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
    for a in range(-150, 181, 50):
        o.append(f'<text x="{sx(a):.1f}" y="{PY + PH + 16}" font-size="11" fill="#444" text-anchor="middle">{a}</text>')
    for z in (range(0, 91, 15) if X0 == PX[0] else ()):   # y tick labels only on the left panel
        o.append(f'<text x="{X0 - 6}" y="{sy(z) + 4:.1f}" font-size="11" fill="#444" text-anchor="end">{z}</text>')
    o.append(f'<text x="{X0 + PW / 2}" y="{PY + PH + 34}" font-size="13" text-anchor="middle">Azimuth τ [deg]</text>')
    return o


base = SIM + r"\configs\submitted\constants_eve_"
s3 = Scenario(base + "3_M16.yaml")                   # paper test scenario
s5 = Scenario(base + "5_M16.yaml", orbit=dict(i_s=88.0, omega_s=0.0,   # eavesdroppers fly in trains: 2 on one orbit, 3 on another, 4 deg apart
                                              i_e=[87.0, 87.0, 96.0, 96.0, 96.0], omega_e=[20.0, 20.0, -45.0, -45.0, -45.0],
                                              u_off=[3.0, 7.0, -6.0, -2.0, 2.0]))
for sco in (s3, s5):
    print("visible eves:", [sum(e[2] for e in sco.geometry(sco.dur * f / 10)[1:]) for f in range(10)], "pass", sco.dur)
o = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 820 500" font-family="Helvetica, Arial, sans-serif">',
     '<rect width="820" height="500" fill="#fff"/>']
o += panel(s3, PX[0], "Configuration A")
o += panel(s5, PX[1], "Configuration B")
o.append(f'<text transform="translate(18 {PY + PH / 2}) rotate(-90)" font-size="13" text-anchor="middle">Zenith ζ [deg]</text>')
bar = np.repeat(cmap(np.linspace(1, 0, PH))[:, None, :], 14, 1)
b = io.BytesIO(); Image.fromarray(bar).save(b, "PNG")
CBX = PX[1] + PW + 14
o.append(f'<image x="{CBX}" y="{PY}" width="12" height="{PH}" preserveAspectRatio="none" href="data:image/png;base64,{base64.b64encode(b.getvalue()).decode()}"/>'
         f'<rect x="{CBX}" y="{PY}" width="12" height="{PH}" fill="none" stroke="#6b7080"/>')
for db in (0, -10, -20, -30):
    o.append(f'<text x="{CBX + 16}" y="{PY + (-db) / DR * PH + 4:.1f}" font-size="11">{db} dB</text>')
LX, LY = PX[1] + PW - 122, PY + PH - 76             # legend: vertical, inside the right panel (bottom-right)
o.append(f'<rect x="{LX}" y="{LY}" width="114" height="66" rx="5" fill="#fff" fill-opacity=".88" stroke="#888"/>'
         f'<g transform="translate({LX + 14} {LY + 15}) scale(.85)">{star}</g><text x="{LX + 26}" y="{LY + 19}" font-size="11">Serving satellite</text>'
         f'<g transform="translate({LX + 14} {LY + 34}) scale(.85)">{tri}</g><text x="{LX + 26}" y="{LY + 38}" font-size="11">Eavesdropper</text>'
         f'<line x1="{LX + 6}" y1="{LY + 52}" x2="{LX + 22}" y2="{LY + 52}" stroke="#5c6070"/><text x="{LX + 26}" y="{LY + 56}" font-size="11">Orbit trace</text>')
o.append('</svg>')
open("assets/img/research/ai-rlbf-2config-anim.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")

# Animated SVG (SMIL only, works inside <img>) of how AI is used in the JSAC paper
# "Beamspace-transported neural warm start (BT-NWS-GPI)". Top: the per-slot pipeline (beamspace transport + neural
# rebalancing -> warm start -> a few GPI updates, fed back through a one-slot delay). Bottom: a zoom into the
# permutation-equivariant rebalancing network (shared encoder, mean pooling, per-user / common heads, bounded
# corrections, softmax reconstruction), which is the AI component of the method.
# Usage: python tools/figures/make_btnws_anim.py   (writes assets/img/research/ai-btnws-anim.svg)
import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from svgtex import mixed  # noqa: E402

W, H = 1000, 576
T_ = lambda t: ("t", t)
M_ = lambda m: ("m", m)
PINK, PINKD = "#f1aeb5", "#c2255c"
o = [f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 {W} {H}" font-family="Arial, Helvetica, sans-serif">',
     '<defs><marker id="ah" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     '<path d="M0 0L10 5L0 10z" fill="#222"/></marker>'
     '<marker id="ahp" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto">'
     f'<path d="M0 0L10 5L0 10z" fill="{PINKD}"/></marker></defs>',
     f'<rect width="{W}" height="{H}" fill="#fff"/>']


def rbox(x, y, w, h, lines, fill, px=16, gap=6, stroke="#333", bold_first=True):
    out = [f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="{fill}" stroke="{stroke}" stroke-width="1.6"/>']
    for i, parts in enumerate(lines):
        out.append(mixed(parts, x + w / 2, y + h / 2 + (i - (len(lines) - 1) / 2) * (px + gap), px, anchor="middle",
                         bold=(bold_first and i == 0))[0])
    return "".join(out)


def arrow(path, col="#222", w=1.7, mk="ah", dash=False):
    return (f'<path d="{path}" fill="none" stroke="{col}" stroke-width="{w}" marker-end="url(#{mk})"'
            + (' stroke-dasharray="6 5"' if dash else '') + '/>')


def pulse(path, col, dur=1.6, begin=0.0, r=3.8):
    return (f'<circle r="{r}" fill="{col}"><animateMotion dur="{dur}s" begin="{begin}s" repeatCount="indefinite" path="{path}"/>'
            f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.9;1" dur="{dur}s" begin="{begin}s" repeatCount="indefinite"/></circle>')


def glow(x, y, w, h, begin):
    return (f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="8" fill="#fff" opacity="0">'
            f'<animate attributeName="opacity" values="0;.22;0" dur="1.6s" begin="{begin}s" repeatCount="indefinite"/></rect>')


def region(x, y, w, h, title, fill, stroke="#222"):
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="20" fill="{fill}" fill-opacity=".45" stroke="{stroke}" stroke-width="1.6" stroke-dasharray="7 5"/>')
    if title:
        o.append(f'<text x="{x + w / 2}" y="{y - 9}" font-size="21" font-weight="bold" text-anchor="middle">{title}</text>')


def R(b): return b[0] + b[2]
def L(b): return b[0]
def CY(b): return b[1] + b[3] / 2
def CX(b): return b[0] + b[2] / 2


# ================= top: per-slot pipeline
# (no frame around the per-slot pipeline)
PV = (30, 28, 192, 72)
CU = (30, 114, 192, 72)
BT = (254, 28, 244, 72)
NN = (254, 114, 244, 72)
WS = (536, 71, 150, 72)
GP = (722, 71, 186, 72)
ZX = 948                                             # x of the solution label z_t
o.append(rbox(*PV, [[T_("Previous slot")], [M_(r"$\mathbf{F}_{t-1},\,\tilde{\mathbf{p}}_{t-1},\,\tilde{\mathbf{q}}_{t-1}$")]], "#f8f9fa", 18))
o.append(rbox(*CU, [[T_("Current slot")], [M_(r"$\mathbf{A}_t,\ \mathbf{d}_t$")]], "#f8f9fa", 18))
o.append(rbox(*BT, [[T_("Beamspace transport")], [M_(r"$\mathbf{A}_t\mathbf{A}_{t-1}^{\dagger}\mathbf{F}_{t-1}$")]], "#cfe2ff", 18))
o.append(rbox(*NN, [[T_("Neural rebalancing")]], PINK, 18, stroke=PINKD))
o.append(rbox(*WS, [[T_("Warm start")], [M_(r"$\mathbf{z}_t^{(0)}$")]], "#e5dbff", 18))
o.append(rbox(*GP, [[T_("GPI updates")], [M_(r"$\mathcal{G}_t^{\,T}$"), T_(", few steps")]], "#e2f0d9", 18))
o.append(mixed([M_(r"$\mathbf{z}_t$")], (R(GP) + 978) / 2, CY(GP) - 20, 23, anchor="middle")[0])
top = [f"M{R(PV)} {CY(PV)} L{L(BT) - 2} {CY(BT)}",
       f"M{R(CU)} {CU[1] + 18} C{R(CU) + 22} {CU[1] + 18} {L(BT) - 22} {BT[1] + 46} {L(BT) - 2} {BT[1] + 46}",
       f"M{R(CU)} {CY(CU) + 8} L{L(NN) - 2} {CY(CU) + 8}",
       f"M{R(PV)} {PV[1] + 46} C{R(PV) + 22} {PV[1] + 46} {L(NN) - 22} {NN[1] + 16} {L(NN) - 2} {NN[1] + 16}",
       f"M{R(BT)} {CY(BT)} C{R(BT) + 26} {CY(BT)} {L(WS) - 26} {WS[1] + 18} {L(WS) - 2} {WS[1] + 18}",
       f"M{R(NN)} {CY(NN)} C{R(NN) + 26} {CY(NN)} {L(WS) - 26} {WS[1] + 44} {L(WS) - 2} {WS[1] + 44}",
       f"M{R(WS)} {CY(WS)} L{L(GP) - 2} {CY(GP)}",
       f"M{R(GP)} {CY(GP)} L978 {CY(GP)}"]
cols = ["#1971c2", "#1971c2", PINKD, PINKD, "#1971c2", PINKD, "#7048e8", "#2b8a3e"]
for p in top:
    o.append(arrow(p))
for i, p in enumerate(top):
    o.append(pulse(p, cols[i], 1.3, 0.12 * i))

# ================= bottom: zoom into the rebalancing network, reusing the animated network figure of the paper
import re as _re
ZY0, ZY1 = 236, 566
region(14, ZY0, 972, ZY1 - ZY0, "", "none", PINKD)
_fill_at = len(o)                                    # white fills of the two sub-frames go here (under the content)
o.append(f'<path d="M{L(NN)} {NN[1] + NN[3]} L34 {ZY0} M{R(NN)} {NN[1] + NN[3]} L966 {ZY0}" stroke="{PINKD}" stroke-width="1" stroke-dasharray="3 4" fill="none" opacity=".6"/>')
src = open("assets/img/research/ai-network-anim.svg", encoding="utf-8").read()
vb = _re.search(r'viewBox="([^"]+)"', src).group(1)
vw, vh = [float(v) for v in vb.split()[2:]]
inner = src[src.index(">", src.index("<svg")) + 1:src.rindex("</svg>")]
inner = _re.sub(r'id="([^"]+)"', r'id="nw_\1"', inner)
inner = _re.sub(r'href="#([^"]+)"', r'href="#nw_\1"', inner)
inner = _re.sub(r'url\(#([^)]+)\)', r'url(#nw_\1)', inner)
NH = ZY1 - ZY0 - 28
NW_ = NH * vw / vh
NX, NY = 24, ZY0 + 14
o.append(f'<svg x="{NX}" y="{NY}" width="{NW_:.1f}" height="{NH}" viewBox="{vb}" overflow="visible">{inner}</svg>')
# the encoder's "shared" label sits under the sub-frame tag; hide it and label the encoder group from below instead
_k = NH / vh
_ex0, _ex1, _ey1 = 43.0, 71.8, 79.8                  # encoder group box in network units (x range, bottom)
o.append(f'<rect x="{NX + _ex0 * _k:.1f}" y="{NY - 2}" width="{(_ex1 - _ex0) * _k:.1f}" height="{8.6 * _k:.1f}" fill="#fff"/>')
o.append(f'<text x="{NX + (_ex0 + _ex1) / 2 * _k:.1f}" y="{NY + (_ey1 + 7) * _k:.1f}" font-size="{6.3 * _k:.1f}" fill="#4f6b3a" text-anchor="middle">shared</text>')
# scores -> bounded corrections -> reconstruction
BC = (986 - (NX + 6 - 14) - 14 - 274, ZY0 + 40, 274, 116)
SM = (BC[0], ZY0 + 190, 274, 116)
a1 = f"M{NX + NW_ - 8} {CY(BC)} L{L(BC) - 16} {CY(BC)}"           # network frame edge -> post-processing frame edge
a2 = f"M{CX(BC)} {BC[1] + BC[3]} L{CX(SM)} {SM[1] - 2}"
o.append(arrow(a1)); o.append(arrow(a2))
o.append(pulse(a1, PINKD, 0.9, 0.2)); o.append(pulse(a2, "#e8590c", 0.9, 0.7))
o.append(mixed([M_(r"$\mathbf{r}^{p}_t,\,\mathbf{r}^{q}_t$")], (NX + NW_ - 8 + L(BC) - 14) / 2, CY(BC) - 20, 17, anchor="middle")[0])
o.append(rbox(*BC, [[T_("Bounded correction")], [M_(r"$\boldsymbol{\ell}=\ell_{\max}\tanh(\mathbf{r}/\ell_{\max})$")]], "#fff3bf", 18, 14))
o.append(glow(*BC, 0.4))
o.append(rbox(*SM, [[T_("Reconstruct")], [M_(r"$\mathbf{p}_t^{(0)}=\mathrm{softmax}(\log\tilde{\mathbf{p}}_{t-1}+\boldsymbol{\ell}^{p})$")],
                    [M_(r"$\mathbf{q}_t^{(0)}=\mathrm{softmax}(\log\tilde{\mathbf{q}}_{t-1}+\boldsymbol{\ell}^{q})$")]], "#e5dbff", 18, 10))
o.append(glow(*SM, 0.9))
def subframe(x, y, w, h, label, col):
    """inner dashed frame with its label sitting on the top edge"""
    tw = len(label) * 8.6 + 16
    o.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{col}" stroke-width="1.4" stroke-dasharray="5 4"/>'
             f'<rect x="{x + 14}" y="{y - 11}" width="{tw:.0f}" height="22" rx="6" fill="#fff" stroke="{col}" stroke-width="1.2"/>'
             f'<text x="{x + 14 + tw / 2:.0f}" y="{y + 5}" font-size="15" font-weight="bold" fill="{col}" text-anchor="middle">{label}</text>')


subframe(NX + 6, ZY0 + 22, NW_ - 14, ZY1 - ZY0 - 34, "Rebalancing network", "#2b8a3e")
subframe(L(BC) - 14, ZY0 + 22, BC[2] + 28, ZY1 - ZY0 - 34, "Post-processing", "#868e96")
o.append('</svg>')
open("assets/img/research/ai-btnws-anim.svg", "w", encoding="utf-8").write("\n".join(o))
print("ok")

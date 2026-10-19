# Shared helpers for animated research figures: Arial text mixed with LaTeX math (latex + dvisvgm -> SVG outlines).
# ---------------- LaTeX labels: latex + dvisvgm (MiKTeX) -> glyph outlines embedded as nested <svg>
import os, re, subprocess, tempfile
_TEXN = [0]
TEXDIR = os.path.join(tempfile.gettempdir(), "svgtex_cache")


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

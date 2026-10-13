# PDF figure -> vector SVG with signal dots animated along arrows
import sys, math, pymupdf
src, out = sys.argv[1], sys.argv[2]
doc = pymupdf.open(src); pg = doc[0]
svg = pg.get_svg_image(text_as_path=True)
dr = pg.get_drawings()

heads = []   # small filled shapes = arrowheads
for d in dr:
    if d.get('fill') is not None and d['rect'].width < 9 and d['rect'].height < 9 and d['type'] in ('f', 'fs'):
        r = d['rect']; heads.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2, d['fill']))

def near(p, q, tol=7): return math.hypot(p[0] - q[0], p[1] - q[1]) < tol
paths = []
for d in dr:
    if d['type'] not in ('s', 'fs') or d.get('color') is None: continue
    pts = []
    ok = True
    for it in d['items']:
        if it[0] != 'l': ok = False; break
        a, b = (it[1].x, it[1].y), (it[2].x, it[2].y)
        if not pts: pts = [a, b]
        elif near(pts[-1], a, 0.6): pts.append(b)
        else: ok = False; break
    if not ok or len(pts) < 2: continue
    L = sum(math.hypot(pts[i+1][0]-pts[i][0], pts[i+1][1]-pts[i][1]) for i in range(len(pts)-1))
    if L < 12: continue
    end, start = pts[-1], pts[0]
    he = [h for h in heads if near(h[:2], end, 8)]
    hs = [h for h in heads if near(h[:2], start, 8)]
    if hs and not he: pts = pts[::-1]; he = hs
    if not he: continue
    paths.append((pts, L, d['color']))

def col(c): return '#%02x%02x%02x' % tuple(int(v * 255) for v in c)
g = ['<g class="signals">']
for i, (pts, L, c) in enumerate(paths):
    dpath = 'M' + ' L'.join(f'{x:.2f} {y:.2f}' for x, y in pts)
    dur = max(1.2, L / 55)
    begin = (pts[0][0] / pg.rect.width) * 1.6   # left-to-right stagger
    color = col(c)
    if color in ('#000000', '#3f3f3f', '#404040', '#333333') or sum(c) < 0.9: color = '#e8590c'
    g.append(f'<circle r="1.9" fill="{color}" opacity="0"><animateMotion dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite" path="{dpath}"/>'
             f'<animate attributeName="opacity" values="0;1;1;0" keyTimes="0;.1;.85;1" dur="{dur:.2f}s" begin="{begin:.2f}s" repeatCount="indefinite"/></circle>')
g.append('</g>')
svg = svg.replace('</svg>', '\n'.join(g) + '\n</svg>')
# make it responsive
import re
svg = re.sub(r'<svg([^>]*?) width="[^"]*" height="[^"]*"', r'<svg\1', svg, count=1)
open(out, 'w', encoding='utf-8').write(svg)
print(out, 'arrows animated:', len(paths), 'heads:', len(heads))

# PDF block diagram -> vector SVG with signals flowing along the wires.
# Usage: python tools/animate_figure.py figure.pdf out.svg
#
#  - every stroked straight segment is a wire; small filled shapes are arrowheads,
#    larger shapes are blocks (boxes, adders, antenna arrays, ...).
#  - wire directions start at arrowheads and are propagated through junctions and blocks.
#  - start times are propagated along the graph (also through blocks), so a pulse travels
#    from the inputs all the way to the outputs; then the cycle repeats.
#  - every source gets its own colour; when signals merge, the pulse shows the blended colour.
import sys, math, re, pymupdf

SPEED = 70.0      # pt per second
TOL = 3.2         # endpoint matching tolerance (pt), bridges junction dots
PALETTE = [(232, 89, 12), (47, 158, 68), (28, 126, 214), (214, 51, 108), (245, 159, 0), (112, 72, 232)]

src, out = sys.argv[1], sys.argv[2]
pg = pymupdf.open(src)[0]
svg = pg.get_svg_image(text_as_path=True)

heads, blocks, segs = [], [], []
for d in pg.get_drawings():
    r = d['rect']
    kinds = ''.join(it[0] for it in d['items'])
    if d.get('fill') is not None and d['type'] in ('f', 'fs'):
        if r.width < 4.5 and r.height < 4.5:
            if kinds != 'cccc':                     # not a junction dot -> arrowhead
                heads.append(((r.x0 + r.x1) / 2, (r.y0 + r.y1) / 2))
            continue
        if r.width < 0.5 * pg.rect.width:           # skip background panels
            blocks.append((r.x0, r.y0, r.x1, r.y1))
    if d['type'] in ('s', 'fs') and d.get('color') is not None:
        if set(kinds) != {'l'}:
            if d['type'] == 's' and r.width > 4 and r.height > 4:
                blocks.append((r.x0, r.y0, r.x1, r.y1))   # stroked circle / outline
            continue
        for it in d['items']:
            a, b = (it[1].x, it[1].y), (it[2].x, it[2].y)
            if math.dist(a, b) > 0.8:
                segs.append({'a': a, 'b': b, 'col': d['color'], 'dir': 0})

def inside(p, b): return b[0] - .3 <= p[0] <= b[2] + .3 and b[1] - .3 <= p[1] <= b[3] + .3
def touches(p, b, m=1.5): return b[0] - m <= p[0] <= b[2] + m and b[1] - m <= p[1] <= b[3] + m
# drop strokes drawn inside blocks (e.g. the '+' of an adder)
segs = [s for s in segs if not any(inside(s['a'], b) and inside(s['b'], b) for b in blocks)]

def on_seg(p, s, tol=TOL):
    (x1, y1), (x2, y2) = s['a'], s['b']
    L2 = (x2 - x1) ** 2 + (y2 - y1) ** 2
    t = ((p[0] - x1) * (x2 - x1) + (p[1] - y1) * (y2 - y1)) / L2
    if t < -0.02 or t > 1.02: return None
    return t if math.dist(p, (x1 + t * (x2 - x1), y1 + t * (y2 - y1))) < tol else None

def start(s): return s['a'] if s['dir'] == 1 else s['b']
def end(s): return s['b'] if s['dir'] == 1 else s['a']

# 1) arrowheads give directions
for s in segs:
    for h in heads:
        da, db = math.dist(s['a'], h), math.dist(s['b'], h)
        if min(da, db) < 3.5:
            s['dir'] = 1 if db < da else -1
            break

# 2) propagate directions through junctions, then out of blocks
def junction_pass():
    changed = True
    while changed:
        changed = False
        for s in segs:
            if s['dir']: continue
            for which, p in ((1, s['b']), (-1, s['a'])):
                for d in segs:
                    if d is s or not d['dir'] or on_seg(p, d) is None: continue
                    s['dir'] = -which if math.dist(p, end(d)) < TOL else which
                    changed = True; break
                if s['dir']: break

junction_pass()
for _ in range(3):
    for s in segs:
        if s['dir']: continue
        for which, p in ((1, s['a']), (-1, s['b'])):
            for b in blocks:
                if touches(p, b) and any(d['dir'] and touches(end(d), b, 6) for d in segs if d is not s):
                    s['dir'] = which; break
            if s['dir']: break
    junction_pass()

wires = [s for s in segs if s['dir']]
# remaining undirected strokes (antenna arrays, symbols): each connected cluster is a block
groups = []
for s in [s for s in segs if not s['dir']]:
    hit = [g for g in groups if any(min(math.dist(p, q) for p in (s['a'], s['b']) for q in (t['a'], t['b'])) < TOL for t in g)]
    groups = [g for g in groups if g not in hit] + [[s] + [t for g in hit for t in g]]
for g in groups:
    xs = [p[0] for s in g for p in (s['a'], s['b'])]; ys = [p[1] for s in g for p in (s['a'], s['b'])]
    blocks.append((min(xs), min(ys), max(xs), max(ys)))

def near_block(p):
    for b in blocks:
        if touches(p, b, 6): return b
    return None

for s in wires:
    s['len'] = math.dist(s['a'], s['b'])

# 3) predecessors, start times and colours
def preds(s):
    p = start(s); res = []
    for d in wires:
        if d is s: continue
        if math.dist(end(d), p) < TOL:
            res.append((d, d['len']))
        else:
            t = on_seg(p, d)
            if t is not None and math.dist(p, start(d)) > TOL:
                res.append((d, math.dist(start(d), p)))
    if not res:
        blk = near_block(p)
        if blk:
            ins = [d for d in wires if d is not s and near_block(end(d)) == blk]
            straight = abs(end(s)[1] - p[1]) < 1
            aligned = [d for d in ins if abs(end(d)[1] - p[1]) < 2 and abs(end(d)[1] - start(d)[1]) < 1]
            if straight and aligned:
                ins = aligned            # straight-through path keeps its own signal
            res = [(d, d['len'] + 4) for d in ins]
    return res

def rgb(c): return tuple(int(v * 255) for v in c)
k = 0
for s in wires:
    s['P'] = preds(s); s['t0'] = None; s['src'] = None
    if not s['P']:
        c = rgb(s['col'])
        if sum(c) < 230:                 # black/grey source -> distinct palette colour
            c = PALETTE[k % len(PALETTE)]; k += 1
        s['src'] = {c}; s['t0'] = 0.0
for _ in range(len(wires) + 5):
    for s in wires:
        if s['P'] and all(d['t0'] is not None for d, _ in s['P']):
            s['t0'] = max(d['t0'] + off / SPEED for d, off in s['P'])
            s['src'] = set().union(*[d['src'] for d, _ in s['P']])
for s in wires:
    if s['t0'] is None: s['t0'] = 0.0
    if not s['src']: s['src'] = {PALETTE[0]}

cycle = max(s['t0'] + s['len'] / SPEED for s in wires) + 0.8

def colour(s):
    cs = list(s['src'])
    return '#%02x%02x%02x' % tuple(round(sum(c[i] for c in cs) / len(cs)) for i in range(3))

# 4) emit
g = ['<g class="signals">']
for s in wires:
    a, b = start(s), end(s)
    t0 = s['t0'] / cycle
    t1 = min((s['t0'] + s['len'] / SPEED) / cycle, 0.999)
    r = 1.7 + 0.25 * (len(s['src']) - 1)
    g.append(
        f'<circle r="{r:.2f}" fill="{colour(s)}" opacity="0">'
        f'<animateMotion dur="{cycle:.2f}s" repeatCount="indefinite" calcMode="linear" keyPoints="0;0;1;1" '
        f'keyTimes="0;{t0:.4f};{t1:.4f};1" path="M{a[0]:.2f} {a[1]:.2f} L{b[0]:.2f} {b[1]:.2f}"/>'
        f'<animate attributeName="opacity" dur="{cycle:.2f}s" repeatCount="indefinite" values="0;0;1;1;0;0" '
        f'keyTimes="0;{max(t0 - 0.001, 0):.4f};{t0:.4f};{t1:.4f};{min(t1 + 0.001, 1):.4f};1"/></circle>')
g.append('</g>')
svg = svg.replace('</svg>', '\n'.join(g) + '\n</svg>')
svg = re.sub(r'<svg([^>]*?) width="[^"]*" height="[^"]*"', r'<svg\1', svg, count=1)
open(out, 'w', encoding='utf-8').write(svg)
print(out, 'wires:', len(wires), 'of', len(segs), 'cycle %.1fs' % cycle, 'sources:', k)

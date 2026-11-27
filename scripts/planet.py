"""ASCII planet as a flowing field (in the spirit of an ASCII shader).

A fixed texture of backend / infra / agent tokens sits on a character grid. Each
frame, a density field decides what every cell shows: dense cells reveal the token
under them, thinner cells show a ramp glyph ('+', '-', ':', '.'), empty cells
nothing. The field is a sphere rising out of the right edge whose limb ripples,
whose '....::::----++++' tail breathes, and through which darker channels drift.
Every time-dependent term goes round a whole number of times per loop, so the
last frame flows straight back into the first. Pure Python, deterministic."""
import math
import random

FONT = "SFMono-Regular, ui-monospace, Menlo, Consolas, 'Liberation Mono', monospace"
TOKENS = [
    "GET /v1/users 200 OK", "kafka.poll(events)", "pod/api-7f9c 1/1 Running", "agent.tool_call()",
    "{}", "=>", "grpc", "k8s", "async", "ACK", "retry(3)", "SELECT 1", "llm.step()", "202 Accepted",
    "go", "py", "lag=0", "HPA 3->12", "ready", "200", "await", "fn", "[]", "ok",
]
RAMP = [(.66, None), (.52, "+"), (.38, "-"), (.25, ":"), (.11, ".")]     # density -> glyph
RAMP_OP = {"+": .62, "-": .5, ":": .38, ".": .28}


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _hash(*k):
    """Deterministic 0..1 noise per integer tuple."""
    h = 2166136261
    for v in k:
        h = ((h ^ (v & 0xFFFFFFFF)) * 16777619) & 0xFFFFFFFF
        h ^= h >> 13
    return (h % 10007) / 10007.0


def _smooth_noise(x, y, seed):
    xi, yi = math.floor(x), math.floor(y)
    xf, yf = x - xi, y - yi
    u, v = xf * xf * (3 - 2 * xf), yf * yf * (3 - 2 * yf)
    a, b = _hash(xi, yi, seed), _hash(xi + 1, yi, seed)
    c, d = _hash(xi, yi + 1, seed), _hash(xi + 1, yi + 1, seed)
    return (a * (1 - u) + b * u) * (1 - v) + (c * (1 - u) + d * u) * v


class FlowPlanet:
    def __init__(self, x0, y0, x1, y1, cw, ch, cx, cy, R, tail=120.0, seed=4, frames=24,
                 star_x0=None, stars=.010, amp=1.0):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.cw, self.ch, self.cx, self.cy, self.R = cw, ch, cx, cy, R
        self.tail, self.seed, self.N, self.amp = tail, seed, frames, amp
        self.cols = int(math.ceil((x1 - x0) / cw))
        self.rows = int((y1 - y0) // ch)
        self.star_x0 = x0 if star_x0 is None else star_x0
        self.stars = stars
        L = (-0.72, -0.42, 0.55)
        ln = math.sqrt(sum(v * v for v in L))
        self.L = tuple(v / ln for v in L)

    # ---- geometry helpers
    def cell(self, c, r):
        return self.x0 + c * self.cw, round(self.y0 + (r + 1) * self.ch - self.ch * .27)   # x, baseline

    def light(self, x, y):
        """Crescent lambert term (sun off to the left, a little behind)."""
        dx, dy = (x - self.cx) / self.R, (y - self.cy) / self.R
        d2 = dx * dx + dy * dy
        if d2 >= 1:
            return .5
        dz = math.sqrt(1 - d2)
        return max(0.0, dx * self.L[0] + dy * self.L[1] + dz * self.L[2])

    def density(self, c, r, f):
        th = 2 * math.pi * f / self.N
        a = self.amp
        x = self.x0 + (c + .5) * self.cw
        y = self.y0 + (r + .5) * self.ch
        # the limb ripples: two waves travelling along it plus a fixed ragged edge
        wx = a * (8 * math.sin(y / 27 + th) + 4 * math.sin(y / 12 - 2 * th + 1.3)) \
            + 7 * (_smooth_noise(r * .5, 3.1, self.seed) - .5)
        dx, dy = (x + wx - self.cx) / self.R, (y - self.cy) / self.R
        dist = math.sqrt(dx * dx + dy * dy)
        jit = (_hash(c, r, f, self.seed) - .5) * .06 + (_hash(c, r, self.seed + 9) - .5) * .06
        if dist <= 1:
            # now and then a short '-++-' segment drifts down the surface
            band = math.sin(y / 21 - 2 * th)
            patch = _smooth_noise(c * .09 + 1.7, r * .35 - f * 4 / self.N * .35 * 3, self.seed + 3)
            if band > .93 and patch > .62:
                return .5 + jit
            return .9 + jit
        out = (dist - 1) * self.R                     # px outside the limb
        L = self.tail * (.32 + .68 * max(0.0, 1 - abs(dy)) ** .5) \
            * (1 + a * .18 * math.sin(y / 37 + th + .5))
        main = .68 * max(0.0, 1 - out / max(L, 1.0)) ** 1.2
        # a second, thinner '-++-' ring halfway out, which ripples outwards
        rc = L * (.5 + .08 * math.sin(y / 19 - th * 2))
        ring = .3 * math.exp(-((out - rc) / (L * .085)) ** 2)
        return main + ring + jit

    # ---- output
    def token_rows(self, P):
        """Static texture: one token stream per row, periodic with period P cells and
        reaching P cells left of anything visible, so it can scroll right P steps and
        loop. -> [(xs, baseline, text)]"""
        rnd = random.Random(self.seed * 31 + 7)
        out = []
        for r in range(self.rows):
            y = self.y0 + (r + .5) * self.ch
            dy = (y - self.cy) / self.R
            if abs(dy) >= 1.08:
                continue
            half = math.sqrt(max(0.0, 1 - min(1.0, dy * dy))) * self.R
            c0 = max(0, int((self.cx - half - 26 - self.x0) // self.cw))
            period = ""
            while len(period) < P:
                period += rnd.choice(TOKENS) + " " * rnd.choice((1, 2, 2, 3))
            period = period[:P]
            if period[-1] != " ":
                period = period[:-1] + " "          # tokens never fuse across the seam
            n = self.cols - c0 + P
            text = (period * (n // P + 2))[:n]
            xs = [self.x0 + (c0 - P + i) * self.cw for i in range(n)]
            out.append((xs, self.cell(0, r)[1], text))
        return out

    def frame(self, f):
        """-> (token_runs [(x, top, w, h)], ramp_glyphs [(x, y, glyph, opacity)])"""
        runs, ramp = [], []
        for r in range(self.rows):
            top = self.y0 + r * self.ch
            start = None
            for c in range(self.cols + 1):
                d = self.density(c, r, f) if c < self.cols else -1
                is_tok = d >= RAMP[0][0]
                if is_tok and start is None:
                    start = c
                if not is_tok and start is not None:
                    runs.append((self.x0 + start * self.cw, top, (c - start) * self.cw, self.ch))
                    start = None
                if c == self.cols or is_tok:
                    continue
                g = next((gl for th_, gl in RAMP[1:] if d >= th_), None)
                x, base = self.cell(c, r)
                if g is None:
                    if x >= self.star_x0 and _hash(c, r, self.seed + 77) < self.stars:
                        ramp.append((x, base, ".", .2))
                    continue
                lit = .62 + .38 * self.light(x + self.cw / 2, top + self.ch / 2)
                ramp.append((x, base, g, RAMP_OP[g] * lit))
        return runs, ramp


def glyph_runs(items, levels=6, lo=.12, hi=.62):
    """[(x, y, glyph, opacity)] -> a few <text> runs grouped by brightness, with
    explicit x/y lists, so the grid is exact whatever monospace font the viewer has."""
    buckets = [[] for _ in range(levels)]
    for x, y, g, op in items:
        k = 0 if hi == lo else int(round((min(hi, max(lo, op)) - lo) / (hi - lo) * (levels - 1)))
        buckets[k].append((x, y, g))
    out = []
    for k, its in enumerate(buckets):
        if not its:
            continue
        op = lo + (hi - lo) * k / (levels - 1)
        out.append(f'<text x="{" ".join(_n(x) for x, _, _ in its)}" y="{" ".join(_n(y) for _, y, _ in its)}" '
                   f'fill-opacity="{op:.2f}">{_esc("".join(g for _, _, g in its))}</text>')
    return "".join(out)


def row_text(xs, y, text):
    keep = [(x, g) for x, g in zip(xs, text) if g != " "]
    return (f'<text x="{" ".join(_n(x) for x, _ in keep)}" y="{_n(y)}">'
            f'{_esc("".join(g for _, g in keep))}</text>')


def flowing(pl, pid, frame_dt=.125, scroll_dt=.09, P=48, token_op=.84):
    """-> (defs, body) for a FlowPlanet: N field frames shown in turn (discrete
    visibility), each revealing the scrolling token texture through its own clip and
    adding its own ramp glyphs. Tokens drift left to right, one cell per scroll_dt."""
    N = pl.N
    D = N * frame_dt
    defs, body = [], []
    rows = pl.token_rows(P)
    scroll = (f'<animateTransform attributeName="transform" type="translate" '
              f'values="{";".join(_n(i * pl.cw) for i in range(P))}" calcMode="discrete" '
              f'dur="{P * scroll_dt:.3f}s" repeatCount="indefinite"/>')
    defs.append(f'<g id="{pid}t" fill-opacity="{token_op}">{scroll}'
                + "".join(row_text(xs, y, t) for xs, y, t in rows) + "</g>")
    lx, ly = pl.cx - pl.R * .93, pl.cy - pl.R * .22
    defs.append(f'<radialGradient id="{pid}g" cx="{_n(lx)}" cy="{_n(ly)}" r="{_n(pl.R * 1.3)}" '
                f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/>'
                f'<stop offset=".34" stop-color="#d6d6d6"/><stop offset=".62" stop-color="#555"/>'
                f'<stop offset="1" stop-color="#1e1e1e"/></radialGradient>'
                f'<mask id="{pid}m" maskUnits="userSpaceOnUse" x="{_n(pl.x0)}" y="{_n(pl.y0)}" '
                f'width="{_n(pl.x1 - pl.x0)}" height="{_n(pl.y1 - pl.y0)}">'
                f'<rect x="{_n(pl.x0)}" y="{_n(pl.y0)}" width="{_n(pl.x1 - pl.x0)}" '
                f'height="{_n(pl.y1 - pl.y0)}" fill="url(#{pid}g)"/></mask>')
    for f in range(N):
        runs, ramp = pl.frame(f)
        d = "".join(f"M{_n(x)} {_n(y)}h{_n(w)}v{_n(h)}h-{_n(w)}z" for x, y, w, h in runs) or "M0 0z"
        defs.append(f'<clipPath id="{pid}k{f}"><path d="{d}"/></clipPath>')
        if f == 0:
            vals, kts = "visible;hidden", f"0;{1 / N:.5f}"
        elif f == N - 1:
            vals, kts = "hidden;visible", f"0;{f / N:.5f}"
        else:
            vals, kts = "hidden;visible;hidden", f"0;{f / N:.5f};{(f + 1) / N:.5f}"
        anim = (f'<animate attributeName="visibility" values="{vals}" keyTimes="{kts}" '
                f'calcMode="discrete" dur="{D:.3f}s" repeatCount="indefinite"/>')
        body.append(f'<g visibility="{"visible" if f == 0 else "hidden"}">{anim}'
                    f'<g clip-path="url(#{pid}k{f})" mask="url(#{pid}m)"><use href="#{pid}t"/></g>'
                    f'{glyph_runs(ramp)}</g>')
    return "".join(defs), "".join(body)

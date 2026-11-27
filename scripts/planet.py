"""ASCII planet: a sphere rising at the right edge of the terminal, its surface a
stream of backend / infra / agent tokens, with a ramp tail ('....::::----++++')
trailing off the lit limb. The token surface can scroll sideways one cell at a
time, so the planet appears to turn. Pure Python, deterministic."""
import math
import random

FONT = "SFMono-Regular, ui-monospace, Menlo, Consolas, 'Liberation Mono', monospace"
TOKENS = [
    "GET /v1/users 200 OK", "kafka.poll(events)", "pod/api-7f9c 1/1 Running", "agent.tool_call()",
    "{}", "=>", "grpc", "k8s", "async", "ACK", "retry(3)", "SELECT 1", "llm.step()", "202 Accepted",
    "go", "py", "lag=0", "HPA 3->12", "ready", "200", "await", "fn", "[]", "ok",
]
TAIL = "+-:."          # nearest the limb first


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _n(v):
    s = f"{v:.1f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _stream(rnd, length):
    out = ""
    while len(out) < length:
        out += rnd.choice(TOKENS) + " " * rnd.choice((1, 2, 2, 3))
    return out[:length]


class Planet:
    """Geometry on a cw x ch character grid. (cx, cy, R) in pixels; the grid covers
    [x0, x1) x [y0, y1)."""

    def __init__(self, x0, y0, x1, y1, cw, ch, cx, cy, R, tail=120.0, seed=4, stars=.010, period=48,
                 star_x0=None):
        self.x0, self.y0, self.x1, self.y1 = x0, y0, x1, y1
        self.cw, self.ch, self.cx, self.cy, self.R = cw, ch, cx, cy, R
        self.tail, self.seed, self.stars, self.P = tail, seed, stars, period
        self.star_x0 = x0 if star_x0 is None else star_x0
        self.cols = int(math.ceil((x1 - x0) / cw))
        self.rows = int((y1 - y0) // ch)

    def _row(self, r):
        yc = self.y0 + (r + .5) * self.ch
        base = self.y0 + (r + 1) * self.ch - self.ch * .27
        dy = (yc - self.cy) / self.R
        return yc, base, dy

    def static(self):
        """Tail ramp + sparse stars: [(x, y, glyph, level)]."""
        rnd = random.Random(self.seed)
        out = []
        for r in range(self.rows):
            yc, base, dy = self._row(r)
            if abs(dy) < 1:
                xl = self.cx - math.sqrt(1 - dy * dy) * self.R
                tl = self.tail * (0.3 + 0.7 * (1 - dy * dy) ** .5) * rnd.uniform(.8, 1.15)
            else:
                xl, tl = None, 0.0
            for c in range(self.cols):
                x = self.x0 + c * self.cw
                xm = x + self.cw / 2
                if xl is not None and xm >= xl:
                    continue
                if xl is not None and xm >= xl - tl:
                    t = min(.999, max(0.0, (xl - xm) / tl + rnd.uniform(-.07, .07)))
                    if rnd.random() < t * .6:
                        continue
                    out.append((x, base, TAIL[int(t * len(TAIL))], .62 * (1 - t) + .12))
                elif rnd.random() < self.stars and x >= self.star_x0:
                    out.append((x, base, ".", .2))
        return out

    def surface(self):
        """Token rows inside the sphere. Each row starts at its first visible cell and
        runs P cells past the right edge, so it can scroll left P steps and loop."""
        rnd = random.Random(self.seed * 31 + 7)
        rows, clip = [], []
        for r in range(self.rows):
            yc, base, dy = self._row(r)
            if abs(dy) >= 1:
                continue
            xl = self.cx - math.sqrt(1 - dy * dy) * self.R
            c0 = max(0, int(math.ceil((xl - self.x0) / self.cw - .5)))
            ncell = self.cols - c0
            if ncell <= 0:
                continue
            period = _stream(rnd, self.P)
            text = (period * (ncell // self.P + 3))[: ncell + self.P]
            xs = [self.x0 + (c0 + i) * self.cw for i in range(len(text))]
            rows.append((xs, base, text))
            top = self.y0 + r * self.ch
            clip.append((self.x0 + c0 * self.cw, top, self.x1 - (self.x0 + c0 * self.cw), self.ch))
        return rows, clip

    def shading_mask(self, mid):
        """Crescent light: the sun sits off to the left and a little behind, so only
        the limb facing the text is bright; the far side keeps a faint earthshine."""
        cx, cy, R = self.cx, self.cy, self.R
        return (f'<radialGradient id="{mid}g" cx="{_n(cx - R * .93)}" cy="{_n(cy - R * .22)}" r="{_n(R * 1.3)}" '
                f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff"/>'
                f'<stop offset=".34" stop-color="#d6d6d6"/><stop offset=".62" stop-color="#555"/>'
                f'<stop offset="1" stop-color="#1e1e1e"/></radialGradient>'
                f'<mask id="{mid}" maskUnits="userSpaceOnUse" x="0" y="0" width="{_n(self.x1 + 10)}" '
                f'height="{_n(self.y1 + 10)}"><circle cx="{_n(cx)}" cy="{_n(cy)}" r="{_n(R + 2)}" '
                f'fill="url(#{mid}g)"/></mask>')


def glyph_runs(items, levels=6, lo=.12, hi=.75, attrs=""):
    """[(x, y, glyph, level)] -> a few <text> runs grouped by brightness, with explicit
    x/y lists, so the grid is exact whatever monospace font the viewer has."""
    buckets = [[] for _ in range(levels)]
    for x, y, g, lvl in items:
        if g != " ":
            buckets[min(levels - 1, int(lvl * levels))].append((x, y, g))
    out = []
    for k, its in enumerate(buckets):
        if not its:
            continue
        op = lo + (hi - lo) * (k / (levels - 1)) ** 1.2
        out.append(f'<text x="{" ".join(_n(x) for x, _, _ in its)}" y="{" ".join(_n(y) for _, y, _ in its)}" '
                   f'fill-opacity="{op:.2f}"{attrs}>{_esc("".join(g for _, _, g in its))}</text>')
    return "".join(out)


def row_text(xs, y, text):
    keep = [(x, g) for x, g in zip(xs, text) if g != " "]
    return (f'<text x="{" ".join(_n(x) for x, _ in keep)}" y="{_n(y)}">'
            f'{_esc("".join(g for _, g in keep))}</text>')

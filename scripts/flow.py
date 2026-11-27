"""Flowing ASCII streams: the terminal's backdrop.

Rows of backend / infra / agent tokens, with davemi-style '..::--++' ramps between
them, glide continuously from left to right, each row at its own speed (faster
rows are brighter, like nearer ones). A soft elliptical mask anchored past the
right edge makes every glyph spawn fully transparent around the middle of the
window and grow opaque as it travels right. Every row's text is periodic and its
translation is exactly one period per loop, so the motion never jumps.
Pure Python, deterministic."""
import random

FONT = "SFMono-Regular, ui-monospace, Menlo, Consolas, 'Liberation Mono', monospace"
TOKENS = [
    "GET /v1/users 200 OK", "kafka.poll(events)", "pod/api-7f9c 1/1 Running", "agent.tool_call()",
    "{}", "=>", "grpc", "k8s", "async", "ACK", "retry(3)", "SELECT 1", "llm.step()", "202 Accepted",
    "go", "py", "lag=0", "HPA 3->12", "ready", "200", "await", "[]", "ok", "stream.ack()",
]
RAMPS = ["..::--++", ".::--++", "::--++", "-++-", "..::", "--++", ".:-+"]


def _n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def _esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def _text(cells, y, cls_op):
    """cells: [(x, glyph)] -> one <text> with an explicit x per glyph (exact grid)."""
    cells = [(x, g) for x, g in cells if g != " "]
    if not cells:
        return ""
    return (f'<text x="{" ".join(_n(x) for x, _ in cells)}" y="{_n(y)}"{cls_op}>'
            f'{_esc("".join(g for _, g in cells))}</text>')


def streams(pid, x0, y0, x1, y1, lh, cw, fsz, cx, cy, rx, ry, seed=5, speed=(16.0, 38.0),
            period=(58, 84), ramp_op=.55):
    """-> (defs, body). Rows fill [x0, x1) x [y0, y1); the mask is an ellipse centred
    at (cx, cy) with radii (rx, ry): opaque at its centre, clear at its rim."""
    rnd = random.Random(seed)
    rows = int((y1 - y0) // lh)
    defs = [
        f'<radialGradient id="{pid}g" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" '
        f'gradientTransform="translate({_n(cx)} {_n(cy)}) scale({_n(rx)} {_n(ry)})">'
        '<stop offset="0" stop-color="#fff"/><stop offset=".42" stop-color="#fff" stop-opacity=".9"/>'
        '<stop offset=".68" stop-color="#fff" stop-opacity=".5"/>'
        '<stop offset=".86" stop-color="#fff" stop-opacity=".14"/>'
        '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<mask id="{pid}m" maskUnits="userSpaceOnUse" x="{_n(x0)}" y="{_n(y0)}" '
        f'width="{_n(x1 - x0)}" height="{_n(y1 - y0)}"><rect x="{_n(x0)}" y="{_n(y0)}" '
        f'width="{_n(x1 - x0)}" height="{_n(y1 - y0)}" fill="url(#{pid}g)"/></mask>'
    ]
    body = []
    vmin, vmax = speed
    for r in range(rows):
        base = round(y0 + (r + 1) * lh - lh * .27)
        v = rnd.uniform(vmin, vmax)
        P = rnd.randint(*period)
        s, kinds = "", ""
        sparse = rnd.random() < .3                       # some rows carry less, so it breathes
        while len(s) < P:
            piece = rnd.choice(TOKENS) if rnd.random() < .7 else rnd.choice(RAMPS)
            kind = "t" if piece in TOKENS else "r"
            gap = " " * (rnd.choice((6, 8, 10, 13)) if sparse else rnd.choice((3, 3, 4, 5, 6)))
            s += piece + gap
            kinds += kind * len(piece) + " " * len(gap)
        s, kinds = s[:P], kinds[:P]
        if s[-1] != " ":                        # pieces never fuse across the seam
            s, kinds = s[:-1] + " ", kinds[:-1] + " "
        span = P * cw
        ncell = int((x1 - x0) / cw) + P + 2
        text = (s * (ncell // P + 2))[:ncell]
        kind = (kinds * (ncell // P + 2))[:ncell]
        xs = [x0 - span + i * cw for i in range(ncell)]
        op = .38 + .62 * (v - vmin) / (vmax - vmin)          # faster rows read as nearer
        tok = _text([(x, g) for x, g, k in zip(xs, text, kind) if k == "t"], base,
                    f' fill-opacity="{op:.2f}"')
        rmp = _text([(x, g) for x, g, k in zip(xs, text, kind) if k == "r"], base,
                    f' fill-opacity="{op * ramp_op:.2f}"')
        dur = span / v
        body.append(f'<g><animateTransform attributeName="transform" type="translate" '
                    f'from="0 0" to="{_n(span)} 0" dur="{dur:.3f}s" repeatCount="indefinite"/>'
                    f'{tok}{rmp}</g>')
    art = (f'<g mask="url(#{pid}m)" fill="#fff" font-family="{FONT}" font-size="{_n(fsz)}" '
           f'xml:space="preserve">' + "".join(body) + "</g>")
    return "".join(defs), art

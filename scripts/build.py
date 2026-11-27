#!/usr/bin/env python3
"""ami.sh — generates the profile README artwork (assets/*.svg) and README.md.

    pip install fonttools brotli
    python3 scripts/build.py

Design system
  * Surfaces: opaque matte-black panels (#0A0A0A) with a soft top-left key
    light, fine film grain, a lit top edge and a hairline border. Opaque art
    looks intentional on GitHub's dark AND light themes, so no theme swap.
  * Type: Geist Sans + Geist Mono (SIL OFL, in ../fonts), outlined to paths by
    typeset.py so every visitor sees exactly this typography.
  * Greys only. One slow, quiet motion (orbits, a pulse, a cursor).
  * Phones (<= 600px) get stacked variants of the hero and stats via
    <picture media>; project cards are fixed-width so they stack by themselves.
"""
import math
import os
import sys
from xml.sax.saxutils import quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 846          # desktop width of every full-width piece: GitHub's profile README
                 # column is 847px at any viewport >= ~1280px (measured on github.com)
GAP = 12         # gutter between panels, everywhere (horizontal AND vertical)

# ------------------------------------------------------------------ palette
BG = "#0A0A0A"
INK = "#F0F0F0"
INK2 = "#9C9C9C"
INK3 = "#6E6E6E"
INK4 = "#454545"
INK5 = "#2A2A2A"

# ------------------------------------------------------------------ content
INTRO = ["I build scalable backends,", "infra and agentic systems."]
STACK = ["PYTHON", "GO", "KUBERNETES", "KAFKA", "LANGGRAPH"]

STATS = [
    dict(call="backends()", spark="rise",
         big=[("10", "big"), ("→", "arrow"), ("800", "big")],
         lines=["users in a week, zero downtime", "backend of an LLM markets agent"]),
    dict(call="infra()", spark="fall",
         big=[("90%", "big"), ("+", "suffix")],
         lines=["cut in mean time to first response", "self-healing k8s · 75+ services"]),
    dict(call="agents()", spark="step",
         big=[("up to ", "prefix"), ("+10", "big"), (" pp", "suffix")],
         lines=["Qwen · AndroidWorld, MobileWorld", "via my harness's trajectories"]),
]

CARDS = [
    dict(slug="pr-reviewer", url="https://github.com/Ami-sh/pr-reviewer",
         lines=["Independent one-shot LLM review for any PR,", "with an adversarial verifier on every finding."],
         mlines=["One-shot LLM review for", "any PR with an adversarial", "verifier on each finding."],
         tag="python · claude"),
    dict(slug="agentami", url="https://github.com/Ami-sh/agentami",
         lines=["A LangGraph agent for when your AI has too", "many tools: picks the top-k for every turn."],
         mlines=["A LangGraph agent for AIs", "with too many tools: picks", "the top-k on every turn."],
         tag="pip install agentami", mtag="python · pypi"),
]

LINKS = [
    ("LeetCode", "https://leetcode.com/u/f20191386/"),
    ("Stack Overflow", "https://stackoverflow.com/users/16179688/amish-gupta"),
    ("Physics SE", "https://physics.stackexchange.com/users/274874/amish-gupta"),
    ("Math SE", "https://math.stackexchange.com/users/824283/amish-gupta"),
]

ALT = dict(
    hero="ami.sh — intro(): I build scalable backends, infra and agentic systems. "
         "Python, Go, Kubernetes, Kafka, LangGraph.",
    stats="backends(): 10 → 800 users in a week with zero downtime, the backend of an LLM "
          "markets agent. infra(): mean time to first response cut by over 90%, a "
          "self-healing Kubernetes operator across 75+ services. agents(): up to +10 "
          "percentage points for open-source Qwen models on AndroidWorld / MobileWorld, "
          "trained on trajectories from my agent harness.",
)


# ------------------------------------------------------------------ helpers
def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def svg(w, h, body, defs="", label="", pad_bottom=GAP):
    h = h + pad_bottom
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(w)}" height="{n(h)}" '
            f'viewBox="0 0 {n(w)} {n(h)}" role="img" aria-label={quoteattr(label)}>'
            f'<title>{label}</title><defs>{defs}</defs>{body}</svg>\n')


def panel(pid, x, y, w, h, r=20, key=(0.18, 0.0), keyr=1.0, keya=0.085):
    """Matte panel: base, key light, grain, lit top edge, hairline border."""
    kx, ky = x + key[0] * w, y + key[1] * h
    kr = keyr * max(w, h) * 0.75
    defs = (
        f'<clipPath id="{pid}c"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}"/></clipPath>'
        f'<radialGradient id="{pid}k" cx="{n(kx)}" cy="{n(ky)}" r="{n(kr)}" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="{keya}"/>'
        f'<stop offset=".55" stop-color="#fff" stop-opacity="{n(keya * .25)}"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="{pid}e" x1="{n(x)}" y1="0" x2="{n(x + w)}" y2="0" gradientUnits="userSpaceOnUse">'
        f'<stop offset="0" stop-color="#fff" stop-opacity="0"/>'
        f'<stop offset=".35" stop-color="#fff" stop-opacity=".22"/>'
        f'<stop offset=".7" stop-color="#fff" stop-opacity=".08"/>'
        f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>'
    )
    body = (
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" rx="{r}" fill="{BG}"/>'
        f'<g clip-path="url(#{pid}c)">'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{pid}k)"/>'
        f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" filter="url(#grain)" opacity=".055"/>'
        f'</g>'
        f'<path d="M{n(x + r)} {n(y + .75)}H{n(x + w - r)}" stroke="url(#{pid}e)" stroke-width="1"/>'
        f'<rect x="{n(x + .5)}" y="{n(y + .5)}" width="{n(w - 1)}" height="{n(h - 1)}" rx="{r - .5}" '
        f'fill="none" stroke="#fff" stroke-opacity=".085"/>'
    )
    return defs, body


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="11" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.2 0 0 0 -1.05"/></filter>')
BLUR = lambda i, s: f'<filter id="{i}" x="-50%" y="-50%" width="200%" height="200%"><feGaussianBlur stdDeviation="{s}"/></filter>'  # noqa: E731


def vgrad(gid, y1, y2, top="#FFFFFF", bottom="#B0B0B0"):
    return (f'<linearGradient id="{gid}" x1="0" y1="{n(y1)}" x2="0" y2="{n(y2)}" gradientUnits="userSpaceOnUse">'
            f'<stop offset="0" stop-color="{top}"/><stop offset="1" stop-color="{bottom}"/></linearGradient>')


def fits(s, size, maxw, kind="sans", wght=400):
    w = T.width(s, size, kind, wght)
    if w > maxw:
        raise SystemExit(f"text too wide ({w:.0f} > {maxw:.0f}px): {s!r}")


def mono(s, x, y, size, fill, wght=400, tracking=0.0, anchor="start"):
    return T.text(s, x, y, size, "mono", wght, fill, tracking, anchor)


def sans(s, x, y, size, fill, wght=400, tracking=0.0, anchor="start", extra=""):
    return T.text(s, x, y, size, "sans", wght, fill, tracking, anchor, extra)


def status(x, y):
    """Pulsing 'live' dot + path label."""
    dot = (f'<circle cx="{n(x)}" cy="{n(y)}" r="7" fill="none" stroke="#fff" stroke-opacity=".5">'
           '<animate attributeName="r" values="3;10" dur="2.6s" repeatCount="indefinite"/>'
           '<animate attributeName="stroke-opacity" values=".45;0" dur="2.6s" repeatCount="indefinite"/></circle>'
           f'<circle cx="{n(x)}" cy="{n(y)}" r="3" fill="{INK}"/>')
    label, _ = mono("~/ami.sh", x + 12, y + 4, 12, INK3, tracking=.02)
    return dot + label


def wordmark(x, y, size):
    """'ami' lit, '.sh' recessed; returns (defs, body, width)."""
    f = T.face("sans", 600)
    tr = -0.045
    p1, w1 = sans("ami", x, y, size, "url(#wm)", 600, tr)
    gap = f.kern(f.gname("i"), f.gname(".")) * size / f.upm + tr * size
    p2, w2 = sans(".sh", x + w1 + gap, y, size, "#4D4D4D", 600, tr)
    glow, _ = sans("ami", x, y, size, "#fff", 600, tr, extra=' filter="url(#bloom)" opacity=".2"')
    defs = vgrad("wm", y - size * .74, y + size * .02, "#FFFFFF", "#ABABAB") + BLUR("bloom", size * .14)
    return defs, glow + p1 + p2, w1 + gap + w2


def cursor(x, y, size):
    h, w = size * .92, size * .42
    return (f'<rect x="{n(x)}" y="{n(y - h * .82)}" width="{n(w)}" height="{n(h)}" rx="1.5" fill="{INK}">'
            '<animate attributeName="opacity" values="1;1;0;0" keyTimes="0;.5;.5;1" dur="1.15s" '
            'repeatCount="indefinite"/></rect>')


def stack_row(x, y, size=11, items=STACK, maxw=None):
    out, cx = [], x
    for i, it in enumerate(items):
        if i:
            p, w = mono("·", cx + size * .9, y, size, INK4)
            out.append(p)
            cx += size * .9 + w + size * .9
        p, w = mono(it, cx, y, size, INK3, tracking=.16)
        out.append(p)
        cx += w
    return "".join(out), cx - x


def orbit(cx, cy, radii, speeds, scale=1.0):
    """Concentric orbits with nodes; slow rotation; glowing core."""
    s = scale
    parts = []
    # rings
    styles = ['stroke-opacity=".10"', 'stroke-opacity=".16" stroke-dasharray="1.2 5.5" stroke-linecap="round"',
              'stroke-opacity=".07"']
    for r, st in zip(radii, styles):
        parts.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" fill="none" stroke="#fff" {st}/>')
    nodes = [
        [(28, 3.4 * s, "lit"), (208, 2.4 * s, "#8A8A8A")],
        [(84, 3.6 * s, "box"), (204, 2.2 * s, "#6A6A6A"), (318, 3.0 * s, "lit")],
        [(146, 2.6 * s, "#5C5C5C"), (262, 2.0 * s, "#7A7A7A"), (338, 2.4 * s, "#4A4A4A")],
    ]
    for (r, dur, ring), direction in zip(zip(radii, speeds, nodes), (1, -1, 1)):
        g = []
        for ang, rad, kind in ring:
            a = math.radians(ang)
            x, y = cx + r * math.cos(a), cy + r * math.sin(a)
            if kind == "lit":
                g.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad * 2.4)}" fill="#fff" opacity=".35" filter="url(#soft)"/>'
                         f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad)}" fill="#fff"/>')
            elif kind == "box":
                b = rad * 1.9
                g.append(f'<rect x="{n(x - b / 2)}" y="{n(y - b / 2)}" width="{n(b)}" height="{n(b)}" rx="1.5" '
                         f'fill="{BG}" stroke="#BDBDBD" stroke-width="1.1"/>')
            else:
                g.append(f'<circle cx="{n(x)}" cy="{n(y)}" r="{n(rad)}" fill="{kind}"/>')
        frm, to = (0, 360) if direction > 0 else (360, 0)
        parts.append(f'<g>{"".join(g)}<animateTransform attributeName="transform" type="rotate" '
                     f'from="{frm} {n(cx)} {n(cy)}" to="{to} {n(cx)} {n(cy)}" dur="{dur}s" '
                     'repeatCount="indefinite"/></g>')
    # core
    parts.append(f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(16 * s)}" fill="#fff" opacity=".22" filter="url(#soft)"/>'
                 f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(9 * s)}" fill="none" stroke="#fff" stroke-opacity=".4">'
                 f'<animate attributeName="r" values="{n(6 * s)};{n(30 * s)}" dur="3.2s" repeatCount="indefinite"/>'
                 '<animate attributeName="stroke-opacity" values=".4;0" dur="3.2s" repeatCount="indefinite"/></circle>'
                 f'<circle cx="{n(cx)}" cy="{n(cy)}" r="{n(4.6 * s)}" fill="#fff"/>')
    return "".join(parts)


def dots(pid, x, y, w, h, cx, cy, r, step=16):
    """Dot grid that fades out radially from (cx, cy)."""
    defs = (f'<pattern id="{pid}p" x="{n(x)}" y="{n(y)}" width="{step}" height="{step}" patternUnits="userSpaceOnUse">'
            f'<circle cx="{step / 2}" cy="{step / 2}" r=".8" fill="#fff"/></pattern>'
            f'<radialGradient id="{pid}g" cx="{n(cx)}" cy="{n(cy)}" r="{n(r)}" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>'
            f'<mask id="{pid}m"><rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{pid}g)"/></mask>')
    body = (f'<rect x="{n(x)}" y="{n(y)}" width="{n(w)}" height="{n(h)}" fill="url(#{pid}p)" '
            f'mask="url(#{pid}m)" opacity=".11"/>')
    return defs, body


# --------------------------------------------------------------------- hero
def hero(mobile=False):
    if mobile:
        w, h = 400, 540
        wm_size, wm_y, pad = 86, 168, 26
        orb = (300, 468, (44, 84, 128), .85)
    else:
        w, h = W, 420
        wm_size, wm_y, pad = 116, 194, 36
        orb = (W - 166, 208, (64, 120, 182), 1.0)
    defs, body = [GRAIN, BLUR("soft", 4)], []
    d, b = panel("h", 0, 0, w, h, r=22, key=(.2, 0), keyr=1.1, keya=.095)
    defs.append(d); body.append(b)
    ocx, ocy, radii, sc = orb
    # second, very soft light behind the orbit
    defs.append(f'<radialGradient id="ol" cx="{n(ocx)}" cy="{n(ocy)}" r="{n(radii[2] * 1.25)}" gradientUnits="userSpaceOnUse">'
                '<stop offset="0" stop-color="#fff" stop-opacity=".06"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    dd, db = dots("hd", 0, 0, w, h, ocx, ocy, radii[2] * 1.35)
    defs.append(dd)
    body.append(f'<g clip-path="url(#hc)"><rect width="{w}" height="{h}" fill="url(#ol)"/>{db}'
                f'{orbit(ocx, ocy, radii, (38, 66, 120), sc)}</g>')
    body.append(status(pad + 4, pad + 8))
    d, b, _ = wordmark(pad - 4, wm_y, wm_size)
    defs.append(d); body.append(b)
    # intro() → statement
    ly = wm_y + (44 if mobile else 52)
    p, lw = mono("intro()", pad, ly, 13, INK3)
    body.append(p)
    p, _ = mono("→", pad + lw + 9, ly, 13, INK4)
    body.append(p)
    size = 24 if mobile else 27
    lead = size * 1.32
    y = ly + size * 1.45
    for i, line in enumerate(INTRO):
        p, lw2 = sans(line, pad - 1, y, size, INK, 450, -0.018)
        body.append(p)
        if i == len(INTRO) - 1:
            body.append(cursor(pad - 1 + lw2 + size * .2, y, size))
        y += lead
    # stack
    if mobile:
        r1, _ = stack_row(pad, y + 6, 10.5, STACK[:3])
        r2, _ = stack_row(pad, y + 26, 10.5, STACK[3:])
        body += [r1, r2]
    else:
        r, _ = stack_row(pad, h - 38, 11)
        body.append(r)
    return svg(w, h, "".join(body), "".join(defs), ALT["hero"])


# -------------------------------------------------------------------- stats
def spark(kind, x, y, w, h):
    pts = {
        "rise": [(0, .96), (.25, .92), (.5, .82), (.7, .62), (.85, .36), (1, .04)],
        "fall": [(0, .06), (.18, .14), (.36, .40), (.55, .70), (.75, .86), (1, .93)],
        "step": [(0, .78), (.42, .78), (.5, .70), (.58, .26), (1, .22)],
    }[kind]
    P = [(x + px * w, y + py * h) for px, py in pts]
    # smooth through points (Catmull-Rom -> cubic)
    d = f"M{n(P[0][0])} {n(P[0][1])}"
    for i in range(len(P) - 1):
        p0 = P[i - 1] if i else P[i]
        p1, p2 = P[i], P[i + 1]
        p3 = P[i + 2] if i + 2 < len(P) else p2
        c1 = (p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6)
        c2 = (p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6)
        d += f"C{n(c1[0])} {n(c1[1])} {n(c2[0])} {n(c2[1])} {n(p2[0])} {n(p2[1])}"
    area = d + f"L{n(x + w)} {n(y + h)}L{n(x)} {n(y + h)}Z"
    gid = f"sa{kind}"
    defs = (f'<linearGradient id="{gid}" x1="0" y1="{n(y)}" x2="0" y2="{n(y + h)}" gradientUnits="userSpaceOnUse">'
            '<stop offset="0" stop-color="#fff" stop-opacity=".14"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>')
    ex, ey = P[-1]
    body = (f'<path d="{area}" fill="url(#{gid})"/>'
            f'<path d="{d}" fill="none" stroke="#A8A8A8" stroke-width="1.4" stroke-linecap="round" stroke-linejoin="round"/>'
            f'<circle cx="{n(ex)}" cy="{n(ey)}" r="5" fill="#fff" opacity=".25" filter="url(#soft)"/>'
            f'<circle cx="{n(ex)}" cy="{n(ey)}" r="2.3" fill="#fff"/>')
    return defs, body


def figure(parts, x, y, size):
    """Big number built from runs: big / arrow / prefix / suffix."""
    out, cx = [], x
    for txt, kind in parts:
        if kind == "big":
            p, w = sans(txt, cx, y, size, "url(#num)", 600, -0.04)
        elif kind == "arrow":
            p, w = sans(txt, cx + size * .06, y - size * .02, size * .62, INK3, 400)
            w += size * .12
        elif kind == "prefix":
            p, w = sans(txt, cx, y, size * .34, INK2, 450, 0)
            w += 0
        else:  # suffix
            p, w = sans(txt, cx + size * .02, y, size * .46, INK2, 500, -0.01)
            w += size * .02
        out.append(p)
        cx += w
    return "".join(out), cx - x


def tile(i, st, x, y, w, h, mobile=False):
    pid = f"t{i}"
    d, b = panel(pid, x, y, w, h, r=18, key=(.12, 0), keyr=1.0, keya=.075)
    defs, body = [d], [b]
    pad = 22
    p, _ = mono(st["call"], x + pad, y + 34, 12.5, INK3)
    body.append(p)
    sw, sh = (84, 26) if mobile else (62, 20)
    sd, sb = spark(st["spark"], x + w - pad - sw, y + 20, sw, sh)
    defs.append(sd); body.append(sb)
    big = 50 if mobile else 46
    fy = y + (92 if mobile else 92)
    p, _ = figure(st["big"], x + pad - 2, fy, big)
    body.append(p)
    ly = fy + 30
    for line in st["lines"]:
        fits(line, 13, w - 2 * pad)
        p, lw = sans(line, x + pad, ly, 13, INK2, 400, 0)
        body.append(p)
        ly += 19
    return "".join(defs), "".join(body)


def stats(mobile=False):
    defs, body = [GRAIN, BLUR("soft", 3), vgrad("num", 0, 0)], []
    if mobile:
        w, th = 400, 158
        h = 3 * th + 2 * GAP
        for i, st in enumerate(STATS):
            d, b = tile(i, st, 0, i * (th + GAP), w, th, True)
            defs.append(d); body.append(b)
    else:
        w, h = W, 166
        tw = (W - 2 * GAP) / 3
        for i, st in enumerate(STATS):
            d, b = tile(i, st, i * (tw + GAP), 0, tw, h)
            defs.append(d); body.append(b)
    # number gradient spans one tile row; userSpace per tile is approximated
    # by objectBoundingBox so each numeral gets the same top-lit sheen
    defs[2] = ('<linearGradient id="num" x1="0" y1="0" x2="0" y2="1">'
               '<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#A9A9A9"/></linearGradient>')
    return svg(w, h, "".join(body), "".join(defs), ALT["stats"])


# -------------------------------------------------------------------- cards
CARD_H = 148
SLAB_W = (W - GAP) / 2        # two slabs + one gutter = W (GitHub's inline space is 4px)
CARD_GUTTER = GAP             # transparent strip on the left card's right side
M_SLAB, M_H = 176, 146        # phone cards: two compact tiles side by side (~50% each)
M_GUTTER = 6


def card(c, gutter):
    w = SLAB_W
    defs, body = [GRAIN, BLUR("soft", 3)], []
    d, b = panel("c", 0, 0, w, CARD_H, r=18, key=(.15, 0), keyr=1.0, keya=.075)
    defs.append(d); body.append(b)
    pad = 22
    p, _ = mono(c["tag"], pad, 34, 12, INK3)
    body.append(p)
    bx, by = w - pad - 14, 29
    body.append(f'<circle cx="{n(bx)}" cy="{n(by)}" r="14.5" fill="#121212" stroke="#fff" stroke-opacity=".14"/>')
    p, _ = sans("↗", bx, by + 5, 14, INK, 500, anchor="middle")
    body.append(p)
    p, _ = sans(c["slug"], pad - 1, 76, 26, INK, 600, -0.03)
    body.append(p)
    y = 104
    for line in c["lines"]:
        fits(line, 13.5, w - 2 * pad)
        p, _ = sans(line, pad, y, 13.5, INK2, 400)
        body.append(p)
        y += 20
    alt = f'{c["slug"]}: {" ".join(c["lines"])} ({c["tag"]})'
    return svg(w + gutter, CARD_H, "".join(body), "".join(defs), alt), w + gutter


def card_mobile(c, gutter):
    """Compact phone tile, drawn at ~1:1 for a 50% slot of a ~358px column."""
    w, h = M_SLAB, M_H
    defs, body = [GRAIN, BLUR("soft", 3)], []
    d, b = panel("m", 0, 0, w, h, r=16, key=(.15, 0), keyr=1.0, keya=.08)
    defs.append(d); body.append(b)
    pad = 14
    fits(c.get("mtag", c["tag"]), 10, w - 2 * pad - 26, "mono")
    p, _ = mono(c.get("mtag", c["tag"]), pad, 24, 10, INK3)
    body.append(p)
    bx, by = w - pad - 10, 20
    body.append(f'<circle cx="{n(bx)}" cy="{n(by)}" r="10.5" fill="#121212" stroke="#fff" stroke-opacity=".14"/>')
    p, _ = sans("↗", bx, by + 3.6, 10.5, INK, 500, anchor="middle")
    body.append(p)
    p, _ = sans(c["slug"], pad - .5, 60, 20, INK, 600, -0.03)
    body.append(p)
    y = 84
    for line in c["mlines"]:
        fits(line, 12, w - 2 * pad)
        p, _ = sans(line, pad, y, 12, INK2, 400)
        body.append(p)
        y += 17
    alt = f'{c["slug"]}: {" ".join(c["lines"])} ({c["tag"]})'
    return svg(w + gutter, h, "".join(body), "".join(defs), alt)


# -------------------------------------------------------------------- pills
PILL_H = 34


def pill(label):
    pad, gutter = 15, GAP - 4
    tw = T.width(label, 12, "mono")
    aw = T.width("↗", 12, "sans", 500)
    pw = pad * 2 + tw + 8 + aw
    body = (f'<rect x=".5" y=".5" width="{n(pw - 1)}" height="{PILL_H - 1}" rx="{PILL_H / 2 - .5}" '
            f'fill="{BG}" stroke="#fff" stroke-opacity=".12"/>')
    p, _ = mono(label, pad, 21.5, 12, "#CFCFCF")
    a, _ = sans("↗", pad + tw + 8, 21.5, 12, INK3, 500)
    return svg(pw + gutter, PILL_H, body + p + a, "", label, pad_bottom=8), pw + gutter


# ------------------------------------------------------------------- readme
def picture(stem, alt):
    return (f'<picture><source media="(max-width: 600px)" srcset="assets/{stem}-mobile.svg">'
            f'<img src="assets/{stem}.svg" width="{W}" align="top" alt={quoteattr(alt)}></picture><br>')


def build():
    files = {
        "assets/hero.svg": hero(),
        "assets/hero-mobile.svg": hero(mobile=True),
        "assets/stats.svg": stats(),
        "assets/stats-mobile.svg": stats(mobile=True),
    }
    lines = [picture("hero", ALT["hero"]), picture("stats", ALT["stats"])]
    # Cards: percentage widths that sum to (just under) 100%, and no whitespace
    # between the two links, so they line up with the hero at every column width.
    # Phones swap in compact tiles via <picture media>; <a><picture> is kept
    # intact by GitHub's README renderer (gfm).
    row = []
    for i, c in enumerate(CARDS):
        gut, mgut = (CARD_GUTTER, M_GUTTER) if i == 0 else (0, 0)
        svgtext, cw = card(c, gut)
        files[f"assets/card-{c['slug']}.svg"] = svgtext
        files[f"assets/card-{c['slug']}-mobile.svg"] = card_mobile(c, mgut)
        pct = math.floor(cw / W * 10000) / 100
        alt = f'{c["slug"]}: {" ".join(c["lines"])}'
        row.append(f'<a href="{c["url"]}"><picture><source media="(max-width: 600px)" '
                   f'srcset="assets/card-{c["slug"]}-mobile.svg"><img src="assets/card-{c["slug"]}.svg" '
                   f'width="{pct}%" align="top" alt={quoteattr(alt)}></picture></a>')
    lines.append("".join(row) + "<br>")
    for label, url in LINKS:
        slug = label.lower().replace(" ", "-")
        s_, pw = pill(label)
        files[f"assets/link-{slug}.svg"] = s_
        lines.append(f'<a href="{url}"><img src="assets/link-{slug}.svg" width="{n(pw)}" '
                     f'align="top" alt="{label}"></a>')
    files["README.md"] = "\n".join([
        "<!-- ami.sh · artwork generated by scripts/build.py (edit the content there) -->",
        "",
        "<p>",
        *lines,
        "</p>",
        "",
    ])
    return files


def main():
    keep = set()
    for rel, text in build().items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        keep.add(os.path.normpath(path))
        print(f"{rel:32s} {len(text.encode()) / 1024:6.1f} KB")
    adir = os.path.join(ROOT, "assets")
    for fn in sorted(os.listdir(adir)):
        p = os.path.normpath(os.path.join(adir, fn))
        if fn.endswith(".svg") and p not in keep:
            os.remove(p)
            print(f"removed stale {fn}")


if __name__ == "__main__":
    main()

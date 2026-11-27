#!/usr/bin/env python3
"""ami.sh — generates the profile README artwork (assets/*.svg) and README.md.

    pip install fonttools brotli
    python3 scripts/build.py

Design system
  * Surfaces: opaque matte-black panels (#0A0A0A) with a soft key light, fine
    film grain, a lit top edge and a hairline border, one radius (18) for every
    panel. Opaque art reads as intentional on GitHub's dark, dimmed AND light
    themes, so nothing swaps per theme.
  * Type: Geist Sans + Geist Mono (SIL OFL, ../fonts), outlined to paths with
    real kerning by typeset.py, so every visitor sees exactly this typography.
  * The hero is the name itself; its period is a breathing white LED — the only
    motion on the page (it settles after ~50s; reduced-motion gets a still).
  * Greys only, three text levels, all small text >= 4.5:1 on the panels.
  * Grid: everything is 847px (GitHub's profile column at viewports >= 1280px)
    with 12px gutters. Cards and keys use % widths, so rows stay aligned at
    any desktop width. Viewports <= 1011px get compact art (drawn for a ~300px
    phone column, capped at 400px) with stacked cards.
"""
import math
import os
import re
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import typeset as T  # noqa: E402

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
W = 847                         # desktop width of every row
GAP = 12                        # one gutter, horizontal and vertical
MW, M_CAP = 340, 400            # compact art: drawn width, max display width
MQ = "(max-width: 1011px)"      # GitHub's README column is <= ~640px below 1012px
PQ = "(max-width: 600px)"       # phones (link keys only)
RM = "(prefers-reduced-motion: reduce)"

# ------------------------------------------------------------------ palette
BG = "#0A0A0A"
INK = "#F0F0F0"                 # 17:1
INK2 = "#ADADAD"                # 8.8:1  body
INK3 = "#858585"                # 5.4:1  labels / function calls
INK4 = "#4A4A4A"                # decorative separators only

# ------------------------------------------------------------------ content
INTRO = ["I build scalable backends,", "infra and agentic systems."]
STACK = ["PYTHON", "GO", "KUBERNETES", "KAFKA", "LANGGRAPH"]

STATS = [
    dict(call="backends()",
         big=[("10", "big"), ("→", "arrow"), ("800", "big")],
         lines=["users in a week, zero downtime", "AI stock-analysis agent backend"]),
    dict(call="infra()",
         big=[("−", "sign"), ("90%", "big")],
         lines=["mean time to first response", "self-healing k8s · 75+ services"]),
    dict(call="agents()",
         big=[("+", "sign"), ("10", "big"), ("pp", "unit")],
         lines=["Qwen · AndroidWorld, MobileWorld", "peak, via my harness's trajectories"]),
]

CARDS = [
    dict(slug="pr-reviewer", url="https://github.com/Ami-sh/pr-reviewer",
         lines=["Independent one-shot LLM review for any PR,", "with an adversarial verifier on every finding."],
         tag="python · claude"),
    dict(slug="agentami", url="https://github.com/Ami-sh/agentami",
         lines=["A LangGraph agent for when your AI has too", "many tools: picks the top-k for every turn."],
         tag="pip install agentami"),
]

LINKS = [
    ("LeetCode", "https://leetcode.com/u/f20191386/", "LeetCode profile"),
    ("Stack Overflow", "https://stackoverflow.com/users/16179688/amish-gupta", "Stack Overflow profile"),
    ("Physics SE", "https://physics.stackexchange.com/users/274874/amish-gupta", "Physics Stack Exchange profile"),
    ("Math SE", "https://math.stackexchange.com/users/824283/amish-gupta", "Math Stack Exchange profile"),
]

ALT = dict(
    hero="ami.sh — intro(): I build scalable backends, infra and agentic systems. "
         "Python, Go, Kubernetes, Kafka, LangGraph.",
    stats="backends(): from 10 to 800 users in a week with zero downtime — the backend of an "
          "AI stock-analysis agent. infra(): mean time to first response cut by over 90% with a "
          "self-healing Kubernetes operator across 75+ services. agents(): up to +10 percentage "
          "points for open-source Qwen models on AndroidWorld and MobileWorld, trained on "
          "trajectories from my agent harness.",
)


# ------------------------------------------------------------------ helpers
def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def svg(w, h, body, defs="", label="", pad_bottom=GAP):
    """Every piece carries its own bottom gutter, so stacked rows get exactly GAP."""
    h = h + pad_bottom
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(w)}" height="{n(h)}" '
            f'viewBox="0 0 {n(w)} {n(h)}" role="img" aria-label={quoteattr(label)}>'
            f'<title>{escape(label)}</title><defs>{defs}</defs>{body}</svg>\n')


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="11" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.2 0 0 0 -1.05"/></filter>')


def panel(pid, x, y, w, h, r=18, key=(0.18, 0.0), keyr=1.0, keya=0.085):
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


def stack_row(x, y, size, items):
    out, cx = [], x
    for i, it in enumerate(items):
        if i:
            p, w = mono("·", cx + size * .9, y, size, INK4)
            out.append(p)
            cx += size * .9 + w + size * .9
        p, w = mono(it, cx, y, size, INK3, tracking=.16)
        out.append(p)
        cx += w
    return "".join(out)


# --------------------------------------------------------------------- hero
WM_WGHT, WM_TR = 500, -0.055        # wordmark weight / tracking (em)
LED_DUR, LED_REPEAT = 4.8, 10       # one slow breath, ~50s, then it rests lit


def _ink(face, ch):
    """Glyph ink box (xmin, ymin, xmax, ymax) in font units."""
    from fontTools.pens.boundsPen import BoundsPen
    bp = BoundsPen(face.glyphs)
    face.glyphs[face.gname(ch)].draw(bp)
    return bp.bounds


def wordmark(x, baseline, size):
    """'ami.sh' whose ink starts exactly at x: 'ami' top-lit, 'sh' recessed, and the
    period is the page's one light source — a breathing white LED.
    Returns (defs, body, ink_width)."""
    f = T.face("sans", WM_WGHT)
    sc = size / f.upm
    lay, _ = f.layout("ami.sh", size, WM_TR)
    x0 = x - _ink(f, "a")[0] * sc
    runs = {"ami": "", ".": "", "sh": ""}
    for (_, off), ch in zip(lay, "ami.sh"):
        runs["ami" if ch in "ami" else "." if ch == "." else "sh"] += f.d(ch, x0 + off, baseline, size)
    ink_w = x0 + lay[-1][1] + _ink(f, "h")[2] * sc - x
    b = _ink(f, ".")
    dcx = x0 + lay[3][1] + (b[0] + b[2]) / 2 * sc
    dcy = baseline - (b[1] + b[3]) / 2 * sc
    top = baseline - .72 * size
    breathe = (f'dur="{LED_DUR}s" calcMode="spline" keyTimes="0;.5;1" '
               f'keySplines=".45 0 .55 1;.45 0 .55 1" repeatCount="{LED_REPEAT}" fill="freeze"')
    defs = (vgrad("wmA", top, baseline, "#E6E6E6", "#5C5C5C")
            + vgrad("wmS", top, baseline, "#474747", "#2A2A2A")
            + '<filter id="ledb" x="-200%" y="-200%" width="500%" height="500%">'
              f'<feGaussianBlur stdDeviation="{n(size * .05)}"/></filter>'
            + f'<radialGradient id="leds" cx="{n(dcx)}" cy="{n(dcy)}" r="{n(size * .62)}" '
              'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity=".16"/>'
              '<stop offset=".4" stop-color="#fff" stop-opacity=".04"/>'
              '<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    body = (f'<path d="{runs["ami"]}" fill="url(#wmA)"/>'
            f'<path d="{runs["sh"]}" fill="url(#wmS)"/>'
            f'<circle cx="{n(dcx)}" cy="{n(dcy)}" r="{n(size * .62)}" fill="url(#leds)">'
            f'<animate attributeName="opacity" values="1;.3;1" {breathe}/></circle>'
            f'<path d="{runs["."]}" fill="#fff" filter="url(#ledb)" opacity=".85">'
            f'<animate attributeName="opacity" values=".85;.2;.85" {breathe}/></path>'
            f'<path d="{runs["."]}" fill="#fff">'
            f'<animate attributeName="fill-opacity" values="1;.62;1" {breathe}/></path>')
    return defs, body, ink_w


def hero(compact=False):
    """Masthead: full-width wordmark, then intro() → statement; stack on the right."""
    if compact:
        w, pad, top, call, st, lead = MW, 20, 22, 11.5, 22, 29
    else:
        w, pad, top, call, st, lead = W, 38, 40, 12.5, 30, 38.5
    size = (w - 2 * pad) / wordmark(0, 0, 100)[2] * 100     # ink spans pad .. w - pad
    base = top + .7186 * size                                # i-dot / h top sits on `top`
    y0 = base + (40 if compact else 54)                      # intro() baseline
    p, lw = mono("intro()", pad, y0, call, INK3)
    a, _ = mono("→", pad + lw + call * .6, y0, call, INK3)
    body = [p, a]
    y = y0 + st * 1.42
    for line in INTRO:
        fits(line, st, w - 2 * pad, "sans", 450)
        body.append(sans(line, pad - 1, y, st, INK, 450, -0.02)[0])
        y += lead
    last = y - lead
    if compact:
        body += [stack_row(pad, last + 30, 10.5, STACK[:3]), stack_row(pad, last + 48, 10.5, STACK[3:])]
        h = round(last + 72)
    else:   # right-aligned column, first/last baselines locked to intro() and the last line
        step = (last - y0) / (len(STACK) - 1)
        body += [mono(s, w - pad, y0 + i * step, 11, INK3, tracking=.16, anchor="end")[0]
                 for i, s in enumerate(STACK)]
        h = round(last + 7 + pad)
    d, b = panel("h", 0, 0, w, h, key=(.2, 0), keyr=1.1, keya=.095)
    wd, wb, _ = wordmark(pad, base, size)
    return svg(w, h, b + f'<g clip-path="url(#hc)">{wb}</g>' + "".join(body), GRAIN + d + wd, ALT["hero"])


def still(svgtext):
    """Same art without motion (for prefers-reduced-motion)."""
    return re.sub(r"<animate(?:Transform)?\b[^>]*/>", "", svgtext)


# -------------------------------------------------------------------- stats
def figure(parts, x, y, size):
    """Big number from runs: big | arrow | sign | unit. All figures share a left edge."""
    out, cx = [], x
    for txt, kind in parts:
        if kind == "big":
            p, w = sans(txt, cx, y, size, "url(#num)", 600, -0.04)
        elif kind == "arrow":    # optically centred on the digits
            p, w = sans(txt, cx + size * .06, y - size * .1355, size * .62, INK3, 400)
            w += size * .12
        elif kind == "sign":     # full-size grey sign, like the grey arrow
            p, w = sans(txt, cx, y, size, INK3, 400)
            w += size * .015
        else:                    # unit
            p, w = sans(txt, cx + size * .12, y, size * .4, INK2, 450)
            w += size * .12
        out.append(p)
        cx += w
    return "".join(out)


TILE_H = 166


def tile(i, st, x, y, w):
    d, b = panel(f"t{i}", x, y, w, TILE_H, key=(.12, 0), keyr=1.0, keya=.075)
    body = [b]
    pad = 22
    body.append(mono(st["call"], x + pad, y + 34, 13, INK3)[0])
    fy = y + 92
    body.append(figure(st["big"], x + pad - 2, fy, 48))
    ly = fy + 30
    for k, line in enumerate(st["lines"]):
        fits(line, 13.5, w - 2 * pad)
        body.append(sans(line, x + pad, ly, 13.5, INK2 if k == 0 else INK3, 400)[0])
        ly += 19.5
    return d, "".join(body)


def stats(compact=False):
    defs = [GRAIN, '<linearGradient id="num" x1="0" y1="0" x2="0" y2="1">'
                   '<stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#A9A9A9"/></linearGradient>']
    body = []
    if compact:
        w, h = MW, 3 * TILE_H + 2 * GAP
        for i, st in enumerate(STATS):
            d, b = tile(i, st, 0, i * (TILE_H + GAP), w)
            defs.append(d); body.append(b)
    else:
        w, h = W, TILE_H
        tw = (W - 2 * GAP) / 3
        for i, st in enumerate(STATS):
            d, b = tile(i, st, i * (tw + GAP), 0, tw)
            defs.append(d); body.append(b)
    return svg(w, h, "".join(body), "".join(defs), ALT["stats"])


# -------------------------------------------------------------------- cards
CARD_H = 148
SLAB_W = (W - GAP) / 2


def card(c, gutter=0, w=SLAB_W):
    d, b = panel("c", 0, 0, w, CARD_H, key=(.15, 0), keyr=1.0, keya=.075)
    body = [b]
    pad = 22
    fits(c["tag"], 12.5, w - 2 * pad - 36, "mono")
    body.append(mono(c["tag"], pad, 34, 12.5, INK3)[0])
    bx, by = w - pad - 14, 29
    body.append(f'<circle cx="{n(bx)}" cy="{n(by)}" r="14.5" fill="#121212" stroke="#fff" stroke-opacity=".14"/>')
    body.append(sans("↗", bx, by + 6.2, 14, INK, 500, anchor="middle")[0])
    body.append(sans(c["slug"], pad - 1, 76, 26, INK, 600, -0.03)[0])
    y = 104
    for line in c["lines"]:
        fits(line, 13.5, w - 2 * pad)
        body.append(sans(line, pad, y, 13.5, INK2, 400)[0])
        y += 20
    alt = f'{c["slug"]}: {" ".join(c["lines"])} ({c["tag"]})'
    return svg(w + gutter, CARD_H, "".join(body), GRAIN + d, alt), w + gutter


# --------------------------------------------------------------------- keys
KEY_H, KEY_R = 44, 12
KEY_W = (W - 3 * GAP) / 4
M_KEY_W, M_KEY_H, M_KEY_R = 80, 50, 11
M_KEY_GUT = M_KEY_W * GAP / KEY_W            # same slab:gutter ratio as desktop


def key(label, gutter):
    w, h = KEY_W, KEY_H
    d, b = panel("k", 0, 0, w, h, r=KEY_R, key=(.12, 0), keyr=1.0, keya=.07)
    pad, size = 16, 12.5
    base = h / 2 + size * .71 / 2                 # cap-height centred
    p, _ = mono(label, pad, base, size, "#CFCFCF")
    a, _ = sans("↗", w - pad, base + size * .087, size, INK3, 500, anchor="end")
    return svg(w + gutter, h, b + p + a, GRAIN + d, label, pad_bottom=0)


def key_compact(label, gutter):
    w, h = M_KEY_W, M_KEY_H
    d, b = panel("q", 0, 0, w, h, r=M_KEY_R, key=(.12, 0), keyr=1.0, keya=.07)
    pad, size = 9, 11
    lines = [label] if T.width(label, size, "mono") <= w - 2 * pad else label.split(" ", 1)
    body = [b]
    y = h - 11 - (len(lines) - 1) * 13
    for ln in lines:
        fits(ln, size, w - 2 * pad, "mono")
        body.append(mono(ln, pad, y, size, "#CFCFCF")[0])
        y += 13
    body.append(sans("↗", w - pad, 18, 10, INK3, 500, anchor="end")[0])
    return svg(w + gutter, h, "".join(body), GRAIN + d, label, pad_bottom=0)


# ------------------------------------------------------------------- readme
def pct(w):
    return f"{math.floor(w / W * 10000) / 100}%"


def picture(stem, alt, motion=False):
    srcs = []
    if motion:
        srcs += [f'<source media="{RM} and {MQ}" srcset="assets/{stem}-compact-still.svg" width="{M_CAP}">',
                 f'<source media="{RM}" srcset="assets/{stem}-still.svg">']
    srcs.append(f'<source media="{MQ}" srcset="assets/{stem}-compact.svg" width="{M_CAP}">')
    return (f'<picture>{"".join(srcs)}<img src="assets/{stem}.svg" width="{W}" align="top" '
            f'alt={quoteattr(alt)}></picture><br>')


def build():
    files = {}
    for compact, suffix in ((False, ""), (True, "-compact")):
        h = hero(compact)
        files[f"assets/hero{suffix}.svg"] = h
        files[f"assets/hero{suffix}-still.svg"] = still(h)
        files[f"assets/stats{suffix}.svg"] = stats(compact)
    lines = [picture("hero", ALT["hero"], motion=True), picture("stats", ALT["stats"])]

    # cards: side by side at % widths on desktop; stacked compact cards below 1012px
    row = []
    for i, c in enumerate(CARDS):
        art, cw = card(c, GAP if i == 0 else 0)
        files[f"assets/card-{c['slug']}.svg"] = art
        files[f"assets/card-{c['slug']}-compact.svg"] = card(c, 0, w=MW)[0]
        alt = f'{c["slug"]}: {" ".join(c["lines"])}'
        row.append(f'<a href="{c["url"]}"><picture><source media="{MQ}" '
                   f'srcset="assets/card-{c["slug"]}-compact.svg" width="{M_CAP}">'
                   f'<img src="assets/card-{c["slug"]}.svg" width="{pct(cw)}" align="top" '
                   f'alt={quoteattr(alt)}></picture></a>')
    lines.append("".join(row) + "<br>")

    # links: one full-width row of four keys
    keys = []
    for i, (label, url, alt) in enumerate(LINKS):
        slug = label.lower().replace(" ", "-")
        gut = 0 if i == len(LINKS) - 1 else GAP
        files[f"assets/link-{slug}.svg"] = key(label, gut)
        files[f"assets/link-{slug}-compact.svg"] = key_compact(label, 0 if gut == 0 else M_KEY_GUT)
        keys.append(f'<a href="{url}"><picture><source media="{PQ}" srcset="assets/link-{slug}-compact.svg">'
                    f'<img src="assets/link-{slug}.svg" width="{pct(KEY_W + gut)}" align="top" '
                    f'alt={quoteattr(alt)}></picture></a>')
    lines.append("".join(keys))

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
        print(f"{rel:38s} {len(text.encode()) / 1024:6.1f} KB")
    adir = os.path.join(ROOT, "assets")
    for fn in sorted(os.listdir(adir)):
        p = os.path.normpath(os.path.join(adir, fn))
        if fn.endswith(".svg") and p not in keep:
            os.remove(p)
            print(f"removed stale {fn}")


if __name__ == "__main__":
    main()

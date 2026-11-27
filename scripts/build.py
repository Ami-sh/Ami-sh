#!/usr/bin/env python3
"""ami.sh — generates the profile README artwork (assets/*.svg) and README.md.

    pip install fonttools brotli
    python3 scripts/build.py

Design
  * The README is a live terminal. One window (title bar, traffic lights) runs a
    shell session: it types `intro` at an even, human rhythm, Enter prints the
    output with a soft fade, a fresh prompt appears, it types `impact`, holds the
    finished screen, then types `clear` and starts over. Characters wipe in as
    the caret glides; the cursor blink breathes; everything is interpolated.
    Reduced-motion visitors get one run that rests on the finished screen.
  * Behind the right half, rows of backend / infra / agent tokens and '..::--++'
    ramps glide left to right, each at its own speed (faster rows are brighter):
    born clear around the middle of the window, opaque by the right edge.
  * Matte black and greys, one soft phosphor green for the prompt and cursor.
  * Type: Geist Mono + Geist Sans (SIL OFL, ../fonts), outlined to paths with
    real kerning by typeset.py, so every visitor sees exactly this typography.
    The streams use the visitor's monospace font, pinned to an exact grid.
  * Grid: 847px (GitHub's profile column at viewports >= 1280px), 12px gutters,
    % widths for side-by-side pieces. Viewports <= 1011px get compact art.
"""
import math
import os
import random
import sys
from xml.sax.saxutils import escape, quoteattr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import flow as FL  # noqa: E402
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
BAR = "#0E0E0E"
INK = "#EDEDED"
INK2 = "#A3A3A3"
INK3 = "#7A7A7A"
INK4 = "#3D3D3D"
ACC = "#A6E3A1"                 # phosphor green: prompt + cursor only
RAD = 12

# ------------------------------------------------------------------ content
USER = "ami@sh"
INTRO = ["I build scalable backends,", "infra and agentic systems."]
INTRO_COMPACT = ["I build scalable", "backends, infra and", "agentic systems."]
STACK = "python · go · kubernetes · kafka · langgraph"
STACK_COMPACT = ["python · go · kubernetes", "kafka · langgraph"]
IMPACT = [
    ("backends", "10 → 800", "users in a week, zero downtime", "AI stock-analysis agent backend"),
    ("infra", "−90%", "mean time to first response", "self-healing k8s operator · 75+ services"),
    ("agents", "+10 pp", "Qwen on AndroidWorld & MobileWorld", "peak, via my harness's trajectories"),
]
CARDS = [
    dict(slug="pr-reviewer", url="https://github.com/Ami-sh/pr-reviewer",
         lines=["Independent one-shot LLM review for any PR,", "with an adversarial verifier on every finding."],
         cmd="python review.py <pr-url>"),
    dict(slug="agentami", url="https://github.com/Ami-sh/agentami",
         lines=["A LangGraph agent for when your AI has too", "many tools: picks the top-k for every turn."],
         cmd="pip install agentami"),
]
LINKS = [
    ("leetcode", "https://leetcode.com/u/f20191386/", "LeetCode profile"),
    ("stackoverflow", "https://stackoverflow.com/users/16179688/amish-gupta", "Stack Overflow profile"),
    ("physics.se", "https://physics.stackexchange.com/users/274874/amish-gupta", "Physics Stack Exchange profile"),
    ("math.se", "https://math.stackexchange.com/users/824283/amish-gupta", "Math Stack Exchange profile"),
]
COMPACT_LABEL = {"stackoverflow": ["stack", "overflow"], "physics.se": ["physics", ".se"]}
ALT = ("Terminal — ami@sh:~$ intro: I build scalable backends, infra and agentic systems. "
       "Python, Go, Kubernetes, Kafka, LangGraph. ami@sh:~$ impact: backends — from 10 to 800 users "
       "in a week with zero downtime (AI stock-analysis agent backend); infra — mean time to first "
       "response cut by 90% with a self-healing Kubernetes operator across 75+ services; agents — up "
       "to +10 percentage points for open-source Qwen models on AndroidWorld and MobileWorld, "
       "trained on trajectories from my agent harness.")


# ------------------------------------------------------------------ helpers
def n(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


G = T.Glyphs()                   # glyph outlines of the artwork being drawn


def svg(w, h, body, defs="", label="", pad_bottom=GAP):
    """Every piece carries its own bottom gutter, so stacked rows get exactly GAP.
    Emits the glyphs drawn since the previous svg() call, then starts a fresh set."""
    global G
    glyphs, G = G.defs(), T.Glyphs()
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{n(w)}" height="{n(h + pad_bottom)}" '
            f'viewBox="0 0 {n(w)} {n(h + pad_bottom)}" role="img" aria-label={quoteattr(label)}>'
            f'<title>{escape(label)}</title><defs>{glyphs}{defs}</defs>{body}</svg>\n')


def fits(s, size, maxw, kind="mono", wght=400, tracking=0.0):
    w = T.width(s, size, kind, wght, tracking)
    if w > maxw:
        raise SystemExit(f"text too wide ({w:.0f} > {maxw:.0f}px): {s!r}")


def mono(s, x, y, size, fill, wght=400, tracking=0.0, anchor="start"):
    return G.text(s, x, y, size, "mono", wght, fill, tracking, anchor)


def sans(s, x, y, size, fill, wght=400, tracking=0.0, anchor="start"):
    return G.text(s, x, y, size, "sans", wght, fill, tracking, anchor)


def runs(parts, x, y, size, wght=400):
    """Consecutive mono runs [(text, fill)] on one baseline -> (svg, end_x)."""
    out, cx = [], x
    for s, fill in parts:
        if s:
            p, w = mono(s, cx, y, size, fill, wght)
            out.append(p)
            cx += w
    return "".join(out), cx


def adv(size, tracking=0.0):
    return size * (.6 + tracking)          # Geist Mono advance is 600/1000


GRAIN = ('<filter id="grain" x="0" y="0" width="100%" height="100%">'
         '<feTurbulence type="fractalNoise" baseFrequency=".85" numOctaves="2" seed="11" stitchTiles="stitch"/>'
         '<feColorMatrix values="0 0 0 0 1  0 0 0 0 1  0 0 0 0 1  2.2 0 0 0 -1.05"/></filter>')


def panel(pid, w, h, r=RAD, glow=(.2, .05)):
    """Matte panel: base, soft top-left light, grain, hairline border."""
    defs = (f'<clipPath id="{pid}c"><rect width="{n(w)}" height="{n(h)}" rx="{r}"/></clipPath>'
            f'<radialGradient id="{pid}k" cx="{n(w * glow[0])}" cy="0" r="{n(max(w, h) * .8)}" '
            f'gradientUnits="userSpaceOnUse"><stop offset="0" stop-color="#fff" stop-opacity="{glow[1]}"/>'
            f'<stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>')
    base = (f'<rect width="{n(w)}" height="{n(h)}" rx="{r}" fill="{BG}"/>'
            f'<g clip-path="url(#{pid}c)"><rect width="{n(w)}" height="{n(h)}" fill="url(#{pid}k)"/>'
            f'<rect width="{n(w)}" height="{n(h)}" filter="url(#grain)" opacity=".05"/></g>')
    edge = (f'<rect x=".5" y=".5" width="{n(w - 1)}" height="{n(h - 1)}" rx="{r - .5}" fill="none" '
            f'stroke="#fff" stroke-opacity=".09"/>')
    return defs, base, edge


# ------------------------------------------------------------------ session
# The terminal is a scripted shell session on one timeline. Every element owns a few
# keyframe tracks (opacity, rise, clip width, caret x / y) that the browser
# interpolates linearly, so every in-between frame is drawn: characters wipe in, the
# caret glides, lines fade up, the cursor blink breathes.
#   loop: replays forever. The session ends by typing `clear`; the screen fades back
#         to its first frame, so the seam is invisible.
#   once: plays through and rests on the finished screen (prefers-reduced-motion).
# Static attributes hold the finished screen, for renderers without SMIL.
KEY_DT = (.07, .09)             # an even, human typing rhythm
KEY_WIPE = .045                 # each character wipes in...
CARET = .06                     # ...while the caret glides one cell right
FADE_IN, FADE_OUT, RISE = .16, .18, 3.0
BLINK_ON, BLINK_FADE, BLINK_OFF = .52, .16, .26


def _kt(t, D):
    return "0" if t <= 0 else "1" if t >= D else f"{t / D:.5f}".rstrip("0").rstrip(".")


class Track:
    """Keyframes of one numeric attribute, interpolated linearly between keys."""

    def __init__(self, v0):
        self.pts = [(0.0, v0)]

    @property
    def v(self):
        return self.pts[-1][1]

    def to(self, t, v, dur=0.0):
        """Hold the current value until t, then reach v after dur (0 = a jump)."""
        t = max(t, self.pts[-1][0])
        if v == self.v:
            return
        self.pts.append((t, self.v))
        self.pts.append((t + max(dur, .002), v))

    def animate(self, attr, D, mode, fmt=n, kind="animate"):
        pts = [p for p in self.pts if p[0] < D - 1e-4] + [(D, self.v)]
        if mode == "loop" and fmt(pts[-1][1]) != fmt(pts[0][1]):
            raise SystemExit(f"{attr}: the loop does not come back to its first value")
        keys = []
        for t, v in pts:
            if keys and t <= keys[-1][0]:
                t = keys[-1][0] + .0005
            keys.append((min(t, D) if (t, v) != pts[-1] else D, v))
        if len(keys) == 2 and fmt(keys[0][1]) == fmt(keys[1][1]):
            return ""                           # never changes
        timing = 'repeatCount="indefinite"' if mode == "loop" else 'fill="freeze"'
        extra = ' type="translate"' if kind == "animateTransform" else ""
        return (f'<{kind} attributeName="{attr}"{extra} values="{";".join(fmt(v) for _, v in keys)}" '
                f'keyTimes="{";".join(_kt(t, D) for t, _ in keys)}" dur="{D:.3f}s" {timing}/>')


class Session:
    def __init__(self, seed=7):
        self.t = 0.0
        self.rnd = random.Random(seed)
        self.items = []             # (svg, opacity, rise)
        self.typed = []             # one per typed command
        self.cx, self.cy, self.cop = Track(0.0), Track(0.0), Track(1.0)
        self.marks = {}             # named moments, for tooling

    def mark(self, name):
        self.marks[name] = round(self.t, 4)

    def home(self, x, y):
        self.cx.pts, self.cy.pts = [(0.0, x)], [(0.0, y)]

    def idle(self, d):
        """The caret breathes in place (fade out, fade in) and is solid by the end."""
        end, t = self.t + d, self.t
        while t + BLINK_ON + 2 * BLINK_FADE + BLINK_OFF <= end:
            t += BLINK_ON
            self.cop.to(t, 0, BLINK_FADE)
            t += BLINK_FADE + BLINK_OFF
            self.cop.to(t, 1, BLINK_FADE)
            t += BLINK_FADE
        self.t = end

    def type(self, cid, inner, x, y, size, step, text):
        """Even keystrokes: each character wipes in as the caret glides past it."""
        full = len(text) * step + 6
        width, op = Track(0.0), Track(1.0)
        for i in range(len(text)):
            if i:
                self.t += self.rnd.uniform(*KEY_DT)
            width.to(self.t, 2 + (i + 1) * step if i < len(text) - 1 else full, KEY_WIPE)
            self.cx.to(self.t, x + (i + 1) * step, CARET)
            self.cop.to(self.t, 1, .03)
        self.typed.append(dict(cid=cid, inner=inner, width=width, op=op,
                               rect=(x - 2, y - size * 1.05, full, size * 1.45)))

    def enter(self, pause=.3):
        """Return. The caret leaves while the program prints."""
        self.t += pause
        self.cop.to(self.t, 0, .08)

    def _show(self, svg_):
        op, rise = Track(0.0), Track(RISE)
        op.to(self.t, 1, FADE_IN)
        rise.to(self.t, 0, FADE_IN)
        self.items.append((svg_, op, rise))

    def print(self, svg_, gap=.045):
        self.t += gap
        self._show(svg_)

    def prompt(self, svg_, x, y, gap=.07):
        self.t += gap
        self._show(svg_)
        self.cx.to(self.t, x)                   # jump while hidden...
        self.cy.to(self.t, y)
        self.cop.to(self.t + .05, 1, .12)       # ...then fade in on the new line
        self.t += .17

    def clear(self, x, y):
        """`clear`: everything fades out and the caret is back at the top prompt."""
        t0 = self.t
        for _, op, rise in self.items:
            op.to(t0, 0, FADE_OUT)
            rise.to(t0 + FADE_OUT, RISE)
        for tp in self.typed:
            tp["op"].to(t0, 0, FADE_OUT)
            tp["width"].to(t0 + FADE_OUT, 0.0)
            tp["op"].to(t0 + FADE_OUT + .002, 1)     # unseen: its width is 0 by now
        t1 = t0 + FADE_OUT + .01
        self.cx.to(t1, x)
        self.cy.to(t1, y)
        self.cop.to(t1 + .02, 1, .14)
        self.t = t1 + .5                            # the loop restarts exactly here

    def render(self, mode, D, size, base, defs):
        body = []
        for svg_, op, rise in self.items:
            body.append(f'<g>{op.animate("opacity", D, mode)}'
                        f'{rise.animate("transform", D, mode, lambda v: "0 " + n(v), "animateTransform")}'
                        f'{svg_}</g>')
        for tp in self.typed:
            x, top, full, hgt = tp["rect"]
            defs.append(f'<clipPath id="{tp["cid"]}"><rect x="{n(x)}" y="{n(top)}" width="{n(full)}" '
                        f'height="{n(hgt)}">{tp["width"].animate("width", D, mode)}</rect></clipPath>')
            body.append(f'<g clip-path="url(#{tp["cid"]})">{tp["op"].animate("opacity", D, mode)}'
                        f'{tp["inner"]}</g>')
        cw, chh, lift = adv(size) * .98, size * 1.2, size * .92
        bx, by = base
        body.append(
            f'<rect x="{n(bx)}" y="{n(by - lift)}" width="{n(cw)}" height="{n(chh)}" rx="1" '
            f'fill="{ACC}" fill-opacity=".9">'
            + self.cx.animate("x", D, mode)
            + self.cy.animate("y", D, mode, lambda v: n(v - lift))
            + self.cop.animate("opacity", D, mode)
            + "</rect>")
        return "".join(body)


# --------------------------------------------------------------------- hero
def window_chrome(w, h, bar, title, tsize):
    defs, base, edge = panel("w", w, h, glow=(.16, .045))
    b = [base, f'<g clip-path="url(#wc)"><rect width="{n(w)}" height="{bar}" fill="{BAR}"/></g>',
         f'<path d="M0 {n(bar - .5)}H{n(w)}" stroke="#fff" stroke-opacity=".06"/>']
    dr, gap = (5.5, 19) if bar > 34 else (4.5, 15)
    for i, c in enumerate(("#FF5F57", "#FEBC2E", "#28C840")):
        b.append(f'<circle cx="{n(dr * 3.6 + i * gap)}" cy="{n(bar / 2)}" r="{dr}" fill="{c}"/>')
    p, _ = mono(title, w / 2, bar / 2 + tsize * .36, tsize, INK3, anchor="middle")
    b.append(p)
    return defs, "".join(b), edge


def prompt_parts(cmd):
    return [(USER, ACC), (":", INK3), ("~", INK2), ("$ ", INK3), (cmd, INK)]


TIMELINES = {}                  # (compact, mode) -> named moments, for tooling
HOLD = 8.0                      # loop: seconds the finished screen stays up before `clear`
BAND = 78                       # compact: height of the stream band under the last prompt


def hero(compact=False, mode="loop"):
    if compact:
        w, bar, pad, tsize = MW, 30, 18, 10.5
        ps, ss, ls_, st_lead = 11, 20, 10.5, 26
        intro, stack = INTRO_COMPACT, STACK_COMPACT
    else:
        w, bar, pad, tsize = W, 38, 32, 11.5
        ps, ss, ls_, st_lead = 13, 30, 12, 39
        intro, stack = INTRO, [STACK]
    s_tr = -0.04
    defs, body = [GRAIN], []
    pstep = adv(ps)
    sh = Session()

    # $ intro
    y1 = bar + (34 if compact else 44)
    p1, x1 = runs(prompt_parts(""), pad, y1, ps)
    body.append(p1)                              # the top prompt never leaves the screen
    sh.home(x1, y1)
    sh.idle(1.0)
    sh.mark("type1")
    sh.type("ty1", mono("intro", x1, y1, ps, INK)[0], x1, y1, ps, pstep, "intro")
    sh.mark("typed1")
    sh.enter()
    sh.mark("enter1")
    y = y1 + (38 if compact else 52)
    for line in intro:
        fits(line, ss, (w * .78 if compact else 520), "mono", 500, s_tr)
        sh.print(mono(line, pad - 1, y, ss, INK, 500, s_tr)[0])
        y += st_lead
    y += (28 if compact else 34) - st_lead
    for line in stack:
        fits(line, ls_, w - 2 * pad)
        sh.print(mono(line, pad, y, ls_, INK3)[0])
        y += 16
    y += (38 if compact else 50) - 16

    # $ impact
    p2, x2 = runs(prompt_parts(""), pad, y, ps)
    sh.prompt(p2, x2, y)
    sh.mark("prompt2")
    sh.idle(1.3)
    sh.mark("type2")
    sh.type("ty2", mono("impact", x2, y, ps, INK)[0], x2, y, ps, pstep, "impact")
    sh.mark("typed2")
    sh.enter()
    sh.mark("enter2")
    if compact:
        y += 26
        for i, (key, fig, desc, ctx) in enumerate(IMPACT):
            last = i == len(IMPACT) - 1
            a, xa = runs([("└─ " if last else "├─ ", INK4), (key + "  ", INK3)], pad, y, 11.5)
            b, _ = mono(fig, xa, y, 11.5, INK, 500)
            sh.print(a + b)
            ind = pad + adv(11.5) * 3
            fits(desc, 11, w - ind - pad); fits(ctx, 11, w - ind - pad)
            pipe1 = "" if last else mono("│", pad, y + 16, 11.5, INK4)[0]
            pipe2 = "" if last else mono("│", pad, y + 31, 11.5, INK4)[0]
            sh.print(pipe1 + mono(desc, ind, y + 16, 11, INK2)[0])
            sh.print(pipe2 + mono(ctx, ind, y + 31, 11, INK3)[0])
            y += 55
        y += 34 - 55 + 31
    else:
        y += 32
        isz = 13
        col_fig = pad + adv(isz) * 14
        col_desc = pad + adv(isz) * 25
        for i, (key, fig, desc, ctx) in enumerate(IMPACT):
            last = i == len(IMPACT) - 1
            a, _ = runs([("└─ " if last else "├─ ", INK4), (key, INK3)], pad, y, isz)
            b, _ = mono(fig, col_fig, y, isz, INK, 500)
            c, _ = mono(desc, col_desc, y, isz, INK2)
            fits(desc, isz, 560 - col_desc)
            sh.print(a + b + c)
            pipe = "" if last else mono("│", pad, y + 19, isz, INK4)[0]
            fits(ctx, 12.5, 560 - col_desc)
            sh.print(pipe + mono(ctx, col_desc, y + 19, 12.5, INK3)[0])
            y += 46
        y += 42 - 46 + 19

    # final prompt: hold, then `clear` and go round again (or rest, for reduced motion)
    p3, x3 = runs(prompt_parts(""), pad, y, ps)
    sh.prompt(p3, x3, y)
    sh.mark("prompt3")
    if mode == "loop":
        sh.idle(HOLD)
        sh.mark("type3")
        sh.type("ty3", mono("clear", x3, y, ps, INK)[0], x3, y, ps, pstep, "clear")
        sh.mark("typed3")
        sh.enter(.28)
        sh.clear(x1, y1)
        D = sh.t
    else:
        sh.idle(3.2)
        D = sh.t + .05
    sh.marks["D"] = round(D, 4)
    TIMELINES[(compact, mode)] = sh.marks
    body.append(sh.render(mode, D, ps, (x3, y), defs))
    h = round(y + (22 + BAND if compact else 30))

    # ---- backdrop: ASCII streams glide left to right, born clear mid-window and
    # growing opaque toward the right edge
    if compact:      # phones: a band of its own under the last prompt, clear of all text
        y0b, y1b = y + 16, h - 3
        fd, fb = FL.streams("f", 0, y0b, w, y1b, 9.6, 4.8, 7.8,
                            w + 24, (y0b + y1b) / 2, w + 24 - 104, (y1b - y0b) / 2 + 26,
                            speed=(11.0, 26.0))
    else:
        fd, fb = FL.streams("f", 400, bar + 2, w, h - 2, 12.0, 6.0, 9.6,
                            w + 34, bar + (h - bar) / 2, w + 34 - 452, (h - bar) / 2 + 70)
    defs.append(fd)
    art = f'<g clip-path="url(#wc)">{fb}</g>'

    cd, cb, edge = window_chrome(w, h, bar, f"{USER}: ~", tsize)
    defs.append(cd)
    return svg(w, h, cb + art + "".join(body) + edge, "".join(defs), ALT)


# -------------------------------------------------------------------- cards
CARD_H = 156
SLAB_W = (W - GAP) / 2


def card(c, gutter=0, w=SLAB_W, compact=False):
    pad = 18 if compact else 22
    h = CARD_H
    defs, base, edge = panel("c", w, h, glow=(.15, .04))
    body = [base]
    body.append(mono(c["slug"], pad, 41, 17, INK, 500)[0])
    bs = 26
    bx, by = w - pad - bs, 21
    body.append(f'<rect x="{n(bx)}" y="{by}" width="{bs}" height="{bs}" rx="7" fill="#141414" '
                f'stroke="#fff" stroke-opacity=".1"/>')
    body.append(sans("↗", bx + bs / 2, by + bs / 2 + 4.6, 13, INK, 500, anchor="middle")[0])
    y = 75
    dsz = 13 if compact else 13.5
    for line in c["lines"]:
        fits(line, dsz, w - 2 * pad, "sans")
        body.append(sans(line, pad, y, dsz, INK2)[0])
        y += 19.5
    sy, sh = 108, 28
    body.append(f'<rect x="{pad}" y="{sy}" width="{n(w - 2 * pad)}" height="{sh}" rx="7" fill="#111" '
                f'stroke="#fff" stroke-opacity=".06"/>')
    cmd, _ = runs([("$ ", ACC), (c["cmd"], INK2)], pad + 12, sy + sh / 2 + 4.3, 12)
    fits("$ " + c["cmd"], 12, w - 2 * pad - 24)
    body.append(cmd)
    alt = f'{c["slug"]}: {" ".join(c["lines"])} ($ {c["cmd"]})'
    return svg(w + gutter, h, "".join(body) + edge, GRAIN + defs, alt), w + gutter


# --------------------------------------------------------------------- keys
KEY_H = 44
KEY_W = (W - 3 * GAP) / 4
M_KEY_W, M_KEY_H = 80, 50
M_KEY_GUT = M_KEY_W * GAP / KEY_W            # same slab:gutter ratio as desktop


def key(label, gutter):
    w, h = KEY_W, KEY_H
    defs, base, edge = panel("k", w, h, r=10, glow=(.12, .035))
    size = 12.5
    base_y = h / 2 + size * .36
    p, _ = runs([("› ", ACC), (label, "#D4D4D4")], 16, base_y, size)
    a, _ = sans("↗", w - 16, base_y + .6, size, INK3, 500, anchor="end")
    return svg(w + gutter, h, base + p + a + edge, GRAIN + defs, label, pad_bottom=0)


def key_compact(label, gutter):
    w, h = M_KEY_W, M_KEY_H
    defs, base, edge = panel("q", w, h, r=10, glow=(.12, .035))
    size = 10.5
    lines = COMPACT_LABEL.get(label, [label])
    body = [base]
    y = h - 11 - (len(lines) - 1) * 13
    for ln in lines:
        fits(ln, size, w - 18)
        body.append(mono(ln, 9, y, size, "#D4D4D4")[0])
        y += 13
    body.append(sans("↗", w - 9, 18, 10, INK3, 500, anchor="end")[0])
    return svg(w + gutter, h, "".join(body) + edge, GRAIN + defs, label, pad_bottom=0)


# ------------------------------------------------------------------- readme
def pct(w):
    return f"{math.floor(w / W * 10000) / 100}%"


def build():
    files = {}
    for compact, suffix in ((False, ""), (True, "-compact")):
        files[f"assets/terminal{suffix}.svg"] = hero(compact, "loop")
        files[f"assets/terminal{suffix}-once.svg"] = hero(compact, "once")
    lines = [f'<picture><source media="{RM} and {MQ}" srcset="assets/terminal-compact-once.svg" width="{M_CAP}">'
             f'<source media="{RM}" srcset="assets/terminal-once.svg">'
             f'<source media="{MQ}" srcset="assets/terminal-compact.svg" width="{M_CAP}">'
             f'<img src="assets/terminal.svg" width="{W}" align="top" alt={quoteattr(ALT)}></picture><br>']

    row = []
    for i, c in enumerate(CARDS):
        art, cw = card(c, GAP if i == 0 else 0)
        files[f"assets/card-{c['slug']}.svg"] = art
        files[f"assets/card-{c['slug']}-compact.svg"] = card(c, 0, w=MW, compact=True)[0]
        alt = f'{c["slug"]}: {" ".join(c["lines"])}'
        row.append(f'<a href="{c["url"]}"><picture><source media="{MQ}" '
                   f'srcset="assets/card-{c["slug"]}-compact.svg" width="{M_CAP}">'
                   f'<img src="assets/card-{c["slug"]}.svg" width="{pct(cw)}" align="top" '
                   f'alt={quoteattr(alt)}></picture></a>')
    lines.append("".join(row) + "<br>")

    keys = []
    for i, (label, url, alt) in enumerate(LINKS):
        slug = label.replace(".", "-")
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
        print(f"{rel:40s} {len(text.encode()) / 1024:6.1f} KB")
    adir = os.path.join(ROOT, "assets")
    for fn in sorted(os.listdir(adir)):
        p = os.path.normpath(os.path.join(adir, fn))
        if fn.endswith(".svg") and p not in keep:
            os.remove(p)
            print(f"removed stale {fn}")


if __name__ == "__main__":
    main()

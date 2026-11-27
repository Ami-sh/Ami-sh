#!/usr/bin/env python3
"""Build the ami.sh profile README. Stdlib only.

    python3 scripts/build.py      # writes assets/*.svg (dark + light) and README.md

The page is a shell script you can call. Each function is a native
<details>: the <summary> is the call and its return value (always visible),
and clicking it "runs" the call and prints more output underneath. That is
the only interactivity GitHub allows in a README (no JS/CSS), and it needs
no JS.

Rules learned from GitHub's renderer:
  * <picture> inside <summary> is kept and NOT wrapped in a link, so a click
    toggles the section. A bare <img> there WOULD be wrapped in a link
    (opening the raw file instead), so every image here is a <picture>.
  * Never put a <picture> inside <a>: the sanitiser splits them apart.

Layout is a monospace character grid. Every run of text is pinned with
textLength and every arrow is a drawn path, so the grid holds in SF Mono,
Menlo, Consolas or Liberation Mono.
"""
import math
import os
from xml.sax.saxutils import escape, quoteattr

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONT = ("ui-monospace, 'SF Mono', SFMono-Regular, Menlo, Consolas, "
        "'Liberation Mono', monospace")

# ------------------------------------------------------------------ grid --
F = 22                 # the one text size below the wordmark
ADV = 0.6 * F          # one monospace cell
LH = 30                # line pitch
TOP = 21               # first baseline inside a row image (sits by the ▸ marker)
COL_ARROW = 11         # gutter arrow starts here (calls are <= 10 cells)
COL_RET = 14           # return values start here
OUT_COL = 1.2          # clicked-call output starts here (under the call name)
COLS = 42              # grid width in cells; every image is the same width
W = math.ceil(COLS * ADV)
WM = 78                # wordmark size
WM_BASE = 64
WM_KERN = [0, 0.6, 1.2, 1.68, 2.14, 2.74]   # tucked dot: reads as one word

THEMES = {
    # matte greys, no hue. wm = wordmark, p = ink, s = secondary, t = syntax.
    # p and s pass 4.5:1 on GitHub dark, dark-dimmed and light.
    "dark": dict(wm="#f2f2f2", p="#e6e6e6", s="#8f8f8f", t="#737373"),
    "light": dict(wm="#0a0a0a", p="#141414", s="#666666", t="#8f8f8f"),
}

# ---------------------------------------------------------------- content --
# A line is a list of (text, tone) runs; tone "p" = ink, "s" = grey,
# "t" = faint. A ("->", tone) run draws an inline arrow (3 cells).
A = ("->", "p")
HINT = "# click a call to run it"

CALLS = [
    dict(name="intro",
         ret=[[("I build scalable backends,", "p")],
              [("infra and agentic systems.", "p")]],
         out=[[("python and go, api to cluster", "s")],
              [("now   ", "t"), ("agent harnesses, evals, MCP", "s")],
              [("before", "t"), (" self-healing infra, LLM", "s")],
              [("      pipelines for operations", "s")]]),
    dict(name="backends",
         ret=[[("backend of a markets agent", "p")],
              [("10", "p"), A, ("800", "p"), (" users in a week,", "s")],
              [("zero downtime", "s")]],
         out=[[("natural-language queries", "s"), ("->", "s"), ("", "s")],
              [("indicators, patterns, screens", "s")],
              [("fastapi · langgraph · redis · mongodb", "s")],
              [("tiered easy/medium/hard evals", "s")],
              [("agentami was open-sourced from it", "s")],
              [("+", "t"), (" a RAG app backend in 2 days", "s")]]),
    dict(name="infra",
         ret=[[("self-healing k8s operator", "p")],
              [("in Go, ", "s"), ("75+", "p"), (" services;", "s")],
              [("mean time to first response", "s")],
              [("cut by ", "s"), ("over 90%", "p")]],
         out=[[("operator pattern (CRDs): monitors,", "s")],
              [("auto-remediates, alerts owners", "s")],
              [("kafka event-driven autoscaling", "s")],
              [("+", "t"), (" crawlers feeding an LLM runbook", "s")],
              [("  pipeline, langchain", "s"), ("->", "s"), ("langgraph", "s")]]),
    dict(name="agents",
         ret=[[("Android agent harness", "p")],
              [("training on its trajectories", "s")],
              [("lifted Qwen up to ", "s"), ("+10 pp", "p"), (" on", "s")],
              [("AndroidWorld / MobileWorld", "s")]],
         out=[[("5k+ generated Android tasks", "s")],
              [("eval suite any model can run:", "s")],
              [("  AndroidWorld, MobileWorld, ALE", "s")],
              [("+", "t"), (" an MCP server for a ChatGPT", "s")],
              [("  app, tuned for implicit triggers", "s")]]),
    dict(name="lang",
         ret=[[("Python, Go", "p")]],
         out=[[("fastapi · kubernetes · kafka", "s")],
              [("docker · redis · mongodb · postgres", "s")],
              [("langgraph · pyspark · playwright", "s")]]),
]

OSS = [  # oss() is open by default: its output is real, clickable links
    ("pr-reviewer", "https://github.com/Ami-sh/pr-reviewer",
     "one-shot LLM PR review that tries to refute its own findings"),
    ("agentami", "https://github.com/Ami-sh/agentami",
     "a LangGraph agent that picks its top-k tools per turn · on PyPI"),
    ("Hangman", "https://github.com/Ami-sh/Hangman",
     "~51% win rate on unseen words vs an 18% baseline"),
]
OSS_RET = [[("pr-reviewer, agentami", "p")]]

ELSEWHERE = [
    ("LeetCode", "https://leetcode.com/u/f20191386/"),
    ("Stack Overflow", "https://stackoverflow.com/users/16179688/amish-gupta"),
    ("Physics SE", "https://physics.stackexchange.com/users/274874/amish-gupta"),
    ("Math SE", "https://math.stackexchange.com/users/824283/amish-gupta"),
]


# ------------------------------------------------------------- primitives --
def cx(col):
    return round(col * ADV, 2)


def text_of(ln):
    return "".join(" → " if t == "->" else t for t, _ in ln)


def run(col, y, s, fill):
    lead = len(s) - len(s.lstrip(" "))
    s = s.strip(" ")
    if not s:
        return ""
    return (f'<text x="{cx(col + lead)}" y="{y}" fill="{fill}" '
            f'textLength="{cx(len(s))}" lengthAdjust="spacing">{escape(s)}</text>')


def arrow(x0, x1, y, fill, head=4.5, width=1.5):
    return (f'<path d="M{x0} {y}H{x1}M{x1 - head} {y - head}L{x1} {y}'
            f'L{x1 - head} {y + head}" fill="none" stroke="{fill}" '
            f'stroke-width="{width}" stroke-linecap="round" '
            f'stroke-linejoin="round"/>')


def line(col, y, runs, c):
    out = []
    for text, tone in runs:
        if text == "->":
            out.append(arrow(cx(col + 0.7), cx(col + 2.3), y - 7, c[tone], 3.5))
            col += 3
            continue
        out.append(run(col, y, text, c[tone]))
        col += len(text)
    return out, col


def svg(body, h, label, anim=False):
    style = "text{font-variant-ligatures:none;font-kerning:none}"
    if anim:  # cursor: solid at t=0, blinks a few times, rests solid
        style += ("@keyframes b{50%{opacity:0}}#c{animation:b 1.1s step-end 4}"
                  "@media (prefers-reduced-motion:reduce){#c{animation:none}}")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{h}" '
            f'viewBox="0 0 {W} {h}" role="img" aria-label={quoteattr(label)}>'
            f'<title>{escape(label)}</title><style>{style}</style>'
            f'<g font-family="{FONT}" font-size="{F}">{"".join(body)}</g></svg>\n')


# ------------------------------------------------------------------ parts --
def wordmark(c):
    xs = [round(-3 + k * WM, 1) for k in WM_KERN]
    body = [f'<text y="{WM_BASE}" font-size="{WM}" font-weight="600">'
            f'<tspan x="{" ".join(map(str, xs[:3]))}" fill="{c["wm"]}">ami</tspan>'
            f'<tspan x="{" ".join(map(str, xs[3:]))}" fill="{c["s"]}">.sh</tspan></text>',
            run(0, WM_BASE + 44, HINT, c["t"])]
    return body, WM_BASE + 58


def row(name, ret, c, cursor=False):
    """The call and its return value: what the <summary> shows."""
    y = TOP
    body = [run(0, y, name, c["s"]), run(len(name), y, "()", c["s"]),
            arrow(cx(COL_ARROW), cx(COL_ARROW) + 20, y - 6.5, c["t"])]
    end = COL_RET
    for i, ln in enumerate(ret):
        out, end = line(COL_RET, y + i * LH, ln, c)
        body += out
    last = y + (len(ret) - 1) * LH
    if cursor:
        body.append(f'<rect id="c" x="{cx(end) + 4}" y="{last - 17}" width="11" '
                    f'height="21" fill="{c["p"]}"/>')
    return body, last + 11


def output(lines, c):
    """What the call prints when clicked: a stdout block with a hairline gutter.
    Text sits at OUT_COL so it lines up (roughly) with the call names, which
    the browser's ▸ marker pushes right by ~1.2 cells."""
    body = []
    for i, ln in enumerate(lines):
        body += line(OUT_COL, TOP + i * LH, ln, c)[0]
    bottom = TOP + (len(lines) - 1) * LH + 8
    body.insert(0, f'<path d="M1.5 {TOP - 17}V{bottom}" stroke="{c["t"]}" '
                   f'stroke-width="1.5" stroke-linecap="round" opacity=".55"/>')
    return body, bottom + 6


def alt_row(name, ret):
    return f"{name}() returns: " + " ".join(text_of(l).strip() for l in ret)


def alt_out(name, lines):
    return f"output of {name}(): " + " / ".join(text_of(l).strip() for l in lines)


# ----------------------------------------------------------------- readme --
def picture(stem, alt, align=None):
    a = f' align="{align}"' if align else ""
    return ('<picture>'
            f'<source media="(prefers-color-scheme: dark)" srcset="assets/{stem}-dark.svg">'
            f'<img src="assets/{stem}-light.svg" width="{W}"{a} alt={quoteattr(alt)}>'
            '</picture>')


def build():
    files = {}
    for theme, c in THEMES.items():
        b, h = wordmark(c)
        files[f"assets/ami-{theme}.svg"] = svg(b, h, f"ami.sh  {HINT}")
        for call in CALLS:
            n = call["name"]
            b, h = row(n, call["ret"], c, cursor=(n == "intro"))
            files[f"assets/{n}-{theme}.svg"] = svg(b, h, alt_row(n, call["ret"]), n == "intro")
            b, h = output(call["out"], c)
            files[f"assets/{n}-out-{theme}.svg"] = svg(b, h, alt_out(n, call["out"]))
        b, h = row("oss", OSS_RET, c)
        files[f"assets/oss-{theme}.svg"] = svg(b, h, alt_row("oss", OSS_RET))

    parts = ["<!-- ami.sh · generated by scripts/build.py; edit the content there -->", "",
             picture("ami", f"ami.sh  {HINT}"), ""]
    for call in CALLS:
        n = call["name"]
        parts += ["<details>",
                  f"<summary>{picture(n, alt_row(n, call['ret']), 'top')}</summary>",
                  picture(f"{n}-out", alt_out(n, call["out"])),
                  "</details>", ""]
    parts += ["<details open>",
              f"<summary>{picture('oss', alt_row('oss', OSS_RET), 'top')}</summary>", ""]
    parts += [f"[{n}]({u}) — {d}\n" for n, u, d in OSS]
    parts += ["</details>", ""]
    parts.append(" · ".join(f"[{n.replace(' ', '&nbsp;')}]({u})" for n, u in ELSEWHERE))
    files["README.md"] = "\n".join(parts) + "\n"
    return files


def main():
    keep = set()
    for rel, text in build().items():
        path = os.path.join(ROOT, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        keep.add(os.path.normpath(path))
        print(f"{rel}  {len(text.encode())} bytes")
    # drop stale generated SVGs (e.g. a renamed call)
    adir = os.path.join(ROOT, "assets")
    for fn in os.listdir(adir):
        p = os.path.normpath(os.path.join(adir, fn))
        if fn.endswith(".svg") and p not in keep:
            os.remove(p)
            print(f"removed {fn}")


if __name__ == "__main__":
    main()

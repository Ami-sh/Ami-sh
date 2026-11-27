"""Generate assets/terminal.svg: a matte-black terminal window that types itself out.

Usage:  python3 scripts/terminal_svg.py            -> assets/terminal.svg (animated)
        python3 scripts/terminal_svg.py --static   -> prints a non-animated SVG to stdout (for previews)
Edit LINES below to change what the terminal says.
"""
import sys
from html import escape
from pathlib import Path

PROMPT = "~ $ "

# (kind, text) — "cmd" lines are typed after the prompt, "out" lines appear at once.
# "out" text may contain segments as a list of (text, style) where style is one of STYLES.
LINES = [
    ("cmd", "./ami.sh"),
    ("out", [("ami", "hi"), ("  ·  scalable backends, infra & agentic systems", "dim")]),
    ("gap", None),
    ("cmd", "cat stack.txt"),
    ("out", [("backend  ", "hi"), ("python · fastapi · async services · event streams", "dim")]),
    ("out", [("agents   ", "hi"), ("langgraph · claude · tool routing · LLM review loops", "dim")]),
    ("out", [("infra    ", "hi"), ("built to scale · backoff & jitter · graceful failure", "dim")]),
    ("gap", None),
    ("cmd", "ls ~/featured"),
    ("out", [("pr-reviewer/   agentami/   hangman-solver/   masked-face-verification/", "dir")]),
    ("gap", None),
    ("end", None),
]

W = 860
FONT = 15
CHAR_W = 9.05           # approx advance of a 15px monospace glyph
LINE_H = 24
PAD_X = 26
TOP = 74                # baseline of first line
BAR_H = 36

STYLES = {
    "prompt": "fill:#6f6f6f",
    "cmd": "fill:#ededed",
    "hi": "fill:#f2f2f2;font-weight:700",
    "dim": "fill:#9a9a9a",
    "dir": "fill:#d4d4d4;font-weight:700",
}

TYPE_SPEED = 0.06       # seconds per typed char
PAUSE_BEFORE_CMD = 0.35
PAUSE_AFTER_CMD = 0.25


def build(static: bool) -> str:
    rows, defs = [], []
    t = 0.4
    y = TOP
    for i, (kind, text) in enumerate(LINES):
        if kind == "gap":
            y += LINE_H * 0.55
            continue
        if kind in ("cmd", "end"):
            t += PAUSE_BEFORE_CMD
            show = "" if static else f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
            op = "1" if static else "0"
            prompt_w = len(PROMPT) * CHAR_W
            parts = [f'<g opacity="{op}">{show}',
                     f'<text x="{PAD_X}" y="{y}" style="{STYLES["prompt"]}">{escape(PROMPT)}</text>']
            if kind == "cmd":
                n = len(text)
                cid = f"c{i}"
                start = t + 0.15
                if static:
                    clip = ""
                else:
                    steps = ";".join(f"{k * CHAR_W:.1f}" for k in range(n + 1))
                    defs.append(
                        f'<clipPath id="{cid}"><rect x="{PAD_X + prompt_w}" y="{y - FONT}" height="{LINE_H}" width="0">'
                        f'<animate attributeName="width" values="{steps}" dur="{n * TYPE_SPEED:.2f}s" '
                        f'begin="{start:.2f}s" calcMode="discrete" fill="freeze"/></rect></clipPath>')
                    clip = f' clip-path="url(#{cid})"'
                parts.append(f'<text x="{PAD_X + prompt_w}" y="{y}" style="{STYLES["cmd"]}"{clip}>{escape(text)}</text>')
                t = start + n * TYPE_SPEED + PAUSE_AFTER_CMD
            else:  # final prompt with blinking block cursor
                blink = "" if static else (
                    f'<animate attributeName="opacity" values="1;0" dur="1.1s" begin="{t:.2f}s" '
                    f'calcMode="discrete" repeatCount="indefinite"/>')
                parts.append(f'<rect x="{PAD_X + prompt_w + 2}" y="{y - FONT + 2}" width="{CHAR_W}" height="{FONT + 3}" '
                             f'fill="#cfcfcf">{blink}</rect>')
            parts.append("</g>")
            rows.append("".join(parts))
        else:  # out
            show = "" if static else f'<set attributeName="opacity" to="1" begin="{t:.2f}s" fill="freeze"/>'
            op = "1" if static else "0"
            spans = "".join(f'<tspan style="{STYLES[s]}">{escape(seg)}</tspan>' for seg, s in text)
            rows.append(f'<g opacity="{op}">{show}<text x="{PAD_X}" y="{y}">{spans}</text></g>')
            t += 0.12
        y += LINE_H
    H = int(y + 6)

    dots = "".join(f'<circle cx="{22 + k * 20}" cy="{BAR_H / 2}" r="6" fill="{c}"/>'
                   for k, c in enumerate(["#4a4a4a", "#3d3d3d", "#333333"]))
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" role="img" aria-label="ami.sh terminal: scalable backends, infra and agentic systems">
<defs>{"".join(defs)}
<linearGradient id="bar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#242424"/><stop offset="1" stop-color="#1b1b1b"/></linearGradient>
</defs>
<style>text{{font-family:'JetBrains Mono','SF Mono',SFMono-Regular,Menlo,Consolas,'Liberation Mono',monospace;font-size:{FONT}px;white-space:pre}}</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="10" fill="#0e0e0e" stroke="#2a2a2a"/>
<path d="M0.5 {BAR_H} V10.5 a10 10 0 0 1 10 -10 H{W - 10.5} a10 10 0 0 1 10 10 V{BAR_H} Z" fill="url(#bar)"/>
<line x1="0.5" y1="{BAR_H}" x2="{W - 0.5}" y2="{BAR_H}" stroke="#2a2a2a"/>
{dots}
<text x="{W / 2}" y="{BAR_H / 2 + 5}" text-anchor="middle" style="fill:#7a7a7a;font-size:13px">ami.sh — bash</text>
{"".join(rows)}
</svg>
'''


if __name__ == "__main__":
    if "--static" in sys.argv:
        sys.stdout.write(build(static=True))
    else:
        out = Path(__file__).resolve().parent.parent / "assets" / "terminal.svg"
        out.parent.mkdir(exist_ok=True)
        out.write_text(build(static=False))
        print(f"wrote {out}")

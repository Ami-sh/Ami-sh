"""Tiny typesetter: turns text into SVG <path> outlines using the Geist fonts
in ../fonts (SIL OFL 1.1), with the font's own kerning (GPOS 'kern').

Outlined text renders identically on every machine and needs no web fonts,
which GitHub's image proxy would block anyway.

Requires: fonttools + brotli  (pip install fonttools brotli)
"""
import functools
import os

from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

HERE = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(os.path.dirname(HERE), "fonts")
FILES = {"sans": "geist-sans.woff2", "mono": "geist-mono.woff2"}


def _num(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


class Face:
    def __init__(self, tt):
        self.tt = tt
        self.upm = tt["head"].unitsPerEm
        self.cmap = tt.getBestCmap()
        self.glyphs = tt.getGlyphSet()
        self.hmtx = tt["hmtx"].metrics
        os2 = tt["OS/2"]
        self.cap = getattr(os2, "sCapHeight", 0) or 700
        self.xh = getattr(os2, "sxHeight", 0) or 500
        self._lookups = self._kern_lookups()

    # ---- kerning (GPOS PairPos, formats 1 and 2, incl. extension lookups)
    def _kern_lookups(self):
        if "GPOS" not in self.tt:
            return []
        g = self.tt["GPOS"].table
        idx = sorted({i for fr in g.FeatureList.FeatureRecord if fr.FeatureTag == "kern"
                      for i in fr.Feature.LookupListIndex})
        lookups = []
        for i in idx:
            lk = g.LookupList.Lookup[i]
            subs = []
            for st in lk.SubTable:
                t = lk.LookupType
                if t == 9:
                    t, st = st.ExtensionLookupType, st.ExtSubTable
                if t != 2:
                    continue
                cov = {gn: n for n, gn in enumerate(st.Coverage.glyphs)}
                if st.Format == 1:
                    pairs = []
                    for ps in st.PairSet:
                        d = {}
                        for rec in ps.PairValueRecord:
                            v = rec.Value1
                            d[rec.SecondGlyph] = getattr(v, "XAdvance", 0) or 0 if v else 0
                        pairs.append(d)
                    subs.append((1, cov, pairs))
                else:
                    c1 = st.ClassDef1.classDefs if st.ClassDef1 else {}
                    c2 = st.ClassDef2.classDefs if st.ClassDef2 else {}
                    subs.append((2, cov, (c1, c2, st.Class1Record)))
            lookups.append(subs)
        return lookups

    @functools.lru_cache(maxsize=None)
    def kern(self, left, right):
        total = 0
        for subs in self._lookups:
            for fmt, cov, data in subs:
                if left not in cov:
                    continue
                if fmt == 1:
                    d = data[cov[left]]
                    if right in d:
                        total += d[right]
                        break
                    continue
                c1, c2, recs = data
                rec = recs[c1.get(left, 0)].Class2Record[c2.get(right, 0)]
                v = rec.Value1
                total += (getattr(v, "XAdvance", 0) or 0) if v else 0
                break
        return total

    def gname(self, ch):
        return self.cmap.get(ord(ch), ".notdef")

    def layout(self, text, size, tracking=0.0):
        """[(glyph, x)], width.  tracking is in em (e.g. -0.03)."""
        s = size / self.upm
        x, out, prev = 0.0, [], None
        for ch in text:
            g = self.gname(ch)
            if prev is not None:
                x += self.kern(prev, g) * s
            out.append((g, x))
            x += self.hmtx[g][0] * s + tracking * size
            prev = g
        if text:
            x -= tracking * size
        return out, x

    def width(self, text, size, tracking=0.0):
        return self.layout(text, size, tracking)[1]

    def d(self, text, x0, y0, size, tracking=0.0):
        """SVG path data for text whose baseline starts at (x0, y0)."""
        s = size / self.upm
        parts = []
        for g, x in self.layout(text, size, tracking)[0]:
            pen = SVGPathPen(self.glyphs, ntos=_num)
            self.glyphs[g].draw(TransformPen(pen, (s, 0, 0, -s, x0 + x, y0)))
            cmd = pen.getCommands()
            if cmd:
                parts.append(cmd)
        return "".join(parts)


@functools.lru_cache(maxsize=None)
def face(kind="sans", wght=400):
    tt = TTFont(os.path.join(FONT_DIR, FILES[kind]))
    tt = instancer.instantiateVariableFont(tt, {"wght": wght})
    return Face(tt)


def text(s, x, y, size, kind="sans", wght=400, fill="#fff", tracking=0.0,
         anchor="start", extra=""):
    """A <path> for one run of text. anchor: start | middle | end."""
    f = face(kind, wght)
    w = f.width(s, size, tracking)
    if anchor == "middle":
        x -= w / 2
    elif anchor == "end":
        x -= w
    return f'<path d="{f.d(s, x, y, size, tracking)}" fill="{fill}"{extra}/>', w


def width(s, size, kind="sans", wght=400, tracking=0.0):
    return face(kind, wght).width(s, size, tracking)


class Glyphs:
    """Outline each glyph once per document and <use> it everywhere it repeats.

    Mono text repeats a lot, so this keeps the SVGs small while the type stays
    exactly Geist. Call text() while drawing, then put defs() in <defs>."""

    def __init__(self, prefix="g"):
        self.prefix, self.ids, self.paths = prefix, {}, []

    def _ref(self, kind, wght, gname):
        key = (kind, wght, gname)
        if key not in self.ids:
            f = face(kind, wght)
            pen = SVGPathPen(f.glyphs, ntos=_num)
            f.glyphs[gname].draw(TransformPen(pen, (1, 0, 0, -1, 0, 0)))     # font units, y down
            d = pen.getCommands()
            gid = None
            if d:
                gid = f"{self.prefix}{len(self.paths)}"
                self.paths.append(f'<path id="{gid}" d="{d}"/>')
            self.ids[key] = gid
        return self.ids[key]

    def text(self, s, x, y, size, kind="sans", wght=400, fill="#fff", tracking=0.0,
             anchor="start", extra=""):
        f = face(kind, wght)
        lay, w = f.layout(s, size, tracking)
        if anchor == "middle":
            x -= w / 2
        elif anchor == "end":
            x -= w
        sc = size / f.upm
        uses = []
        for g, off in lay:
            gid = self._ref(kind, wght, g)
            if gid:
                uses.append(f'<use href="#{gid}" x="{_num(off / sc)}"/>')
        return (f'<g fill="{fill}" transform="translate({_num(x)} {_num(y)}) scale({sc:.6g})"{extra}>'
                + "".join(uses) + "</g>"), w

    def defs(self):
        return "".join(self.paths)

"""Generates the profile canvas (assets/canvas-dark.svg, assets/canvas-light.svg).

The canvas is an index of work: one row per project, each with a generated
mark that depicts what the project actually does.

Edit WORKS below, then run:

    python3 assets/canvas.py
"""
import math

W, H = 1200, 700
M = 80          # side margin
ROW_TOP = 130   # first row's top edge
ROW_H = 160     # row pitch
GW, GH = 210, 86  # mark box

THEMES = {
    "dark": dict(
        bg0="#0e1a0b", bg1="#0a1208",
        ink="#f4f5f1", muted="#a4b09d", faint="#76846f",
        accent="#9bb363", rule="#f4f5f1", rule_op="0.12",
        mark_op="0.9",
    ),
    "light": dict(
        bg0="#f6f6f1", bg1="#eaece3",
        ink="#12170e", muted="#525d4b", faint="#7b8673",
        accent="#5c6f32", rule="#12170e", rule_op="0.14",
        mark_op="0.95",
    ),
}

# ---- content ---------------------------------------------------------------
# (kind, name, description lines, mark)
WORKS = [
    ("R PACKAGE \u00b7 ZENODO DOI", "FibroDynMix", [
        "Marker-anchored negative-binomial modeling of fibroblast-state",
        "mixtures from single-cell counts. NB optimizer, VI posterior, transfer.",
    ], "mixture"),
    ("R PACKAGE", "ncfigR", [
        "Bioinformatics figure panels drawn from tidy source-data tables \u2014",
        "embedding, composition, heatmap, network, trajectory, export.",
    ], "panels"),
    ("CODEX SKILL \u00b7 7 R PACKAGES", "nc-bioinformatics-figure-skills", [
        "NC-style figure training and plotting toolkits: a Codex skill,",
        "reference notes, and seven R packages from ncfigR to multiomfigR.",
    ], "layout"),
]


# ---- generated marks -------------------------------------------------------
# All three share one language: a common baseline, thin strokes, one accent
# fill, and roughly equal ink coverage, so they read as a set.

def _baseline(th):
    return [f'<line x1="0" y1="{GH}" x2="{GW}" y2="{GH}" stroke="{th["ink"]}" stroke-opacity="0.20"/>']


def mark_mixture(th):
    """Overlapping component densities under their mixture envelope."""
    comps = [(0.30, 0.13, 0.62), (0.52, 0.09, 0.95), (0.74, 0.15, 0.55)]
    N = 64
    xs = [i / N for i in range(N + 1)]

    def dens(t):
        return [a * math.exp(-((t - mu) ** 2) / (2 * sd * sd)) for mu, sd, a in comps]

    def path(vals):
        pts = [f"{t*GW:.1f},{GH - v*(GH-10):.1f}" for t, v in zip(xs, vals)]
        return "M" + "L".join(pts)

    env = path([min(1.0, sum(dens(t))) for t in xs])
    out = [f'<path d="{env}L{GW},{GH}L0,{GH}Z" fill="{th["accent"]}" opacity="0.14"/>']
    for k in range(len(comps)):
        out.append(f'<path d="{path([dens(t)[k] for t in xs])}" fill="none" '
                   f'stroke="{th["ink"]}" stroke-width="1" opacity="0.28"/>')
    out.append(f'<path d="{env}" fill="none" stroke="{th["accent"]}" stroke-width="1.8"/>')
    return out + _baseline(th)


def mark_panels(th):
    """A rendered multi-panel figure: bars, a trend, a heatmap."""
    gap = 16
    pw = (GW - 2 * gap) / 3
    out = []
    # a - bars
    bars = [0.38, 0.66, 0.50, 0.84, 0.32]
    bw = pw / 9
    for i, v in enumerate(bars):
        x = i * (pw / len(bars)) + bw * 0.6
        out.append(f'<rect x="{x:.1f}" y="{GH-v*(GH-10):.1f}" width="{bw:.1f}" '
                   f'height="{v*(GH-10):.1f}" fill="{th["accent"]}" opacity="0.70"/>')
    # b - trend
    x0 = pw + gap
    ys = [0.26, 0.44, 0.38, 0.62, 0.80]
    pts = [(x0 + i * (pw / (len(ys) - 1)), GH - v * (GH - 10)) for i, v in enumerate(ys)]
    out.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
               f'" fill="none" stroke="{th["ink"]}" stroke-width="1.4" opacity="0.45"/>')
    for x, y in pts:
        out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.4" fill="{th["accent"]}" opacity="0.85"/>')
    # c - heatmap, light enough to read as cells rather than a block
    x0 = 2 * (pw + gap)
    cols, rows = 4, 3
    cw, ch = pw / cols, (GH - 10) / rows
    vals = [0.14, 0.52, 0.28, 0.74,
            0.60, 0.20, 0.68, 0.34,
            0.26, 0.78, 0.42, 0.16]
    for r in range(rows):
        for c in range(cols):
            v = vals[r * cols + c]
            out.append(f'<rect x="{x0 + c*cw:.1f}" y="{10 + r*ch:.1f}" width="{cw-3:.1f}" '
                       f'height="{ch-3:.1f}" fill="{th["accent"]}" opacity="{0.10 + v*0.55:.2f}"/>')
    return out + _baseline(th)


def mark_layout(th):
    """The grid behind a figure: panels, alignment guides, panel letters."""
    st = th["ink"]
    out = []
    lw = GW * 0.46
    rw = GW - lw - 12
    x1 = lw + 12
    sh = (GH - 10 - 12) / 2

    def panel(x, y, w, h, tint=False):
        f = f'fill="{th["accent"]}" opacity="0.16"' if tint else 'fill="none"'
        r = [f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" {f}/>']
        r.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" fill="none" '
                 f'stroke="{th["accent"] if tint else st}" stroke-opacity="{0.55 if tint else 0.30}"/>')
        return r

    out += panel(0, 10, lw, GH - 10)
    out += panel(x1, 10, rw, sh)
    out += panel(x1, 10 + sh + 12, rw, sh, tint=True)
    # alignment guides inside the big panel
    for i in range(1, 4):
        y = 10 + (GH - 10) * i / 4
        out.append(f'<line x1="9" y1="{y:.1f}" x2="{lw-9:.1f}" y2="{y:.1f}" '
                   f'stroke="{st}" stroke-opacity="0.13"/>')
    # a content trace, so the grid is clearly holding a figure
    pts = [(9 + i * (lw - 18) / 4, 10 + (GH - 10) * v) for i, v in
           enumerate([0.70, 0.44, 0.56, 0.26, 0.38])]
    out.append('<polyline points="' + " ".join(f"{x:.1f},{y:.1f}" for x, y in pts) +
               f'" fill="none" stroke="{th["accent"]}" stroke-width="1.4" opacity="0.75"/>')
    # panel letters
    for lx, ly, ch in ((0, 6, "a"), (x1, 6, "b"), (x1, 6 + sh + 12, "c")):
        out.append(f'<text class="m tick" x="{lx:.1f}" y="{ly:.1f}">{ch}</text>')
    return out


MARKS = {"mixture": mark_mixture, "panels": mark_panels, "layout": mark_layout}


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def build(theme_name):
    th = THEMES[theme_name]
    S = []
    A = S.append

    names = ", ".join(w[1] for w in WORKS)
    A(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
      f'role="img" aria-label="Jiang Congxin — work index. {esc(names)}. '
      f'Contact jcx981212@163.com.">')
    A("  <defs>")
    A(f'    <linearGradient id="bg" x1="0" y1="0" x2="0.6" y2="1">'
      f'<stop offset="0" stop-color="{th["bg0"]}"/><stop offset="1" stop-color="{th["bg1"]}"/></linearGradient>')
    A("    <style>")
    A('      .s { font-family: "Avenir Next", "Helvetica Neue", Helvetica, Arial, sans-serif; }')
    A('      .m { font-family: Menlo, Consolas, "DejaVu Sans Mono", monospace; }')
    A(f'      .wordmark {{ font-weight: 500; font-size: 27px; letter-spacing: -0.4px; fill: {th["ink"]}; }}')
    A(f'      .num   {{ font-weight: 500; font-size: 15px; letter-spacing: 1px; fill: {th["accent"]}; }}')
    A(f'      .kind  {{ font-weight: 600; font-size: 11.5px; letter-spacing: 2.6px; fill: {th["faint"]}; }}')
    A(f'      .title {{ font-weight: 400; font-size: 37px; letter-spacing: -1.1px; fill: {th["ink"]}; }}')
    A(f'      .desc  {{ font-weight: 400; font-size: 18px; letter-spacing: -0.15px; fill: {th["muted"]}; }}')
    A(f'      .tick  {{ font-weight: 500; font-size: 10px; letter-spacing: 0.5px; fill: {th["faint"]}; }}')
    A(f'      .foot  {{ font-weight: 500; font-size: 14px; letter-spacing: 1.6px; fill: {th["muted"]}; }}')
    A("    </style>")
    A("  </defs>")
    A("")
    A(f'  <rect width="{W}" height="{H}" fill="url(#bg)"/>')
    A("")

    # masthead — the name, and nothing else
    A(f'  <text class="s wordmark" x="{M}" y="74">Jiang Congxin</text>')
    A(f'  <text class="m foot" x="{W-M}" y="72" text-anchor="end" opacity="0.7">WORK</text>')
    A(f'  <line x1="{M}" y1="110" x2="{W-M}" y2="110" stroke="{th["rule"]}" '
      f'stroke-opacity="{th["rule_op"]}" stroke-width="1"/>')
    A("")

    for i, (kind, name, desc, mark) in enumerate(WORKS):
        t = ROW_TOP + i * ROW_H
        dy = (2 - len(desc)) * 12  # center rows with fewer lines
        A(f'  <g transform="translate(0 {t})">')
        A(f'    <text class="m num"  x="{M}" y="{72+dy}">{i+1:02d}</text>')
        A(f'    <text class="s kind" x="{M+58}" y="{32+dy}">{esc(kind)}</text>')
        A(f'    <text class="s title" x="{M+56}" y="{72+dy}">{esc(name)}</text>')
        for j, line in enumerate(desc):
            A(f'    <text class="s desc" x="{M+58}" y="{104 + j*25 + dy}">{esc(line)}</text>')
        A(f'    <g transform="translate({W-M-GW} 30)" opacity="{th["mark_op"]}">')
        for el in MARKS[mark](th):
            A(f'      {el}')
        A("    </g>")
        A(f'    <line x1="{M}" y1="{ROW_H}" x2="{W-M}" y2="{ROW_H}" stroke="{th["rule"]}" '
          f'stroke-opacity="{th["rule_op"]}" stroke-width="1"/>')
        A("  </g>")
        A("")

    A(f'  <circle cx="{M+4}" cy="{H-36}" r="4" fill="{th["accent"]}"/>')
    A(f'  <text class="m foot" x="{M+20}" y="{H-32}">jcx981212@163.com</text>')
    A(f'  <text class="m foot" x="{W-M}" y="{H-32}" text-anchor="end" opacity="0.7">'
      f'github.com/jiangcongxin</text>')
    A("</svg>")
    return "\n".join(S) + "\n"


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    for name in ("dark", "light"):
        path = os.path.join(here, f"canvas-{name}.svg")
        with open(path, "w", encoding="utf-8") as f:
            f.write(build(name))
        print("wrote", path)

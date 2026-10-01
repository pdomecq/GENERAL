"""Gráficos SVG del libro: árbol de cinco generaciones, árboles por rama,
abanico de siete generaciones y el esquema de «Dos veces Domecq».

Todas las medidas van en milímetros: el viewBox usa 1 unidad = 1 mm y el
SVG se dibuja a ese tamaño en la página impresa. Los colores salen de clases
CSS (.pat, .mat, .dup...) definidas en la hoja de estilos del libro.
"""
import math
from html import escape

from datos import P, gen, real, side, fmt, nos


def esc(s):
    return escape(str(s), quote=True)


def wrap(text, width):
    """Parte un texto en líneas de como mucho `width` caracteres, por palabras."""
    words, lines, cur = str(text).split(), [], ""
    for w in words:
        if cur and len(cur) + 1 + len(w) > width:
            lines.append(cur)
            cur = w
        else:
            cur = f"{cur} {w}".strip()
    if cur:
        lines.append(cur)
    return lines


def conf_class(k):
    p = P.get(str(real(k)))
    if not p:
        return "unk"
    return {"ok": "ok", "tree": "tree", "ded": "ded", "doubt": "doubt", "none": "unk", "self": "ok"}.get(p.get("c"), "unk")


def known(k):
    p = P.get(str(k))
    if not p:
        return False
    if p.get("same"):
        return True
    return p.get("c") not in (None, "none")


def name_of(k, root_label=None):
    if k == 1 and root_label:
        return root_label
    p = P.get(str(real(k)), {})
    return p.get("n", "")


def dates_of(k):
    return P.get(str(real(k)), {}).get("d", "")


# ---------------------------------------------------------------- 5 generaciones
def pedigree5(root_label="Los hermanos Domecq Vergara"):
    """Árbol clásico: generación I a la izquierda, V a la derecha (16 casillas)."""
    W, H = 166.0, 236.0
    widths = [27.0, 29.5, 31.0, 32.0, 34.5]
    gap = (W - sum(widths)) / 4
    xs = []
    x = 0.0
    for w in widths:
        xs.append(x)
        x += w + gap
    leaf_h = H / 16
    out = [f'<svg class="chart pedigree" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Árbol de cinco generaciones">']

    def ypos(k):
        g = gen(k)
        i = k - 2 ** (g - 1)
        span = 16 // 2 ** (g - 1)
        return (i * span + span / 2) * leaf_h

    box_h = {1: 22.0, 2: 21.0, 3: 20.0, 4: 18.0, 5: 13.2}
    # conectores
    for k in range(1, 16):
        g = gen(k)
        x1 = xs[g - 1] + widths[g - 1]
        xm = x1 + gap / 2
        y = ypos(k)
        yf, ym = ypos(2 * k), ypos(2 * k + 1)
        out.append(f'<path class="link" d="M{x1:.2f} {y:.2f} H{xm:.2f} M{xm:.2f} {yf:.2f} V{ym:.2f} M{xm:.2f} {yf:.2f} H{xs[g]:.2f} M{xm:.2f} {ym:.2f} H{xs[g]:.2f}"/>')
    for k in range(1, 32):
        g = gen(k)
        w, h = widths[g - 1], box_h[g]
        x, y = xs[g - 1], ypos(k) - h / 2
        p = P.get(str(k), {})
        dup = bool(p.get("same"))
        cls = ["box", side(k) or "self", conf_class(k)]
        if dup:
            cls.append("dupbox")
        out.append(f'<rect class="{" ".join(cls)}" x="{x:.2f}" y="{y:.2f}" width="{w:.2f}" height="{h:.2f}" rx="0.8"/>')
        fs = 2.35 if g < 5 else 2.15
        lh = fs * 1.18
        nm = name_of(k, root_label)
        lines = wrap(nm, int(w / (fs * 0.47)))[:3]
        num = f"nº {k}" + (f" · = nº {p['same']}" if dup else "")
        ty = y + 2.9
        out.append(f'<text class="bnum {side(k) or "self"}" x="{x + 1.4:.2f}" y="{ty:.2f}" font-size="1.85">{esc(num)}</text>')
        ty += 0.6
        for ln in lines:
            ty += lh
            out.append(f'<text class="bname" x="{x + 1.4:.2f}" y="{ty:.2f}" font-size="{fs}">{esc(ln)}</text>')
        d = dates_of(k)
        t = nos(P.get(str(real(k)), {}).get("t", ""))
        extra = d
        if t and g <= 4 and k != 1 and len(t) < 40:
            extra = (d + " · " if d else "") + t
        if extra:
            for ln in wrap(extra, int(w / (1.9 * 0.47)))[:2 if g < 5 else 1]:
                ty += 1.9 * 1.25
                out.append(f'<text class="bdate" x="{x + 1.4:.2f}" y="{ty:.2f}" font-size="1.9">{esc(ln)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------- árbol por rama
def branch_tree(roots, depth, width=166.0, row_h=11.4, label=None):
    """Árbol compacto de los antepasados conocidos de una o varias personas.

    Cada columna es una generación; solo se dibujan los antepasados que
    constan, y cada persona se centra entre sus padres conocidos.
    """
    rows = []
    pos = {}
    next_row = [0]

    def place(k, d):
        kids = [c for c in (2 * k, 2 * k + 1) if d < depth and known(c) and not P.get(str(c), {}).get("same")]
        ys = [place(c, d + 1) for c in kids]
        if ys:
            y = sum(ys) / len(ys)
        else:
            y = next_row[0]
            next_row[0] += 1
        pos[k] = (d, y)
        rows.append(k)
        return y

    for r in roots:
        place(r, 0)
        next_row[0] += 0.35
    nrows = next_row[0] - 0.35
    gap = 3.2
    colw = (width - gap * depth) / (depth + 1)
    H = max(nrows, 1) * row_h + 2
    out = [f'<svg class="chart branch" viewBox="0 0 {width:.1f} {H:.1f}" width="{width:.1f}mm" height="{H:.1f}mm" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{esc(label or "Árbol de la rama")}">']
    bh = row_h - 1.6

    def xy(k):
        d, y = pos[k]
        return d * (colw + gap), y * row_h + 1 + row_h / 2

    for k, (d, y) in pos.items():
        kids = [c for c in (2 * k, 2 * k + 1) if c in pos]
        if not kids:
            continue
        x, yc = xy(k)
        x1 = x + colw
        xm = x1 + gap / 2
        ys = [xy(c)[1] for c in kids]
        segs = [f"M{x1:.2f} {yc:.2f} H{xm:.2f}", f"M{xm:.2f} {min(ys + [yc]):.2f} V{max(ys + [yc]):.2f}"]
        for c in kids:
            segs.append(f"M{xm:.2f} {xy(c)[1]:.2f} H{xy(c)[0]:.2f}")
        out.append(f'<path class="link" d="{" ".join(segs)}"/>')
    fs = 2.2 if colw >= 26 else 2.0
    for k in pos:
        x, yc = xy(k)
        y = yc - bh / 2
        cls = ["box", side(k) or "self", conf_class(k)]
        out.append(f'<rect class="{" ".join(cls)}" x="{x:.2f}" y="{y:.2f}" width="{colw:.2f}" height="{bh:.2f}" rx="0.8"/>')
        nm = name_of(k)
        maxc = int((colw - 2.2) / (fs * 0.47))
        lines = wrap(nm, maxc)
        d = dates_of(k)
        if len(lines) > 3:
            lines = lines[:3]
            lines[-1] = lines[-1].rstrip(",") + "…"
        ty = y + 2.45
        out.append(f'<text class="bnum {side(k) or "self"}" x="{x + 1.1:.2f}" y="{ty:.2f}" font-size="1.7">{esc("nº " + fmt(k))}{(" · " + esc(d)) if d else ""}</text>')
        for ln in lines:
            ty += fs * 1.15
            out.append(f'<text class="bname" x="{x + 1.1:.2f}" y="{ty:.2f}" font-size="{fs}">{esc(ln)}</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------- abanico
FAN_R = [0, 17.0, 32.0, 47.0, 63.0, 82.0, 102.0, 124.0]


def _pt(cx, cy, r, a):
    t = math.radians(a)
    return cx + r * math.cos(t), cy - r * math.sin(t)


def _sector(cx, cy, r0, r1, a0, a1):
    """Sector de corona entre los ángulos a0 > a1 (grados, sentido horario)."""
    x0, y0 = _pt(cx, cy, r1, a0)
    x1, y1 = _pt(cx, cy, r1, a1)
    large = 1 if (a0 - a1) > 180 else 0
    if r0 <= 0:
        return f"M{cx:.2f} {cy:.2f} L{x0:.2f} {y0:.2f} A{r1:.2f} {r1:.2f} 0 {large} 1 {x1:.2f} {y1:.2f} Z"
    x2, y2 = _pt(cx, cy, r0, a1)
    x3, y3 = _pt(cx, cy, r0, a0)
    return (f"M{x0:.2f} {y0:.2f} A{r1:.2f} {r1:.2f} 0 {large} 1 {x1:.2f} {y1:.2f} "
            f"L{x2:.2f} {y2:.2f} A{r0:.2f} {r0:.2f} 0 {large} 0 {x3:.2f} {y3:.2f} Z")


def _dup_of(k):
    """Si k está en la rama repetida (28–29 y sus antepasados), su doble."""
    g = gen(k)
    if g < 5:
        return None
    a5 = k >> (g - 5)
    if a5 in (28, 29):
        return k - (12 << (g - 5))
    return None


def fan_chart(gens=7, root_label=("Los hermanos", "Domecq Vergara"), decorative=False, uid="fan"):
    R = FAN_R[: gens + 1]
    r_max = R[gens]
    W = 2 * r_max + 6
    Hh = r_max + 13
    cx, cy = W / 2, r_max + 3
    cls_svg = "chart fan deco" if decorative else "chart fan"
    out = [f'<svg class="{cls_svg}" viewBox="0 0 {W:.1f} {Hh:.1f}" width="{W:.1f}mm" height="{Hh:.1f}mm" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Abanico de {gens} generaciones">']
    defs = []
    for g in range(1, gens + 1):
        n = 2 ** (g - 1)
        span = 180.0 / n
        for i in range(n):
            k = n + i
            a0 = 180.0 - i * span
            a1 = a0 - span
            dup = _dup_of(k)
            p = P.get(str(k))
            if g == 1:
                cls = "seg self"
            elif dup:
                cls = "seg dupseg"
            elif p and p.get("c") == "doubt":
                cls = "seg doubtseg"
                out.append(f'<path d="{_sector(cx, cy, R[g - 1], R[g], a0, a1)}" fill="url(#{uid}hatch)" class="hatchfill"/>')
            elif p and known(k):
                cls = f"seg {side(k)} {conf_class(k)}"
            else:
                cls = "seg unk"
            out.append(f'<path class="{cls}" d="{_sector(cx, cy, R[g - 1], R[g], a0, a1)}"/>')
            if decorative:
                continue
            mid = (a0 + a1) / 2
            if g == 1:
                out.append(f'<text class="fname root" x="{cx:.2f}" y="{cy - 7.5:.2f}" font-size="2.8" text-anchor="middle">{esc(root_label[0])}</text>')
                out.append(f'<text class="fname root" x="{cx:.2f}" y="{cy - 4.2:.2f}" font-size="2.8" text-anchor="middle">{esc(root_label[1])}</text>')
                continue
            if dup:
                if g <= 6:
                    rm = (R[g - 1] + R[g]) / 2
                    x, y = _pt(cx, cy, rm, mid)
                    rot = -mid if mid <= 90 else 180 - mid
                    out.append(f'<text class="fdup" transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f})" font-size="1.7" text-anchor="middle" dy="0.6">= nº {dup}</text>')
                continue
            if not (p and known(k)):
                continue
            nm = p.get("n", "")
            dt = p.get("d", "")
            if g <= 4:
                # texto en arco, a lo largo de la corona
                fs = {2: 3.0, 3: 2.6, 4: 2.25}[g]
                arc_len = math.radians(span) * (R[g - 1] + R[g]) / 2
                maxc = int((arc_len - 3) / (fs * 0.46))
                lines = wrap(nm, maxc)[:3]
                if dt:
                    lines.append(dt)
                nl = len(lines)
                ring = R[g] - R[g - 1]
                step = min(fs * 1.22, (ring - 2) / max(nl, 1))
                r_top = (R[g - 1] + R[g]) / 2 + step * (nl - 1) / 2
                for j, ln in enumerate(lines):
                    r = r_top - j * step - fs * 0.32
                    pid = f"{uid}a{k}_{j}"
                    x0, y0 = _pt(cx, cy, r, a0 - 0.3)
                    x1, y1 = _pt(cx, cy, r, a1 + 0.3)
                    defs.append(f'<path id="{pid}" d="M{x0:.2f} {y0:.2f} A{r:.2f} {r:.2f} 0 0 1 {x1:.2f} {y1:.2f}"/>')
                    cl = "fdate" if (dt and j == nl - 1) else "fname"
                    f2 = fs * 0.85 if cl == "fdate" else fs
                    out.append(f'<text class="{cl}" font-size="{f2:.2f}"><textPath href="#{pid}" startOffset="50%" text-anchor="middle">{esc(ln)}</textPath></text>')
            else:
                # texto radial
                fs = {5: 2.0, 6: 1.75, 7: 1.5}[g]
                ring = R[g] - R[g - 1]
                maxc = int((ring - 2.0) / (fs * 0.47))
                arcw = math.radians(span) * (R[g - 1] + R[g]) / 2
                max_lines = max(1, int((arcw - 0.6) / (fs * 1.12)))
                lines = wrap(nm, maxc)
                if dt and len(lines) < max_lines:
                    lines.append(dt)
                if len(lines) > max_lines:
                    lines = lines[:max_lines]
                    lines[-1] = lines[-1] + "…"
                rm = (R[g - 1] + R[g]) / 2
                x, y = _pt(cx, cy, rm, mid)
                rot = -mid if mid <= 90 else 180 - mid
                nl = len(lines)
                off0 = -(nl - 1) * fs * 1.12 / 2 + fs * 0.34
                tsp = []
                for j, ln in enumerate(lines):
                    cl = "fdate" if (dt and ln == dt) else "fname"
                    tsp.append(f'<tspan class="{cl}" x="0" y="{off0 + j * fs * 1.12:.2f}">{esc(ln)}</tspan>')
                out.append(f'<text transform="translate({x:.2f} {y:.2f}) rotate({rot:.2f})" font-size="{fs}" text-anchor="middle">{"".join(tsp)}</text>')
    defs.append(f'<pattern id="{uid}hatch" width="1.6" height="1.6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)"><rect class="hatchbg" width="1.6" height="1.6"/><line class="hatchln" x1="0" y1="0" x2="0" y2="1.6"/></pattern>')
    out.insert(1, "<defs>" + "".join(defs) + "</defs>")
    if not decorative:
        # etiquetas de generación sobre la base
        for g in range(2, gens + 1):
            rm = (R[g - 1] + R[g]) / 2
            for sx in (-1, 1):
                out.append(f'<text class="fgen" x="{cx + sx * rm:.2f}" y="{cy + 4.2:.2f}" font-size="2.1" text-anchor="middle">{["", "I", "II", "III", "IV", "V", "VI", "VII"][g]}</text>')
        out.append(f'<text class="fside pat" x="{cx - r_max / 2:.2f}" y="{cy + 8.5:.2f}" font-size="2.6" text-anchor="middle">Por papá</text>')
        out.append(f'<text class="fside mat" x="{cx + r_max / 2:.2f}" y="{cy + 8.5:.2f}" font-size="2.6" text-anchor="middle">Por mamá</text>')
    out.append("</svg>")
    return "\n".join(out)


# ---------------------------------------------------------------- dos veces Domecq
def convergence():
    W, H = 150.0, 112.0
    out = [f'<svg class="chart conv" viewBox="0 0 {W} {H}" width="{W}mm" height="{H}mm" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Dos veces Domecq">']

    def box(x, y, w, h, cls, num, name, sub):
        out.append(f'<rect class="box {cls}" x="{x}" y="{y}" width="{w}" height="{h}" rx="1"/>')
        out.append(f'<text class="bnum {cls}" x="{x + w / 2}" y="{y + 4.2}" font-size="2.1" text-anchor="middle">{esc(num)}</text>')
        out.append(f'<text class="bname" x="{x + w / 2}" y="{y + 8.6}" font-size="3.0" text-anchor="middle">{esc(name)}</text>')
        if sub:
            out.append(f'<text class="bdate" x="{x + w / 2}" y="{y + 12.4}" font-size="2.3" text-anchor="middle">{esc(sub)}</text>')

    def line(d):
        out.append(f'<path class="link" d="{d}"/>')

    def rel(x, y, txt):
        out.append(f'<text class="rel" x="{x}" y="{y}" font-size="2.3" text-anchor="middle">{esc(txt)}</text>')

    bw, bh = 56, 15
    box(25, 2, 100, 15, "dupbox self", "nº 16–17 y también nº 28–29", "Pedro Domecq Núñez de Villavicencio × María Rivero González", "I marqueses de Casa Domecq · casaron en Jerez en 1892")
    line("M75 17 V23 M30 23 H120 M30 23 V29 M120 23 V29")
    box(2, 29, bw, bh, "pat", "nº 8", "José Manuel Domecq Rivero", "1895–1981")
    box(92, 29, bw, bh, "mat", "nº 14", "Juan Pedro Domecq Rivero", "1910–1995")
    rel(75, 37.5, "hermanos")
    line("M30 44 V56 M120 44 V56")
    box(2, 56, bw, bh, "pat", "nº 4", "José Manuel Domecq Hidalgo", "nuestro abuelo")
    box(92, 56, bw, bh, "mat", "nº 7", "Beatriz Domecq López de Carrizosa", "nuestra abuela")
    rel(75, 64.5, "primos hermanos")
    line("M30 71 V83 M120 71 V83")
    box(2, 83, bw, bh, "pat", "nº 2", "Pablo Domecq Bohórquez", "papá")
    box(92, 83, bw, bh, "mat", "nº 3", "Beatriz Vergara Domecq", "mamá")
    rel(75, 91.5, "primos segundos")
    line("M58 90.5 H66 M84 90.5 H92 M30 98 V101 H120 V98 M75 101 V104")
    out.append(f'<text class="bname" x="75" y="108" font-size="3.0" text-anchor="middle">Los hermanos Domecq Vergara · nº 1</text>')
    out.append("</svg>")
    return "\n".join(out)

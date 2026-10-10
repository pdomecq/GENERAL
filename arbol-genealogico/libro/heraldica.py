"""Escudos de armas, cruces de órdenes y coronas, dibujados en SVG.

Las figuras (león, lobo, roble, espada, guantes, columnas, flores de lis, aspas
y cruces) vienen de la biblioteca de muebles heráldicos del Fantasy Map
Generator de Azgaar: las sencillas son de dominio público (CC0) y las demás,
dibujos de WappenWiki con licencia CC BY-NC-SA 3.0. El resto (el escudo, las
piezas, los dragantes, las hojas de higuera, los carrizos y las coronas) está
dibujado aquí.
"""
import json
import math
import re
from pathlib import Path

AQUI = Path(__file__).resolve().parent
FIG = AQUI / "heraldica" / "figuras"
BBOX = json.loads((AQUI / "heraldica" / "figuras.json").read_text())

# Esmaltes, algo apagados para que impriman con dignidad.
T = {
    "oro": "#CFA63F", "plata": "#F6F4EE", "gules": "#A3242E", "azur": "#25508E",
    "sinople": "#2E6A3C", "sable": "#1D1B19", "purpura": "#6B2C63",
}
LINE = "#1E1A16"
W, H = 200.0, 236.0          # escudo español: cuadrilongo con la punta redonda
R = 100.0                    # radio de la punta


def shield_path(inset=0.0, w=W, h=H):
    """Contorno del escudo español, con un margen interior opcional."""
    r = w / 2 - inset
    y0 = h - w / 2
    return (f"M{inset:.2f},{inset:.2f} H{w - inset:.2f} V{y0:.2f} "
            f"A{r:.2f},{r:.2f} 0 0 1 {inset:.2f},{y0:.2f} Z")


def rect_path(inset=0.0, w=W, h=H):
    return f"M{inset},{inset} H{w - inset} V{h - inset} H{inset} Z"


# ---------------------------------------------------------------- figuras
_cache = {}


def _charge_body(name):
    if name not in _cache:
        s = (FIG / f"{name}.svg").read_text()
        s = re.sub(r"<metadata[^>]*/>", "", s)
        body = s[s.index(">", s.index("<svg")) + 1: s.rindex("</svg>")]
        _cache[name] = body
    return _cache[name]


def charge(name, cx, cy, w, h, fill, second=None, rot=0.0, flip=False, stroke=LINE, sw=None):
    """Coloca la figura `name` centrada en (cx, cy) dentro de una caja w × h."""
    bb = BBOX[name]
    s = min(w / bb["w"], h / bb["h"])
    ox, oy = bb["x"] + bb["w"] / 2, bb["y"] + bb["h"] / 2
    body = _charge_body(name)
    sec = second or fill
    body = re.sub(r'class="secondary"(?![^>]*\sfill=)', f'class="secondary" fill="{sec}"', body)
    sx = -s if flip else s
    tr = f"translate({cx:.2f},{cy:.2f}) rotate({rot:.2f}) scale({sx:.4f},{s:.4f}) translate({-ox:.2f},{-oy:.2f})"
    extra = f' stroke-width="{sw}"' if sw else ""
    return f'<g transform="{tr}" fill="{fill}" stroke="{stroke}"{extra}>{body}</g>'


def dragon_head(x, y, ang, scale=1.0, fill=None):
    """Cabeza de dragón de perfil que se traga el extremo de una banda.

    En coordenadas locales la boca mira hacia +x y abarca y ∈ [-21, 21].
    """
    fill = fill or T["sinople"]
    head = ("M0,-23 C-6,-34 -24,-42 -42,-36 C-54,-31 -62,-18 -62,-2 "
            "C-62,14 -54,28 -40,33 C-26,38 -10,34 0,23 L-14,21 L-14,-21 Z")
    ear = "M-40,-34 L-52,-52 L-30,-38 Z"
    crest = "M-58,-14 L-74,-20 L-62,-4 L-76,4 L-61,10 L-72,22 L-55,20 Z"
    teeth = ("M-14,-21 L-10,-15 L-6,-21 L-2,-15 L0,-21 Z "
             "M-14,21 L-10,15 L-6,21 L-2,15 L0,21 Z")
    return (f'<g transform="translate({x:.2f},{y:.2f}) rotate({ang:.2f}) scale({scale:.3f})" stroke="{LINE}" stroke-width="1.4" stroke-linejoin="round">'
            f'<path d="{crest}" fill="{fill}"/><path d="{ear}" fill="{fill}"/><path d="{head}" fill="{fill}"/>'
            f'<path d="{teeth}" fill="{T["plata"]}" stroke-width="0.9"/>'
            f'<circle cx="-34" cy="-14" r="5" fill="{T["plata"]}"/><circle cx="-33" cy="-14" r="2.4" fill="{LINE}" stroke="none"/>'
            f'<path d="M-52,8 Q-44,14 -36,8" fill="none"/></g>')


def fig_leaf(cx, cy, size, fill, rot=0.0):
    """Hoja de higuera, con el tallo hacia abajo."""
    d = ("M0,0.55 C-0.18,0.6 -0.42,0.55 -0.5,0.42 C-0.75,0.48 -0.95,0.3 -0.88,0.08 "
         "C-0.98,-0.1 -0.85,-0.3 -0.62,-0.28 C-0.55,-0.35 -0.45,-0.42 -0.32,-0.4 "
         "C-0.36,-0.72 -0.15,-0.95 0,-0.98 C0.15,-0.95 0.36,-0.72 0.32,-0.4 "
         "C0.45,-0.42 0.55,-0.35 0.62,-0.28 C0.85,-0.3 0.98,-0.1 0.88,0.08 "
         "C0.95,0.3 0.75,0.48 0.5,0.42 C0.42,0.55 0.18,0.6 0,0.55 Z")
    veins = "M0,0.95 L0,-0.78 M0,0.2 L-0.66,-0.05 M0,0.2 L0.66,-0.05 M0,0.42 L-0.42,0.36 M0,0.42 L0.42,0.36"
    k = size / 2
    return (f'<g transform="translate({cx:.2f},{cy:.2f}) rotate({rot:.1f}) scale({k:.3f})" stroke="{LINE}" stroke-linejoin="round">'
            f'<path d="{d}" fill="{fill}" stroke-width="{1.3 / k:.4f}"/>'
            f'<path d="{veins}" fill="none" stroke-width="{1.0 / k:.4f}"/></g>')


def reed(x, base, top, fill):
    """Un carrizo: tallo, dos hojas y la espiga."""
    sw = 1.2
    leaf1 = f"M{x},{base - 40} C{x - 18},{base - 70} {x - 22},{base - 96} {x - 26},{base - 112} C{x - 14},{base - 90} {x - 6},{base - 70} {x + 1.5},{base - 52} Z"
    leaf2 = f"M{x},{base - 70} C{x + 16},{base - 96} {x + 20},{base - 118} {x + 24},{base - 132} C{x + 12},{base - 112} {x + 5},{base - 96} {x - 1.5},{base - 82} Z"
    stem = f"M{x - 2.2},{base} L{x - 1.4},{top + 30} L{x + 1.4},{top + 30} L{x + 2.2},{base} Z"
    head = f'<rect x="{x - 5.5}" y="{top}" width="11" height="34" rx="5.5" fill="{fill}" stroke="{LINE}" stroke-width="{sw}"/>'
    tip = f'<path d="M{x},{top} L{x},{top - 14}" stroke="{LINE}" stroke-width="2.2" fill="none"/>'
    return (f'<g fill="{fill}" stroke="{LINE}" stroke-width="{sw}" stroke-linejoin="round">'
            f'<path d="{leaf1}"/><path d="{leaf2}"/><path d="{stem}"/></g>{tip}{head}')


# ---------------------------------------------------------------- armas
# Cada función dibuja en el espacio 200 × 236; `shape` dice si el contenedor
# es el escudo entero ("shield") o un cuartel rectangular ("rect"), para que
# las bordura sigan su contorno.

def _field(t):
    return f'<rect x="-2" y="-2" width="{W + 4}" height="{H + 4}" fill="{T[t]}"/>'


def _bordure(t, shape, b=24):
    outer = shield_path(0) if shape == "shield" else rect_path(0)
    inner = shield_path(b) if shape == "shield" else rect_path(b)
    return f'<path d="{outer} {inner}" fill="{T[t]}" fill-rule="evenodd" stroke="{LINE}" stroke-width="1.2"/>'


def arms_domecq(shape="shield"):
    return "".join([
        _field("azur"),
        charge("sword", 100, 118, 60, 186, T["oro"], T["plata"], rot=-45, sw=0.32),
        charge("gauntlet", 150, 66, 46, 72, T["plata"], T["plata"], rot=8, sw=0.7),
        charge("gauntlet", 52, 168, 46, 72, T["plata"], T["plata"], rot=8, sw=0.7),
    ])


def arms_bohorquez(shape="shield"):
    b = 24
    ang = 45
    c, s = math.cos(math.radians(ang)), math.sin(math.radians(ang))
    cx, cy = 100, 112
    d = 56
    band = f'<rect x="{cx - d - 6}" y="{cy - 17}" width="{2 * d + 12}" height="34" fill="{T["oro"]}" stroke="{LINE}" stroke-width="1.3" transform="rotate({ang} {cx} {cy})"/>'
    h1 = dragon_head(cx - d * c, cy - d * s, ang, 0.62)
    h2 = dragon_head(cx + d * c, cy + d * s, ang + 180, 0.62)
    yb = H - 12 if shape == "shield" else H - 12
    return "".join([
        _field("gules"),
        f'<g>{band}{h1}{h2}</g>',
        _bordure("azur", shape, b),
        charge("fleurDeLis", 100, 12, 17, 18, T["oro"], sw=0.6),
        charge("fleurDeLis", 100, yb, 17, 18, T["oro"], sw=0.6),
        charge("column", 12, 116, 18, 76, T["plata"], sw=0.5),
        charge("column", 188, 116, 18, 76, T["plata"], sw=0.5),
    ])


def arms_vergara(shape="shield"):
    links = "".join(
        f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5.2" ry="3.2" transform="rotate({a} {x:.1f} {y:.1f})" fill="none" stroke="{T["oro"]}" stroke-width="2.6"/>'
        f'<ellipse cx="{x:.1f}" cy="{y:.1f}" rx="5.2" ry="3.2" transform="rotate({a} {x:.1f} {y:.1f})" fill="none" stroke="{LINE}" stroke-width="0.5"/>'
        for x, y, a in [(108, 158, -20), (117, 155, 60), (126, 152, -20)])
    return "".join([
        _field("oro"),
        charge("oak", 100, 104, 168, 186, T["sinople"], "#24532F", sw=0.42),
        charge("wolfPassant", 98, 178, 124, 76, T["sable"], T["gules"], sw=0.45),
        links,
    ])


def arms_carrizosa(shape="shield"):
    b = 24
    reeds = "".join(reed(x, 206, top, T["oro"]) for x, top in [(58, 58), (86, 44), (114, 44), (142, 58)])
    pts = [(16, 16), (100, 12), (184, 16), (12, 104), (188, 104), (30, 184), (100, H - 12), (170, 184)]
    if shape == "rect":
        pts = [(14, 14), (100, 12), (186, 14), (12, 118), (188, 118), (14, H - 14), (100, H - 12), (186, H - 14)]
    aspas = "".join(charge("crossSaltire", x, y, 15, 15, T["oro"], sw=0.6) for x, y in pts)
    return "".join([
        _field("gules"),
        charge("lionPassant", 100, 150, 150, 80, T["purpura"], T["gules"], sw=0.4),
        reeds,
        _bordure("azur", shape, b),
        aspas,
    ])


def arms_villavicencio(shape="shield"):
    out = [_field("azur")]
    for yc in (52, 114, 176):
        out.append(f'<rect x="-2" y="{yc - 17}" width="{W + 4}" height="34" fill="{T["oro"]}" stroke="{LINE}" stroke-width="1.2"/>')
        for i in range(5):
            x = 32 + i * 34
            out.append(f'<path d="M{x - 3.5},{yc - 12} Q{x},{yc - 15} {x + 3.5},{yc - 12} L{x + 3},{yc + 9} Q{x},{yc + 14} {x - 3},{yc + 9} Z" fill="{T["gules"]}" stroke="{LINE}" stroke-width="0.7"/>')
    return "".join(out)


def arms_figueroa(shape="shield"):
    out = [_field("oro")]
    for x, y in [(100, 112), (54, 62), (146, 62), (54, 164), (146, 164)]:
        out.append(fig_leaf(x, y, 58, T["sinople"]))
    return "".join(out)


def arms_spinola(shape="shield"):
    out = [_field("oro")]
    n, size, y0 = 10, 20.0, 112
    for row in range(3):
        for col in range(n + 1):
            colr = T["gules"] if (row + col) % 2 == 0 else T["plata"]
            out.append(f'<rect x="{col * size}" y="{y0 + row * size}" width="{size}" height="{size}" fill="{colr}"/>')
    out.append(f'<rect x="-2" y="{y0}" width="{W + 4}" height="{3 * size}" fill="none" stroke="{LINE}" stroke-width="1.3"/>')
    out.append(charge("fleurDeLis", 100, 64, 70, 80, T["gules"], sw=0.6))
    return "".join(out)


ARMS = {
    "domecq": arms_domecq, "bohorquez": arms_bohorquez, "vergara": arms_vergara,
    "carrizosa": arms_carrizosa, "villavicencio": arms_villavicencio,
    "figueroa": arms_figueroa, "spinola": arms_spinola,
}


def _sheen(uid):
    return (f'<radialGradient id="{uid}-sh" cx="0.32" cy="0.22" r="0.95">'
            f'<stop offset="0" stop-color="#fff" stop-opacity="0.22"/>'
            f'<stop offset="0.55" stop-color="#fff" stop-opacity="0"/>'
            f'<stop offset="1" stop-color="#000" stop-opacity="0.16"/></radialGradient>')


def shield(name, uid, cls="arms"):
    """Escudo completo de un linaje."""
    inner = ARMS[name]("shield") if name in ARMS else ""
    return _wrap(inner, uid, cls, f"Armas de {name}")


def costados(uid, cls="arms costados"):
    """Cuartelado: 1.º y 4.º Domecq, 2.º Bohórquez, 3.º Vergara."""
    q = [("domecq", 0, 0), ("bohorquez", 1, 0), ("vergara", 0, 1), ("domecq", 1, 1)]
    parts = []
    for i, (n, cx, cy) in enumerate(q):
        x, y = cx * W / 2, cy * H / 2
        parts.append(f'<clipPath id="{uid}-q{i}"><rect x="{x}" y="{y}" width="{W / 2}" height="{H / 2}"/></clipPath>'
                     f'<g clip-path="url(#{uid}-q{i})"><g transform="translate({x},{y}) scale(0.5)">{ARMS[n]("rect")}</g></g>')
    parts.append(f'<path d="M{W / 2},0 V{H} M0,{H / 2} H{W}" stroke="{LINE}" stroke-width="1.6"/>')
    return _wrap("".join(parts), uid, cls, "Armas de los cuatro costados")


def _wrap(inner, uid, cls, label):
    sp = shield_path(0)
    return (f'<svg class="{cls}" viewBox="-6 -6 {W + 12} {H + 12}" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="{label}">'
            f'<defs><clipPath id="{uid}-cl"><path d="{sp}"/></clipPath>{_sheen(uid)}</defs>'
            f'<g clip-path="url(#{uid}-cl)">{inner}<path d="{sp}" fill="url(#{uid}-sh)"/></g>'
            f'<path d="{sp}" fill="none" stroke="{LINE}" stroke-width="3.2"/>'
            f'<path d="{shield_path(-3.4)}" fill="none" stroke="{T["oro"]}" stroke-width="1.6"/></svg>')


# ---------------------------------------------------------------- cruces de órdenes
ORDER_CROSS = {
    "calatrava": ("crossFleury", T["gules"], None),
    "santiago": ("crossSantiago", T["gules"], None),
    "sanjuan": ("crossMaltese", T["plata"], None),
    "carlos3": ("crossMaltese", "#7FA6D6", None),
}


def cross(order, cls="ocross"):
    name, fill, _ = ORDER_CROSS[order]
    return (f'<svg class="{cls} {order}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Cruz de {order}">'
            f'{charge(name, 50, 50, 92, 92, fill, sw=1.2)}</svg>')


# ---------------------------------------------------------------- coronas
def coronet(rank, cls="coronet"):
    """Coronas de rango a la española, de frente (marqués, conde, barón)."""
    g, line = T["oro"], LINE
    base = (f'<path d="M8,46 Q50,40 92,46 L92,56 Q50,50 8,56 Z" fill="{g}" stroke="{line}" stroke-width="1.2"/>'
            f'<ellipse cx="30" cy="50" rx="3" ry="2.4" fill="{T["gules"]}"/><ellipse cx="50" cy="48.5" rx="3.2" ry="2.6" fill="{T["sinople"]}"/>'
            f'<ellipse cx="70" cy="50" rx="3" ry="2.4" fill="{T["gules"]}"/>')
    pearl = lambda x, y, r=3.2: f'<circle cx="{x}" cy="{y}" r="{r}" fill="{T["plata"]}" stroke="{line}" stroke-width="0.9"/>'
    leaf = lambda x, y, s=1.0: (f'<path transform="translate({x},{y}) scale({s})" d="M0,0 C-9,-4 -12,-14 -6,-20 C-4,-14 -2,-12 0,-12 '
                                f'C-3,-18 -2,-26 0,-30 C2,-26 3,-18 0,-12 C2,-12 4,-14 6,-20 C12,-14 9,-4 0,0 Z" fill="{g}" stroke="{line}" stroke-width="1"/>')
    if rank == "marques":
        top = leaf(14, 46, 0.8) + leaf(50, 43, 1.0) + leaf(86, 46, 0.8)
        top += "".join(pearl(x, y) for x, y in [(30, 40), (34, 40), (32, 35), (66, 40), (70, 40), (68, 35)])
    elif rank == "conde":
        xs = [10, 20, 30, 40, 50, 60, 70, 80, 90]
        top = "".join(f'<path d="M{x},{46 - (0 if x in (10, 90) else 1.5)} L{x},{34 - abs(50 - x) * 0.06}" stroke="{g}" stroke-width="2.2"/>' + pearl(x, 31 - abs(50 - x) * 0.06, 3.6) for x in xs)
    else:  # barón: aro con un hilo de perlas enroscado
        top = "".join(f'<path d="M{x},56 L{x + 9},44" stroke="{T["plata"]}" stroke-width="3.2" stroke-linecap="round"/>'
                      f'<path d="M{x},56 L{x + 9},44" stroke="{line}" stroke-width="0.6" stroke-dasharray="1.6 1.6"/>' for x in range(12, 88, 13))
        return f'<svg class="{cls} {rank}" viewBox="0 20 100 42" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Corona de barón">{base}{top}</svg>'
    return f'<svg class="{cls} {rank}" viewBox="0 20 100 42" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Corona de {rank}">{base}{top}</svg>'


def title_rank(text):
    t = (text or "").lower()
    if "marqu" in t:
        return "marques"
    if "conde" in t:
        return "conde"
    if "barón" in t or "baron" in t:
        return "baron"
    return ""


# ---------------------------------------------------------------- adornos
def fleuron(cls="fleuron"):
    return (f'<svg class="{cls}" viewBox="0 0 160 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">'
            f'<path d="M4,12 H62 M98,12 H156" stroke="{T["oro"]}" stroke-width="1"/>'
            f'<path d="M62,12 L70,8 L70,16 Z M98,12 L90,8 L90,16 Z" fill="{T["oro"]}"/>'
            f'{charge("fleurDeLis", 80, 12, 18, 22, T["oro"], stroke=T["oro"], sw=0.4)}</svg>')


CREDITS = ("Escudos dibujados para este libro a partir de los blasones de cada linaje. Las figuras heráldicas "
           "proceden de la biblioteca de muebles del Fantasy Map Generator (Azgaar): las sencillas, de dominio "
           "público (CC0), y el león, el lobo, el roble, la espada, los guantes y las columnas, de WappenWiki, "
           "con licencia Creative Commons BY-NC-SA 3.0.")

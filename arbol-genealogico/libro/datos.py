"""Datos del árbol (sacados de arbol.html) y utilidades comunes del libro."""
import json
import math
import re
import subprocess
from pathlib import Path

AQUI = Path(__file__).resolve().parent

_raw = subprocess.run(["node", str(AQUI / "extraer_datos.js")], check=True,
                      capture_output=True, text=True).stdout
D = json.loads(_raw)
S, P, LINE, STARS, COSTADOS, ORD = D["S"], D["P"], D["LINE"], D["STARS"], D["COSTADOS"], D["ORD"]
DUP = {int(k): v for k, v in D["DUP"].items()}


def gen(k):
    return int(math.log2(int(k))) + 1


def real(k):
    p = P.get(str(k))
    return int(p["same"]) if p and p.get("same") else int(k)


def person(k):
    return P.get(str(real(k)), {})


def side(k):
    k = int(k)
    if k < 2:
        return ""
    g = gen(k)
    base = 2 ** (g - 1)
    return "pat" if k < base * 1.5 else "mat"


def is_dup_branch(k):
    """True si k es una casilla repetida (28–29 o sus antepasados)."""
    k = int(k)
    g = gen(k)
    return g >= 5 and (k >> (g - 5)) in (28, 29)


def both_ways(k):
    """Antepasados de los Domecq–Rivero (16–17): lo son por papá y por mamá."""
    k = int(k)
    g = gen(k)
    return g >= 5 and (k >> (g - 5)) in (16, 17)


def fmt(n):
    s = str(int(n))
    if len(s) <= 4:
        return s
    out = []
    while s:
        out.insert(0, s[-3:])
        s = s[:-3]
    return ".".join(out)


ROMAN = [(10, "X"), (9, "IX"), (5, "V"), (4, "IV"), (1, "I")]


def roman(n):
    r = ""
    for v, s in ROMAN:
        while n >= v:
            r += s
            n -= v
    return r


NAMES = {2: ("padre", "madre"), 3: ("abuelo", "abuela"), 4: ("bisabuelo", "bisabuela"),
         5: ("tatarabuelo", "tatarabuela"), 6: ("trastatarabuelo", "trastatarabuela")}


def rel(k, cap=True):
    """Parentesco con los hermanos Domecq Vergara (nº 1)."""
    k = int(k)
    if k == 1:
        return "Nosotros"
    g, fem = gen(k), k % 2 == 1
    r = NAMES[g][fem] if g in NAMES else f"{g - 2}.{'ª abuela' if fem else 'º abuelo'}"
    if both_ways(k):
        r += " por las dos vías"
    elif g > 2:
        r += (" paterna" if fem else " paterno") if side(k) == "pat" else (" materna" if fem else " materno")
    return r[0].upper() + r[1:] if cap else r


# --- De «tu» a «nuestro»: las notas del árbol están escritas para Pedro;
# el libro habla en nombre de los hermanos.
_FEM = r"(?:abuela|bisabuela|tatarabuela|trastatarabuela|antepasada|línea|ascendencia|rama|madre|familia|casa|\d+\.ª abuela)"


def nos(text):
    t = str(text)
    t = re.sub(r"\b([Tt])us\s", lambda m: ("N" if m.group(1) == "T" else "n") + "uestros ", t)
    t = re.sub(r"\b([Tt])u\s(?=" + _FEM + r"\b)", lambda m: ("N" if m.group(1) == "T" else "n") + "uestra ", t)
    t = re.sub(r"\b([Tt])u\s", lambda m: ("N" if m.group(1) == "T" else "n") + "uestro ", t)
    t = re.sub(r"\btuyos\b", "nuestros", t)
    t = re.sub(r"\btuyo\b", "nuestro", t)
    t = t.replace("desciendes", "descendemos").replace("Desciendes", "Descendemos")
    t = t.replace("te llega", "nos llega")
    return t


SCRIPT_TU = re.compile(r"\b(tu|tus|tuyo|tuyos|tienes|desciendes|eres)\b", re.I)

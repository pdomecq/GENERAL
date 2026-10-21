"""Cubierta para la encuadernación en tapa dura forrada en símil piel con
grabado en oro (stamping).

Uso: python3 cubierta.py [--lomo MM]

Produce:
  De-donde-venimos-cubierta-stamping.pdf → arte final para el grabado: todo lo
      negro se graba en oro. Una sola página con contraportada + lomo + portada
      y 20 mm de margen por cada lado para forrar el cartón, como pide la
      imprenta para su producto de tapa dura en símil piel con stamping.
  De-donde-venimos-cubierta-maqueta.pdf  → la misma cubierta simulada en verde
      y oro, con las líneas de corte y de lomo, para ver cómo queda.

El lomo se calcula con el número de páginas del interior y el grosor del
papel; la imprenta da la medida exacta al hacer el pedido y basta volver a
ejecutar el script con --lomo.
"""
import argparse
import re
import subprocess
from pathlib import Path

import pymupdf

import heraldica as HR
from generar_libro import CHROMIUM, FUENTES, PDF_IMPRENTA, font_faces

AQUI = Path(__file__).resolve().parent
ANCHO, ALTO = 168.0, 240.0       # libro cortado
MARGEN = 20.0                    # para forrar el cartón
CARTON = 2.5                     # grosor de cada tapa
HOJA = 0.135                     # estucado mate de 150 g, en mm por hoja
VERDE, ORO = "#21392F", "#C9A54A"


def lomo_estimado():
    paginas = pymupdf.open(PDF_IMPRENTA).page_count
    return round(paginas / 2 * HOJA + 2 * CARTON + 0.5, 1), paginas


def escudo_grabado():
    """Las armas de los cuatro costados en línea, a una sola tinta."""
    svg = HR.costados("stamp")
    svg = re.sub(r'fill="(?!none)[^"]*"', 'fill="none"', svg)
    svg = re.sub(r'stroke="(?!none)[^"]*"', 'stroke="currentColor"', svg)
    style = "<style>*{vector-effect:non-scaling-stroke;stroke-width:1.15px;stroke-linejoin:round}</style>"
    return svg.replace("<defs>", style + "<defs>", 1)


def html(lomo, maqueta):
    W = 2 * MARGEN + 2 * ANCHO + lomo
    H = 2 * MARGEN + ALTO
    tinta = ORO if maqueta else "#000"
    fondo = VERDE if maqueta else "#fff"
    x_lomo = MARGEN + ANCHO
    x_port = x_lomo + lomo
    guias = ""
    if maqueta:
        guias = f"""<div class="guia" style="left:{MARGEN}mm;top:{MARGEN}mm;width:{2 * ANCHO + lomo}mm;height:{ALTO}mm"></div>
<div class="guia" style="left:{x_lomo}mm;top:{MARGEN}mm;width:{lomo}mm;height:{ALTO}mm"></div>
<p class="nota" style="left:{MARGEN}mm;top:{H - MARGEN + 4}mm">Contraportada · lomo de {lomo} mm · portada. La línea discontinua es el borde de la tapa; lo de fuera se dobla hacia dentro.</p>"""
    lis = HR.charge("fleurDeLis", 100, 100, 160, 200, "currentColor", stroke="currentColor", sw=0.6)
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><style>
{font_faces()}
@page{{size:{W}mm {H}mm;margin:0}}
html,body{{margin:0;background:{fondo}}}
body{{width:{W}mm;height:{H}mm;position:relative;color:{tinta};overflow:hidden}}
.a{{position:absolute}}
.marco{{border:.5mm solid {tinta};box-sizing:border-box}}
.marco2{{border:.25mm solid {tinta};box-sizing:border-box}}
.c{{text-align:center;left:{x_port}mm;width:{ANCHO}mm}}
.t{{font-family:'IM Fell English';font-size:31pt;line-height:1}}
.s{{font-family:'Alegreya';font-style:italic;font-size:12.5pt}}
.y{{font-family:'Alegreya Sans SC';font-weight:500;font-size:10pt;letter-spacing:.32em}}
.fl svg{{width:40mm;height:6mm;display:block;margin:0 auto}}
.fl svg *{{fill:currentColor;stroke:currentColor}}
.es svg{{width:48mm;height:auto;display:block;margin:0 auto;color:{tinta}}}
.lomo{{left:{x_lomo}mm;top:{MARGEN}mm;width:{lomo}mm;height:{ALTO}mm;display:flex;align-items:center;justify-content:center}}
.lomo p{{writing-mode:vertical-rl;font-family:'IM Fell English';font-size:10.5pt;letter-spacing:.14em;white-space:nowrap;margin:0}}
.lomo small{{font-family:'Alegreya Sans SC';font-weight:500;font-size:7.5pt;letter-spacing:.2em}}
.lis svg{{width:5mm;height:6mm;display:block}}
.guia{{position:absolute;border:.3mm dashed #E8E2CF;box-sizing:border-box}}
.nota{{position:absolute;margin:0;font-family:'Alegreya Sans';font-size:9pt;color:#E8E2CF}}
</style></head><body>
<div class="a marco" style="left:{x_port + 10}mm;top:{MARGEN + 10}mm;width:{ANCHO - 20}mm;height:{ALTO - 20}mm"></div>
<div class="a marco2" style="left:{x_port + 12.2}mm;top:{MARGEN + 12.2}mm;width:{ANCHO - 24.4}mm;height:{ALTO - 24.4}mm"></div>
<p class="a c t" style="top:{MARGEN + 42}mm;margin:0">De dónde venimos</p>
<div class="a c fl" style="top:{MARGEN + 57}mm">{HR.fleuron()}</div>
<p class="a c s" style="top:{MARGEN + 67}mm;margin:0">Linaje y armas de los Domecq Vergara</p>
<div class="a c es" style="top:{MARGEN + 88}mm">{escudo_grabado()}</div>
<p class="a c y" style="top:{MARGEN + 190}mm;margin:0">1264 · 2026</p>
<div class="a lomo"><p>DE DÓNDE VENIMOS&nbsp;&nbsp;·&nbsp;&nbsp;<small>Domecq Vergara</small></p></div>
<div class="a lis" style="left:{x_lomo + lomo / 2 - 2.5}mm;top:{MARGEN + 14}mm"><svg viewBox="0 0 200 240">{lis}</svg></div>
<div class="a lis" style="left:{x_lomo + lomo / 2 - 2.5}mm;top:{MARGEN + ALTO - 20}mm"><svg viewBox="0 0 200 240">{lis}</svg></div>
{guias}
</body></html>"""


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lomo", type=float, help="grosor del lomo en mm (por defecto, estimado)")
    a = ap.parse_args()
    lomo, paginas = lomo_estimado()
    if a.lomo:
        lomo = a.lomo
    for nombre, maqueta in (("stamping", False), ("maqueta", True)):
        h = AQUI / f"cubierta-{nombre}.html"
        pdf = AQUI / f"De-donde-venimos-cubierta-{nombre}.pdf"
        h.write_text(html(lomo, maqueta), encoding="utf-8")
        subprocess.run([CHROMIUM, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                        "--virtual-time-budget=10000", f"--print-to-pdf={pdf}", h.as_uri()],
                       check=True, capture_output=True, timeout=120)
        h.unlink()
    print(f"Cubierta: {paginas} páginas, lomo {lomo} mm, pliego {2 * MARGEN + 2 * ANCHO + lomo} × {2 * MARGEN + ALTO} mm")


if __name__ == "__main__":
    main()

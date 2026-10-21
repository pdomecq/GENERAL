"""Genera el libro «De dónde venimos» a partir de los datos de arbol.html.

Produce:
  libro_impresion.html          → la versión que se imprime (fuentes locales)
  De-donde-venimos-imprenta.pdf → el interior para la imprenta: 168 × 240 mm
                                  con 3 mm de sangrado (Chromium headless)
  De-donde-venimos.pdf          → el mismo PDF recortado a 168 × 240, para leer
  libro.html                    → la versión para leer en pantalla y publicar

Uso: python3 generar_libro.py
Requiere node (para leer arbol.html), Chromium y PyMuPDF (pip install pymupdf).
Si Chromium no está en el PATH, indica su ruta con la variable CHROMIUM.
"""
import os
import re
import shutil
import subprocess
from pathlib import Path

import pymupdf

import capitulos as C

AQUI = Path(__file__).resolve().parent
FUENTES = AQUI / "fuentes"
CHROMIUM = (os.environ.get("CHROMIUM") or shutil.which("chromium") or shutil.which("chromium-browser")
            or shutil.which("google-chrome") or "/opt/pw-browsers/chromium")
PDF = AQUI / "De-donde-venimos.pdf"
PDF_IMPRENTA = AQUI / "De-donde-venimos-imprenta.pdf"
CORTE = (168 / 25.4 * 72, 240 / 25.4 * 72)  # 168 × 240 mm en puntos
TITULO = "De dónde venimos"

TOKENS = """
  /* Libro A4 a una columna centrada; árboles a todo el ancho de la caja. */
  :root{
    --paper:#FFFFFF; --ink:#1B2130; --muted:#5A6170; --line:#BFC3CA; --soft:#EEF0EC;
    --pat:#2E5E4E; --mat:#94580F; --dup:#8C2F39;
    --pat-t:#DCE8E3; --mat-t:#F3E6D3; --dup-t:#F1E0E2; --unk-t:#F3F4F1; --self-t:#E6E8E3;
    --display:'IM Fell English', 'Iowan Old Style', Georgia, serif;
    --body:'Alegreya', Georgia, 'Times New Roman', serif;
    --sans:'Alegreya Sans', 'Gill Sans', 'Segoe UI', sans-serif;
    --sc:'Alegreya Sans SC', 'Alegreya Sans', 'Gill Sans', sans-serif;
  }
"""

DARK = """
  @media screen and (prefers-color-scheme: dark){
    :root:not([data-theme="light"]){
      color-scheme:dark;
      --paper:#12161C; --ink:#E6E8EC; --muted:#9CA3B0; --line:#3A4250; --soft:#1C222B;
      --pat:#7DBBA5; --mat:#E0A862; --dup:#E68C97;
      --pat-t:#1E3A31; --mat-t:#3D2E19; --dup-t:#3E2227; --unk-t:#191E26; --self-t:#232A35;
    }
  }
  :root[data-theme="dark"]{
    color-scheme:dark;
    --paper:#12161C; --ink:#E6E8EC; --muted:#9CA3B0; --line:#3A4250; --soft:#1C222B;
    --pat:#7DBBA5; --mat:#E0A862; --dup:#E68C97;
    --pat-t:#1E3A31; --mat-t:#3D2E19; --dup-t:#3E2227; --unk-t:#191E26; --self-t:#232A35;
  }
"""

BASE_CSS = """
  html,body{background:var(--paper)}
  body{margin:0;background:var(--paper);color:var(--ink);font-family:var(--body);font-size:10.5pt;line-height:1.48;
       font-variant-numeric:oldstyle-nums proportional-nums;text-rendering:optimizeLegibility}
  h1,h2,h3,h4{margin:0;font-weight:400;text-wrap:balance}
  p{margin:0}
  b{font-weight:700}
  .num,.k,.yr,.when,.ix-k,.toc-p{font-variant-numeric:lining-nums tabular-nums}

  /* ---- prosa */
  .prose{max-width:128mm;margin:0 auto}
  .prose p + p{text-indent:5mm}
  .prose h2{font-family:var(--display);font-size:16pt;line-height:1.15;margin:7mm 0 2.2mm}
  .prose h2 + p{text-indent:0}
  .lead{font-size:11.6pt;line-height:1.45;margin-bottom:2.5mm}
  .chapter > .prose:first-of-type .lead::first-letter,
  .rama .lead::first-letter{initial-letter:3;font-family:var(--display);color:var(--dup);margin-right:1.6mm}
  .small{font-size:9pt;color:var(--muted);margin-top:3mm}
  .prose ul,.prose ol{margin:2mm 0 2mm 5mm;padding:0}
  .prose li{margin:1.2mm 0}
  .marks{list-style:none;margin-left:0 !important}
  .mk{font-family:var(--sans);font-weight:700}
  .mk.ok{color:var(--ink)} .mk.tree{color:var(--muted)} .mk.ded{color:var(--muted)} .mk.doubt{color:var(--dup)} .mk.none{color:var(--line)}

  /* ---- cabecera de capítulo */
  .ch-head{padding-top:26mm;margin-bottom:10mm;max-width:128mm;margin-inline:auto}
  .ch-num{font-family:var(--sc);font-weight:500;font-size:10pt;letter-spacing:.14em;color:var(--dup)}
  .ch-head h1{font-family:var(--display);font-size:31pt;line-height:1.05;margin-top:3mm}
  .ch-head svg.fleuron{display:block;width:44mm;height:auto;margin:4mm 0 0 -1mm}

  /* ---- ramas */
  .rama-title{font-family:var(--display);font-size:22pt;line-height:1.1;max-width:128mm;margin:0 auto 6mm}
  .cards-title{font-family:var(--sc);font-weight:500;font-size:9.5pt;letter-spacing:.12em;color:var(--muted);margin:8mm 0 2mm}

  /* ---- fichas */
  .cards{display:flex;flex-direction:column}
  .card{display:grid;grid-template-columns:31mm minmax(0,1fr);column-gap:5mm;padding:2.1mm 0 2.3mm;border-top:.4pt solid var(--line);break-inside:avoid}
  .keep{break-inside:avoid}
  .card-k{display:flex;flex-direction:column;gap:.4mm;font-family:var(--sans);font-size:8pt;line-height:1.25;color:var(--muted)}
  .card-k .num{font-weight:700;font-size:9pt;color:var(--ink)}
  .card.pat .card-k .num{color:var(--pat)} .card.mat .card-k .num{color:var(--mat)}
  .card-b h4{font-family:var(--body);font-weight:700;font-size:10.5pt;line-height:1.25}
  .card-b .meta{font-style:italic;color:var(--muted);font-size:9.2pt;margin-top:.4mm}
  .card-b p{font-size:9.6pt;line-height:1.42;margin-top:.8mm}

  /* ---- figuras y gráficos */
  .fig{margin:7mm 0;break-inside:avoid}
  .fig-art{display:flex;justify-content:center}
  .fig figcaption{font-style:italic;font-size:8.6pt;color:var(--muted);text-align:center;margin-top:2mm}
  .chart-title{font-family:var(--display);font-size:16pt;text-align:center;margin-bottom:2mm}
  .chart-note{font-size:8.8pt;color:var(--muted);text-align:center;max-width:150mm;margin:0 auto 3mm}
  .legend{display:flex;flex-wrap:wrap;justify-content:center;gap:2mm 6mm;font-family:var(--sans);font-size:8pt;color:var(--muted);margin-bottom:3mm}
  .legend span{display:inline-flex;align-items:center;gap:1.6mm}
  .sw{display:inline-block;width:6mm;height:2.6mm;border:.6pt solid var(--line);border-radius:.6mm}
  .sw.pat{border-color:var(--pat)} .sw.mat{border-color:var(--mat)} .sw.dashed{border-style:dashed;border-color:var(--ink)} .sw.doubt{border-style:dashed;border-color:var(--dup)}
  svg.chart text{font-family:var(--body);fill:var(--ink)}
  svg .link{fill:none;stroke:var(--line);stroke-width:.3}
  svg .box{fill:var(--paper);stroke:var(--line);stroke-width:.3}
  svg .box.pat{stroke:var(--pat)} svg .box.mat{stroke:var(--mat)} svg .box.self{stroke:var(--ink)}
  svg .box.ded{stroke-dasharray:1 .6} svg .box.doubt{stroke:var(--dup);stroke-dasharray:1 .6} svg .box.dupbox{stroke:var(--dup)}
  svg .bnum{font-family:var(--sans) !important;fill:var(--muted) !important}
  svg .bnum.pat{fill:var(--pat) !important} svg .bnum.mat{fill:var(--mat) !important}
  svg .bname{font-weight:700}
  svg .bdate{fill:var(--muted) !important}
  svg .rel{font-family:var(--sans) !important;fill:var(--dup) !important}
  svg .seg{stroke:var(--paper);stroke-width:.35}
  svg .seg.pat{fill:var(--pat-t)} svg .seg.mat{fill:var(--mat-t)} svg .seg.self{fill:var(--self-t)}
  svg .seg.unk{fill:var(--unk-t)} svg .seg.dupseg{fill:var(--dup-t)} svg .seg.doubtseg{fill:none}
  svg .seg.ded{fill-opacity:.55}
  svg .hatchbg{fill:var(--dup-t)} svg .hatchln{stroke:var(--dup);stroke-width:.25}
  svg .fdate{fill:var(--muted) !important} svg .fdup{fill:var(--dup) !important;font-family:var(--sans) !important}
  svg .fgen{fill:var(--muted) !important;font-family:var(--sans) !important}
  svg .fside{font-family:var(--sc) !important;letter-spacing:.08em} svg .fside.pat{fill:var(--pat) !important} svg .fside.mat{fill:var(--mat) !important}
  svg.deco .seg{stroke-width:.5}

  /* ---- dieciséis apellidos */
  .surnames{display:grid;grid-template-columns:repeat(8,minmax(0,1fr));border-top:.4pt solid var(--line);border-left:.4pt solid var(--line);margin:4mm 0 2mm}
  .sn{display:flex;flex-direction:column;gap:.6mm;padding:2mm 2mm 2.4mm;border-right:.4pt solid var(--line);border-bottom:.4pt solid var(--line);min-height:20mm}
  .sn .k{font-family:var(--sans);font-size:7.5pt;font-weight:700}
  .sn.pat .k{color:var(--pat)} .sn.mat .k{color:var(--mat)}
  .sn b{font-family:var(--display);font-weight:400;font-size:12pt;line-height:1.05}
  .sn.dup b{color:var(--dup)}
  .sn small{font-size:7.2pt;line-height:1.25;color:var(--muted)}

  /* ---- línea más antigua */
  .line{list-style:none;margin:6mm 0 0;padding:0}
  .line > li{display:grid;grid-template-columns:20mm 6mm minmax(0,1fr);column-gap:3mm;break-inside:avoid}
  .line .yr{text-align:right;font-family:var(--sans);font-size:8.5pt;color:var(--muted);padding-top:1mm}
  .line .rail{position:relative;display:flex;justify-content:center}
  .line .rail::before{content:"";position:absolute;top:0;bottom:0;left:50%;border-left:.6pt solid var(--line)}
  .line li.weak .rail::before{border-left-style:dashed}
  .line .rail .mk{position:relative;background:var(--paper);font-size:9pt;line-height:1;padding:.6mm 0;margin-top:.6mm}
  .line .lb{padding:0 0 4mm}
  .line .gl{font-family:var(--sc);font-weight:500;font-size:8pt;letter-spacing:.06em;color:var(--muted)}
  .line .who{font-size:10.5pt;line-height:1.3}
  .line .x{color:var(--muted)}
  .line .tx{font-size:9.6pt;line-height:1.42;color:var(--ink);margin-top:.6mm}
  .line li.era .eralabel{font-family:var(--display);font-style:italic;font-size:13pt;color:var(--muted);padding:2mm 0 3mm}

  /* ---- tablas */
  table{border-collapse:collapse;width:100%;font-size:9.4pt;line-height:1.4;margin:5mm 0}
  th,td{text-align:left;vertical-align:top;padding:2mm 2.5mm 2mm 0;border-top:.4pt solid var(--line)}
  thead th{font-family:var(--sc);font-weight:500;font-size:8pt;letter-spacing:.08em;color:var(--muted);border-top:none}
  tbody th{font-weight:700;width:42mm}
  td.when{white-space:nowrap;font-family:var(--sans);font-size:8.6pt;color:var(--muted);width:28mm}
  tr{break-inside:avoid}
  table.costados td.st{white-space:nowrap;font-family:var(--sans);font-size:8.6pt}
  table.costados tr.doubt td.st{color:var(--dup)}
  table.crono th{width:14mm;font-family:var(--sans);font-weight:700;font-size:9pt;color:var(--dup)}
  table.crono td,table.crono th{padding-top:.95mm;padding-bottom:.95mm}
  table.cuantos{max-width:136mm;margin:3mm auto 4mm}
  table.cuantos th,table.cuantos td{padding-top:1.05mm;padding-bottom:1.05mm}
  table.cuantos tbody th{width:20mm;font-family:var(--sans);font-size:8.8pt;color:var(--dup)}
  table.cuantos .num{text-align:right;font-variant-numeric:tabular-nums;padding-right:0;padding-left:4mm;white-space:nowrap}
  table.cuantos thead th.num{text-align:right}

  /* ---- órdenes */
  .ords{max-width:128mm;margin:4mm auto;padding-left:0;font-size:9.8pt;list-style:none}
  .ords li{margin:2.2mm 0;display:flex;gap:3.5mm;align-items:flex-start}
  .ocross-l{flex:none;width:7mm;height:7mm} .ocross-l svg{width:7mm;height:7mm;display:block}

  /* ---- heráldica */
  svg.arms{display:block;width:100%;height:auto}
  .ico{display:inline-block;vertical-align:-.1em;margin-left:1.4mm}
  .ico svg.ocross{width:3.4mm;height:3.4mm;display:block}
  .ico svg.coronet{width:6.4mm;height:2.7mm;display:block}
  .prose .ico{margin:0 .6mm}
  .tcrown{display:block;width:11mm;margin-bottom:1mm} .tcrown svg{width:11mm;height:auto;display:block}
  .rama-head{display:flex;align-items:flex-end;justify-content:space-between;gap:8mm;max-width:128mm;margin:0 auto 6mm}
  .rama-head .rama-title{margin:0;flex:1 1 auto}
  .rama-arms{flex:none;width:27mm;margin:0;text-align:center}
  .rama-arms figcaption{font-family:var(--sc);font-weight:500;font-size:7pt;letter-spacing:.08em;color:var(--muted);margin-top:1.2mm}
  .armorial{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7mm 9mm;margin:7mm auto 6mm;max-width:150mm;break-inside:avoid}
  .armorial figure{margin:0;text-align:center}
  .armorial figcaption{font-family:var(--display);font-size:11pt;margin-top:1.6mm}
  .costados-arms{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:7mm;margin:5mm auto 6mm;max-width:128mm;break-inside:avoid}
  .costados-arms figure{margin:0;text-align:center}
  .costados-arms figcaption{font-size:8.4pt;line-height:1.3;margin-top:1.6mm;color:var(--muted)}
  .costados-arms b{color:var(--ink);font-family:var(--display);font-size:11.5pt;font-weight:400}
  .map-fig .fig-art svg.map{width:100%;max-width:132mm;height:auto;display:block;margin:0 auto}
  .photos{display:flex;flex-wrap:wrap;justify-content:center;align-items:flex-start;gap:5mm 7mm;margin:6mm auto 7mm;max-width:150mm;break-inside:avoid}
  .ph{display:table;margin:0;break-inside:avoid}
  .ph img{display:block;height:48mm;width:auto;border:.5pt solid var(--line);padding:1.5mm;background:#fff}
  .ph figcaption{display:table-caption;caption-side:bottom;font-style:italic;font-size:8.2pt;line-height:1.32;color:var(--muted);text-align:center;padding-top:1.8mm}
  .ph.wide img{height:auto;width:118mm;max-width:100%}
  .photos.kings{gap:4mm 5mm}
  .photos.kings .ph img{height:34mm}
  .photos.kings .ph figcaption{font-size:7.8pt}
  .photos.mixed .ph img{height:44mm}
  .star-ph{float:left;display:flex;gap:1.5mm;margin:.6mm 3.2mm 1.4mm 0}
  .star-ph img{display:block;height:31mm;width:auto;border:.5pt solid var(--line);padding:1mm;background:#fff}
  .star-ph.n2 img{height:27mm}
  .star::after{content:"";display:block;clear:both}
  .roncal-fig img{display:block;width:72mm;height:auto;margin:0 auto;border:.6pt solid var(--line);padding:2.5mm;background:#fff}
  .plate{text-align:center}
  .plate-art svg{width:92mm;height:auto;margin:0 auto}
  .plate-title{font-family:var(--display);font-size:20pt;font-weight:400;margin:9mm 0 4mm}
  .plate-text{max-width:122mm;margin:0 auto;font-size:9.8pt;line-height:1.5;text-align:justify;hyphens:auto}
  .plate-note{max-width:122mm;margin:4mm auto 0;font-size:9pt;font-style:italic;color:var(--muted)}
  .credits h2{margin-top:8mm}
  .credits p{font-size:8.8pt;color:var(--muted)}

  /* ---- personajes */
  .stars{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:4mm 6mm;margin-top:4mm}
  .star{border-top:.8pt solid var(--ink);padding-top:2.4mm;break-inside:avoid}
  .star-g{font-family:var(--sc);font-weight:500;font-size:7.8pt;letter-spacing:.08em;color:var(--dup)}
  .star h3{font-family:var(--display);font-size:13.5pt;line-height:1.1;margin:.8mm 0 .6mm}
  .star-rel{font-family:var(--sans);font-size:8pt;color:var(--muted);margin-bottom:1.2mm}
  .star p:last-child{font-size:9.2pt;line-height:1.42}

  /* ---- apellidos */
  .apellidos{columns:2;column-gap:8mm;margin-top:4mm}
  .ap{break-inside:avoid;padding:2.2mm 0 2.6mm;border-top:.4pt solid var(--line)}
  .ap h3{font-family:var(--display);font-size:13pt;line-height:1.1;margin-bottom:.8mm}
  .ap p{font-size:9.2pt;line-height:1.4}
  .ap .blazon{margin-top:1.2mm;padding:1.4mm 2mm;background:var(--soft);font-style:italic}
  .ap .blazon span{font-style:normal;font-family:var(--sc);font-weight:500;font-size:7.8pt;letter-spacing:.08em;color:var(--dup)}
  .ap-k{font-family:var(--sans);font-size:7.6pt;color:var(--muted);margin-top:.8mm}

  /* ---- índice de antepasados */
  .index{columns:2;column-gap:8mm;margin-top:4mm}
  .ix-g{break-inside:auto}
  .ix-g h3{font-family:var(--sc);font-weight:500;font-size:8.6pt;letter-spacing:.08em;color:var(--dup);margin:3mm 0 1mm;break-after:avoid}
  .ix-g ul{list-style:none;margin:0;padding:0}
  .ix-g li{font-size:8.4pt;line-height:1.35;padding:.5mm 0;break-inside:avoid;text-indent:-9mm;padding-left:9mm}
  .ix-k{display:inline-block;width:8mm;text-indent:0;font-family:var(--sans);font-weight:700;font-size:7.6pt}
  .ix-g li.pat .ix-k{color:var(--pat)} .ix-g li.mat .ix-k{color:var(--mat)}
  .ix-m{color:var(--muted);font-style:italic}

  /* ---- fuentes */
  .sources{columns:2;column-gap:8mm;list-style:none;margin:4mm 0 0;padding:0;font-size:7.8pt;line-height:1.3}
  .sources li{break-inside:avoid;padding:.9mm 0}
  .sources .url{font-family:var(--sans);font-size:6.6pt;color:var(--muted);word-break:break-all}

  /* ---- índice general */
  .toc h1{font-family:var(--display);font-size:28pt;margin:22mm 0 8mm;max-width:128mm;margin-inline:auto}
  .toc-list{list-style:none;margin:0 auto;padding:0;max-width:128mm}
  .toc-list li{display:flex;align-items:baseline;gap:2mm}
  .toc-ch{font-size:11.5pt;margin-top:2.4mm}
  .toc-sec{font-size:9.6pt;padding-left:10mm;color:var(--ink)}
  .toc-l{min-width:8mm;font-family:var(--sans);font-size:8.6pt;color:var(--dup);font-weight:700}
  .toc-sec .toc-l{display:none}
  .toc-t{flex:0 1 auto}
  .toc-list li::after{content:"";order:2;flex:1 1 auto;border-bottom:.6pt dotted var(--line);transform:translateY(-1mm)}
  .toc-p{order:3;font-family:var(--sans);font-size:9pt}

  /* ---- páginas para completar */
  .wi{max-width:128mm;margin:6mm auto 0}
  .wi h3{font-family:var(--display);font-size:13pt;margin-bottom:1mm}
  .wline{height:8mm;border-bottom:.4pt solid var(--line)}
  .fillbox{break-inside:avoid;margin-top:9mm;padding:4mm 6mm 5mm;border:.6pt solid var(--line);border-radius:1.5mm}
  .fillbox h3{font-family:var(--display);font-size:13pt;margin-bottom:1.5mm}
  .fillbox p{font-size:9.4pt;line-height:1.42;color:var(--muted)}
  .fillrow{display:flex;align-items:flex-end;gap:3mm;margin-top:3.2mm}
  .fillrow span:first-child{width:32mm;flex:none;font-family:var(--sans);font-size:8.6pt;color:var(--muted)}
  .fillrow .fl{flex:1;height:6mm;border-bottom:.4pt solid var(--line)}
  .colophon{max-width:110mm;margin:0 auto;text-align:center;font-size:9pt;color:var(--muted);font-style:italic}
  .colophon p + p{margin-top:2mm}

  /* ---- portada y páginas de cortesía */
  .cover{text-align:center}
  .cover-kicker{font-family:var(--sc);font-weight:500;letter-spacing:.16em;font-size:10pt;color:var(--muted)}
  .cover-title{font-family:var(--display);font-size:46pt;line-height:1;margin-top:6mm}
  .cover-sub{font-style:italic;font-size:16pt;margin-top:4mm}
  .cover-years{font-family:var(--sans);letter-spacing:.3em;font-size:10pt;color:var(--dup)}
  .cover-foot{font-size:10pt;color:var(--muted);line-height:1.5}
  .colophon-front p{font-size:9pt;color:var(--muted);max-width:110mm;margin:0 auto 2mm}
  .dedication p{font-family:var(--display);font-style:italic;font-size:16pt;text-align:center;line-height:1.5}
"""

# Edición encuadernada: 168 × 240 mm a sangre (3 mm por lado), así que cada
# página del PDF mide 174 × 246 mm. Los márgenes se cuentan desde el borde del
# PDF: 3 mm de sangrado más el margen real del libro (17 arriba, 22 abajo,
# 19 al lomo y 15 al corte). La caja de texto queda en 134 × 201 mm.
PRINT_CSS = """
  @page{size:174mm 246mm;margin:20mm 18mm 25mm 22mm}
  @page :right{margin-left:22mm;margin-right:18mm;
    @bottom-right{content:counter(page);font-family:'Alegreya Sans';font-size:8.5pt;color:#5A6170}
    @bottom-left{content:"De dónde venimos";font-family:'Alegreya Sans SC';font-size:7.5pt;letter-spacing:.12em;color:#8A909B}}
  @page :left{margin-left:18mm;margin-right:22mm;
    @bottom-left{content:counter(page);font-family:'Alegreya Sans';font-size:8.5pt;color:#5A6170}
    @bottom-right{content:"Los Domecq Vergara";font-family:'Alegreya Sans SC';font-size:7.5pt;letter-spacing:.12em;color:#8A909B}}
  @page cover:right{margin:0;@bottom-right{content:none} @bottom-left{content:none}}
  @page cover:left{margin:0;@bottom-right{content:none} @bottom-left{content:none}}
  @page plain:right{@bottom-right{content:none} @bottom-left{content:none}}
  @page plain:left{@bottom-right{content:none} @bottom-left{content:none}}
  @page blank:right{@bottom-right{content:none} @bottom-left{content:none}}
  @page blank:left{@bottom-right{content:none} @bottom-left{content:none}}
  @page chart:right{margin:16mm 16mm 22mm 18mm}
  @page chart:left{margin:16mm 18mm 22mm 16mm}
  .blank-page{page:blank;break-before:page;height:1mm}
  .halftitle{page:plain;padding-top:52mm;text-align:center}
  .halftitle h1{font-family:var(--display);font-size:24pt;font-weight:400}
  .halftitle svg.fleuron{display:block;width:36mm;height:5.4mm;margin:4mm auto 0}
  .cover{page:cover;break-before:page;height:246mm;display:flex}
  .cover-frame{margin:17mm 18mm 17mm 22mm;flex:1;border:.8pt solid #2E5E4E;outline:.4pt solid #2E5E4E;outline-offset:-2.4mm;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:0;padding:12mm 10mm}
  .cover-title{font-size:38pt}
  .cover-sub{font-size:14pt}
  .cover-art{margin:10mm 0 9mm} .cover-art svg{width:66mm;height:auto}
  .cover-foot{margin-top:10mm}
  .front{page:plain;break-before:page}
  .colophon-front{display:flex;flex-direction:column;justify-content:flex-end;height:201mm}
  .plate{page:plain;break-before:page;display:flex;flex-direction:column;justify-content:center;height:201mm}
  .plate-art svg{width:74mm}
  .plate-title{font-size:18pt;margin:7mm 0 3mm}
  .dedication{display:flex;flex-direction:column;justify-content:center;height:150mm}
  .toc{page:plain}
  .toc h1{margin-top:14mm}
  .chapter{break-before:page}
  .ch-head{padding-top:16mm;margin-bottom:8mm}
  .ch-head h1{font-size:27pt}
  .rama{break-before:page}
  .rama:first-of-type{break-before:auto}
  .rama-title{font-size:20pt}
  .rama-arms{width:24mm}
  .fullpage{break-before:page;break-after:page}
  .chartpage{page:chart}
  .chartpage svg{display:block;margin:0 auto;width:auto;height:184mm;max-width:100%}
  .fanpage{page:chart;position:relative;height:208mm;overflow:hidden}
  .fanpage .landscape{position:absolute;width:208mm;height:140mm;left:calc(50% - 104mm);top:calc(50% - 70mm);transform:rotate(-90deg);display:flex;flex-direction:column;align-items:center}
  .fanpage .landscape svg{width:208mm;height:auto}
  .fanpage .chart-title{margin:0 0 1.5mm}
  .fanpage .chart-note{max-width:190mm;margin:0 auto 3mm;text-align:center}
  .fig-art svg{max-width:100%;height:auto}
  .surnames{grid-template-columns:repeat(4,minmax(0,1fr))}
  .photos{max-width:134mm;gap:4mm 6mm}
  .ph img{height:42mm}
  .ph.wide img{width:112mm}
  .photos.kings{gap:3mm 4mm}
  .photos.kings .ph img{height:29mm}
  .photos.mixed .ph img{height:38mm}
  .star-ph img{height:28mm} .star-ph.n2 img{height:24mm}
  .armorial{max-width:134mm;gap:6mm 7mm}
  table.cuantos{max-width:134mm}
  .colophon{page:plain;break-before:page;height:201mm;display:flex;flex-direction:column;justify-content:flex-end}
  .writein{page:plain}
  .wi-page{break-before:page;padding-top:4mm}
  .wi{margin-top:5mm} .wline{height:7mm}
  .notes{page:plain;break-before:page;max-width:128mm;margin:0 auto;padding-top:4mm}
  .notes h3{font-family:var(--display);font-size:13pt;font-weight:400;margin-bottom:1mm}
  a{color:inherit;text-decoration:none}
"""

SCREEN_CSS = """
  @media screen{
    body{font-size:17px}
    .book{max-width:860px;margin:0 auto;padding-inline:20px;padding-block:24px 80px}
    .topbar{display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:12px;padding:10px 0 18px;border-bottom:1px solid var(--line);margin-bottom:24px}
    .topbar .tb-t{font-family:var(--sc);letter-spacing:.12em;font-size:13px;color:var(--muted)}
    .topbar .tb-r{display:flex;align-items:center;gap:12px}
    #dl{font:inherit;font-family:var(--sans);font-size:15px;padding:8px 14px;border-radius:4px;border:1px solid var(--pat);background:var(--pat);color:var(--paper);cursor:pointer}
    #dl:hover{filter:brightness(1.08)} #dl:disabled{opacity:.6;cursor:default}
    #dl:focus-visible{outline:2px solid var(--dup);outline-offset:2px}
    #dlmsg{font-family:var(--sans);font-size:14px;color:var(--muted)}
    .cover{padding:40px 0 30px;border-bottom:1px solid var(--line)}
    .cover-frame{display:flex;flex-direction:column;align-items:center;gap:10px}
    .cover-art svg{width:min(70%,280px);height:auto;margin:0 auto}
    .plate{padding:36px 0;border-bottom:1px solid var(--line)} .plate-art svg{width:min(60%,240px)}
    .armorial,.costados-arms{grid-template-columns:repeat(2,minmax(0,1fr))}
    .rama-arms{width:90px}
    .front,.toc,.chapter,.colophon{padding-top:36px}
    .colophon-front{display:none}
    .dedication{padding:30px 0;border-bottom:1px solid var(--line)}
    .toc-p{display:none}
    .toc-list li::after{display:none}
    .ch-head{padding-top:28px}
    .prose{max-width:38em}
    .rama{margin-top:48px}
    .fig-art,.chartpage,.fanpage{overflow-x:auto}
    .fig-art svg,.chartpage svg{min-width:620px;max-width:100%;height:auto}
    .chartpage svg{width:100%}
    .fanpage svg{width:100%;min-width:640px;height:auto}
    .card{grid-template-columns:7.5em minmax(0,1fr)}
    .surnames{grid-template-columns:repeat(4,minmax(0,1fr))}
    .stars{grid-template-columns:1fr}
    .apellidos,.index,.sources{columns:1}
    .sources .url{word-break:break-all}
    .wi,.writein,.fillbox,.print-only,.blank-page,.notes{display:none}
    table{display:block;overflow-x:auto}
  }
  @media screen and (min-width:700px){
    .stars{grid-template-columns:repeat(2,minmax(0,1fr))}
    .apellidos,.index,.sources{columns:2}
    .surnames{grid-template-columns:repeat(8,minmax(0,1fr))}
    .armorial,.costados-arms{grid-template-columns:repeat(4,minmax(0,1fr))}
  }
  @media screen and (max-width:560px){
    body{font-size:16px}
    .ch-head h1{font-size:30px}
    .prose p + p{text-indent:0;margin-top:.7em}
  }
"""


def font_faces():
    faces = [("Alegreya", 400, "normal", "alegreya-latin-400-normal"), ("Alegreya", 400, "italic", "alegreya-latin-400-italic"),
             ("Alegreya", 500, "normal", "alegreya-latin-500-normal"), ("Alegreya", 700, "normal", "alegreya-latin-700-normal"),
             ("Alegreya", 700, "italic", "alegreya-latin-700-italic"), ("Alegreya Sans", 400, "normal", "alegreya-sans-latin-400-normal"),
             ("Alegreya Sans", 500, "normal", "alegreya-sans-latin-500-normal"), ("Alegreya Sans", 700, "normal", "alegreya-sans-latin-700-normal"),
             ("Alegreya Sans SC", 500, "normal", "alegreya-sans-sc-latin-500-normal"), ("Alegreya Sans SC", 700, "normal", "alegreya-sans-sc-latin-700-normal"),
             ("IM Fell English", 400, "normal", "im-fell-english-latin-400-normal"), ("IM Fell English", 400, "italic", "im-fell-english-latin-400-italic")]
    return "\n".join(f"@font-face{{font-family:'{f}';font-weight:{w};font-style:{s};src:url('{(FUENTES / (n + '.woff2')).as_uri()}') format('woff2')}}" for f, w, s, n in faces)


def page(body, web=False):
    if web:
        head = f"""<title>{TITULO}</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,400;0,500;0,700;1,400;1,700&family=Alegreya+Sans:wght@400;500;700&family=Alegreya+Sans+SC:wght@500;700&family=IM+Fell+English:ital@0;1&display=swap" rel="stylesheet">
<style>{TOKENS}{DARK}{BASE_CSS}{SCREEN_CSS}</style>"""
        top = """<div class="topbar"><span class="tb-t">Libro de familia · Domecq Vergara</span>
<span class="tb-r"><span id="dlmsg" role="status"></span><button type="button" id="dl" hidden>Descargar el PDF para imprimir</button></span></div>"""
        script = """<script>
(async function(){
  var btn = document.getElementById('dl'), msg = document.getElementById('dlmsg');
  var downloads = null;
  try { downloads = window.claude && window.claude.use ? await window.claude.use('downloads') : null; } catch (e) { downloads = null; }
  if (!downloads) return;
  btn.hidden = false;
  btn.addEventListener('click', async function(){
    btn.disabled = true; msg.textContent = 'Preparando el PDF…';
    try {
      var res = await fetch('De-donde-venimos.pdf');
      if (!res.ok) throw { code: 'fetch' };
      var blob = await res.blob();
      await downloads.save({ filename: 'De donde venimos - Domecq Vergara.pdf', data: blob });
      msg.textContent = 'Listo.';
    } catch (e) {
      msg.textContent = (e && e.code === 'declined') ? 'Descarga cancelada.' : 'No se ha podido descargar el PDF.';
    }
    btn.disabled = false;
  });
})();
</script>"""
        return f"""{head}
<main class="book" lang="es">{top}
{body}
</main>
{script}"""
    return f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><title>{TITULO}</title>
<style>{font_faces()}{TOKENS}{BASE_CSS}{PRINT_CSS}</style></head><body class="book">
{body}
</body></html>"""


def to_pdf(html_path, pdf_path):
    subprocess.run([CHROMIUM, "--headless=new", "--no-sandbox", "--disable-gpu", "--no-pdf-header-footer",
                    "--virtual-time-budget=20000", f"--print-to-pdf={pdf_path}", html_path.as_uri()],
                   check=True, capture_output=True, timeout=300)


def norm(t):
    return re.sub(r"\s+", " ", t).strip()


def find_pages(pdf_path):
    doc = pymupdf.open(pdf_path)
    texts = [norm(p.get_text()) for p in doc]
    toc_page = next(i for i, t in enumerate(texts) if "Índice" in t and "Cómo leer este libro" in t)
    pages = []
    start = toc_page + 1
    for level, num, title in C.TOC_STRUCTURE:
        if level == 1:
            label = f"Capítulo {num}" if num else {"Cómo leer este libro": "Antes de empezar", "Fuentes": "Al final", "Para completar a mano": "Para la familia"}[title]
            needle = norm(f"{label} {title}")
        else:
            needle = norm(title)
        found = None
        for i in range(start, len(texts)):
            if needle in texts[i]:
                found = i
                break
        pages.append(found + 1 if found is not None else "")
        if found is not None and level == 1:
            start = found
    return pages, doc.page_count


def maquetar(entries, blanks=(), pad=0):
    html_print = AQUI / "libro_impresion.html"
    html_print.write_text(page(C.build_body(entries, blanks, pad)), encoding="utf-8")
    to_pdf(html_print, PDF_IMPRENTA)
    return find_pages(PDF_IMPRENTA)


def cajas():
    """Marca la caja de corte en el PDF de imprenta y guarda la copia de lectura."""
    doc = pymupdf.open(PDF_IMPRENTA)
    for pg in doc:
        r = pg.mediabox
        pg.set_bleedbox(r)
        dx, dy = (r.width - CORTE[0]) / 2, (r.height - CORTE[1]) / 2
        pg.set_trimbox(pymupdf.Rect(r.x0 + dx, r.y0 + dy, r.x1 - dx, r.y1 - dy))
    doc.save(PDF_IMPRENTA.with_suffix(".tmp.pdf"), garbage=3, deflate=True)
    doc.close()
    PDF_IMPRENTA.with_suffix(".tmp.pdf").replace(PDF_IMPRENTA)
    doc = pymupdf.open(PDF_IMPRENTA)
    for pg in doc:
        pg.set_cropbox(pg.trimbox)
    doc.save(PDF, garbage=3, deflate=True)


def main():
    entries = [(lvl, num, title, "") for lvl, num, title in C.TOC_STRUCTURE]
    # 1. Sin blancos, para ver en qué página cae cada capítulo.
    pages, total = maquetar(entries)
    blanks, shift = set(), 0
    for (lvl, num, title), pg in zip(C.TOC_STRUCTURE, pages):
        if lvl == 1 and pg and (pg + shift) % 2 == 0:
            blanks.add(title)
            shift += 1
    # 2. Con una página en blanco delante de cada capítulo que caía en par.
    pages, total = maquetar(entries, blanks)
    entries = [(lvl, num, title, pg) for (lvl, num, title), pg in zip(C.TOC_STRUCTURE, pages)]
    pad = (-total) % 4
    # 3. Con el índice numerado y el total redondeado a múltiplo de 4.
    pages, total = maquetar(entries, blanks, pad)
    cajas()
    (AQUI / "libro.html").write_text(page(C.build_body(entries), web=True), encoding="utf-8")
    missing = [t for (l, n, t), p in zip(C.TOC_STRUCTURE, pages) if not p]
    pares = [t for (l, n, t), p in zip(C.TOC_STRUCTURE, pages) if l == 1 and p and p % 2 == 0]
    print(f"PDF: {PDF_IMPRENTA.name} y {PDF.name} · {total} páginas")
    print("Índice:", ", ".join(f"{t} → {p}" for (l, n, t), p in zip(C.TOC_STRUCTURE, pages)))
    if missing:
        print("Sin página:", missing)
    if pares or total % 4:
        print("AVISO: capítulos en página par", pares, "o total no múltiplo de 4:", total)


if __name__ == "__main__":
    main()

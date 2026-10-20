"""Prepara las imágenes del libro a partir de las descargadas de Wikimedia Commons.

Uso: python3 preparar_fotos.py CARPETA_DE_DESCARGAS

Las descargas se nombran como el archivo de Commons, con los caracteres raros
cambiados por «_» y cortado a 80 caracteres. Cada imagen se recorta según el
catálogo de fotos.py, se reduce a 1000 px como mucho y se guarda en JPEG.
"""
import re
import sys
from pathlib import Path

from PIL import Image, ImageOps

from fotos import DIR, FOTOS

MAX = 1000


def local(name):
    return re.sub(r"[^A-Za-z0-9._-]", "_", name.replace(" ", "_"))[:80]


def main(src):
    DIR.mkdir(parents=True, exist_ok=True)
    for fid, (name, crop, *_rest) in FOTOS.items():
        p = Path(src) / local(name)
        if not p.exists() or p.stat().st_size < 3000:
            print("falta", fid)
            continue
        im = ImageOps.exif_transpose(Image.open(p))
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, "white")
            bg.paste(im, mask=im.split()[-1])
            im = bg
        im = im.convert("RGB")
        if crop:
            w, h = im.size
            im = im.crop((round(crop[0] * w), round(crop[1] * h), round(crop[2] * w), round(crop[3] * h)))
        im.thumbnail((MAX, MAX), Image.LANCZOS)
        im.save(DIR / f"{fid}.jpg", "JPEG", quality=82, optimize=True, progressive=True)
        print("ok", fid, im.size)


if __name__ == "__main__":
    main(sys.argv[1])

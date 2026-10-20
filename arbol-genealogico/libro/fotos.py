"""Retratos, grabados y vistas del libro, con su procedencia.

Todas las imágenes vienen de Wikimedia Commons. preparar_fotos.py las recorta
y las guarda en ilustraciones/fotos/; aquí está el catálogo con el autor y la
licencia de cada una, que el capítulo de fuentes reproduce.
"""
import base64
from html import escape
from pathlib import Path

DIR = Path(__file__).resolve().parent / "ilustraciones" / "fotos"

# id: (archivo en Commons, recorte (izq, arriba, dcha, abajo) en fracciones o None,
#      descripción para los créditos, autor, licencia)
FOTOS = {
    "domecq_lembeye": ("Pedro-domecq-lembeye-1787-1839.png", None,
                       "Pedro Domecq Lembeye", "autor desconocido", "dominio público"),
    "domecq_loustau": ("Pedro_domecq_loustau.jpg", None,
                       "Pedro Domecq Loustau", "autor desconocido", "dominio público"),
    "carmen_villavicencio": ("Carmen_Núñez_de_Villavicencio_y_Olaguer_Feliú,_1868.jpg", None,
                             "Carmen Núñez de Villavicencio y Olaguer-Feliú, 1868", "José María Pavón Maraver", "CC BY 4.0"),
    "usquain": ("64_TABAILLE_USQUAIN_(2).jpg", None,
                "La iglesia de Usquain, en el Béarn", "Mireille Grumberg", "CC BY-SA 4.0"),
    "bodegas_domecq": ("Bodegas_Domecq_Fundador-P1100822.jpg", None,
                       "Un patio de las bodegas Domecq, en Jerez", "El Pantera", "CC BY-SA 4.0"),
    "palacio_domecq": ("Plaza_Aladro_Palacio_Domecq_Jerez.JPG", None,
                       "El palacio Domecq, en la plaza de Aladro de Jerez", "Jerezplataforma", "CC BY 3.0"),
    "gaston_febus": ("GastonPhoebusChPau.jpg", (0, 0, 1, .62),
                     "Estatua de Gaston Fébus en el castillo de Pau", "Jibi44", "CC BY-SA 3.0"),
    "orthez": ("Pont-Vieux_d'Orthez_-896.jpg", None,
               "El puente viejo de Orthez", "MOSSOT", "CC BY 3.0"),
    "palacio_villavicencio": ("Jerez_de_la_Frontera_-_Alcázar,_Palacio_de_Villavicencio_1.jpg", None,
                              "El palacio de Villavicencio, en el Alcázar de Jerez", "Zarateman", "CC0"),
    "olaguer": ("Virrey_Antonio_de_Olaguer_Feliú_y_Heredia_Domec.jpg", None,
                "Antonio Olaguer Feliú, virrey del Río de la Plata", "Tom99argie (fotografía)", "CC BY-SA 4.0"),
    "gonzalez_angel": ("Manuel_Maria_Gonzalez_Ángel.png", None,
                       "Manuel María González Ángel", "autor desconocido", "dominio público"),
    "bodega_gonzalez": ("1865-09-17,_El_Museo_Universal,_Interior_de_uno_de_los_departamentos_de_la_bodega_de_los_señores_González_y_Byass,_en_Jerez_de_la_Frontera.jpg", None,
                        "Bodega de González y Byass, en El Museo Universal, 1865", "Bernardo Rico (grabador)", "dominio público"),
    "melendez_bruna": ("Salvador_Meléndez_y_Bruna.jpg", None,
                       "Salvador Meléndez Bruna", "Augusto Manuel de Quesada", "dominio público"),
    "thebussem": ("Mariano_pardo.jpg", None,
                  "Mariano Pardo de Figueroa, el Doctor Thebussem", "ilustrador desconocido", "dominio público"),
    "medina_sidonia": ("CastilloMedinaSidonia_001.JPG", None,
                       "El castillo de Medina Sidonia", "Danipan", "CC BY 3.0"),
    "ubrique": ("Ubrique_Andalousie_Espagne.jpg", None,
                "Ubrique", "Grez", "CC BY-SA 3.0"),
    "gomez_imaz": ("Vicealmirante_Gómez_Imaz,_ministro_de_Marina,_en_La_Ilustración_Católica_de_España.jpg", None,
                   "José Gómez-Imaz, ministro de Marina, en La Ilustración Católica de España", "autor desconocido", "dominio público"),
    "canal": ("1923-05-25,_El_Financiero,_Carlos_Cañal_Migolla_(cropped).jpg", None,
              "Carlos Cañal y Migolla, en El Financiero, 1923", "autor desconocido", "dominio público"),
    "urzainqui": ("Urzainqui_(Valle_de_Roncal,_Navarra)_07.jpg", None,
                  "Urzainqui, en el valle del Roncal", "Jialxv", "CC BY-SA 4.0"),
    "navarrenx": ("FR-64-Navarrenx3.JPG", None,
                  "Navarrenx", "Szeder László", "CC BY-SA 4.0"),
    "quito_1779": ("Real_Audiencia_de_Quito_1779.jpg", None,
                   "Mapa de la Real Audiencia de Quito, 1779", "Francisco Requena", "dominio público"),
    "molina": ("Joaquín_de_Molina.jpg", None,
               "Joaquín de Molina y Zulueta", "autor desconocido", "dominio público"),
    "ahumada": ("41_Agustín_Ahumada_Villalón_(Palacio_Ayuntamiento_México).jpg", None,
                "Agustín de Ahumada y Villalón, virrey de Nueva España, en el Palacio del Ayuntamiento de México", "Jojagal (fotografía)", "CC0"),
    "san_juan": ("Iglesia_juan_caballeros_jerez_fachada_campanario_01.JPG", None,
                 "San Juan de los Caballeros, en Jerez", "Jerezplataforma", "CC BY 3.0"),
    "alfonso_x": ("Alfonso_X_el_Sabio_en_El_libro_de_los_juegos.jpg", None,
                  "Alfonso X en el Libro de los juegos, 1283", "taller de Alfonso X", "dominio público"),
    "carlos_ii": ("Rey_Carlos_II_de_España.jpg", (.2, .1, .8, .58),
                  "Carlos II, por Juan Carreño de Miranda", "Juan Carreño de Miranda", "dominio público"),
    "felipe_v": ("Felipe_V_de_España.jpg", (.18, 0, .84, .62),
                 "Felipe V, por Jean Ranc", "Jean Ranc", "dominio público"),
    "fernando_vii": ("Fernando_VII_-_Vicente_López.jpg", (.08, .04, .92, .72),
                     "Fernando VII, por Vicente López", "Vicente López", "dominio público"),
    "alfonso_xiii": ("Rey_Alfonso_XIII_de_España,_by_Kaulak.jpg", (.22, 0, .98, .72),
                     "Alfonso XIII, por Kaulak", "Kaulak", "dominio público"),
}


def disponible(fid):
    return (DIR / f"{fid}.jpg").exists()


def _uri(fid):
    return "data:image/jpeg;base64," + base64.b64encode((DIR / f"{fid}.jpg").read_bytes()).decode()


def img(fid, cls=""):
    return f'<img class="{cls}" src="{_uri(fid)}" alt="{escape(FOTOS[fid][2])}">'


def foto(fid, pie, cls=""):
    """Una imagen con su pie, o nada si no está."""
    if not disponible(fid):
        return ""
    return f'<figure class="ph {cls}">{img(fid)}<figcaption>{pie}</figcaption></figure>'


def lamina(*items, cls=""):
    """Varias imágenes en fila: items = (id, pie[, clase])."""
    figs = "".join(foto(*it) for it in items)
    return f'<div class="photos {cls}">{figs}</div>' if figs else ""


def creditos():
    usadas = [f for f in FOTOS if disponible(f)]
    lis = []
    for f in usadas:
        _, _, desc, autor, lic = FOTOS[f]
        quien = ", ".join(x for x in (autor, lic) if x)
        lis.append(f"<li>{escape(desc)}{': ' + escape(quien) if quien else ''}.</li>")
    return "".join(lis)

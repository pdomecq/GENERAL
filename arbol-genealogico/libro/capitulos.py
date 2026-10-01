"""Contenido del libro: capítulos, fichas y tablas.

La narración está escrita a mano a partir de lo investigado; las fichas de
cada antepasado salen de los datos del árbol (arbol.html) para que libro y
árbol digan siempre lo mismo.
"""
from html import escape

from datos import P, S, LINE, STARS, COSTADOS, ORD, gen, real, side, fmt, roman, rel, nos, both_ways
from graficos import pedigree5, branch_tree, fan_chart, convergence


def esc(s):
    return escape(str(s), quote=False)


MARK = {"ok": ("●", "Confirmado"), "tree": ("○", "Árbol publicado"), "ded": ("◌", "Deducido"),
        "doubt": ("◇", "En duda"), "none": ("·", "Sin documentar"), "self": ("", "")}


def mark(c):
    m, title = MARK.get(c, ("", ""))
    return f'<span class="mk {c}" title="{title}">{m}</span>' if m else ""


def pname(k):
    return P.get(str(real(k)), {}).get("n", "")


# --------------------------------------------------------------------- fichas
def card(k):
    p = P[str(k)]
    meta = " · ".join(x for x in (p.get("d", ""), nos(p.get("t", ""))) if x)
    note = nos(p.get("note", ""))
    return f"""<article class="card {side(k) or 'self'}">
  <div class="card-k"><span class="num">nº {fmt(k)}</span><span class="rel">{esc(rel(k))}</span>{mark(p.get('c'))}</div>
  <div class="card-b"><h4>{esc(p['n'])}</h4>{f'<p class="meta">{esc(meta)}</p>' if meta else ''}{f'<p>{esc(note)}</p>' if note else ''}</div>
</article>"""


def cards(keys, title=""):
    items = [card(k) for k in keys]
    if title and items:
        # El título va pegado a la primera ficha para que no quede solo al pie de una página.
        items[0] = f'<div class="keep"><h3 class="cards-title">{title}</h3>{items[0]}</div>'
    return '<div class="cards">' + "\n".join(items) + "</div>"


def subtree(root, max_gen=99):
    """Antepasados conocidos de `root` (incluido), sin casillas repetidas."""
    out = []
    for key, p in P.items():
        k = int(key)
        if p.get("same") or k < root:
            continue
        g, gr = gen(k), gen(root)
        if g < gr or g > max_gen:
            continue
        if (k >> (g - gr)) == root:
            out.append(k)
    return sorted(out)


LINE_KEYS = {k for r in LINE for k in r.get("ks", [])}


# --------------------------------------------------------------------- piezas
def chapter(cid, label, title, body, lead=""):
    return f"""<section class="chapter" id="{cid}">
<header class="ch-head"><p class="ch-num">{esc(label)}</p><h1>{esc(title)}</h1>{f'<p class="ch-lead">{lead}</p>' if lead else ''}</header>
{body}
</section>"""


def figure(svg, caption, cls=""):
    return f'<figure class="fig {cls}"><div class="fig-art">{svg}</div><figcaption>{caption}</figcaption></figure>'


HAS_DOUBT = any(p.get("c") == "doubt" for p in P.values())


def legend():
    doubt = '<span><i class="sw doubt"></i>En duda</span>' if HAS_DOUBT else ''
    return ('<p class="legend"><span><i class="sw pat"></i>Por papá</span><span><i class="sw mat"></i>Por mamá</span>'
            f'<span><i class="sw dashed"></i>Enlace deducido</span>{doubt}</p>')


# ===================================================================== textos
def front_matter():
    return """<section class="cover">
  <div class="cover-frame">
    <p class="cover-kicker">Historia y genealogía de una familia de Jerez</p>
    <h1 class="cover-title">De dónde venimos</h1>
    <p class="cover-sub">Los antepasados de los Domecq Vergara</p>
    <div class="cover-art">""" + fan_chart(7, decorative=True, uid="cov") + """</div>
    <p class="cover-years">1264 · 2026</p>
    <p class="cover-foot">Recopilado por Pedro Domecq Vergara<br>Jerez de la Frontera, 2026</p>
  </div>
</section>
<section class="front colophon-front">
  <p>Edición familiar, para los hermanos Domecq Vergara y sus padres. No se vende.</p>
  <p>Compilado en septiembre y octubre de 2026 a partir de fuentes publicadas: la Real Academia de la Historia, el Boletín Oficial del Estado, estudios universitarios, Wikipedia y árboles genealógicos en línea. La lista completa está al final del libro.</p>
  <p>El árbol interactivo, con las mismas fichas y enlaces a cada fuente, acompaña a este libro y se irá corrigiendo a medida que aparezcan documentos.</p>
</section>
<section class="front dedication">
  <p>Para papá y mamá, Pablo y Beatriz.</p>
  <p>Y para nuestros hermanos, y para los que vengan detrás.</p>
</section>"""


def toc(entries):
    rows = []
    for level, label, title, page in entries:
        cls = "toc-ch" if level == 1 else "toc-sec"
        rows.append(f'<li class="{cls}"><span class="toc-l">{esc(label)}</span><span class="toc-t">{esc(title)}</span><span class="toc-p">{page}</span></li>')
    return f"""<section class="front toc"><h1>Índice</h1><ol class="toc-list">{''.join(rows)}</ol></section>"""


def intro():
    body = """<div class="prose">
<p class="lead">Este libro reúne lo que hemos podido saber de nuestros antepasados: quiénes fueron, de dónde vinieron, qué hicieron y cómo se fueron enlazando las familias hasta llegar a nosotros. Empieza por papá y mamá y por los abuelos, sigue con la línea más antigua, que llega hasta la conquista de Jerez en 1264, y recorre después, una por una, las ramas de la familia. Al final hay capítulos de consulta: los títulos, las órdenes militares, los apellidos y sus escudos, una cronología y el árbol completo.</p>
<h2>Los números</h2>
<p>Cada antepasado lleva un número, el que le corresponde en la numeración de Sosa-Stradonitz, la que usan los genealogistas. Nosotros, los hermanos, somos el 1. El padre de cualquier persona tiene el doble de su número y la madre el doble más uno. Papá es el 2 y mamá el 3; los padres de papá, el 4 y el 5; los de mamá, el 6 y el 7. Los hombres llevan números pares y las mujeres impares, y basta el número para saber el lugar exacto de cada uno en el árbol. Miguel Fernández de Villavicencio, el antepasado más antiguo, es el 17.367.424.</p>
<h2>Las generaciones</h2>
<p>Usamos los nombres de siempre: padres, abuelos, bisabuelos, tatarabuelos y trastatarabuelos. A partir de ahí contamos: quintos abuelos, sextos abuelos y así hasta los vigésimo terceros (23.º abuelos), que vivieron en el siglo XIII. Cada generación dobla a la anterior: tenemos 2 padres, 4 abuelos, 8 bisabuelos, 16 tatarabuelos, y en la décima generación ya serían 512 personas.</p>
<h2>Por papá, por mamá y por las dos vías</h2>
<p>Paterno o materno indica si el antepasado nos llega por papá o por mamá; en los árboles, lo que viene por papá va en verde y lo que viene por mamá, en ocre. Papá y mamá son primos segundos, así que una parte de los antepasados nos llega por los dos lados a la vez: los marqueses de Casa Domecq y toda su ascendencia, los Domecq del Béarn, los Villavicencio, los Rivero y los González. A esos los llamamos antepasados «por las dos vías».</p>
<h2>Lo seguro y lo probable</h2>
<p>No todo lo que cuenta este libro está igual de probado, y cada ficha lo dice con una marca:</p>
<ul class="marks">
<li><span class="mk ok">●</span> <b>Confirmado</b> en fuentes de referencia (la Real Academia de la Historia, el BOE, estudios publicados, Wikipedia) o por la propia familia.</li>
<li><span class="mk tree">○</span> <b>Tomado de árboles genealógicos publicados</b> (Geneanet, Geni, FamilySearch), sin comprobar todavía en documentos originales.</li>
<li><span class="mk ded">◌</span> <b>Deducido</b> de las relaciones documentadas: encaja por nombres, fechas y lugares, pero falta el papel que lo pruebe.</li>
<li><span class="mk doubt">◇</span> <b>En duda</b>, porque las fuentes se contradicen.%%DUDA%%</li>
</ul>
<p>Nada de lo que aquí se cuenta se ha inventado, pero hay eslabones que conviene comprobar en los archivos. El último capítulo explica cuáles y dónde buscarlos. La investigación se hizo en septiembre y octubre de 2026 con fuentes publicadas en internet; no se han consultado archivos físicos. Cuando alguien de la familia lo haga, este libro se podrá corregir y ampliar.</p>
</div>"""
    body = body.replace("%%DUDA%%", "" if HAS_DOUBT else " Ahora mismo no queda ninguno: la última duda, la de los padres del bisabuelo José Bohórquez, la resolvió papá.")
    return chapter("intro", "Antes de empezar", "Cómo leer este libro", body)


def cap1():
    p8 = """<div class="prose">
<p class="lead">Somos los hijos de Pablo Domecq Bohórquez y Beatriz Vergara Domecq. Papá es hijo de José Manuel Domecq Hidalgo y Victoria Bohórquez Mora-Figueroa, y tiene cuatro hermanos: Victoria, José Manuel, Almudena y Jorge. Mamá es hija de Eduardo Vergara Lacave y Beatriz Domecq López de Carrizosa, y también tiene cuatro hermanos: Begoña María, Mercedes, María del Rocío y Juan Pedro.</p>
<h2>Los cuatro abuelos</h2>
<p><b>José Manuel Domecq Hidalgo</b>, el abuelo paterno, era hijo de José Manuel Domecq Rivero (1895–1981), caballero de Calatrava, y de María del Carmen Hidalgo Enrile (1897–1998), hija de los marqueses de Pardo de Figueroa y de Negrón. Por su padre era nieto del I marqués de Casa Domecq.</p>
<p><b>Victoria Bohórquez Mora-Figueroa</b>, la abuela paterna, era hija de José Bohórquez Gómez, hijo del diputado Bartolomé Bohórquez Rubiales y hermano del ganadero Fermín Bohórquez Gómez, y de María Francisca de Mora-Figueroa y Gómez-Imaz (1907–2003), hija del VII marqués de Tamarón. Su nombre le venía de su abuela materna, Victoria Gómez-Imaz.</p>
<p><b>Eduardo Vergara Lacave</b> (1940–2008), el abuelo materno, era con toda probabilidad hijo del bodeguero Juan Vicente Vergara Sanchiz (1899–1974) y de Eugenia María Lacave Patero (1912–2008), de la familia gaditana de los vinos Lacave. Es el único de los cuatro cuyos padres no aparecen nombrados en ningún documento publicado; todo lo demás encaja, y su partida de nacimiento lo confirmaría.</p>
<p><b>Beatriz Domecq López de Carrizosa</b>, la abuela materna, murió en junio de 2023. Era hija del ganadero Juan Pedro Domecq Rivero (1910–1995) y de Ángeles López de Carrizosa y Eizaguirre, dama de la Real Maestranza de Ronda e hija del I barón de Algar del Campo. Fue camarera de María Santísima de la Encarnación, de la Hermandad del Santo Crucifijo, y tuvo siete hermanos: María, Javier, Teresa, Juan Pedro, Fernando, Lucía y Gonzalo.</p>
</div>"""
    conv = """<div class="prose"><h2>Dos veces Domecq</h2>
<p>El abuelo José Manuel y la abuela Beatriz eran primos hermanos. Sus padres, José Manuel y Juan Pedro Domecq Rivero, eran hermanos, hijos de Pedro Domecq Núñez de Villavicencio, I marqués de Casa Domecq, y de María Rivero González. Por eso papá y mamá son primos segundos, y los marqueses de Casa Domecq son tatarabuelos nuestros por partida doble. En el árbol ocupan dos casillas, la 16–17 y la 28–29, y toda su ascendencia (los Domecq del Béarn, los Villavicencio de Jerez, los Rivero y los González de González Byass) lo es nuestra por las dos vías.</p></div>""" + figure(convergence(), "Cómo se juntan las dos ramas Domecq.", "conv-fig")
    sixteen = ["Domecq", "Rivero", "Hidalgo", "Enrile", "Bohórquez", "Gómez", "Mora-Figueroa", "Gómez-Imaz",
               "Vergara", "Sanchiz", "Lacave", "Patero", "Domecq", "Rivero", "López de Carrizosa", "Eizaguirre"]
    cells = "".join(
        f'<div class="sn {side(16 + i)}{" dup" if i in (12, 13) else ""}"><span class="k">nº {16 + i}</span><b>{s}</b><small>{esc(pname(16 + i)) if not P[str(16 + i)].get("same") else "repite nº " + str(P[str(16 + i)]["same"])}</small></div>'
        for i, s in enumerate(sixteen))
    sn = f"""<div class="prose"><h2>Los dieciséis apellidos</h2>
<p>En la tradición genealógica española, los apellidos de los dieciséis tatarabuelos resumen una ascendencia. Los nuestros son estos; Domecq y Rivero aparecen dos veces.</p></div>
<div class="surnames">{cells}</div>"""
    chart = f"""<div class="fullpage chartpage">
<h2 class="chart-title">Nuestro árbol de cinco generaciones</h2>
{legend()}
{pedigree5()}
</div>"""
    fichas = '<div class="prose"><h2>Padres, abuelos y bisabuelos</h2><p>Las fichas de las tres primeras generaciones. Las de los tatarabuelos están en el capítulo de cada rama.</p></div>' + cards(range(2, 16))
    return chapter("c1", "Capítulo 1", "Quiénes somos", p8 + conv + sn + chart + fichas)


def cap2():
    rows = []
    for r in LINE:
        if r.get("era"):
            rows.append(f'<li class="era"><span class="yr"></span><span class="rail"></span><p class="eralabel">{esc(r["era"])}</p></li>')
            continue
        k0 = r["ks"][0]
        g = gen(k0)
        who = " <span class='x'>×</span> ".join(f"<b>{esc(pname(k))}</b>" for k in r["ks"])
        gl = "Nosotros" if k0 == 1 else f"Generación {roman(g)} · {esc(rel(k0))} · nº {fmt(k0)}"
        c = P[str(real(k0))].get("c", "")
        tx = nos(r.get("t", ""))
        if k0 == 1:
            who = "<b>Los hermanos Domecq Vergara</b>"
        rows.append(f'<li class="{"weak" if r.get("weak") else ""}"><span class="yr">{esc(r["y"])}</span><span class="rail">{mark(c)}</span><div class="lb"><p class="gl">{gl}</p><p class="who">{who}</p>{f"<p class=tx>{esc(tx)}</p>" if tx else ""}</div></li>')
    body = f"""<div class="prose">
<p class="lead">De todas nuestras líneas, la que llega más lejos es la de los Villavicencio de Jerez. Sube por papá y por mamá a la vez, a través de los marqueses de Casa Domecq; pasa por Carmen Núñez de Villavicencio, la marquesa de Domecq d’Usquain, por los condes de Cañete del Pinar y los marqueses de Valhermoso, y termina en Miguel Fernández de Villavicencio, uno de los caballeros que tomaron Jerez con Alfonso X en 1264. Son veinticinco generaciones.</p>
<p>El documento directo más antiguo de la cadena es el mayorazgo que fundó Pedro Camacho «el Rico» en 1507, estudiado en una revista de la Universidad Complutense. Lo anterior se apoya en la biografía que la Real Academia de la Historia dedica al alcaide Lorenzo Fernández de Villavicencio y en la tradición de los genealogistas jerezanos. Dos eslabones son deducidos: van marcados con ◌ y con trazo discontinuo. La fecha de la izquierda es una época aproximada de nacimiento.</p>
</div>
<ol class="line">{"".join(rows)}</ol>"""
    return chapter("c2", "Capítulo 2", "La línea más antigua", body)


# --------------------------------------------------------------------- ramas
RAMAS = []


def rama(rid, title, lead, prose, chart_roots, chart_depth, keys, chart_caption, extra=""):
    chart = ""
    if chart_roots:
        chart = figure(branch_tree(chart_roots, chart_depth, label=title), chart_caption, "branch-fig")
    RAMAS.append((rid, title))
    return f"""<section class="rama" id="{rid}">
<h2 class="rama-title">{esc(title)}</h2>
<div class="prose"><p class="lead">{lead}</p>{prose}</div>
{chart}
{cards(keys, "Fichas de la rama") if keys else ''}
{extra}
</section>"""


def fillbox(title, text, fields):
    rows = "".join(f'<div class="fillrow"><span>{esc(x)}</span><span class="fl"></span></div>' for x in fields)
    return f'<div class="fillbox"><h3>{esc(title)}</h3><p>{esc(text)}</p>{rows}</div>'


def cap3():
    domecq = rama(
        "r-domecq", "Los Domecq, del Béarn a Jerez",
        "Los Domecq vienen de Usquain, una aldea del Béarn, al pie de los Pirineos franceses, cerca de Sauveterre. En bearnés, su apellido designa una casa noble, y eso era la casa Domecq de Usquain: un pequeño dominio con su señor.",
        """<p>La primera noticia es del 5 de abril de 1364, cuando Bertrand, señor de Domecq, rindió homenaje a Gaston Fébus, conde de Foix y vizconde de Béarn, en el castillo de Orthez. La casa vuelve a aparecer en el censo del Béarn de 1385, y en 1666 un Juan de Domecq rindió homenaje a Luis XIV.</p>
<p>El camino hacia Jerez empieza con una boda. Jean Domecq, señor de la casa de Usquain, se casó en 1780 con Catherine Lembeye Haurie, cuya madre, Marie Haurie, era hermana de Juan Haurie, un bearnés de Vielleségure que había llegado a Jerez como refugiado en 1740. Juan Haurie hizo fortuna con el vino: a la muerte de su amigo irlandés Patrick Murphy, en 1764, heredó su negocio junto con Juan Pedro Lacoste, y ganó contra el gremio de vinateros de Jerez un pleito que acabó en la Real Orden de 1778, la que liberalizó el comercio del vino. En 1791 metió en la casa a cinco sobrinos.</p>
<p>Los hijos de Jean y Catherine siguieron el camino de su tío abuelo. Pedro Domecq Lembeye dio en 1822 su nombre a la casa, que desde entonces se llamó Pedro Domecq. Fue socio en el negocio del jerez de John James Ruskin, el padre del gran crítico de arte inglés John Ruskin, y en 1836 su hija Adèle fue el primer amor del joven Ruskin. Otro hermano, Juan Pedro, continuó la bodega. Nuestro antepasado es un tercer hermano, al que los árboles llaman Pierre Pascal o Pedro Pascual, casado con Marie de Loustau; las fuentes no se ponen de acuerdo en sus fechas.</p>
<p>Su hijo Pierre Patient, que en España se llamó Pedro Domecq Loustau, nació en Usquain en 1824 y en 1848 entró en la bodega de su tío en Jerez. Hacia 1874 empezó a vender Fundador, el primer brandy de Jerez. En 1868 se casó con Carmen Núñez de Villavicencio y Olaguer-Feliú, de uno de los linajes más antiguos de la ciudad. Juntos fundaron colegios para niños pobres, asilos de ancianos y centros para mujeres, y según Infocatólica (2025) van camino de los altares. Alfonso XIII hizo a Carmen marquesa de Domecq d’Usquain en 1920.</p>
<p>Su hijo Pedro Domecq Núñez de Villavicencio (1869–1921) dirigió la casa después de él y recibió en 1906 del papa Pío X el título pontificio de marqués de Casa Domecq. Se casó en 1892 con María Rivero González, de los bodegueros Rivero, y de ellos vienen nuestros dos bisabuelos Domecq: José Manuel (1895–1981), caballero de Calatrava, padre del abuelo José Manuel, y Juan Pedro (1910–1995), ganadero de bravo, padre de la abuela Beatriz. Al morir en 1979 su hermano Pedro, Juan Pedro llevó la ganadería familiar con su hijo Gonzalo, y en 1999 sus hijos Gonzalo y Juan Pedro fundaron la ganadería Casa de los Toreros.</p>""",
        [32], 3, [16, 17] + subtree(32), "Los Domecq del Béarn: de Pedro Domecq Loustau a los Haurie y los Lembeye.")

    vill_keys = [k for k in subtree(33) if k not in LINE_KEYS or k in (33, 66, 67, 132, 133)]
    vill_keys = sorted(set(vill_keys) | {k for k in subtree(33, 12)})
    villa = rama(
        "r-villavicencio", "Los Villavicencio y sus alianzas",
        "Con Carmen Núñez de Villavicencio entra en la familia el linaje más antiguo de Jerez, y con él una larga lista de alianzas: los Camacho, los Spínola de Génova, los Carrizosa, los Zurita, los Angulo, los Lasso de la Vega y los Olaguer-Feliú. La línea principal está en el capítulo anterior; aquí van las ramas que la rodean.",
        """<p><b>Los condes de Cañete del Pinar.</b> Carlos II creó el título el 11 de mayo de 1688; al principio se llamó Cañete la Real y cambió de nombre en 1764. Todo indica que lo tuvieron José Núñez de Villavicencio (nacido en 1758), veinticuatro de Jerez y señor de Casarejo, y su mujer, Inés de Angulo y Lasso de la Vega, que murió en Écija en 1845. Su hijo José Juan (1800–1875), caballero de Calatrava, se casó con María Regla Olaguer-Feliú, y el hermano de Carmen, Manuel Núñez de Villavicencio (nacido en 1838), también fue conde de Cañete del Pinar.</p>
<p><b>Los Olaguer-Feliú.</b> María Regla Olaguer-Feliú (1798–1864) era sobrina de Antonio Olaguer Feliú, virrey del Río de la Plata entre 1797 y 1799 y después secretario de Guerra de Carlos IV. Su padre, José, teniente coronel de Estado Mayor, se bautizó en Barcelona en 1747, y su abuelo, Tomás, nacido en Ceuta, fue capitán del Regimiento de Infantería de Granada.</p>
<p><b>Los Angulo y los Lasso de la Vega.</b> Por la condesa Inés llegan los Angulo de Lucena y los Lasso de la Vega de Écija. Su abuelo Antonio García Lasso de la Vega fue caballero de la Orden de San Juan desde 1725.</p>
<p><b>Los Zurita.</b> Bruno Núñez de Villavicencio se casó en 1725 con Francisca de Zurita, hija de Álvaro Diego de Zurita y Haro, II marqués de Campo Real, un título creado en 1689. Los Zurita de Jerez se tenían por descendientes de Fagut de Zurita, otro caballero de la conquista de 1264.</p>
<p><b>Los marqueses de Valhermoso.</b> Petronila Inés Fernández de Villavicencio, la mujer de José Antonio Núñez de Villavicencio, era hija del III marqués de Valhermoso de Pozuela. Por ella sigue nuestra línea más antigua: su abuelo, el II marqués, gobernó Canarias, y su bisabuelo, el I, fue mayordomo mayor de la reina Mariana de Austria.</p>
<p><b>Los Carrizosa y los Spínola.</b> Juan Fernández de Villavicencio y Carrizosa, señor de Valhermoso, era hijo de Diego Fernández de Villavicencio y de Isabel Melgarejo y Carrizosa, hija a su vez de Íñigo López de Carrizosa, el veinticuatro que en 1479 fundó la capilla funeraria de los Carrizosa en San Juan de los Caballeros. Juan se casó con Mencía Spínola, nieta de Pedro Camacho el Rico y hija de Luis de Spínola, un genovés que luchó en la conquista de Granada. Los Spínola vuelven a entrar dos siglos después con María Manuela Spínola, mujer del II marqués de Valhermoso.</p>""",
        [33], 5, vill_keys, "La rama de Carmen Núñez de Villavicencio hasta la undécima generación.")

    rivero = rama(
        "r-rivero", "Los Rivero y los González: CZ y González Byass",
        "María Rivero González (1869–1962), la mujer del I marqués de Casa Domecq y tatarabuela nuestra por partida doble, unía dos de las grandes familias bodegueras de Jerez.",
        """<p><b>Los Rivero.</b> Por su padre, Tomás Rivero O'Neale (1835–1902), venía de los Rivero, de origen cántabro. Pedro Agustín Rivero y de la Herrán (1762–1829), alcalde de la Santa Hermandad de Jerez, se casó en 1791 con Tomasa de la Tixera y Menchaca, heredera de una bodega fundada en 1650 con la marca CZ, y así nacieron las bodegas Rivero-CZ. Su hijo Joaquín (1797–1868), caballero de Carlos III y maestrante de Zaragoza, presidió el Ayuntamiento de Jerez; su hermano Rafael fue alcalde de la ciudad en tres etapas, y otro hermano, Francisco, gentilhombre de cámara de Isabel II. Joaquín se casó con Carmen O'Neale Saelices, de una familia jerezana de origen irlandés.</p>
<p><b>Los González.</b> Por su madre, Emilia González de Soto (1841–1889), venía de los González de González Byass. Manuel María González Ángel (Sanlúcar de Barrameda, 1812 – Jerez, 1887) se instaló en Jerez en 1835 y fundó la bodega que, al asociarse con el inglés Robert Blake Byass, acabó llamándose González Byass. Su tío José Ángel y Vargas, el «Tío Pepe», le aconsejó en el negocio y dio nombre al vino más famoso de la casa. Fue diputado a Cortes por Sanlúcar. Su padre, José Antonio González y Rodríguez, era un segoviano de la Guardia de Corps que llegó a Sanlúcar en 1783 como visitador de las salinas reales, y su madre, María del Rosario Ángel, una sanluqueña a la que llamaban Rosario Peña por el apellido de su padrastro.</p>
<p>Manuel María se casó en 1837 con Victorina de Soto y Lavaggi, hija de Pedro Nolasco de Soto y Araco, un comerciante de Briviesca que hizo fortuna en México antes de establecerse en Cádiz. Tuvieron nueve hijos; uno de ellos, Pedro Nolasco, fue I marqués de Torresoto de Briviesca, y otra, Emilia, se casó en 1865 con Tomás Rivero O'Neale. Así, el fundador de González Byass y los creadores de Rivero-CZ son antepasados nuestros, y por las dos vías.</p>""",
        [17], 4, subtree(34) + subtree(35), "La rama de María Rivero González: los Rivero, los O'Neale, los González y los Soto.")

    hidalgo = rama(
        "r-hidalgo", "Los Hidalgo, los Pardo de Figueroa y los Enrile",
        "La bisabuela María del Carmen Hidalgo Enrile (1897–1998), mujer del bisabuelo José Manuel Domecq Rivero, era hija de Salvador Hidalgo y Pardo de Figueroa (1865–1939), II marqués de Pardo de Figueroa y V de Negrón, caballero de Calatrava y maestrante de Sevilla, nacido en Medina Sidonia. Su hermano Baltasar fue III marqués de Pardo de Figueroa y VI de Negrón.",
        """<p><b>Los marqueses de Negrón.</b> El primero fue Luis Meléndez y Bruna (1763–1824), mariscal de campo, sevillano y hermano de Salvador Meléndez Bruna, gobernador de Puerto Rico. Con María Lorenza Beyens, de una familia gaditana de origen flamenco, tuvo a Salvadora Meléndez y Beyens, que llevó el título a los Hidalgo al casarse con Salvador Juan Manuel Hidalgo y Sarria. Su hijo Baltasar Hidalgo y Meléndez (1831–1894) fue IV marqués de Negrón.</p>
<p><b>Los Pardo de Figueroa.</b> Baltasar se casó en Medina Sidonia en 1863 con Josefa Pardo de Figueroa y de la Serna. Ya viuda, Alfonso XIII creó para ella en 1927 el marquesado de Pardo de Figueroa. Su hermano Mariano fue el «Doctor Thebussem» (1828–1918), escritor, cervantista y gastrónomo, primer cartero honorario de España, que publicó en 1888 y 1889 las <i>Notas genealógicas</i> de la familia. Los Pardo de Figueroa venían de Arcos: allí nacieron su padre, José María, regidor perpetuo de Cádiz, y su abuelo.</p>
<p><b>Los Enrile.</b> La madre de la bisabuela, María del Carmen Enrile y González de la Mota (1859–1901), era hija de Joaquín Enrile y Méndez de Sotomayor (1826–1886), teniente coronel de Artillería y autor de un <i>Prontuario de Artillería</i> (1856), de una familia gaditana de origen genovés, y de María de la Paz González de la Mota y Velázquez-Gaztelu.</p>""",
        [9], 5, subtree(18) + subtree(19), "La rama de la bisabuela María del Carmen Hidalgo Enrile.")

    bohorquez = rama(
        "r-bohorquez", "Los Bohórquez, de Ubrique",
        "La abuela Victoria era hija de José Bohórquez Gómez y nieta de Bartolomé Bohórquez Rubiales (1862–1925), un terrateniente de Ubrique que representó a la Sierra de Cádiz en las Cortes durante siete legislaturas. El hermano de José, Fermín Bohórquez Gómez (Jerez, 1904–1973), fue uno de los grandes ganaderos andaluces de su tiempo: en 1946 compró la ganadería de reses de Murube que desde entonces lleva su nombre, y su hijo, Fermín Bohórquez Escribano, primo hermano de la abuela, fue un rejoneador célebre.",
        """<p><b>El diputado de las tres palabras.</b> Bartolomé nació en Ubrique en 1862, hijo de Fermín Bohórquez Zarco y Ana Rubiales Olmedo, y se hizo bachiller en el Instituto Columela de Cádiz en 1881. Fue seis veces diputado por el distrito de Grazalema, desde 1899, y senador por Cádiz en 1919 y 1920. Un estudio de la UNED sobre las elecciones en Cádiz lo describe como el hombre fuerte del distrito en la primera década del siglo XX. En Ubrique se contaba que en todas esas legislaturas solo habló para decir «Jesús, María y José» cuando tosía algún colega, y de ahí su apodo. Murió en Jerez en octubre de 1925. Su mujer, Ana María Gómez Bohórquez, le sobrevivió hasta 1940. Tuvieron tres hijos: Ana María, José, nuestro bisabuelo, y Fermín.</p>
<p><b>Un error de los árboles publicados.</b> Varios árboles de internet daban como padres de José y Fermín a Pedro Bohórquez Piñero «el Chico», un republicano federal de Ubrique, y a su mujer, Juana Gómez Tocón. Las fechas no encajaban, porque en el padrón de 1867 los dos tenían ya unos cuarenta años. Papá lo ha aclarado: en Ubrique hubo dos familias Bohórquez Gómez, y los árboles las mezclaron. Los padres de José y Fermín eran Bartolomé y Ana María.</p>
<p><b>Ubrique.</b> En el siglo XIX los Bohórquez fueron una de las familias principales de Ubrique, con alcaldes, comerciantes, abogados y políticos. De allí eran también los padres y los abuelos de Bartolomé: los Bohórquez Marchán, los Zarco Morales, los Rubiales y los Olmedo. Y en Ubrique se presentó en público como rejoneador, en 1959, Fermín Bohórquez Escribano.</p>
<p><b>El apellido.</b> Según los tratados de heráldica, los Bohórquez son un linaje de origen castellano, del valle de Runanza, en la merindad de Trasmiera (Cantabria), que bajó a Andalucía con la Reconquista y fundó casa en Villamartín. Gonzalo Argote de Molina cuenta que un caballero Bohórquez que luchó en la batalla del Salado recibió del rey la Banda, y de ahí sus armas. El enlace de los Bohórquez de Ubrique con esa casa está por documentar.</p>""",
        [10], 4, sorted(subtree(20) + subtree(21)), "La rama del bisabuelo José Bohórquez Gómez.", extra=fillbox(
            "Para completar: los padres de Ana María Gómez Bohórquez",
            "Son los que faltan en esta rama. La partida de nacimiento de su hijo Fermín (Registro Civil de Jerez, 10 de septiembre de 1904) da los nombres de sus cuatro abuelos y de dónde eran. Cuando la tengamos, aquí van:",
            ["Padre", "Madre", "De dónde eran"]))

    tamaron = rama(
        "r-tamaron", "Los Mora-Figueroa, marqueses de Tamarón",
        "La bisabuela María Francisca de Mora-Figueroa y Gómez-Imaz (1907–2003), madre de la abuela Victoria, era hija de José de Mora-Figueroa y Ferrer (1871–1929), VII marqués de Tamarón, nacido en El Puerto de Santa María y el mayor de diez hermanos varones: cinco militares, cuatro abogados y un ingeniero.",
        """<p><b>El marquesado.</b> Felipe V creó el título el 4 de abril de 1712 para Diego Pablo de Mora-Figueroa, Miranda y Morales, caballero de Calatrava y vecino de Cádiz, que es nuestro 9.º abuelo. Le sucedió en 1716 su hijo Ignacio Teodomiro, también caballero de Calatrava (desde 1711) y juez comisario de la Santa Hermandad Vieja de Ciudad Real, casado con María Magdalena Pertiet y Boillot, de ascendencia francesa. El III marqués, Diego Mora-Figueroa y Pertiet, fue guardiamarina y alférez de navío. José María Mora-Figueroa y Duarte (1767–1841) sucedió a su hermano Ramón como V marqués; como su hijo José María murió antes que él, el título pasó a su nieto José de Mora-Figueroa y Daza (1839–1909), nacido en Vejer, terrateniente y ganadero de bravo, padre del VII.</p>
<p><b>Los Ferrer.</b> El VI marqués se casó en El Puerto en 1870 con Francisca Ferrer y Rabech (1852–1924), con la que tuvo dieciséis hijos. Su padre, Federico Ferrer Sahuervain, fue elegido diputado a Cortes por El Puerto en 1864 y otra vez en 1865, y llegó a tener ochenta y una fincas repartidas por toda la provincia de Cádiz.</p>
<p><b>Los Gómez-Imaz.</b> El VII marqués se casó con Victoria Gómez-Imaz Vázquez, hija de Manuel Gómez-Imaz (La Habana, 1844 – Sevilla, 1922), periodista, bibliógrafo y académico, presidente de la Real Academia Sevillana de Buenas Letras. Reunió una de las mejores colecciones privadas sobre la Guerra de la Independencia, hoy en la Biblioteca Nacional, y en 1896 publicó el inventario de las 999 obras de arte que los franceses se llevaron de Sevilla en 1810. Su hermano José fue contralmirante y ministro de Marina en 1899 y 1900, justo después del desastre del 98, y su yerno Carlos Cañal y Migolla fue el primer ministro de Trabajo de España, en 1920.</p>
<p>Los hermanos de la bisabuela también dejaron huella. José de Mora-Figueroa y Gómez-Imaz (1899–1976), VIII marqués de Tamarón, fue catedrático, historiador, académico de la Real Academia de la Historia y alcalde de Jerez; Manuel (1904–1964) llegó a contralmirante. Hoy el título lo tiene Santiago de Mora-Figueroa y Williams, IX marqués, diplomático y escritor, embajador de España en el Reino Unido entre 1999 y 2004, hijo del VIII y primo hermano de la abuela Victoria.</p>""",
        [11], 5, subtree(22) + subtree(23), "La rama de la bisabuela María Francisca de Mora-Figueroa hasta la novena generación.")

    vergara = rama(
        "r-vergara", "Los Vergara, del Roncal a Jerez",
        "El abuelo Eduardo Vergara Lacave (1940–2008) era, con toda probabilidad, hijo del bodeguero Juan Vicente Vergara Sanchiz (1899–1974) y de Eugenia María Lacave Patero (1912–2008), que se casaron en 1933 y bautizaron a su hijo Juan Pedro en la Colegial de Jerez en 1937. Juan Vicente tuvo bodega propia: «Juan Vicente Vergara, vinos y coñacs».",
        """<p>Su padre, Juan Vicente Vergara Lassaletta (1831–1900), fue bodeguero e industrial en Jerez; su casa de vinos acabó integrada en Palomino &amp; Vergara a principios del siglo XX. Se casó primero con María Ana Quesada Caugh, con la que tuvo, entre otros, a Mateo Vergara Quesada (1871–1954), dueño de las fábricas de hielo y de lápices de Jerez. Viudo, se casó con la sobrina de su mujer, María Josefa Sanchiz Quesada (1860–1934), hija de Eliseo Sanchiz Basadre y de Isabel Quesada Caugh, que es nuestra tatarabuela.</p>
<p><b>Del Roncal a El Puerto.</b> Los Vergara bodegueros de El Puerto de Santa María descienden de Francisco Vergara Lorea, nacido en 1726 en Urzainqui, en el valle navarro del Roncal, que ya tenía bodegas en El Puerto en 1765. Sus nietos, los hermanos Vergara y Vegas, llevaron la casa a Jerez en 1869. Todo indica que Eduardo Vergara, el padre de Juan Vicente Vergara Lassaletta, era uno de esos hermanos, pero falta el documento que lo pruebe. El libro <i>La familia Vergara del Norte al Sur</i>, de Alfonso de la Calle Vergara, cuenta esta historia.</p>
<p>Los vecinos del valle del Roncal eran todos hidalgos por un privilegio que Carlos III de Navarra confirmó en 1412, y el valle tenía un escudo común a todos ellos, que recuerda la leyenda de la batalla de Olast. Si se documenta el enlace, los Vergara tendrían esa hidalguía.</p>
<p><b>Los Lassaletta.</b> La madre de Juan Vicente, María del Pilar Lassaletta y Fesser (1812–1903), era de una familia de comerciantes de Cádiz. Según la historiadora Fátima Ruiz de Lassaletta, los Lassaletta figuran entre las familias de origen bearnés que impulsaron el comercio del jerez, como los Haurie, los Lacoste y los Domecq.</p>""",
        [12], 4, subtree(24) + subtree(25), "La rama del bisabuelo Juan Vicente Vergara Sanchiz.")

    lacave = rama(
        "r-lacave", "Los Lacave y el título que vino de Quito",
        "La bisabuela Eugenia María Lacave Patero era hija de Pedro Lacave de la Rocha (1883–1926), II marqués de Fiel Pérez Calixto, y de María Josefa Patero d’Etchecopar, que se casaron en Cádiz en 1908.",
        """<p><b>De Navarrenx a Cádiz.</b> Pedro Lacave Miramont nació en 1776 en Navarrenx, en el Béarn, a pocos kilómetros de Usquain, la cuna de los Domecq. Era el sexto de once hijos de unos labradores, y en 1791, durante una crisis de alimentos en Francia, se fue a Cádiz, donde un tío materno tenía casa de comercio. En 1810 fundó la casa de vinos Lacave y Compañía, que llegó a ser una de las grandes exportadoras de vino de Jerez. Se casó en 1821 con la jerezana Ana María Lacoste Salazar, pero no tuvieron hijos, y trajo de Francia a sus sobrinos. Uno de ellos, Pedro Lacave Soulé (nacido en 1809), es nuestro antepasado: se casó en 1831 con Catalina Perrot Vignasse y tuvieron once hijos. Su hermano Juan Pedro fue banquero en Sevilla. Dos familias del mismo rincón del Béarn, los Domecq y los Lacave, vuelven a juntarse en nosotros.</p>
<p><b>Un título que vino de Quito.</b> Lorenzo Lacave Perrot (1846–1905) se casó con María del Carmen de la Rocha y Pérez (1859–1926), para quien Alfonso XIII creó en 1894 el marquesado de Fiel Pérez Calixto. Era el heredero del de Casa Fiel Pérez Calisto, que Fernando VII había concedido en 1820 a un pariente de su familia materna, el quiteño Pedro José María Pérez Calisto, en recuerdo de sus antepasados muertos defendiendo la causa del rey en América. El título sigue en la familia: lo heredaron su hijo Pedro, nuestro tatarabuelo, sus nietos Pedro (1916–2001) y Juan Lacave Patero (1920–2005), hermanos de la bisabuela, y desde 2005 su bisnieto Juan Lacave y Vergara, primo hermano del abuelo Eduardo.</p>
<p><b>Los Patero y los Etchecopar.</b> El segundo apellido de la tatarabuela María Josefa coincide con el de Juan Pablo Echecopar, socio de Pedro Lacave desde 1830, pero no se ha comprobado el parentesco.</p>""",
        [13], 4, subtree(26) + subtree(27), "La rama de la bisabuela Eugenia María Lacave Patero.")

    carrizosa = rama(
        "r-carrizosa", "Los López de Carrizosa",
        "La abuela Beatriz era hija de Ángeles López de Carrizosa y Eizaguirre (nacida en 1918), dama de la Real Maestranza de Ronda, y nieta de Pedro López de Carrizosa y Giles (1868–1930), a quien Alfonso XIII hizo barón de Algar del Campo en 1907, y de María Josefa de Eizaguirre y Dasqui-Leguía (1892–1973).",
        """<p><b>Un linaje de la conquista.</b> Los López de Carrizosa descienden de Rodrigo de Carrizosa, uno de los caballeros que recibieron tierras en el repartimiento de Jerez en 1266. En 1494 los Reyes Católicos llamaron a su corte a dos hidalgos jerezanos del apellido, Pedro Díaz de Carrizosa y el jurado Diego de Carrizosa. Íñigo López de Carrizosa, veinticuatro de Jerez nacido en 1440, fundó en 1479 la capilla funeraria de la familia en San Juan de los Caballeros, hoy sacristía de la iglesia; como su hija Isabel se casó con un señor de Valhermoso, Íñigo es también antepasado nuestro por la línea de los Villavicencio. Desde hace unas veinte generaciones, los López de Carrizosa son patronos del Hospital de la Santa Resurrección de Utrera, fundado en 1514.</p>
<p><b>La línea documentada.</b> Empieza con el veinticuatro Álvaro López de Carrizosa Perea, que murió en 1770 y cuya viuda, Rosa María Adorno, reformó el palacio familiar de Jerez. Su hijo Francisco Álvaro (1760–1803) fue veinticuatro, maestrante de Sevilla y patrono de la fundación de Utrera, y su nieto José López de Carrizosa y Dávila (1800–1842), coronel de Caballería, se casó con Vicenta Pavón, de los marqueses de Casa Pavón, que según todo indica era su prima hermana. Su hijo Francisco Javier López de Carrizosa y Pavón (1825–1882), senador y maestrante de Sevilla, heredó el marquesado de Casa Pavón y recibió el de Mochales en 1878; se casó con María del Rosario de Giles y Rivero, hija de Miguel de Giles, caballero de Carlos III y consejero real de Agricultura.</p>
<p><b>Casa Pavón.</b> Felipe V creó el marquesado el 31 de diciembre de 1706, con el vizcondado previo de Trobal, para Miguel José Pavón de Fuentes, nacido en Jerez en 1671: veinticuatro, coronel de Dragones, mariscal de campo, gobernador de La Habana y caballero de Santiago.</p>
<p><b>Los Eizaguirre.</b> De la familia de la bisabuela María Josefa de Eizaguirre y Dasqui-Leguía no hemos encontrado nada todavía.</p>""",
        [15], 5, [k for k in subtree(30) + subtree(31)], "La rama de la bisabuela Ángeles López de Carrizosa y Eizaguirre.")

    intro_txt = """<div class="prose"><p class="lead">Cada uno de nuestros dieciséis tatarabuelos abre una rama. Aquí van agrupadas por familias, cada una con su historia, un árbol con los antepasados que constan y las fichas de todos ellos. La rama de los marqueses de Casa Domecq, que es la nuestra por partida doble, ocupa las tres primeras secciones: los Domecq, los Villavicencio y los Rivero.</p></div>"""
    body = intro_txt + domecq + villa + rivero + hidalgo + bohorquez + tamaron + vergara + lacave + carrizosa
    return chapter("c3", "Capítulo 3", "Las ramas de la familia", body)


# --------------------------------------------------------------------- títulos
TITULOS = [
    ("Marquesado de Valhermoso de Pozuela", "1681 · Carlos II", "Lorenzo Fernández de Villavicencio y Benítez Melgarejo, nuestro 10.º abuelo por las dos vías. Sus hijo y nieto, II y III marqueses, son también antepasados nuestros. Antes de ser marquesado fue un señorío medieval, que según la tradición fundaron Gonzalo Núñez de Villavicencio y María Alonso de Astudillo."),
    ("Condado de Cañete del Pinar", "1688 · Carlos II", "Creado como Cañete la Real para Francisco José Núñez de Villavicencio y Sandier. Todo indica que lo tuvieron nuestros 6.º abuelos José Núñez de Villavicencio e Inés de Angulo, y más tarde Manuel Núñez de Villavicencio y Olaguer-Feliú, hermano de nuestra trastatarabuela Carmen."),
    ("Marquesado de Campo Real", "1689 · Carlos II", "Su II marqués, Álvaro Diego de Zurita y Haro, es nuestro 9.º abuelo por las dos vías."),
    ("Marquesado de Casa Pavón", "1706 · Felipe V", "Creado con el vizcondado previo de Trobal para Miguel José Pavón de Fuentes, gobernador de La Habana. Lo tuvieron los hermanos de nuestra 5.ª abuela Vicenta Pavón; su hijo Francisco Javier López de Carrizosa y Pavón, nuestro trastatarabuelo, fue el VIII marqués."),
    ("Marquesado de Tamarón", "1712 · Felipe V", "Diego Pablo de Mora-Figueroa, nuestro 9.º abuelo, fue el I marqués. También son antepasados directos el II, el III, el V, el VI y el VII, José de Mora-Figueroa y Ferrer, nuestro tatarabuelo; el IV, Ramón, era hermano del V. Hoy lo tiene el IX, Santiago de Mora-Figueroa y Williams, primo hermano de la abuela Victoria."),
    ("Marquesado de Negrón", "hacia 1800", "Su I marqués, Luis Meléndez y Bruna, es nuestro 6.º abuelo. Pasó a los Hidalgo por su hija Salvadora: Baltasar Hidalgo y Meléndez fue el IV y Salvador Hidalgo y Pardo de Figueroa, nuestro tatarabuelo, el V."),
    ("Marquesado de Mochales", "1878 · Alfonso XII", "Concedido a nuestro trastatarabuelo Francisco Javier López de Carrizosa y Pavón."),
    ("Marquesado de Fiel Pérez Calixto", "1894 · Alfonso XIII", "Creado para nuestra trastatarabuela María del Carmen de la Rocha y Pérez, heredero del de Casa Fiel Pérez Calisto, que Fernando VII concedió en 1820 a un noble de Quito. Su hijo Pedro Lacave de la Rocha, nuestro tatarabuelo, fue el II marqués, y hoy lo tiene el V, Juan Lacave y Vergara."),
    ("Marquesado de Casa Domecq", "1906 · Pío X", "Título pontificio, cuyo uso se autorizó en España ese mismo año. Su I marqués, Pedro Domecq Núñez de Villavicencio, es nuestro tatarabuelo por las dos vías; lo heredaron su hijo Pedro Domecq Rivero y después Pedro Domecq Hidalgo, hermano del abuelo José Manuel."),
    ("Baronía de Algar del Campo", "1907 · Alfonso XIII", "Concedida a nuestro tatarabuelo Pedro López de Carrizosa y Giles. El II barón fue su hijo Pedro, hermano de la bisabuela Ángeles."),
    ("Marquesado de Domecq d’Usquain", "1920 · Alfonso XIII", "Creado para nuestra trastatarabuela Carmen Núñez de Villavicencio, viuda de Pedro Domecq Loustau. El II marqués fue su nieto Pedro Domecq Rivero."),
    ("Marquesado de Pardo de Figueroa", "1927 · Alfonso XIII", "Creado para nuestra trastatarabuela Josefa Pardo de Figueroa y de la Serna, ya viuda. El II marqués fue su hijo Salvador, nuestro tatarabuelo, y el III su nieto Baltasar Hidalgo y Enrile."),
]

PARIENTES_TITULOS = ("En las ramas colaterales aparecen además el marquesado del Mérito (José María López de Carrizosa y Pavón), el de Torresoto de Briviesca (Pedro Nolasco González de Soto, hijo del fundador de González Byass), el de Saavedra (los Imaz, los Cañal y los Mora-Figueroa) y otros títulos de los López de Carrizosa, como el marquesado de Salobral y los condados del Moral de Calatrava y de Peraleja.")


def cap4():
    rows = "".join(f'<tr><th scope="row">{esc(t)}</th><td class="when">{esc(w)}</td><td>{esc(x)}</td></tr>' for t, w, x in TITULOS)
    body = f"""<div class="prose"><p class="lead">Doce títulos nobiliarios pasaron por nuestros antepasados directos. Los más antiguos son del siglo XVII y premiaban servicios a la Corona; los del siglo XX, la obra de familias que habían hecho fortuna con el vino y la ganadería. Al menos dos siguen hoy en manos de parientes cercanos: Tamarón, que tiene Santiago de Mora-Figueroa, primo hermano de la abuela Victoria, y Fiel Pérez Calixto, que tiene Juan Lacave y Vergara, primo hermano del abuelo Eduardo.</p>
<p>Un título se hereda, por lo general, por el primogénito, así que la mayoría de nuestros antepasados no lo tuvo aunque descendamos de quien lo recibió. La tabla dice, para cada uno, quién fue el primer titular y por dónde nos llega.</p></div>
<table class="titles"><thead><tr><th>Título</th><th>Creación</th><th>Por dónde nos llega</th></tr></thead><tbody>{rows}</tbody></table>
<div class="prose"><p class="small">{esc(PARIENTES_TITULOS)}</p>
<p class="small">Hubo además señoríos y mayorazgos más antiguos que los títulos: el señorío de Valhermoso y Pozuela, el de Casarejo y el mayorazgo que fundó Pedro Camacho el Rico en 1507, el más antiguo que se conserva en Jerez.</p></div>"""
    return chapter("c4", "Capítulo 4", "Títulos nobiliarios", body)


def cap5():
    ords = []
    extra = {"Orden de Santiago": "y el Doctor Thebussem, hermano de nuestra trastatarabuela Josefa"}
    for o in ORD:
        people = "; ".join(f"{esc(pname(k))} (nº {fmt(k)}, {esc(rel(k, False))})" for k in o["ks"])
        ex = extra.get(o["o"])
        ords.append(f'<li><b>{esc(o["o"])}</b>: {people}{"; " + esc(ex) if ex else ""}.</li>')
    ords.insert(0, "<li><b>Orden de la Banda</b>: Lorenzo Fernández de Villavicencio, alcaide de Jerez desde 1326 (nº 4.341.856, 21.º abuelo por las dos vías), a quien hizo caballero de la Banda el propio Alfonso XI, que la había fundado.</li>")
    cst = "".join(f'<tr class="{c["st"]}"><th scope="row">{esc(c["h"])}</th><td>{esc(pname(c["k"]))}</td><td class="st">{mark(c["st"])} {esc(c["lab"])}</td><td>{esc(nos(c["t"]))}</td></tr>' for c in COSTADOS)
    body = f"""<div class="prose"><p class="lead">Las órdenes militares de Santiago, Calatrava, Alcántara y Montesa nacieron en la Edad Media como órdenes de caballeros que combatían en la frontera; con los siglos se convirtieron en corporaciones honoríficas que exigían probar la nobleza. Entre nuestros antepasados directos hay seis caballeros de Calatrava, uno de Santiago, uno de San Juan y uno de la Banda, además de caballeros de Carlos III y maestrantes de Sevilla, Ronda y Zaragoza.</p></div>
<ul class="ords">{"".join(ords)}</ul>
<div class="prose"><h2>Los cuatro costados</h2>
<p>Para entrar en las órdenes había que probar la nobleza de sangre de los cuatro abuelos, los «cuatro costados», y las órdenes lo siguen pidiendo hoy. Cada abuelo cuenta por su primer apellido: la nobleza de la abuela Victoria depende de los Bohórquez, no de su madre Mora-Figueroa. Así están los nuestros:</p></div>
<table class="costados"><thead><tr><th>Costado</th><th>Abuelo o abuela</th><th>Situación</th><th>Por qué</th></tr></thead><tbody>{cst}</tbody></table>
<div class="prose"><p>De sangre noble, sin duda: descendemos de marqueses, condes, veinticuatros de Jerez y caballeros de varias órdenes, por muchas ramas distintas. Pero en sentido estricto hoy solo se pueden dar por probados dos costados de los cuatro, los dos Domecq.</p>
<p>La Orden de Calatrava es hoy honorífica y católica. El Real Consejo de las Órdenes Militares examina las pruebas de nobleza de los cuatro costados y propone al Rey la concesión del hábito. Los dos costados Domecq dan medio camino hecho, y el hábito del bisabuelo José Manuel es el mejor punto de partida; los expedientes de pruebas antiguos se guardan en la Sección de Órdenes Militares del Archivo Histórico Nacional. Faltaría probar el costado Bohórquez y cerrar el Vergara. La Real Asociación de Hidalgos de España, en cambio, solo pide la línea de varonía, la de los Domecq, con tres actos positivos de nobleza, y el hábito de Calatrava del bisabuelo es uno de ellos.</p></div>"""
    return chapter("c5", "Capítulo 5", "Órdenes, maestranzas y los cuatro costados", body)


def cap6():
    items = []
    for s in STARS:
        if s.get("k"):
            relx = f"{rel(s['k'])} · nº {fmt(s['k'])}"
        else:
            relx = f"{nos(s['vt'])} {pname(s['via'])} (nº {fmt(s['via'])})"
        items.append(f"""<article class="star"><p class="star-g">{esc(s['g'])} · {esc(s['y'])}</p><h3>{esc(s['h'])}</h3><p class="star-rel">{esc(relx)}</p><p>{esc(nos(s['t']))}</p></article>""")
    body = f"""<div class="prose"><p class="lead">Una selección de antepasados y de parientes muy cercanos, de la conquista de Jerez al siglo XX: los que hicieron historia y los que dejaron las historias más curiosas.</p></div>
<div class="stars">{"".join(items)}</div>"""
    return chapter("c6", "Capítulo 6", "Personajes de la familia", body)


APELLIDOS = [
    ("Adorno", "Familia de origen genovés asentada en Jerez.", [481], None),
    ("Angulo", "Inés de Angulo, condesa de Cañete del Pinar; su padre nació en Lucena.", [133, 266, 532], None),
    ("Beyens", "Comerciantes de Cádiz de origen flamenco; uno de ellos, caballero de Carlos III.", [147, 294, 295], None),
    ("Bohórquez", "Linaje castellano del valle de Runanza, en Trasmiera (Cantabria), que fundó casa en Villamartín. Según Argote de Molina, un Bohórquez que luchó en el Salado recibió la Banda del rey. Nuestra rama es de Ubrique, donde fueron una de las familias principales del siglo XIX.", [5, 10, 20, 40, 80], "En campo de gules, una banda de oro con dragantes de sinople; bordura de azur con dos flores de lis de oro, una en el jefe y otra en la punta, y una columna de plata a cada costado."),
    ("Camacho", "Pedro Camacho de Villavicencio «el Rico», el caballero más acaudalado de Jerez a finales del siglo XV.", [271366, 542733], None),
    ("Carrizosa y López de Carrizosa", "Linaje con casa en Medina de Pomar (Burgos) del que una rama pasó a Jerez; Rodrigo de Carrizosa recibió tierras en el repartimiento de 1266. Sus armas son «parlantes»: los carrizos son cañas.", [15, 30, 60, 120, 240, 480, 271362], "En campo de gules, cuatro carrizos de oro y un león de púrpura echado detrás de las cañas; bordura de azur con ocho aspas de oro."),
    ("Daza", "Josefa Daza y Caballero, madre del VI marqués de Tamarón.", [89], None),
    ("Domecq", "De Usquain, en el Béarn; en bearnés el apellido designa una casa noble. Documentados desde 1364; pasaron a Jerez a finales del siglo XVIII.", [2, 4, 7, 8, 14, 16, 32, 64, 128], "En campo de azur, una espada de plata con la empuñadura de oro, puesta en banda y con la punta hacia arriba, acompañada de dos guantes blancos, uno en lo alto y otro en lo bajo."),
    ("Eizaguirre", "Apellido vasco; la familia de la bisabuela María Josefa está todavía por investigar.", [31], None),
    ("Enrile", "Familia gaditana de origen genovés: militares y marinos.", [19, 38, 76], None),
    ("Ferrer", "Gaditanos asentados en El Puerto; Federico Ferrer Sahuervain fue diputado a Cortes.", [45, 90, 180], None),
    ("Giles", "Miguel de Giles, caballero de Carlos III, diputado y consejero real de Agricultura.", [61, 122, 244], None),
    ("Gómez", "Uno de los apellidos más comunes de España. El nuestro llega por Ana María Gómez Bohórquez, mujer del diputado Bartolomé Bohórquez Rubiales; sus padres están por documentar.", [21], None),
    ("Gómez-Imaz", "Familia de Cádiz con rama en La Habana: un erudito sevillano y un ministro de Marina.", [23, 46, 92], None),
    ("González", "Del segoviano José Antonio González, que llegó a Sanlúcar en 1783; su hijo fundó González Byass.", [35, 70, 140], None),
    ("Haurie", "De Vielleségure, en el Béarn; Juan Haurie está en el origen de la casa Domecq.", [259], None),
    ("Hidalgo", "Medina Sidonia; marqueses de Negrón y de Pardo de Figueroa.", [9, 18, 36, 72], None),
    ("Lacave", "De Navarrenx, en el Béarn; fundaron en Cádiz Lacave y Compañía en 1810.", [13, 26, 52, 104, 208], None),
    ("Lassaletta", "Comerciantes de Cádiz, de origen bearnés según Fátima Ruiz de Lassaletta.", [49], None),
    ("Lasso de la Vega", "Rama de Écija; un caballero de San Juan en 1725.", [267, 534, 1068], None),
    ("Lembeye", "Bearneses; por Catherine Lembeye Haurie se enlazan los Domecq con los Haurie.", [129, 258], None),
    ("Loustau", "Bearneses; el apellido viene del gascón l’ostau, «la casa».", [65], None),
    ("Meléndez", "Sevillanos; Luis Meléndez y Bruna fue el I marqués de Negrón y su hermano Salvador, gobernador de Puerto Rico.", [73, 146], None),
    ("Mora-Figueroa", "Marqueses de Tamarón desde 1712, con casa en Cádiz y luego en Vejer, El Puerto y Jerez.", [11, 22, 44, 88, 176, 352, 704, 1408], None),
    ("Núñez de Villavicencio", "Una de las tres casas de los Villavicencio de Jerez: condes de Cañete del Pinar y señores de Casarejo.", [33, 66, 132, 264, 528], None),
    ("Olaguer-Feliú", "Familia de militares catalanes; un virrey del Río de la Plata.", [67, 134, 268], None),
    ("O'Neale", "Familia jerezana de origen irlandés.", [69], None),
    ("Pardo de Figueroa", "De Arcos y Medina Sidonia; de esta familia salió el Doctor Thebussem.", [37, 74, 148, 296], None),
    ("Patero", "Familia de Cádiz; la tatarabuela María Josefa Patero d’Etchecopar.", [27], None),
    ("Pavón", "Jerezanos; marqueses de Casa Pavón desde 1706.", [121, 242], None),
    ("Quesada", "Familia de Cádiz y Jerez.", [51, 102], None),
    ("Rivero", "Familia jerezana de origen cántabro: las bodegas Rivero-CZ y dos presidentes del Ayuntamiento.", [17, 34, 68, 136], None),
    ("Rocha", "Jerezanos; María del Carmen de la Rocha fue I marquesa de Fiel Pérez Calixto.", [53], None),
    ("Rubiales", "Familia de Ubrique. Ana Rubiales Olmedo fue la madre del diputado Bartolomé Bohórquez Rubiales.", [41, 82], None),
    ("Sanchiz", "Familia de Jerez.", [25, 50], None),
    ("Soto", "De Briviesca (Burgos); Pedro Nolasco de Soto hizo fortuna en México y se estableció en Cádiz.", [71, 142], None),
    ("Spínola", "Genoveses, al servicio del marqués de Villena y de los Reyes Católicos.", [1061, 67841, 135682, 271364], None),
    ("Tixera", "Herederos de la bodega CZ, fundada en 1650.", [137], None),
    ("Vergara", "Bodegueros de El Puerto y Jerez, del valle navarro del Roncal. Las armas más extendidas son las de los Vergara de Guipúzcoa; los de Navarra usaban, según una ejecutoria de 1630, «un puerco jabalí bajo un árbol e una ave rampante».", [3, 6, 12, 24, 48, 96, 192], "En campo de oro, un roble de sinople con un lobo de sable atado al tronco con una cadena de oro (Vergara de Guipúzcoa)."),
    ("Villavicencio", "El linaje de la conquista de Jerez (1264), con presencia continuada en la ciudad desde entonces: alcaides, veinticuatros y marqueses de Valhermoso.", [2120, 4341856, 17367424], None),
    ("Zarco", "Familia de Ubrique. Rafaela Zarco Morales fue la abuela paterna del diputado Bartolomé Bohórquez Rubiales.", [81], None),
    ("Zurita", "Marqueses de Campo Real; los Zurita de Jerez se tenían por descendientes de Fagut de Zurita, caballero de la conquista.", [529, 1058], None),
]


def cap7():
    items = []
    for name, txt, ks, blazon in APELLIDOS:
        nums = ", ".join(fmt(k) for k in ks if str(k) in P)
        items.append(f"""<article class="ap{' has-blazon' if blazon else ''}"><h3>{esc(name)}</h3><p>{esc(txt)}</p>{f'<p class="blazon"><span>Armas.</span> {esc(blazon)}</p>' if blazon else ''}<p class="ap-k">En el árbol: nº {nums}</p></article>""")
    body = f"""<div class="prose"><p class="lead">Los apellidos de nuestros antepasados, de la A a la Z: de dónde vienen, por dónde entran en el árbol y, en los cuatro de nuestros abuelos con escudo documentado, sus armas.</p>
<p class="small">Las armas se describen en el lenguaje de la heráldica: el campo es el fondo del escudo; los colores (esmaltes) se llaman gules (rojo), azur (azul), sinople (verde), sable (negro) y púrpura, y los metales, oro y plata. Un escudo de apellido no pertenece a todos los que lo llevan; describe las armas que usó el linaje.</p></div>
<div class="apellidos">{"".join(items)}</div>"""
    return chapter("c7", "Capítulo 7", "Nuestros apellidos y sus escudos", body)


CRONO = [
    ("1264", "Alfonso X conquista Jerez. Entre los caballeros que reciben casas y tierras está Miguel Fernández de Villavicencio."),
    ("1266", "Rodrigo de Carrizosa recibe tierras en el repartimiento de Jerez."),
    ("1326", "Alfonso XI nombra alcaide del alcázar de Jerez a Lorenzo Fernández de Villavicencio y le hace caballero de la Banda."),
    ("1340", "Batalla del Salado. Según los genealogistas, combatió en ella Gonzalo Núñez de Villavicencio."),
    ("1364", "Bertrand, señor de Domecq, rinde homenaje a Gaston Fébus en Orthez: primera noticia de los Domecq."),
    ("1385", "La casa Domecq de Usquain aparece en el censo del Béarn."),
    ("1406", "Lorenzo Fernández de Villavicencio recupera la alcaidía de Jerez que había tenido su abuelo."),
    ("1479", "Íñigo López de Carrizosa funda la capilla de su familia en San Juan de los Caballeros."),
    ("1492", "Luis de Spínola lucha en la conquista de Granada."),
    ("1507", "Pedro Camacho el Rico funda el mayorazgo más antiguo que se conserva en Jerez."),
    ("1520", "Juan Fernández de Villavicencio y Carrizosa sirve a Carlos V en la guerra de las Comunidades."),
    ("1543", "Juan Fernández de Villavicencio y Mencía Spínola fundan mayorazgo."),
    ("1650", "Se funda en Jerez la bodega CZ, que heredarán los Rivero."),
    ("1666", "Un Juan de Domecq rinde homenaje a Luis XIV."),
    ("1681", "Carlos II crea el marquesado de Valhermoso de Pozuela."),
    ("1688", "Carlos II crea el condado de Cañete la Real, después Cañete del Pinar."),
    ("1706", "Felipe V crea el marquesado de Casa Pavón."),
    ("1711", "Ignacio Teodomiro Mora-Figueroa entra en la Orden de Calatrava."),
    ("1712", "Felipe V crea el marquesado de Tamarón."),
    ("1723", "El II marqués de Valhermoso, comandante general de Canarias hasta 1735."),
    ("1725", "Antonio García Lasso de la Vega, caballero de San Juan. Bruno Núñez de Villavicencio se casa con Francisca de Zurita."),
    ("1726", "Nace en Urzainqui, en el Roncal, Francisco Vergara Lorea."),
    ("1740", "Juan Haurie llega a Jerez como refugiado."),
    ("1764", "Muere Patrick Murphy; Juan Haurie y Juan Pedro Lacoste heredan su negocio de vinos."),
    ("1765", "Los Vergara ya tienen bodegas en El Puerto de Santa María."),
    ("1776", "Nace en Navarrenx Pedro Lacave Miramont."),
    ("1778", "Una Real Orden, fruto del pleito de Juan Haurie, liberaliza el comercio del vino."),
    ("1780", "Jean Domecq se casa con Catherine Lembeye Haurie."),
    ("1783", "José Antonio González llega a Sanlúcar como visitador de las salinas reales."),
    ("1791", "Pedro Agustín Rivero se casa con Tomasa de la Tixera, heredera de la bodega CZ."),
    ("1797", "Antonio Olaguer Feliú, virrey del Río de la Plata hasta 1799."),
    ("1810", "Pedro Lacave funda en Cádiz Lacave y Compañía. Los franceses se llevan 999 obras de arte de Sevilla."),
    ("1822", "La casa de Juan Haurie pasa a llamarse Pedro Domecq."),
    ("1824", "Nace en Usquain Pedro Domecq Loustau."),
    ("1835", "Manuel María González Ángel funda en Jerez la bodega que será González Byass."),
    ("1836", "Adèle Domecq, primer amor de John Ruskin."),
    ("1848", "Pedro Domecq Loustau entra en la bodega de su tío en Jerez."),
    ("1865", "Emilia González de Soto se casa con Tomás Rivero O'Neale."),
    ("1868", "Pedro Domecq Loustau se casa con Carmen Núñez de Villavicencio."),
    ("1869", "Los Vergara y Vegas llevan su casa a Jerez."),
    ("1874", "Hacia este año sale a la venta Fundador, el primer brandy de Jerez."),
    ("1878", "Alfonso XII crea el marquesado de Mochales."),
    ("1880", "El Doctor Thebussem, primer cartero honorario de España."),
    ("1892", "Boda de Pedro Domecq Núñez de Villavicencio y María Rivero González."),
    ("1894", "Se crea el marquesado de Fiel Pérez Calixto."),
    ("1896", "Manuel Gómez-Imaz publica el inventario de los cuadros que los franceses se llevaron de Sevilla."),
    ("1899", "José Gómez-Imaz y Simón, ministro de Marina. Bartolomé Bohórquez Rubiales sale elegido por primera vez diputado por Grazalema."),
    ("1906", "Pío X concede el marquesado pontificio de Casa Domecq."),
    ("1907", "Alfonso XIII crea la baronía de Algar del Campo."),
    ("1919", "Bartolomé Bohórquez Rubiales, senador por Cádiz."),
    ("1920", "Carlos Cañal, primer ministro de Trabajo de España. Alfonso XIII crea el marquesado de Domecq d’Usquain."),
    ("1925", "Boda de los bisabuelos José Manuel Domecq Rivero y María del Carmen Hidalgo Enrile."),
    ("1927", "Alfonso XIII crea el marquesado de Pardo de Figueroa."),
    ("1933", "Boda de Juan Vicente Vergara Sanchiz y Eugenia María Lacave Patero."),
    ("1946", "Fermín Bohórquez Gómez compra la ganadería que lleva su nombre."),
    ("1979", "Muere Pedro Domecq Rivero, II marqués de Casa Domecq y hermano de nuestros dos bisabuelos Domecq. El bisabuelo Juan Pedro lleva desde entonces la ganadería familiar con su hijo Gonzalo."),
    ("1999", "Los Domecq López de Carrizosa fundan la ganadería Casa de los Toreros."),
    ("2005", "Juan Lacave y Vergara, V marqués de Fiel Pérez Calixto."),
]


def cap8():
    rows = "".join(f'<tr><th scope="row">{y}</th><td>{esc(t)}</td></tr>' for y, t in CRONO)
    body = f"""<div class="prose"><p class="lead">Ocho siglos de la familia, año a año.</p></div>
<table class="crono"><tbody>{rows}</tbody></table>"""
    return chapter("c8", "Capítulo 8", "Cronología", body)


def cuantos():
    """Casillas conocidas por generación, contando dos veces a los Domecq–Rivero."""
    known = [int(k) for k, p in P.items() if not p.get("same") and int(k) > 1]
    deepest = max(gen(k) for k in known)
    gnames = {2: "Padres", 3: "Abuelos", 4: "Bisabuelos", 5: "Tatarabuelos", 6: "Trastatarabuelos"}
    rows, tot_pos, tail = [], 0, [0, 0]
    for g in range(2, deepest + 1):
        lo, hi = 2 ** (g - 1), 2 ** g
        n = sum(1 for k in known if lo <= k < hi)
        n += sum(1 for k in known if lo <= k < hi and both_ways(k))
        tot_pos += n
        if g <= 11:
            pct = n * 100 / (hi - lo)
            pct = f"{pct:.0f} %" if pct >= 1 else "menos del 1 %"
            rows.append(f'<tr><th scope="row">{roman(g)}</th><td>{gnames.get(g, f"{g - 2}.º abuelos")}</td>'
                        f'<td class="num">{fmt(hi - lo)}</td><td class="num">{n}</td><td class="num">{pct}</td></tr>')
        else:
            tail[0] += hi - lo
            tail[1] += n
    rows.append(f'<tr><th scope="row">{roman(12)}–{roman(deepest)}</th><td>10.º a {deepest - 2}.º abuelos</td>'
                f'<td class="num">{fmt(tail[0])}</td><td class="num">{tail[1]}</td><td class="num">casi 0 %</td></tr>')
    table = f"""<table class="cuantos"><thead><tr><th>Gen.</th><th>Quiénes</th><th class="num">Casillas</th><th class="num">Conocidas</th><th class="num"></th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>"""
    return table, len(known), tot_pos, deepest


def cap9():
    table, n_people, n_pos, deepest = cuantos()
    opener = f"""<div class="prose"><p class="lead">Aquí está el árbol entero: primero, un abanico con las siete generaciones más cercanas y, después, la lista de todos los antepasados que conocemos, generación a generación.</p>
<h2>Cuántos antepasados conocemos</h2>
<p>Cada generación duplica a la anterior: dos padres, cuatro abuelos, ocho bisabuelos… Esta tabla cuenta, en cada generación, cuántas casillas tiene el árbol y cuántas sabemos ya quién ocupa.</p></div>
{table}
<div class="prose"><p>Si nadie se repitiera, en la generación {roman(deepest)}, la de Miguel Fernández de Villavicencio, tendríamos {fmt(2 ** (deepest - 1))} antepasados, muchos más que todos los habitantes de la Península en el siglo XIII. La explicación es que los árboles se cierran sobre sí mismos: a fuerza de casarse entre vecinos y parientes, las mismas personas ocupan muchas casillas. Los genealogistas lo llaman implejo. A nosotros nos ocurre ya en la generación V, porque los marqueses de Casa Domecq son a la vez tatarabuelos por papá y por mamá, y desde ellos hacia atrás toda su ascendencia cuenta dos veces. Por eso las {n_people} personas que tenemos en el árbol ocupan {n_pos} casillas.</p></div>"""
    fan = f"""<div class="fullpage fanpage"><div class="landscape"><h2 class="chart-title">El abanico de siete generaciones</h2>
<p class="chart-note"><span class="print-only">Gira el libro para leerlo. </span>En el centro estamos nosotros; cada anillo es una generación, hasta los 64 quintos abuelos. Por papá a un lado y por mamá al otro. Las casillas grises son antepasados que aún no conocemos; las rosadas con un número repiten a los marqueses de Casa Domecq y su ascendencia, que nos llegan por los dos lados{', y las rayadas están en duda' if HAS_DOUBT else ''}.</p>
{fan_chart(7, uid="fanbig")}</div></div>"""
    groups = []
    keys = sorted(int(k) for k, p in P.items() if not p.get("same") and int(k) > 1)
    by_gen = {}
    for k in keys:
        by_gen.setdefault(gen(k), []).append(k)
    gnames = {2: "Padres", 3: "Abuelos", 4: "Bisabuelos", 5: "Tatarabuelos", 6: "Trastatarabuelos"}
    for g in sorted(by_gen):
        label = gnames.get(g, f"{g - 2}.º abuelos")
        items = []
        for k in by_gen[g]:
            p = P[str(k)]
            meta = " · ".join(x for x in (p.get("d", ""), nos(p.get("t", ""))) if x)
            items.append(f'<li class="{side(k)}"><span class="ix-k">{fmt(k)}</span> {mark(p.get("c"))} <b>{esc(p["n"])}</b>{f" <span class=ix-m>{esc(meta)}</span>" if meta else ""}</li>')
        groups.append(f'<section class="ix-g"><h3>Generación {roman(g)} · {label}</h3><ul>{"".join(items)}</ul></section>')
    lst = f"""<div class="prose ix-head"><h2>Todos los antepasados, generación a generación</h2><p>La lista completa de los antepasados que constan en el árbol, con su número y su grado de certeza. Las casillas repetidas, la 28–29 y sus antepasados, solo aparecen una vez.</p></div>
<div class="index">{"".join(groups)}</div>"""
    return chapter("c9", "Capítulo 9", "El árbol completo", opener + fan + lst)


def cap10():
    body = """<div class="prose">
<p class="lead">Este libro es un punto de partida. Estos son los huecos que quedan y los sitios donde se pueden llenar.</p>
<ol class="gaps">
<li><b>Los padres de Ana María Gómez Bohórquez.</b> Gracias a papá ya sabemos que el bisabuelo José Bohórquez Gómez era hijo del diputado Bartolomé Bohórquez Rubiales y de Ana María Gómez Bohórquez. Faltan los padres de ella; su segundo apellido hace pensar que era pariente de su marido. La partida literal de nacimiento de su hijo Fermín en el Registro Civil de Jerez (10-IX-1904) los nombra. Para subir más en los Bohórquez, el Archivo Histórico Municipal de Ubrique guarda los padrones del siglo XIX, y la parroquia de Nuestra Señora de la O, los libros de bautismo.</li>
<li><b>Los padres del abuelo Eduardo.</b> Todo apunta a Juan Vicente Vergara Sanchiz y Eugenia María Lacave Patero; su acta de nacimiento (Jerez, 1940) lo confirmaría.</li>
<li><b>Los Vergara del Roncal.</b> Falta el documento que enlace a Eduardo Vergara, padre de Juan Vicente Vergara Lassaletta, con los Vergara y Vegas de El Puerto. El libro de Alfonso de la Calle Vergara y el Archivo Municipal de El Puerto son los sitios donde buscar.</li>
<li><b>Los López de Carrizosa entre 1479 y 1770.</b> Faltan las generaciones entre Íñigo López de Carrizosa y Álvaro López de Carrizosa Perea, y el enlace con Rodrigo de Carrizosa. Archivo Municipal de Jerez y archivo de la Fundación del Hospital de la Santa Resurrección de Utrera.</li>
<li><b>El enlace medieval de los Villavicencio.</b> No se sabe si Alonso Núñez de Villavicencio era hijo del alcaide Lorenzo o de su hermano Nuño, y los señores de Valhermoso entre 1543 y 1681 salen de árboles publicados. La obra de Rafael Sánchez Saus sobre los linajes medievales de Jerez es la referencia.</li>
<li><b>Nombres que faltan.</b> Las familias de las bisabuelas María Josefa de Eizaguirre y Dasqui-Leguía y María Josefa Patero d’Etchecopar, los padres de María del Carmen de la Rocha y de María del Pilar Lassaletta y Fesser, los Hidalgo y Sarria, los González de la Mota y la madre del II marqués de Tamarón, una Gutiérrez del Mazo.</li>
<li><b>El catedrático del Goya o el Velázquez.</b> En la familia se recuerda a un antepasado de la rama de la abuela Victoria, catedrático y estudioso, de origen granadino y con vida en Sevilla, que tuvo un Goya o un Velázquez y lo donó. No lo hemos identificado. Los que más se le parecen son Manuel Gómez-Imaz, erudito sevillano y gran coleccionista, y su nieto José de Mora-Figueroa, VIII marqués de Tamarón, catedrático; pero ninguno era de Granada, y no consta que donaran un cuadro así. La rama Bohórquez, ya corregida, es de terratenientes y políticos de Ubrique, y tampoco tiene un catedrático conocido.</li>
<li><b>Lacoste y Torquemada.</b> No aparecen como antepasados directos. Los Lacoste están muy cerca (Juan Pedro Lacoste en el origen de la casa Domecq; Ana María Lacoste, mujer de Pedro Lacave Miramont), y de Torquemada no hay rastro.</li>
</ol>
<h2>Archivos</h2>
<p>Registro Civil de Jerez (nacimientos, matrimonios y defunciones desde 1871); Archivo Diocesano de Asidonia-Jerez (partidas de Jerez, Ubrique, Villamartín, Arcos y Medina Sidonia); Archivo Municipal de Jerez; Archivo Histórico Municipal de Ubrique; Archivo Municipal de Villamartín; Archivo Municipal de El Puerto de Santa María; Archivo Histórico Provincial de Cádiz (protocolos notariales); Archivo General del Arzobispado de Sevilla (expedientes matrimoniales); Archivo Histórico Nacional, Sección de Órdenes Militares (expedientes de pruebas de los caballeros de Calatrava y Santiago), y, para las familias del Béarn, los Archivos Departamentales de los Pirineos Atlánticos, en Pau.</p>
<h2>Libros</h2>
<p><i>La familia Vergara del Norte al Sur</i>, de Alfonso de la Calle Vergara. <i>El negocio del vino en la ciudad de Cádiz. Historia empresarial de Lacave y Compañía (1810–1927)</i>, de María Vázquez Fariñas y María del Carmen Cózar Navarro. <i>Notas genealógicas</i>, del Doctor Thebussem (1888–1889). <i>La casa de Domecq d’Usquain</i>, de José Antonio Delgado y Orellana (1966). <i>Linajes medievales de Jerez de la Frontera</i>, de Rafael Sánchez Saus. <i>Franceses en la expansión del jerez</i>, de Fátima Ruiz de Lassaletta.</p>
</div>"""
    return chapter("c10", "Capítulo 10", "Lo que falta por descubrir", body)


HERALDIC_SRC = ["hera_domecq", "hera_bohorquez", "hera_carrizosa", "blasonari_vergara", "roncal_hid", "gen_roncal",
                "wk_casacarrizosa", "wk_camporeal", "wk_usquain", "campos_bearn", "wk_haurie", "wk_fundador",
                "gentecadiz_lacave", "wk_calatrava", "om_hoy", "ahn_om", "rahe_ingreso", "wk_ruskin",
                "postal_thebussem", "wk_fbganad", "wk_fbe", "aun_saavedra", "wk_rrt", "escaparate_gb"]


BOOK_SRC = {
    "wk_smfw": ["Wikipedia · Santiago de Mora-Figueroa y Williams", "https://es.wikipedia.org/wiki/Santiago_de_Mora-Figueroa_y_Williams"],
}


def fuentes():
    S.update(BOOK_SRC)
    used = set(HERALDIC_SRC) | set(BOOK_SRC)
    for p in P.values():
        used.update(p.get("s", []))
    for s in STARS + COSTADOS:
        used.update(s.get("s", []))
    items = sorted(((S[k][0], S[k][1]) for k in used if k in S), key=lambda x: x[0].lower())
    lis = "".join(f'<li>{esc(lbl)}' + (f'<br><span class="url">{esc(url)}</span>' if url else '') + '</li>' for lbl, url in items)
    body = f"""<div class="prose"><p class="lead">Las {len(items)} fuentes en que se apoya este libro, por orden alfabético. Los enlaces están vivos en el árbol interactivo.</p></div><ul class="sources">{lis}</ul>"""
    return chapter("fuentes", "Al final", "Fuentes", body)


def completar():
    lines = "".join('<div class="wline"></div>' for _ in range(5))
    many = "".join('<div class="wline"></div>' for _ in range(26))
    return f"""<section class="chapter writein" id="completar">
<header class="ch-head"><p class="ch-num">Para la familia</p><h1>Para completar a mano</h1></header>
<div class="prose"><p>Este árbol empieza en nosotros, pero no termina aquí. Estas páginas son para escribir lo que venga: nuestros nombres y fechas, las bodas, los hijos, y lo que encontremos en los archivos.</p></div>
<div class="wi"><h3>Los hermanos Domecq Vergara</h3>{lines}</div>
<div class="wi"><h3>Nuestras bodas</h3>{lines}</div>
<div class="wi"><h3>La generación que viene</h3>{lines}</div>
<div class="wi wi-page"><h3>Descubrimientos y correcciones</h3>{many}</div>
</section>
<section class="colophon">
<p>Este libro se compuso con las tipografías Alegreya y Alegreya Sans, de Juan Pablo del Peral, e IM Fell English, de Igino Marini, que reproduce las letras que el obispo John Fell legó a la imprenta de Oxford en el siglo XVII.</p>
<p>Se terminó de componer en Jerez de la Frontera en octubre de 2026.</p>
</section>"""


def build_body(toc_entries):
    RAMAS.clear()
    parts = [front_matter(), toc(toc_entries), intro(), cap1(), cap2(), cap3(), cap4(), cap5(), cap6(), cap7(), cap8(), cap9(), cap10(), fuentes(), completar()]
    return "\n".join(parts)


TOC_STRUCTURE = [
    (1, "", "Cómo leer este libro"),
    (1, "1", "Quiénes somos"),
    (1, "2", "La línea más antigua"),
    (1, "3", "Las ramas de la familia"),
    (2, "", "Los Domecq, del Béarn a Jerez"),
    (2, "", "Los Villavicencio y sus alianzas"),
    (2, "", "Los Rivero y los González: CZ y González Byass"),
    (2, "", "Los Hidalgo, los Pardo de Figueroa y los Enrile"),
    (2, "", "Los Bohórquez, de Ubrique"),
    (2, "", "Los Mora-Figueroa, marqueses de Tamarón"),
    (2, "", "Los Vergara, del Roncal a Jerez"),
    (2, "", "Los Lacave y el título que vino de Quito"),
    (2, "", "Los López de Carrizosa"),
    (1, "4", "Títulos nobiliarios"),
    (1, "5", "Órdenes, maestranzas y los cuatro costados"),
    (1, "6", "Personajes de la familia"),
    (1, "7", "Nuestros apellidos y sus escudos"),
    (1, "8", "Cronología"),
    (1, "9", "El árbol completo"),
    (1, "10", "Lo que falta por descubrir"),
    (1, "", "Fuentes"),
    (1, "", "Para completar a mano"),
]

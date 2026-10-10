// Dibuja los mapas del libro en SVG (ilustraciones/mapa_*.svg).
// Datos: es-atlas (municipios y provincias de España, IGN) y world-atlas (Natural Earth).
// Uso: npm install es-atlas world-atlas topojson-client d3-geo && node hacer_mapas.js
const fs = require("fs");
const path = require("path");
const topo = require("topojson-client");
const d3 = require("d3-geo");

const OUT = path.join(__dirname, "..", "ilustraciones");
const C = { sea: "#E9EEF0", land: "#F4EEE1", land2: "#EFE7D6", line: "#B9AE98", prov: "#8D806A", ink: "#2A2622",
            muted: "#6B6357", gold: "#B8902F", red: "#8C2F39", green: "#2E5E4E" };
const FONT = "font-family=\"Alegreya, Georgia, serif\"";
const SANS = "font-family=\"Alegreya Sans SC, Alegreya Sans, sans-serif\"";
const esc = s => s.replace(/&/g, "&amp;").replace(/</g, "&lt;");

function frame(w, h, body, label) {
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 ${w} ${h}" class="map" role="img" aria-label="${esc(label)}">` +
    `<defs><clipPath id="clip-${label.length}"><rect width="${w}" height="${h}"/></clipPath></defs><g clip-path="url(#clip-${label.length})"><rect width="${w}" height="${h}" fill="${C.sea}"/>${body}</g>` +
    `<rect x="3" y="3" width="${w - 6}" height="${h - 6}" fill="none" stroke="${C.ink}" stroke-width="1.2"/>` +
    `<rect x="7" y="7" width="${w - 14}" height="${h - 14}" fill="none" stroke="${C.gold}" stroke-width="0.6"/></svg>`;
}

function compass(x, y, r) {
  return `<g transform="translate(${x},${y})" stroke="${C.ink}" stroke-width="0.6">` +
    `<circle r="${r}" fill="none" stroke="${C.gold}"/>` +
    `<path d="M0,${-r - 6} L${r * 0.28},0 L0,${r * 0.2} L${-r * 0.28},0 Z" fill="${C.ink}"/>` +
    `<path d="M0,${r + 4} L${r * 0.22},0 L${-r * 0.22},0 Z" fill="#fff"/>` +
    `<text y="${-r - 9}" text-anchor="middle" font-size="9" ${SANS} fill="${C.ink}" stroke="none">N</text></g>`;
}

function label(p, name, sub, opts = {}) {
  const [x, y] = p;
  const dx = opts.dx ?? 6, dy = opts.dy ?? -3, anchor = opts.anchor ?? "start", big = opts.big;
  const fs1 = big ? 15 : 11.5, fs2 = big ? 9.5 : 8.4;
  let t = `<circle cx="${x}" cy="${y}" r="${big ? 4.2 : 2.8}" fill="${big ? C.red : C.ink}" stroke="#fff" stroke-width="1"/>`;
  t += `<text x="${x + dx}" y="${y + dy}" text-anchor="${anchor}" font-size="${fs1}" ${FONT} fill="${C.ink}" paint-order="stroke" stroke="${C.land}" stroke-width="3" stroke-linejoin="round"${big ? ' font-weight="700"' : ""}>${esc(name)}</text>`;
  if (sub) t += `<text x="${x + dx}" y="${y + dy + fs2 + 2}" text-anchor="${anchor}" font-size="${fs2}" ${FONT} font-style="italic" fill="${C.muted}" paint-order="stroke" stroke="${C.land}" stroke-width="3" stroke-linejoin="round">${esc(sub)}</text>`;
  return t;
}

// ---------------------------------------------------------------- Cádiz y Sevilla
(function cadiz() {
  const es = require("es-atlas/es/municipalities.json");
  const muni = topo.feature(es, es.objects.municipalities);
  const prov = topo.feature(es, es.objects.provinces);
  const W = 640, H = 600;
  const box = { type: "MultiPoint", coordinates: [[-6.62, 35.98], [-5.0, 35.98], [-5.0, 37.48], [-6.62, 37.48]] };
  const proj = d3.geoConicConformal().parallels([36, 38]).rotate([5.8, 0]).fitExtent([[10, 10], [W - 10, H - 10]], box);
  const gp = d3.geoPath(proj).digits(1);
  const near = f => ["11", "41", "29", "21"].includes(String(f.id).slice(0, 2));
  let body = "";
  body += `<g fill="${C.land}" stroke="${C.line}" stroke-width="0.35">` +
    muni.features.filter(near).map(f => {
      const home = ["11020", "11038", "11027", "11032", "11012", "11023", "11006", "11039", "41091", "41095"].includes(String(f.id));
      return `<path d="${gp(f)}" fill="${home ? C.land2 : C.land}"/>`;
    }).join("") + "</g>";
  body += `<path d="${gp(topo.mesh(es, es.objects.provinces, (a, b) => a !== b))}" fill="none" stroke="${C.prov}" stroke-width="1.1" stroke-dasharray="4 2"/>`;
  const P = (lon, lat) => proj([lon, lat]);
  const L = [
    [[-6.136, 36.686], "Jerez de la Frontera", "Domecq, Villavicencio, López de Carrizosa, Rivero", { big: true, dx: 8, dy: 4 }],
    [[-6.351, 36.778], "Sanlúcar de Barrameda", "González", { anchor: "end", dx: -6 }],
    [[-6.233, 36.594], "El Puerto de Santa María", "Mora-Figueroa, Vergara, Ferrer", { anchor: "end", dx: -6, dy: 2 }],
    [[-6.288, 36.527], "Cádiz", "Lacave, Enrile, Gómez-Imaz", { anchor: "end", dx: -6, dy: 8 }],
    [[-5.927, 36.457], "Medina Sidonia", "Hidalgo, Pardo de Figueroa", {}],
    [[-5.811, 36.749], "Arcos de la Frontera", "Pardo de Figueroa", {}],
    [[-5.966, 36.252], "Vejer de la Frontera", "Mora-Figueroa y Daza", {}],
    [[-5.446, 36.678], "Ubrique", "Bohórquez", {}],
    [[-5.781, 37.185], "Utrera", "López de Carrizosa", {}],
    [[-5.984, 37.389], "Sevilla", "Gómez-Imaz, Meléndez, Maestranza", {}],
  ];
  for (const [ll, n, s, o] of L) body += label(P(...ll), n, s, o);
  body += `<text x="${W - 30}" y="${H - 24}" text-anchor="end" font-size="13" ${SANS} letter-spacing="2" fill="${C.muted}">Cádiz y Sevilla</text>`;
  body += `<text x="70" y="${H - 60}" font-size="12" ${FONT} font-style="italic" fill="#7A8C96">Océano Atlántico</text>`;
  body += compass(W - 50, 56, 16);
  fs.writeFileSync(path.join(OUT, "mapa_cadiz.svg"), frame(W, H, body, "Mapa de Cádiz y Sevilla con los lugares de la familia"));
})();

// ---------------------------------------------------------------- Orígenes en Europa
(function europa() {
  const world = require("world-atlas/countries-50m.json");
  const land = topo.feature(world, world.objects.land);
  const borders = topo.mesh(world, world.objects.countries, (a, b) => a !== b);
  const W = 640, H = 560;
  const box = { type: "MultiPoint", coordinates: [[-11.5, 35.2], [12.5, 35.2], [12.5, 56.2], [-11.5, 56.2], [0.5, 56.2], [0.5, 35.2]] };
  const proj = d3.geoConicConformal().parallels([38, 52]).rotate([0, 0]).fitExtent([[0, 0], [W, H]], box).clipExtent([[0, 0], [W, H]]);
  const gp = d3.geoPath(proj).digits(1);
  let body = `<path d="${gp(land)}" fill="${C.land}" stroke="${C.line}" stroke-width="0.6"/>`;
  body += `<path d="${gp(borders)}" fill="none" stroke="${C.line}" stroke-width="0.5" stroke-dasharray="2 1.5"/>`;
  const jerez = proj([-6.136, 36.686]);
  const O = [
    [[-0.887, 43.414], "Béarn", "Domecq, Lacave, Haurie, Loustau", { dx: 7, dy: -8 }],
    [[-0.94, 42.83], "Valle del Roncal", "Vergara", { dx: 7, dy: 6 }],
    [[-3.6, 43.45], "Trasmiera", "Bohórquez, Rivero", { anchor: "end", dx: -7, dy: -10 }],
    [[-3.49, 42.93], "Medina de Pomar", "López de Carrizosa", { anchor: "end", dx: -7, dy: 2 }],
    [[-3.32, 42.55], "Briviesca", "Soto", { dx: 7, dy: 12 }],
    [[-4.12, 40.95], "Segovia", "González", { anchor: "end", dx: -7 }],
    [[2.17, 41.39], "Cataluña", "Olaguer-Feliú", {}],
    [[8.93, 44.41], "Génova", "Spínola, Adorno, Enrile", { anchor: "end", dx: -7, dy: -6 }],
    [[4.4, 51.0], "Flandes", "Beyens", {}],
    [[-6.9, 54.6], "Irlanda", "O’Neale", { dx: 7 }],
  ];
  let lines = "";
  for (const [ll] of O) {
    const p = proj(ll);
    const mx = (p[0] + jerez[0]) / 2, my = (p[1] + jerez[1]) / 2;
    const dx = jerez[0] - p[0], dy = jerez[1] - p[1];
    const cx = mx - dy * 0.16, cy = my + dx * 0.16;
    lines += `<path d="M${p[0].toFixed(1)},${p[1].toFixed(1)} Q${cx.toFixed(1)},${cy.toFixed(1)} ${jerez[0].toFixed(1)},${jerez[1].toFixed(1)}" fill="none" stroke="${C.gold}" stroke-width="1.1" stroke-dasharray="1 0" opacity="0.9"/>`;
  }
  body += lines;
  for (const [ll, n, s, o] of O) body += label(proj(ll), n, s, o);
  body += label(jerez, "Jerez", "", { big: true, dx: 8, dy: 5 });
  body += `<g transform="translate(${W - 222},${H - 106})"><rect width="196" height="82" fill="#fff" fill-opacity="0.75" stroke="${C.gold}" stroke-width="0.6"/>` +
    `<text x="10" y="18" font-size="10" ${SANS} letter-spacing="1.5" fill="${C.red}">Y en ultramar</text>` +
    `<text x="10" y="36" font-size="10.5" ${FONT} fill="${C.ink}">La Habana · Gómez-Imaz</text>` +
    `<text x="10" y="52" font-size="10.5" ${FONT} fill="${C.ink}">Quito · Fiel Pérez Calixto</text>` +
    `<text x="10" y="68" font-size="10.5" ${FONT} fill="${C.ink}">México · Soto</text></g>`;
  body += `<text x="40" y="400" font-size="13" ${FONT} font-style="italic" fill="#7A8C96">Océano Atlántico</text>`;
  body += `<text x="452" y="428" font-size="12" ${FONT} font-style="italic" fill="#7A8C96">Mar Mediterráneo</text>`;
  body += compass(W - 46, 50, 15);
  fs.writeFileSync(path.join(OUT, "mapa_origenes.svg"), frame(W, H, body, "Mapa de los lugares de origen de las familias"));
})();
console.log("mapas listos");

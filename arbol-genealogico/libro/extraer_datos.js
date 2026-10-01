// Extrae los datos del árbol (arbol.html) a JSON para generar el libro.
const fs = require("fs");
const path = require("path");
const html = fs.readFileSync(path.join(__dirname, "..", "arbol.html"), "utf8");
const start = html.indexOf("const S = {");
const end = html.indexOf("/* Cifras de cabecera */");
if (start < 0 || end < 0) throw new Error("No encuentro los datos en arbol.html");
const code = html.slice(start, end) +
  "\nmodule.exports = {S, P, LINE, DUP, CONF, STARS, COSTADOS, ORD, EXTRA_SRC};";
const m = { exports: {} };
new Function("module", "exports", code)(m, m.exports);
process.stdout.write(JSON.stringify(m.exports));

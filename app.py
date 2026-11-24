import os
import json
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
CLAVE_ACCESO = os.environ.get("CPRE2_ACCESS_KEY", "CELSO2026").strip()
ARCHIVO_DB = os.environ.get("CPRE2_DB_FILE", "cpre2_datos.json")

DICCIONARIO_PALABRAS = {
    "agua": "Sustantivo. Líquido transparente e indispensable para la vida.",
    "aire": "Sustantivo. Mezcla de gases que rodea la Tierra.",
    "amigo": "Sustantivo. Persona con quien se comparte confianza y cercanía.",
    "aprender": "Verbo. Adquirir conocimientos o habilidades con práctica y estudio.",
    "archivo": "Sustantivo. Conjunto organizado de datos o documento guardado.",
    "ciencia": "Sustantivo. Conocimiento estructurado mediante observación y prueba.",
    "codigo": "Sustantivo. Conjunto de instrucciones para ejecutar un programa.",
    "correo": "Sustantivo. Medio electrónico para enviar, recibir y asociar información.",
    "dato": "Sustantivo. Valor o información concreta lista para registrarse u ordenarse.",
    "diccionario": "Sustantivo. Obra o módulo que reúne palabras con su definición.",
    "estudio": "Sustantivo. Dedicación constante para comprender un tema.",
    "futuro": "Sustantivo. Tiempo posterior al momento actual.",
    "historia": "Sustantivo. Relato y estudio de los hechos del pasado.",
    "idioma": "Sustantivo. Sistema de comunicación propio de una lengua.",
    "juego": "Sustantivo. Dinámica interactiva con reglas y puntuación.",
    "lenguaje": "Sustantivo. Capacidad y sistema de expresar ideas mediante signos.",
    "libro": "Sustantivo. Obra escrita o digital organizada por temas o páginas.",
    "logica": "Sustantivo. Principio de coherencia y razonamiento ordenado.",
    "mundo": "Sustantivo. Conjunto de todo lo existente o el planeta y sus habitantes.",
    "noticia": "Sustantivo. Información relevante o actualizada del día.",
    "numero": "Sustantivo. Expresión matemática de cantidad o posición.",
    "orden": "Sustantivo. Organización de elementos bajo un criterio.",
    "palabra": "Sustantivo. Unidad de lengua con significado propio.",
    "practica": "Sustantivo. Ejercicio repetido para ganar soltura y dominio.",
    "progreso": "Sustantivo. Avance constante en una tarea o aprendizaje.",
    "proyecto": "Sustantivo. Plan estructurado para construir o lograr algo.",
    "sistema": "Sustantivo. Conjunto de elementos conectados que cumplen una función.",
    "tiempo": "Sustantivo. Sucesión continua de momentos y días.",
    "trabajo": "Sustantivo. Esfuerzo aplicado para producir o resolver algo.",
    "vida": "Sustantivo. Estado de actividad y existencia de los seres vivos."
}

NOTICIAS_DIARIAS = [
    "Noticia del día: Mantén tus registros limpios y ordénalos antes de exportarlos.",
    "Noticia del día: Guarda tu progreso con tu correo para no perder ningún avance.",
    "Noticia del día: Consulta palabras en el diccionario y agrega definiciones nuevas.",
    "Noticia del día: Usa fórmulas en la hoja de cálculo para evitar errores manuales.",
    "Noticia del día: Un repaso corto cada día mantiene todo tu trabajo al día.",
    "Noticia del día: Verifica siempre tu clave de acceso y tus datos guardados."
]

VIDEOS_DIARIOS = [
    {"titulo": "Ordenamiento rápido de listas y números", "detalle": "Aprende a ordenar filas de forma ascendente o descendente."},
    {"titulo": "Fórmulas esenciales en hoja de cálculo", "detalle": "Suma y calcula valores de forma directa en la tabla."},
    {"titulo": "Cómo usar y ampliar el diccionario", "detalle": "Busca definiciones y guarda términos nuevos al instante."},
    {"titulo": "Guardar y cargar progreso por correo", "detalle": "Vincula tu correo electrónico para recuperar tu sesión."}
]

def cargar_db():
    if not os.path.exists(ARCHIVO_DB):
        return {"usuarios": {}, "diccionario_extra": {}}
    try:
        with open(ARCHIVO_DB, "r", encoding="utf-8") as f:
            data = json.load(f)
            if isinstance(data, dict):
                data.setdefault("usuarios", {})
                data.setdefault("diccionario_extra", {})
                return data
    except Exception:
        pass
    return {"usuarios": {}, "diccionario_extra": {}}

def guardar_db(data):
    with open(ARCHIVO_DB, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE 2</title>
<style>
* { box-sizing: border-box; }
body {
  margin: 0;
  background: #140507;
  color: #fff5f5;
  font-family: system-ui, -apple-system, Arial, sans-serif;
  font-size: 16px;
  padding-bottom: 60px;
}
header {
  background: #2a060b;
  border-bottom: 2px solid #991b1b;
  padding: 15px 14px;
  text-align: center;
}
header h1 { margin: 0; font-size: 21px; font-weight: 900; color: #ffffff; }
header p { margin: 5px 0 0; font-size: 13px; color: #fca5a5; }
.wrap { max-width: 780px; margin: 0 auto; padding: 14px; }
.card {
  background: #22070b;
  border: 1px solid #7f1d1d;
  border-radius: 10px;
  padding: 15px;
  margin-bottom: 15px;
}
h2 { margin: 0 0 10px; font-size: 18px; color: #fecaca; }
label { display: block; font-size: 14px; font-weight: 700; color: #fee2e2; margin-top: 8px; }
input[type="text"], input[type="password"], input[type="email"], textarea {
  width: 100%;
  padding: 11px 12px;
  font-size: 15px;
  border-radius: 7px;
  border: 1px solid #991b1b;
  background: #120305;
  color: #ffffff;
  margin-top: 6px;
}
textarea { min-height: 88px; font-family: monospace; }
button {
  width: 100%;
  padding: 12px;
  font-size: 15px;
  font-weight: 800;
  border-radius: 7px;
  border: none;
  background: #dc2626;
  color: #ffffff;
  cursor: pointer;
  margin-top: 8px;
}
button:hover { background: #ef4444; }
button.sec {
  background: #3b0a11;
  color: #fecaca;
  border: 1px solid #991b1b;
}
.row-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 8px; }
.box {
  background: #120305;
  border-left: 4px solid #ef4444;
  border-radius: 0 7px 7px 0;
  padding: 11px 12px;
  margin-top: 10px;
  font-size: 14.5px;
  line-height: 1.45;
  white-space: pre-line;
  color: #fff5f5;
}
table { width: 100%; border-collapse: collapse; margin-top: 10px; }
th, td { border: 1px solid #7f1d1d; padding: 6px; text-align: center; }
th { background: #2e080e; font-size: 13px; color: #fecaca; }
td input {
  width: 100%;
  margin: 0;
  padding: 8px;
  font-size: 14px;
  background: #120305;
  color: #ffffff;
  border: 1px solid #5c141c;
  border-radius: 4px;
}
.estado-msg { font-size: 13.5px; color: #fca5a5; margin-top: 8px; }
.overlay-clave {
  position: fixed;
  inset: 0;
  background: #140507;
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
}
.oculto { display: none !important; }
</style>
</head>
<body>

<div id="pantallaClave" class="overlay-clave">
  <div class="card" style="max-width:420px;width:100%;">
    <h2>Clave de Acceso</h2>
    <p style="margin:6px 0 10px;font-size:14px;color:#fca5a5;">Ingresa la clave de acceso para entrar a C-Pre 2.</p>
    <label for="inpClave">Clave:</label>
    <input type="password" id="inpClave" placeholder="Escribe la clave de acceso...">
    <button type="button" onclick="verificarClave()">ENTRAR</button>
    <div id="msgClave" class="estado-msg"></div>
  </div>
</div>

<header>
  <h1>C-PRE 2</h1>
  <p id="lblDiaApp"></p>
</header>

<div id="appPrincipal" class="wrap oculto">
  <div class="card">
    <h2>Correo Electrónico y Progreso</h2>
    <label for="inpCorreo">Correo electrónico:</label>
    <input type="email" id="inpCorreo" placeholder="correo@ejemplo.com">
    <div class="row-2">
      <button type="button" onclick="cargarProgreso()">CARGAR PROGRESO</button>
      <button type="button" class="sec" onclick="guardarProgreso()">GUARDAR PROGRESO</button>
    </div>
    <div id="msgProgreso" class="estado-msg">Ingresa tu correo para guardar o cargar tu progreso.</div>
  </div>

  <div class="card">
    <h2>Diccionario</h2>
    <label for="inpPalabra">Palabra:</label>
    <input type="text" id="inpPalabra" placeholder="Escribe una palabra...">
    <button type="button" onclick="buscarPalabra()">BUSCAR EN DICCIONARIO</button>
    <div id="resDiccionario" class="box">Escribe una palabra para consultar su definición.</div>
    <div id="bloqueNuevaPalabra" class="oculto" style="margin-top:10px;">
      <label for="inpDefNueva">Agregar definición para esta palabra:</label>
      <input type="text" id="inpDefNueva" placeholder="Escribe la definición...">
      <button type="button" class="sec" onclick="agregarPalabra()">GUARDAR DEFINICIÓN</button>
    </div>
  </div>

  <div class="card">
    <h2>Noticias y Videos (Actualización Diaria)</h2>
    <div id="boxNoticia" class="box"></div>
    <div id="boxVideo" class="box"></div>
  </div>

  <div class="card">
    <h2>Archivos y Ordenamiento</h2>
    <label for="inpNombreArchivo">Nombre de archivo:</label>
    <input type="text" id="inpNombreArchivo" value="datos_cpre2.txt">
    <label for="txtDatos">Contenido / registros (uno por línea):</label>
    <textarea id="txtDatos" placeholder="Escribe tus registros aquí..."></textarea>
    <div class="row-2">
      <button type="button" onclick="ordenarDatos('asc')">ORDENAR ASCENDENTE</button>
      <button type="button" class="sec" onclick="ordenarDatos('desc')">ORDENAR DESCENDENTE</button>
    </div>
    <button type="button" class="sec" onclick="exportarArchivo()">GUARDAR / DESCARGAR ARCHIVO</button>
  </div>

  <div class="card">
    <h2>Hoja de Cálculo</h2>
    <table>
      <thead>
        <tr>
          <th>Fila</th>
          <th>Dato A</th>
          <th>Dato B</th>
          <th>Suma (A+B)</th>
        </tr>
      </thead>
      <tbody id="tablaCuerpo"></tbody>
    </table>
    <button type="button" onclick="recalcularTabla()">CALCULAR</button>
    <div id="resTabla" class="box">Total general: 0</div>
  </div>
</div>

<script id="jsonDiccionario" type="application/json">__DICCIONARIO_JSON__</script>
<script id="jsonNoticias" type="application/json">__NOTICIAS_JSON__</script>
<script id="jsonVideos" type="application/json">__VIDEOS_JSON__</script>

<script>
let DICCIONARIO = JSON.parse(document.getElementById("jsonDiccionario").textContent);
const NOTICIAS = JSON.parse(document.getElementById("jsonNoticias").textContent);
const VIDEOS = JSON.parse(document.getElementById("jsonVideos").textContent);

function normalizar(texto) {
  return (texto || "")
    .trim()
    .toLowerCase()
    .normalize("NFD")
    .replace(/[\\u0300-\\u036f]/g, "");
}

async function verificarClave() {
  const clave = document.getElementById("inpClave").value.trim();
  const msg = document.getElementById("msgClave");
  try {
    const r = await fetch("/api/clave", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ clave: clave })
    });
    const d = await r.json();
    if (d.ok) {
      document.getElementById("pantallaClave").classList.add("oculto");
      document.getElementById("appPrincipal").classList.remove("oculto");
    } else {
      msg.textContent = "Clave incorrecta.";
    }
  } catch (e) {
    msg.textContent = "Error al validar la clave.";
  }
}

function cargarDiarios() {
  const hoy = new Date();
  document.getElementById("lblDiaApp").textContent = "Fecha: " + hoy.toLocaleDateString("es-VE");
  const inicio = new Date(hoy.getFullYear(), 0, 0);
  const diaAno = Math.floor((hoy - inicio) / 86400000);

  document.getElementById("boxNoticia").textContent = NOTICIAS[diaAno % NOTICIAS.length];
  const vid = VIDEOS[diaAno % VIDEOS.length];
  document.getElementById("boxVideo").textContent = "Video del día: " + vid.titulo + "\\n" + vid.detalle;
}

function montarTabla(filas) {
  const tbody = document.getElementById("tablaCuerpo");
  tbody.innerHTML = "";
  for (let i = 0; i < 4; i++) {
    const f = (filas && filas[i]) ? filas[i] : ["", ""];
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td>${i + 1}</td>` +
      `<td><input type="text" class="col-a" value="${(f[0] || "").replace(/"/g, "&quot;")}"></td>` +
      `<td><input type="text" class="col-b" value="${(f[1] || "").replace(/"/g, "&quot;")}"></td>` +
      `<td class="col-s">0</td>`;
    tbody.appendChild(tr);
  }
  recalcularTabla();
}

function recalcularTabla() {
  let total = 0;
  document.querySelectorAll("#tablaCuerpo tr").forEach(tr => {
    const a = parseFloat(tr.querySelector(".col-a").value.replace(",", ".")) || 0;
    const b = parseFloat(tr.querySelector(".col-b").value.replace(",", ".")) || 0;
    const s = a + b;
    tr.querySelector(".col-s").textContent = s;
    total += s;
  });
  document.getElementById("resTabla").textContent = "Total general: " + total;
}

function leerTabla() {
  const filas = [];
  document.querySelectorAll("#tablaCuerpo tr").forEach(tr => {
    filas.push([
      tr.querySelector(".col-a").value,
      tr.querySelector(".col-b").value
    ]);
  });
  return filas;
}

function buscarPalabra() {
  const raw = document.getElementById("inpPalabra").value.trim();
  const box = document.getElementById("resDiccionario");
  const bloqueNueva = document.getElementById("bloqueNuevaPalabra");
  if (!raw) {
    box.textContent = "Escribe una palabra primero.";
    bloqueNueva.classList.add("oculto");
    return;
  }
  const clave = normalizar(raw);
  if (DICCIONARIO[clave]) {
    box.textContent = raw + ": " + DICCIONARIO[clave];
    bloqueNueva.classList.add("oculto");
  } else {
    box.textContent = "No se encontró '" + raw + "' en el diccionario.";
    bloqueNueva.classList.remove("oculto");
  }
}

async function agregarPalabra() {
  const raw = document.getElementById("inpPalabra").value.trim();
  const def = document.getElementById("inpDefNueva").value.trim();
  if (!raw || !def) return;
  const clave = normalizar(raw);
  DICCIONARIO[clave] = def;
  document.getElementById("resDiccionario").textContent = raw + ": " + def;
  document.getElementById("bloqueNuevaPalabra").classList.add("oculto");
  document.getElementById("inpDefNueva").value = "";
  try {
    await fetch("/api/diccionario", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ palabra: clave, definicion: def })
    });
  } catch (e) {}
}

function ordenarDatos(sentido) {
  const items = document.getElementById("txtDatos").value
    .split("\\n")
    .map(x => x.trim())
    .filter(x => x.length > 0);
  items.sort((a, b) => {
    const na = parseFloat(a);
    const nb = parseFloat(b);
    if (!isNaN(na) && !isNaN(nb)) {
      return sentido === "asc" ? na - nb : nb - na;
    }
    return sentido === "asc" ? a.localeCompare(b, "es") : b.localeCompare(a, "es");
  });
  document.getElementById("txtDatos").value = items.join("\\n");
}

function exportarArchivo() {
  const nombre = (document.getElementById("inpNombreArchivo").value || "datos_cpre2.txt").trim();
  const blob = new Blob([document.getElementById("txtDatos").value], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
}

async function guardarProgreso() {
  const correo = document.getElementById("inpCorreo").value.trim().toLowerCase();
  const msg = document.getElementById("msgProgreso");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo válido.";
    return;
  }
  const payload = {
    correo: correo,
    progreso: {
      nombre_archivo: document.getElementById("inpNombreArchivo").value,
      datos: document.getElementById("txtDatos").value,
      tabla: leerTabla(),
      palabra: document.getElementById("inpPalabra").value
    }
  };
  try {
    const r = await fetch("/api/progreso/guardar", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    const d = await r.json();
    msg.textContent = d.mensaje || "Guardado.";
  } catch (e) {
    msg.textContent = "Error al guardar.";
  }
}

async function cargarProgreso() {
  const correo = document.getElementById("inpCorreo").value.trim().toLowerCase();
  const msg = document.getElementById("msgProgreso");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo válido.";
    return;
  }
  try {
    const r = await fetch("/api/progreso/cargar?correo=" + encodeURIComponent(correo));
    const d = await r.json();
    if (!d.encontrado) {
      msg.textContent = "No hay progreso guardado para ese correo.";
      return;
    }
    const p = d.progreso || {};
    if (p.nombre_archivo) document.getElementById("inpNombreArchivo").value = p.nombre_archivo;
    if (typeof p.datos === "string") document.getElementById("txtDatos").value = p.datos;
    if (Array.isArray(p.tabla)) montarTabla(p.tabla);
    if (p.palabra) document.getElementById("inpPalabra").value = p.palabra;
    msg.textContent = "Progreso cargado para " + correo + ".";
  } catch (e) {
    msg.textContent = "Error al cargar.";
  }
}

document.getElementById("inpClave").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    verificarClave();
  }
});

cargarDiarios();
montarTabla([]);
</script>
</body>
</html>
"""

@app.route("/")
def index():
    db = cargar_db()
    diccionario_total = dict(DICCIONARIO_PALABRAS)
    diccionario_total.update(db.get("diccionario_extra", {}))
    return (
        HTML_PAGE
        .replace("__DICCIONARIO_JSON__", json.dumps(diccionario_total, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__NOTICIAS_JSON__", json.dumps(NOTICIAS_DIARIAS, ensure_ascii=True).replace("</", "<\\/"))
        .replace("__VIDEOS_JSON__", json.dumps(VIDEOS_DIARIOS, ensure_ascii=True).replace("</", "<\\/"))
    )

@app.route("/api/clave", methods=["POST"])
def api_clave():
    datos = request.get_json(silent=True) or {}
    clave = (datos.get("clave") or "").strip()
    return jsonify({"ok": clave == CLAVE_ACCESO})

@app.route("/api/diccionario", methods=["POST"])
def api_diccionario():
    datos = request.get_json(silent=True) or {}
    palabra = (datos.get("palabra") or "").strip().lower()
    definicion = (datos.get("definicion") or "").strip()
    if palabra and definicion:
        db = cargar_db()
        db["diccionario_extra"][palabra] = definicion
        guardar_db(db)
    return jsonify({"ok": True})

@app.route("/api/progreso/guardar", methods=["POST"])
def api_guardar_progreso():
    datos = request.get_json(silent=True) or {}
    correo = (datos.get("correo") or "").strip().lower()
    progreso = datos.get("progreso") or {}
    if not correo or "@" not in correo:
        return jsonify({"ok": False, "mensaje": "Correo inválido."}), 400
    db = cargar_db()
    db["usuarios"][correo] = {
        "actualizado": datetime.utcnow().isoformat(),
        "datos": progreso
    }
    guardar_db(db)
    return jsonify({"ok": True, "mensaje": f"Progreso guardado para {correo}."})

@app.route("/api/progreso/cargar", methods=["GET"])
def api_cargar_progreso():
    correo = (request.args.get("correo") or "").strip().lower()
    db = cargar_db()
    registro = db.get("usuarios", {}).get(correo)
    if not registro:
        return jsonify({"encontrado": False})
    return jsonify({"encontrado": True, "progreso": registro.get("datos", {})})

if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

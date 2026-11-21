import csv
import io
import math
import os
import statistics
from datetime import datetime
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

CODIGOS_ACCESO = {
    "DEMO2026": {"plan": "DEMO", "limite": 20},
    "VIP100": {"plan": "VIP", "limite": 100},
    "EXCELSO99": {"plan": "PRO", "limite": 500},
}

NOTICIAS_BASE = [
    {
        "titulo": "Avances en eficiencia energética y cálculo computacional",
        "categoria": "Tecnología",
        "fuente": "Portal Tech",
        "fecha": "2026",
        "resumen": "Nuevos enfoques buscan reducir el consumo energético en sistemas de procesamiento intensivo y modelos de cómputo.",
    },
    {
        "titulo": "Dinámica de cuencas sedimentarias y exploración energética",
        "categoria": "Geología",
        "fuente": "GeoNotas",
        "fecha": "2026",
        "resumen": "Revisión técnica sobre trampas estructurales, estratigráficas y gravedad API en yacimientos convencionales y pesados.",
    },
    {
        "titulo": "Desarrollo web ligero para dispositivos de recursos limitados",
        "categoria": "Programación",
        "fuente": "Dev Diario",
        "fecha": "2026",
        "resumen": "Buenas prácticas para mantener aplicaciones rápidas, limpias y estables en teléfonos de gama de entrada.",
    },
]

VIDEOS_BASE = [
    {
        "titulo": "Fundamentos de Python y estructuras de datos",
        "categoria": "Programación",
        "canal": "Código Claro",
        "duracion": "12:40",
        "descripcion": "Repaso práctico de listas, diccionarios, funciones estadísticas y manejo de errores en Python.",
    },
    {
        "titulo": "Geología del petróleo: rocas reservorio y trampa",
        "categoria": "Geología",
        "canal": "Aula Tierra",
        "duracion": "15:10",
        "descripcion": "Explicación visual de porosidad, permeabilidad, roca sello y clasificación del crudo.",
    },
    {
        "titulo": "Diseño de interfaces oscuras de alto contraste",
        "categoria": "Diseño",
        "canal": "UI Lab",
        "duracion": "09:25",
        "descripcion": "Cómo estructurar paneles, botones y jerarquía visual con fondos oscuros y acentos limpios.",
    },
]

WEBS_RECOMENDADAS = [
    {
        "nombre": "Documentación oficial de Python",
        "categoria": "Programación",
        "url": "https://docs.python.org/3/",
        "descripcion": "Referencia completa de la biblioteca estándar, sintaxis y módulos integrados.",
    },
    {
        "nombre": "Documentación de Flask",
        "categoria": "Programación",
        "url": "https://flask.palletsprojects.com/",
        "descripcion": "Guía oficial para rutas, plantillas y despliegue de aplicaciones web en Python.",
    },
    {
        "nombre": "Chart.js",
        "categoria": "Datos",
        "url": "https://www.chartjs.org/",
        "descripcion": "Librería ligera para construir gráficos de barras, líneas y estadísticas en HTML.",
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>CIPRES 2 // C-PRE2</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #070709;
      --panel: #111116;
      --panel-2: #17171f;
      --border: #282834;
      --text: #f4f4f8;
      --muted: #a0a0b2;
      --accent: #e11d48;
      --accent-soft: rgba(225, 29, 72, 0.16);
      --ok: #10b981;
      --warn: #f59e0b;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top, #1b0910 0%, var(--bg) 52%);
      color: var(--text);
      min-height: 100vh;
    }
    .wrap {
      max-width: 1040px;
      margin: 0 auto;
      padding: 18px 14px 48px;
    }
    .login-box {
      max-width: 430px;
      margin: 48px auto;
      background: var(--panel);
      border: 1px solid var(--accent);
      box-shadow: 0 0 32px rgba(225, 29, 72, 0.22);
      border-radius: 16px;
      padding: 24px;
      text-align: center;
    }
    .brand-title {
      margin: 0;
      font-size: 1.8rem;
      letter-spacing: 0.06em;
    }
    .brand-sub {
      margin: 6px 0 18px;
      font-size: 0.82rem;
      color: var(--muted);
      letter-spacing: 0.12em;
    }
    label {
      display: block;
      text-align: left;
      font-size: 0.85rem;
      color: var(--muted);
      margin-bottom: 6px;
    }
    input, select, textarea {
      width: 100%;
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.95rem;
      margin-bottom: 12px;
    }
    input:focus, select:focus, textarea:focus {
      outline: none;
      border-color: var(--accent);
    }
    button {
      cursor: pointer;
      border: none;
      border-radius: 10px;
      padding: 10px 14px;
      font-weight: 600;
      font-size: 0.9rem;
      transition: transform 0.12s ease, opacity 0.15s ease, background 0.15s ease;
    }
    button:active { transform: scale(0.98); }
    .btn-primary {
      width: 100%;
      background: var(--accent);
      color: #fff;
      padding: 12px;
      letter-spacing: 0.04em;
    }
    .btn-secondary {
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--border);
    }
    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 14px 16px;
      margin-bottom: 14px;
    }
    .badge {
      display: inline-block;
      padding: 4px 10px;
      border-radius: 999px;
      font-size: 0.78rem;
      background: var(--accent-soft);
      color: #fda4af;
      border: 1px solid rgba(225, 29, 72, 0.4);
    }
    .nav-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
      gap: 8px;
      margin-bottom: 16px;
    }
    .mod-btn {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      text-align: left;
      padding: 10px 12px;
    }
    .mod-btn.active {
      background: var(--accent-soft);
      border-color: var(--accent);
      color: #fff;
    }
    .mod-panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
    }
    .hidden { display: none !important; }
    .grid-2 {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
      gap: 14px;
    }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
    }
    .stat-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
      gap: 10px;
      margin: 12px 0;
    }
    .stat-box {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
    }
    .stat-label { font-size: 0.76rem; color: var(--muted); }
    .stat-val { font-size: 1.25rem; font-weight: 700; margin-top: 4px; }
    pre {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      overflow-x: auto;
      font-size: 0.85rem;
      color: #e2e8f0;
    }
    table {
      width: 100%;
      border-collapse: collapse;
      font-size: 0.88rem;
    }
    th, td {
      border-bottom: 1px solid var(--border);
      padding: 8px 10px;
      text-align: left;
    }
    .flash-row { background: rgba(16, 185, 129, 0.16); }
    .alert-err {
      background: rgba(239, 68, 68, 0.16);
      border: 1px solid #ef4444;
      color: #fecaca;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.88rem;
    }
    .alert-ok {
      background: rgba(16, 185, 129, 0.14);
      border: 1px solid var(--ok);
      color: #a7f3d0;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.88rem;
    }
    a { color: #fb7185; text-decoration: none; }
    a:hover { text-decoration: underline; }
  </style>
</head>
<body>
<div class="wrap">
  {% if not autorizado %}
    <div class="login-box">
      <h1 class="brand-title">CIPRES 2</h1>
      <p class="brand-sub">PLATAFORMA DIGITAL // C-PRE2</p>
      {% if error %}
        <div class="alert-err">{{ error }}</div>
      {% endif %}
      <form method="POST">
        <label for="codigo">Código de acceso</label>
        <input id="codigo" name="codigo" type="text" placeholder="DEMO2026 o VIP100" required />
        <button class="btn-primary" type="submit">ENTRAR A CIPRES 2</button>
      </form>
    </div>
  {% else %}
    <div class="topbar">
      <div>
        <strong>CIPRES 2</strong> <span class="badge">Código: {{ codigo }} · Plan {{ plan }}</span>
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="badge">Intentos / Uso: {{ uso }} / {{ limite }}</span>
        <a class="btn-secondary" style="padding:8px 12px; border-radius:10px;" href="/">Salir</a>
      </div>
    </div>

    <div class="nav-grid" id="navRenglones">
      <button type="button" class="mod-btn active" onclick="openMod('m1', this)">1. Programar</button>
      <button type="button" class="mod-btn" onclick="openMod('m2', this)">2. Crear base de datos</button>
      <button type="button" class="mod-btn" onclick="openMod('m3', this)">3. Ordenar y graficar</button>
      <button type="button" class="mod-btn" onclick="openMod('m4', this)">4. Noticias del día</button>
      <button type="button" class="mod-btn" onclick="openMod('m5', this)">5. Videos del día</button>
      <button type="button" class="mod-btn" onclick="openMod('m6', this)">6. Webs recomendadas</button>
      <button type="button" class="mod-btn" onclick="openMod('m7', this)">7. Estado y control</button>
    </div>

    <!-- RENGLÓN 1: PROGRAMAR -->
    <section id="m1" class="mod-panel">
      <h2>Renglón 1 · Programar en Python</h2>
      <p style="color:var(--muted)">Escribe expresiones o scripts cortos en Python (sin imports peligrosos ni acceso al sistema) y evalúa resultados numéricos o de texto.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="accion" value="ejecutar_codigo" />
        <label for="code_input">Código Python</label>
        <textarea id="code_input" name="code_input" rows="6">{{ code_input }}</textarea>
        <button type="submit" class="btn-primary">Ejecutar código</button>
      </form>
      {% if code_output is not none %}
        <h3>Salida</h3>
        <pre>{{ code_output }}</pre>
      {% endif %}
    </section>

    <!-- RENGLÓN 2: CREAR BASE DE DATOS -->
    <section id="m2" class="mod-panel hidden">
      <h2>Renglón 2 · Crear base de datos y registros</h2>
      <form method="POST" class="grid-2">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="accion" value="agregar_registro" />
        <div>
          <label for="db_nombre">Nombre / Etiqueta</label>
          <input id="db_nombre" name="db_nombre" type="text" placeholder="Ej: Pozo Norte / Muestra A" required />
        </div>
        <div>
          <label for="db_valor">Valor numérico</label>
          <input id="db_valor" name="db_valor" type="number" step="any" placeholder="Ej: 42.5" required />
        </div>
        <div>
          <label for="db_categoria">Categoría</label>
          <input id="db_categoria" name="db_categoria" type="text" placeholder="Ej: Producción / Prueba" />
        </div>
        <div>
          <label for="db_fecha">Fecha</label>
          <input id="db_fecha" name="db_fecha" type="date" />
        </div>
        <div style="grid-column: 1 / -1; display:flex; gap:10px; flex-wrap:wrap;">
          <button type="submit" class="btn-primary" style="max-width:240px;">Guardar registro</button>
          <a class="btn-secondary" style="padding:10px 14px; border-radius:10px;" href="/descargar-csv?codigo={{ codigo }}">Descargar CSV</a>
        </div>
      </form>

      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Registros</div><div class="stat-val">{{ stats.count }}</div></div>
        <div class="stat-box"><div class="stat-label">Total</div><div class="stat-val">{{ stats.total }}</div></div>
        <div class="stat-box"><div class="stat-label">Promedio</div><div class="stat-val">{{ stats.avg }}</div></div>
        <div class="stat-box"><div class="stat-label">Máximo</div><div class="stat-val">{{ stats.max_val }}</div></div>
      </div>

      <table>
        <thead>
          <tr><th>#</th><th>Nombre</th><th>Valor</th><th>Categoría</th><th>Fecha</th></tr>
        </thead>
        <tbody>
          {% for r in registros %}
            <tr>
              <td>{{ loop.index }}</td>
              <td>{{ r.nombre }}</td>
              <td>{{ r.valor }}</td>
              <td>{{ r.categoria }}</td>
              <td>{{ r.fecha }}</td>
            </tr>
          {% else %}
            <tr><td colspan="5" style="color:var(--muted)">Aún no hay registros guardados en esta sesión.</td></tr>
          {% endfor %}
        </tbody>
      </table>
    </section>

    <!-- RENGLÓN 3: ORDENAR Y GRAFICAR -->
    <section id="m3" class="mod-panel hidden">
      <h2>Renglón 3 · Ordenar datos y graficar</h2>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="accion" value="ordenar_datos" />
        <label for="serie_numeros">Números separados por coma o espacio</label>
        <input id="serie_numeros" name="serie_numeros" type="text" value="{{ serie_raw }}" placeholder="15, 42, 8, 90, 27" />
        <label for="orden_dir">Orden</label>
        <select id="orden_dir" name="orden_dir">
          <option value="asc" {% if orden_dir == 'asc' %}selected{% endif %}>Menor a mayor</option>
          <option value="desc" {% if orden_dir == 'desc' %}selected{% endif %}>Mayor a menor</option>
        </select>
        <button type="submit" class="btn-primary">Ordenar y actualizar gráfico</button>
      </form>
      <p><strong>Serie ordenada:</strong> {{ serie_ordenada }}</p>
      <canvas id="chartDatos" height="110"></canvas>
    </section>

    <!-- RENGLÓN 4: NOTICIAS DEL DÍA -->
    <section id="m4" class="mod-panel hidden">
      <h2>Renglón 4 · Noticias del día</h2>
      <div class="grid-2">
        {% for n in noticias %}
          <article class="card">
            <span class="badge">{{ n.categoria }}</span>
            <h3 style="margin:8px 0 6px">{{ n.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.88rem">{{ n.resumen }}</p>
            <small style="color:var(--muted)">Fuente: {{ n.fuente }} · {{ n.fecha }}</small>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- RENGLÓN 5: VIDEOS DEL DÍA -->
    <section id="m5" class="mod-panel hidden">
      <h2>Renglón 5 · Videos del día</h2>
      <div class="grid-2">
        {% for v in videos %}
          <article class="card">
            <span class="badge">{{ v.categoria }} · {{ v.duracion }}</span>
            <h3 style="margin:8px 0 6px">{{ v.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.88rem">{{ v.descripcion }}</p>
            <small style="color:var(--muted)">Canal: {{ v.canal }}</small>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- RENGLÓN 6: WEBS RECOMENDADAS -->
    <section id="m6" class="mod-panel hidden">
      <h2>Renglón 6 · Páginas web recomendadas</h2>
      <div class="grid-2">
        {% for w in webs %}
          <article class="card">
            <span class="badge">{{ w.categoria }}</span>
            <h3 style="margin:8px 0 6px">{{ w.nombre }}</h3>
            <p style="color:var(--muted); font-size:0.88rem">{{ w.descripcion }}</p>
            <a href="{{ w.url }}" target="_blank" rel="noopener noreferrer">Abrir enlace →</a>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- RENGLÓN 7: ESTADO Y CONTROL -->
    <section id="m7" class="mod-panel hidden">
      <h2>Renglón 7 · Estado del sistema y control</h2>
      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Plataforma</div><div class="stat-val">C-PRE2</div></div>
        <div class="stat-box"><div class="stat-label">Estado</div><div class="stat-val" style="color:var(--ok)">ACTIVO</div></div>
        <div class="stat-box"><div class="stat-label">Plan actual</div><div class="stat-val">{{ plan }}</div></div>
        <div class="stat-box"><div class="stat-label">Uso registrado</div><div class="stat-val">{{ uso }} / {{ limite }}</div></div>
      </div>
      <p style="color:var(--muted)">Todos los 7 módulos están integrados en una sola aplicación Flask lista para Render.</p>
    </section>
  {% endif %}
</div>

<script>
  function openMod(id, btn) {
    document.querySelectorAll('.mod-panel').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.mod-btn').forEach(b => b.classList.remove('active'));
    const target = document.getElementById(id);
    if (target) target.classList.remove('hidden');
    if (btn) btn.classList.add('active');
  }

  {% if autorizado %}
  const ctx = document.getElementById('chartDatos');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: {{ chart_labels | tojson }},
        datasets: [{
          label: 'Valores ordenados',
          data: {{ chart_values | tojson }},
          backgroundColor: 'rgba(225, 29, 72, 0.55)',
          borderColor: '#e11d48',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f4f4f8' } } },
        scales: {
          x: { ticks: { color: '#a0a0b2' }, grid: { color: '#282834' } },
          y: { ticks: { color: '#a0a0b2' }, grid: { color: '#282834' } }
        }
      }
    });
  }
  {% endif %}
</script>
</body>
</html>
"""

ESTADO_SESIONES = {}


def obtener_estado(codigo):
    code = (codigo or "").strip().upper()
    if code not in CODIGOS_ACCESO:
        return None
    if code not in ESTADO_SESIONES:
        ESTADO_SESIONES[code] = {
            "uso": 0,
            "registros": [],
            "code_input": "nums = [15, 42, 8, 90, 27]\nprint('Total:', sum(nums))\nprint('Promedio:', round(sum(nums)/len(nums), 2))\nprint('Raiz max:', round(math.sqrt(max(nums)), 2))",
            "code_output": None,
            "serie_raw": "15, 42, 8, 90, 27",
            "orden_dir": "asc",
        }
    return ESTADO_SESIONES[code]


def parsear_serie(raw_text, orden_dir="asc"):
    partes = [p.strip() for p in (raw_text or "").replace(",", " ").split() if p.strip()]
    nums = []
    for p in partes:
        try:
            nums.append(float(p))
        except ValueError:
            pass
    if not nums:
        nums = [15.0, 42.0, 8.0, 90.0, 27.0]
    reverse = (orden_dir == "desc")
    ordenada = sorted(nums, reverse=reverse)
    limpios = [int(x) if x.is_integer() else round(x, 4) for x in ordenada]
    return limpios


def calcular_stats(registros):
    if not registros:
        return {"count": 0, "total": 0, "avg": 0, "max_val": 0}
    vals = [r["valor"] for r in registros]
    total = sum(vals)
    avg = statistics.mean(vals)
    max_val = max(vals)
    fmt = lambda v: int(v) if float(v).is_integer() else round(float(v), 2)
    return {
        "count": len(vals),
        "total": fmt(total),
        "avg": fmt(avg),
        "max_val": fmt(max_val),
    }


def ejecutar_codigo_seguro(codigo_fuente):
    prohibidos = ["import ", "from ", "__", "open(", "eval(", "exec(", "compile(", "input(", "os.", "sys.", "subprocess"]
    bajo = (codigo_fuente or "").lower()
    for palabra in prohibidos:
        if palabra in bajo:
            return f"Bloqueado por seguridad: no se permite '{palabra}'."
    salida_buffer = io.StringIO()
    entorno_seguro = {
        "__builtins__": {
            "print": lambda *args, **kwargs: print(*args, file=salida_buffer, **kwargs),
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "round": round,
            "abs": abs,
            "range": range,
            "enumerate": enumerate,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
        },
        "math": math,
        "statistics": statistics,
    }
    try:
        exec(codigo_fuente, entorno_seguro, {})
        resultado = salida_buffer.getvalue().strip()
        return resultado if resultado else "Código ejecutado sin salida impresa."
    except Exception as e:
        return f"Error al ejecutar: {e}"


def render_panel(codigo, estado, error_msg=None):
    info = CODIGOS_ACCESO[codigo]
    serie_ordenada = parsear_serie(estado["serie_raw"], estado["orden_dir"])
    labels = [f"Dato {i + 1}" for i in range(len(serie_ordenada))]
    return render_template_string(
        HTML_TEMPLATE,
        autorizado=True,
        error=error_msg,
        codigo=codigo,
        plan=info["plan"],
        limite=info["limite"],
        uso=estado["uso"],
        code_input=estado["code_input"],
        code_output=estado["code_output"],
        registros=estado["registros"],
        stats=calcular_stats(estado["registros"]),
        serie_raw=estado["serie_raw"],
        orden_dir=estado["orden_dir"],
        serie_ordenada=", ".join(str(x) for x in serie_ordenada),
        chart_labels=labels,
        chart_values=serie_ordenada,
        noticias=NOTICIAS_BASE,
        videos=VIDEOS_BASE,
        webs=WEBS_RECOMENDADAS,
    )


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").strip().upper()
        estado = obtener_estado(codigo)
        if not estado:
            return render_template_string(
                HTML_TEMPLATE,
                autorizado=False,
                error="Código no válido. Usa DEMO2026, VIP100 o EXCELSO99.",
            )

        limite = CODIGOS_ACCESO[codigo]["limite"]
        accion = request.form.get("accion")

        if accion:
            if estado["uso"] >= limite:
                return render_panel(codigo, estado, "Has alcanzado el límite de acciones de este código.")
            estado["uso"] += 1

        if accion == "ejecutar_codigo":
            src = request.form.get("code_input") or ""
            estado["code_input"] = src
            estado["code_output"] = ejecutar_codigo_seguro(src)

        elif accion == "agregar_registro":
            nombre = (request.form.get("db_nombre") or "").strip()
            valor_raw = request.form.get("db_valor")
            categoria = (request.form.get("db_categoria") or "General").strip()
            fecha = (request.form.get("db_fecha") or datetime.now().strftime("%Y-%m-%d")).strip()
            try:
                valor = float(valor_raw)
                val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
                if nombre:
                    estado["registros"].append(
                        {"nombre": nombre, "valor": val_fmt, "categoria": categoria, "fecha": fecha}
                    )
            except (TypeError, ValueError):
                return render_panel(codigo, estado, "Ingresa un valor numérico válido en el registro.")

        elif accion == "ordenar_datos":
            estado["serie_raw"] = request.form.get("serie_numeros") or ""
            estado["orden_dir"] = request.form.get("orden_dir") or "asc"

        return render_panel(codigo, estado)

    return render_template_string(HTML_TEMPLATE, autorizado=False, error=None)


@app.route("/descargar-csv")
def descargar_csv():
    codigo = (request.args.get("codigo") or "").strip().upper()
    estado = obtener_estado(codigo)
    if not estado:
        return "Código no autorizado", 403

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nombre", "Valor", "Categoria", "Fecha"])
    for r in estado["registros"]:
        writer.writerow([r["nombre"], r["valor"], r["categoria"], r["fecha"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=cipres2_registros.csv"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

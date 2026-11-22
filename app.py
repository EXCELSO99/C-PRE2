import csv
import io
import json
import math
import os
import re
import statistics
import urllib.parse
from datetime import datetime
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

CODIGOS_ACCESO = {
    "DEMO2026": {"plan": "DEMO", "limite": 500},
    "VIP100": {"plan": "VIP", "limite": 2000},
    "EXCELSO99": {"plan": "PRO", "limite": 999999},
}

IDIOMAS_20 = [
    ("es", "Español"),
    ("en", "English (Inglés)"),
    ("zh", "中文 (Chino mandarín)"),
    ("hi", "हिन्दी (Hindi)"),
    ("ar", "العربية (Árabe)"),
    ("bn", "বাংলা (Bengalí)"),
    ("pt", "Português"),
    ("ru", "Русский (Ruso)"),
    ("ja", "日本語 (Japonés)"),
    ("pa", "ਪੰਜਾਬੀ / پنجابی (Panyabí)"),
    ("de", "Deutsch (Alemán)"),
    ("jv", "Basa Jawa (Javanés)"),
    ("ko", "한국어 (Coreano)"),
    ("fr", "Français (Francés)"),
    ("te", "తెలుగు (Telugu)"),
    ("mr", "मराठी (Maratí)"),
    ("tr", "Türkçe (Turco)"),
    ("ta", "தமிழ் (Tamil)"),
    ("vi", "Tiếng Việt (Vietnamita)"),
    ("it", "Italiano"),
]

RESPUESTAS_NATURALES = {
    "messi": {
        "titulo": "Lionel Messi",
        "concepto": (
            "Lionel Andrés Messi es un futbolista argentino considerado por millones de aficionados y "
            "analistas como uno de los mejores jugadores en la historia del fútbol. Destaca por su visión "
            "de juego, regate en espacios reducidos, precisión en el pase y capacidad goleadora y de "
            "asistencia durante más de dos décadas al máximo nivel. Ha ganado títulos de clubes, torneos "
            "continentales y la Copa del Mundo con Argentina, además de múltiples premios individuales."
        ),
        "ejemplo": (
            "En la práctica: Su nombre suele protagonizar análisis sobre récords históricos, "
            "estadísticas de goles y asistencias, y rendimiento en torneos internacionales."
        ),
    },
    "tecnologia": {
        "titulo": "Tecnología",
        "concepto": (
            "La tecnología reúne herramientas, técnicas, sistemas y conocimientos aplicados para resolver "
            "problemas reales, optimizar procesos y crear soluciones en software, energía, comunicaciones "
            "e industria."
        ),
        "ejemplo": (
            "En la práctica: Permite automatizar cálculos, mejorar el rendimiento de aplicaciones web "
            "y reducir consumos energéticos en procesos digitales."
        ),
    },
    "programacion": {
        "titulo": "Programación",
        "concepto": (
            "La programación consiste en escribir instrucciones claras y ordenadas en un lenguaje como "
            "Python para que un sistema procese datos, ejecute lógica, construya aplicaciones y "
            "automatice tareas."
        ),
        "ejemplo": (
            "En la práctica: Con un script puedes procesar listas, calcular estadísticas, ordenar "
            "información o servir una aplicación web en Flask."
        ),
    },
    "petroleo": {
        "titulo": "Petróleo y geología",
        "concepto": (
            "El petróleo es una mezcla natural de hidrocarburos formada en el subsuelo a partir de "
            "materia orgánica bajo presión y temperatura. En geología del petróleo se estudian cuencas "
            "sedimentarias, rocas generadoras, rocas reservorio, trampas, roca sello y gravedad API."
        ),
        "ejemplo": (
            "En la práctica: La gravedad API indica la densidad del crudo y ayuda a orientar su "
            "manejo, transporte y refinación."
        ),
    },
    "excel": {
        "titulo": "Hojas de cálculo y Excel",
        "concepto": (
            "Una hoja de cálculo organiza datos en filas y columnas formando celdas que admiten "
            "texto, números o fórmulas para calcular totales, promedios, comparaciones y ordenamientos."
        ),
        "ejemplo": (
            "En la práctica: Puedes escribir =B1*C1 por fila y usar =SUMA(D1:D5), =PROMEDIO(C1:C5) "
            "o =SI(D1>=E1;\"Cumple\";\"Ajustar\")."
        ),
    },
}


def _col_letra(idx):
    letters = ""
    n = idx + 1
    while n > 0:
        n, rem = divmod(n - 1, 26)
        letters = chr(65 + rem) + letters
    return letters


def construir_30_noticias():
    temas = [
        ("Tecnología", "N-Tech", "Eficiencia energética y cálculo computacional", "Avances orientados a reducir el consumo eléctrico y mejorar el rendimiento en sistemas digitales.", "eficiencia energetica computacion tecnologia"),
        ("Deportes", "N-Fut", "Fútbol mundial, récords y rendimiento competitivo", "Seguimiento de figuras, marcas históricas, torneos y análisis táctico del fútbol actual.", "futbol mundial records goles"),
        ("Geología", "N-Geo", "Cuencas sedimentarias, gravedad API y yacimientos", "Novedades sobre exploración, caracterización de reservorios y dinámica energética.", "geologia petroleo yacimientos api"),
        ("Programación", "N-Dev", "Python, desarrollo web y automatización", "Tendencias en aplicaciones web, estructuras de datos y optimización de código.", "python desarrollo web programacion"),
        ("Ciencia", "N-Sci", "Ciencia, espacio y física aplicada", "Descubrimientos recientes, observaciones astronómicas y experimentos destacados.", "ciencia astronomia fisica"),
        ("Economía", "N-Eco", "Mercados, innovación y actividad productiva", "Panorama económico, transformación digital y movimientos clave en distintos sectores.", "economia innovacion mercados"),
    ]
    enfoques = ["panorama actual", "análisis detallado", "puntos clave", "actualización del día", "enfoque práctico"]
    noticias = []
    for i in range(30):
        cat, logo, tit, res, q = temas[i % len(temas)]
        enf = enfoques[i % len(enfoques)]
        num = i + 1
        noticias.append({
            "num": num,
            "logo": logo,
            "titulo": f"#{num:02d} · {tit} ({enf})",
            "categoria": cat,
            "fuente": f"Google Noticias · {cat}",
            "fecha": "Hoy",
            "resena": f"{res} ({enf.capitalize()}).",
            "url": f"https://news.google.com/search?q={urllib.parse.quote_plus(q + ' ' + enf)}",
        })
    return noticias


def construir_30_videos():
    plataformas = [
        ("TikTok", "Viral / TikTok", "https://www.tiktok.com/search?q="),
        ("YouTube", "Videos / YouTube", "https://www.youtube.com/results?search_query="),
        ("Instagram", "Reels / Instagram", "https://www.instagram.com/explore/"),
    ]
    temas = [
        ("Tendencias virales y clips destacados", "tendencias virales"),
        ("Fútbol, jugadas y análisis", "futbol jugadas analisis"),
        ("Programación en Python y proyectos", "python programacion proyectos"),
        ("Geología del petróleo y yacimientos", "geologia petroleo yacimientos"),
        ("Hojas de cálculo y fórmulas prácticas", "hoja de calculo formulas"),
        ("Tecnología y novedades digitales", "tecnologia novedades"),
        ("Ciencia, astronomía y experimentos", "ciencia astronomia"),
        ("Matemática y resolución rápida", "matematicas logica"),
        ("Diseño de interfaces y estética", "diseño ui web"),
        ("Productividad y software", "productividad software"),
    ]
    videos = []
    for i in range(30):
        plat, cat, base_u = plataformas[i % len(plataformas)]
        tit, q = temas[i % len(temas)]
        num = i + 1
        url = base_u if plat == "Instagram" else f"{base_u}{urllib.parse.quote_plus(q + ' ' + str(num))}"
        videos.append({
            "num": num,
            "titulo": f"#{num:02d} · {tit}",
            "plataforma": plat,
            "categoria": cat,
            "resena": f"Explorar '{q}' en {plat}.",
            "url": url,
        })
    return videos


NOTICIAS_30 = construir_30_noticias()
VIDEOS_30 = construir_30_videos()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="{{ idioma }}">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>C-PRE2 // Plataforma Digital</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #07070c;
      --panel: #11111a;
      --panel-2: #171722;
      --border: #282838;
      --text: #f4f4fa;
      --muted: #9e9eb4;
      --accent: {{ acento_hex }};
      --accent-soft: rgba(225, 29, 72, 0.14);
      --ok: #10b981;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top, #1b0911 0%, var(--bg) 52%);
      color: var(--text);
      min-height: 100vh;
    }
    .wrap { max-width: 1240px; margin: 0 auto; padding: 14px 12px 56px; }
    .login-box {
      max-width: 420px;
      margin: 56px auto;
      background: var(--panel);
      border: 1px solid var(--accent);
      box-shadow: 0 0 30px rgba(225, 29, 72, 0.2);
      border-radius: 16px;
      padding: 24px;
      text-align: center;
    }
    .brand-title { margin: 0; font-size: 1.9rem; letter-spacing: 0.08em; }
    .brand-sub { margin: 6px 0 18px; font-size: 0.8rem; color: var(--muted); letter-spacing: 0.14em; }
    label { display: block; text-align: left; font-size: 0.82rem; color: var(--muted); margin-bottom: 5px; }
    input, select, textarea {
      width: 100%;
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 9px 11px;
      font-size: 0.92rem;
      margin-bottom: 10px;
    }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent); }
    button {
      cursor: pointer;
      border: none;
      border-radius: 10px;
      padding: 9px 13px;
      font-weight: 600;
      font-size: 0.84rem;
      transition: transform 0.1s ease, background 0.15s ease;
    }
    button:active { transform: scale(0.98); }
    .btn-primary { width: 100%; background: var(--accent); color: #fff; padding: 10px 14px; }
    .btn-secondary {
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--border);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-small { padding: 5px 9px; font-size: 0.78rem; border-radius: 8px; }
    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 12px 16px;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.75rem;
      background: var(--accent-soft);
      color: #fda4af;
      border: 1px solid rgba(225, 29, 72, 0.35);
    }
    .nav-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(126px, 1fr));
      gap: 7px;
      margin-bottom: 14px;
    }
    .mod-btn {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      text-align: left;
      padding: 9px 11px;
      font-size: 0.82rem;
    }
    .mod-btn.active { background: var(--accent-soft); border-color: var(--accent); color: #fff; }
    .mod-panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 16px;
    }
    .hidden { display: none !important; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(270px, 1fr)); gap: 14px; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr)); gap: 12px; }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
    }
    .news-head {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 8px;
      margin-bottom: 8px;
    }
    .news-logo {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      min-width: 46px;
      height: 28px;
      padding: 0 8px;
      border-radius: 8px;
      background: linear-gradient(135deg, var(--accent), #881337);
      color: #fff;
      font-weight: 800;
      font-size: 0.75rem;
    }
    .stat-mini-row {
      display: flex;
      flex-wrap: wrap;
      gap: 14px;
      padding: 10px 14px;
      margin: 12px 0;
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      font-size: 0.84rem;
    }
    .stat-mini-item { display: inline-flex; gap: 6px; align-items: baseline; }
    .stat-mini-lbl { color: var(--muted); font-size: 0.78rem; }
    .stat-mini-val { font-weight: 700; color: var(--text); }
    pre {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      overflow-x: auto;
      font-size: 0.85rem;
      color: #e2e8f0;
    }
    /* Barra de fórmulas tipo Excel */
    .formula-bar {
      display: flex;
      gap: 8px;
      align-items: center;
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 8px 10px;
      margin-bottom: 12px;
      flex-wrap: wrap;
    }
    .cell-box-name {
      min-width: 56px;
      text-align: center;
      font-weight: 700;
      font-size: 0.84rem;
      padding: 6px 8px;
      border-radius: 8px;
      background: var(--bg);
      border: 1px solid var(--accent);
      color: #fda4af;
    }
    .formula-bar input {
      flex: 1 1 220px;
      margin-bottom: 0;
      padding: 7px 10px;
      font-size: 0.86rem;
    }
    .table-wrap {
      overflow-x: auto;
      max-height: 490px;
      overflow-y: auto;
      border: 1px solid var(--border);
      border-radius: 10px;
      user-select: none;
    }
    table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    th, td { border: 1px solid var(--border); padding: 0; text-align: left; }
    th { background: var(--panel-2); position: sticky; top: 0; z-index: 2; padding: 4px 5px; }
    .row-num { background: var(--panel-2); font-weight: 700; text-align: center; min-width: 36px; padding: 4px; color: var(--muted); }
    td.selected-cell {
      background: rgba(59, 130, 246, 0.22);
      box-shadow: inset 0 0 0 2px #60a5fa;
    }
    td.active-cell {
      box-shadow: inset 0 0 0 2px var(--accent);
    }
    .sheet-cell {
      width: 100%;
      min-width: 98px;
      margin-bottom: 0;
      padding: 6px 7px;
      font-size: 0.82rem;
      border-radius: 0;
      border: none;
      background: transparent;
      color: var(--text);
    }
    .sheet-cell:focus {
      outline: none;
      background: var(--bg);
    }
    .alert-err {
      background: rgba(239, 68, 68, 0.16);
      border: 1px solid #ef4444;
      color: #fecaca;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.86rem;
    }
    .alert-ok {
      background: rgba(16, 185, 129, 0.15);
      border: 1px solid var(--ok);
      color: #a7f3d0;
      padding: 10px 12px;
      border-radius: 10px;
      margin-bottom: 12px;
      font-size: 0.86rem;
    }
    .search-row { display: flex; gap: 8px; align-items: stretch; flex-wrap: wrap; margin-bottom: 12px; }
    .search-row input { flex: 1 1 220px; margin-bottom: 0; }
    .search-row button { margin-bottom: 0; }
    a { color: #fb7185; text-decoration: none; }
    a:hover { text-decoration: underline; }
    @media print {
      .topbar, .nav-grid, .btn-secondary, .btn-primary, .formula-bar, form { display: none !important; }
      body { background: #fff; color: #000; }
      .mod-panel { border: none; background: #fff; color: #000; padding: 0; }
      .table-wrap { max-height: none; overflow: visible; border: none; }
      table, th, td { border: 1px solid #444; color: #000; }
      input.sheet-cell { border: none; color: #000; background: transparent; }
    }
  </style>
</head>
<body>
<div class="wrap">
  {% if not autorizado %}
    <div class="login-box">
      <h1 class="brand-title">C-PRE2</h1>
      <p class="brand-sub">PLATAFORMA DIGITAL // C-PRE2</p>
      {% if error %}
        <div class="alert-err">{{ error }}</div>
      {% endif %}
      <form method="POST">
        <label for="codigo">Código de acceso</label>
        <input id="codigo" name="codigo" type="text" placeholder="DEMO2026, VIP100 o EXCELSO99" required />
        <button class="btn-primary" type="submit">ENTRAR A C-PRE2</button>
      </form>
    </div>
  {% else %}
    <div class="topbar">
      <div>
        <strong>C-PRE2</strong> <span class="badge">{{ codigo }} · {{ plan }}</span>
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="badge">{{ idioma_nombre }}</span>
        <span class="badge">{{ uso }} / {{ limite }}</span>
        <a class="btn-secondary" style="padding:7px 11px; border-radius:10px;" href="/">Salir</a>
      </div>
    </div>

    {% if error %}
      <div class="alert-err">{{ error }}</div>
    {% endif %}
    {% if aviso %}
      <div class="alert-ok">{{ aviso }}</div>
    {% endif %}

    <div class="nav-grid" id="navRenglones">
      <button type="button" class="mod-btn {% if active_mod == 'm1' %}active{% endif %}" onclick="openMod('m1', this)">1. Programar</button>
      <button type="button" class="mod-btn {% if active_mod == 'm2' %}active{% endif %}" onclick="openMod('m2', this)">2. Crear base</button>
      <button type="button" class="mod-btn {% if active_mod == 'm3' %}active{% endif %}" onclick="openMod('m3', this)">3. Ordenar</button>
      <button type="button" class="mod-btn {% if active_mod == 'm4' %}active{% endif %}" onclick="openMod('m4', this)">4. Hoja de cálculo</button>
      <button type="button" class="mod-btn {% if active_mod == 'm5' %}active{% endif %}" onclick="openMod('m5', this)">5. Noticias (30)</button>
      <button type="button" class="mod-btn {% if active_mod == 'm6' %}active{% endif %}" onclick="openMod('m6', this)">6. Videos (30)</button>
      <button type="button" class="mod-btn {% if active_mod == 'm7' %}active{% endif %}" onclick="openMod('m7', this)">7. Buscador web</button>
      <button type="button" class="mod-btn {% if active_mod == 'm8' %}active{% endif %}" onclick="openMod('m8', this)">8. Ajustes</button>
    </div>

    <!-- 1. PROGRAMAR -->
    <section id="m1" class="mod-panel {% if active_mod != 'm1' %}hidden{% endif %}">
      <h2>1. Programar en Python</h2>
      <p style="color:var(--muted)">Escribe tu script en Python y ejecuta para ver los resultados.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m1" />
        <input type="hidden" name="accion" value="ejecutar_codigo" />
        <label for="code_input">Código Python</label>
        <textarea id="code_input" name="code_input" rows="9">{{ code_input }}</textarea>
        <button type="submit" class="btn-primary">Ejecutar script</button>
      </form>
      {% if code_output is not none %}
        <h3>Resultado</h3>
        <pre>{{ code_output }}</pre>
      {% endif %}
    </section>

    <!-- 2. CREAR BASE DE DATOS -->
    <section id="m2" class="mod-panel {% if active_mod != 'm2' %}hidden{% endif %}">
      <h2>2. Crear base de datos</h2>
      <p style="color:var(--muted)">Agrega filas, pega un lote o importa un archivo para crear tu base de datos.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0">Nuevo registro</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="agregar_registro" />
          <label for="db_nombre">Nombre / Producto</label>
          <input id="db_nombre" name="db_nombre" type="text" placeholder="Ej: Producto A" required />
          <label for="db_valor">Valor</label>
          <input id="db_valor" name="db_valor" type="number" step="any" placeholder="Ej: 150" required />
          <label for="db_categoria">Categoría</label>
          <input id="db_categoria" name="db_categoria" type="text" placeholder="Ej: Ventas" />
          <label for="db_fecha">Fecha</label>
          <input id="db_fecha" name="db_fecha" type="date" />
          <button type="submit" class="btn-primary">Guardar registro</button>
        </form>

        <form method="POST" class="card">
          <h3 style="margin-top:0">Pegar texto o lote</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="cargar_lote_db" />
          <label for="lote_db_texto">Filas (Nombre, Valor, Categoría, Fecha)</label>
          <textarea id="lote_db_texto" name="lote_db_texto" rows="5" placeholder="Escriba o pegue aquí..."></textarea>
          <label for="modo_carga_db">Modo</label>
          <select id="modo_carga_db" name="modo_carga_db">
            <option value="agregar">Agregar</option>
            <option value="reemplazar">Reemplazar</option>
          </select>
          <button type="submit" class="btn-primary">Cargar</button>
        </form>
      </div>

      <form method="POST" enctype="multipart/form-data" class="card" style="margin-top:12px;">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m2" />
        <input type="hidden" name="accion" value="importar_archivo" />
        <label for="archivo_db">Importar archivo (.csv, .txt, .json)</label>
        <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
          <input id="archivo_db" name="archivo_db" type="file" accept=".csv,.txt,.json" style="flex:1 1 220px; margin-bottom:0;" />
          <button type="submit" class="btn-secondary">Importar</button>
          <a class="btn-secondary" style="padding:9px 13px; border-radius:10px;" href="/descargar-csv?codigo={{ codigo }}">CSV</a>
        </div>
      </form>

      <div class="stat-mini-row">
        <div class="stat-mini-item"><span class="stat-mini-lbl">Filas:</span><span class="stat-mini-val">{{ stats.count }}</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Suma:</span><span class="stat-mini-val">{{ stats.total }}</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Prom:</span><span class="stat-mini-val">{{ stats.avg }}</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Máx:</span><span class="stat-mini-val">{{ stats.max_val }}</span></div>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr><th style="padding:6px">#</th><th style="padding:6px">Nombre / Producto</th><th style="padding:6px">Valor</th><th style="padding:6px">Categoría</th><th style="padding:6px">Fecha</th><th style="padding:6px">Borrar</th></tr>
          </thead>
          <tbody>
            {% for r in registros %}
              <tr>
                <td style="padding:6px">{{ loop.index }}</td>
                <td style="padding:6px">{{ r.nombre }}</td>
                <td style="padding:6px">{{ r.valor }}</td>
                <td style="padding:6px">{{ r.categoria }}</td>
                <td style="padding:6px">{{ r.fecha }}</td>
                <td style="padding:6px">
                  <form method="POST" style="display:inline; margin:0;">
                    <input type="hidden" name="codigo" value="{{ codigo }}" />
                    <input type="hidden" name="active_mod" value="m2" />
                    <input type="hidden" name="accion" value="borrar_fila" />
                    <input type="hidden" name="fila_idx" value="{{ loop.index0 }}" />
                    <button type="submit" class="btn-secondary btn-small">Quitar</button>
                  </form>
                </td>
              </tr>
            {% else %}
              <tr><td colspan="6" style="padding:8px; color:var(--muted)">Sin registros.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 3. ORDENAR -->
    <section id="m3" class="mod-panel {% if active_mod != 'm3' %}hidden{% endif %}">
      <h2>3. Ordenar y graficar</h2>
      <p style="color:var(--muted)">Escribe lo que deseas ordenar (productos, fechas, palabras o números) y grafica el resultado.</p>

      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m3" />
        <input type="hidden" name="accion" value="ordenar_custom" />
        <label for="custom_items">Elementos a ordenar</label>
        <textarea id="custom_items" name="custom_items" rows="5" placeholder="Escriba aquí lo que desea ordenar...">{{ custom_items }}</textarea>
        <div class="grid-2">
          <div>
            <label for="custom_tipo">Tipo</label>
            <select id="custom_tipo" name="custom_tipo">
              <option value="auto" {% if custom_tipo == 'auto' %}selected{% endif %}>Automático</option>
              <option value="texto" {% if custom_tipo == 'texto' %}selected{% endif %}>Texto / Producto (A-Z)</option>
              <option value="fecha" {% if custom_tipo == 'fecha' %}selected{% endif %}>Fecha</option>
              <option value="numero" {% if custom_tipo == 'numero' %}selected{% endif %}>Número</option>
            </select>
          </div>
          <div>
            <label for="custom_dir">Sentido</label>
            <select id="custom_dir" name="custom_dir">
              <option value="asc" {% if custom_dir == 'asc' %}selected{% endif %}>Ascendente</option>
              <option value="desc" {% if custom_dir == 'desc' %}selected{% endif %}>Descendente</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn-primary">Ordenar y graficar</button>
      </form>

      <div class="stat-mini-row">
        <div class="stat-mini-item"><span class="stat-mini-lbl">Ordenado:</span><span class="stat-mini-val">{{ custom_resultado_str }}</span></div>
      </div>
      <canvas id="chartCustom" height="105"></canvas>
    </section>

    <!-- 4. HOJA DE CÁLCULO (SELECCIÓN DE CELDAS + RANGO + BARRA DE FÓRMULAS) -->
    <section id="m4" class="mod-panel {% if active_mod != 'm4' %}hidden{% endif %}">
      <h2>4. Hoja de cálculo ({{ col_max_letra }}1:{{ col_max_letra }}{{ row_max_num }})</h2>
      <p style="color:var(--muted)">Haz clic o arrastra sobre las celdas para seleccionarlas como en Excel, edita en la barra de fórmulas o dentro de cada celda y usa fórmulas como <code>=SUMA(B1:B5)</code>, <code>=PROMEDIO(C1:C5)</code>, <code>=SI(D1&gt;=E1;"Cumple";"Ajustar")</code>.</p>

      <div class="formula-bar">
        <div id="activeCellRef" class="cell-box-name">A1</div>
        <input id="formulaBarInput" type="text" placeholder="Selecciona una celda para ver o editar su valor o fórmula..." />
        <button type="button" class="btn-secondary btn-small" onclick="aplicarFormulaBar()">Aplicar</button>
        <button type="button" class="btn-secondary btn-small" onclick="copiarSeleccion()">Copiar</button>
        <button type="button" class="btn-secondary btn-small" onclick="pegarSeleccion()">Pegar</button>
      </div>

      <form method="POST" enctype="multipart/form-data">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m4" />

        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
          <button type="submit" name="accion" value="sheet_calcular" class="btn-primary" style="width:auto;">Calcular</button>
          <button type="submit" name="accion" value="sheet_add_row" class="btn-secondary">+ Fila</button>
          <button type="submit" name="accion" value="sheet_del_row" class="btn-secondary">- Fila</button>
          <button type="submit" name="accion" value="sheet_add_col" class="btn-secondary">+ Col</button>
          <button type="submit" name="accion" value="sheet_del_col" class="btn-secondary">- Col</button>
          <button type="button" onclick="window.print()" class="btn-secondary">Imprimir</button>
        </div>

        <div class="grid-2" style="margin-bottom:10px;">
          <div class="card">
            <label for="archivo_sheet">Cargar archivo (.csv o .txt)</label>
            <input id="archivo_sheet" name="archivo_sheet" type="file" accept=".csv,.txt" />
            <button type="submit" name="accion" value="sheet_import" class="btn-secondary">Cargar</button>
          </div>
          <div class="card">
            <label for="sheet_sort_col">Ordenar columna</label>
            <div style="display:flex; gap:8px; flex-wrap:wrap;">
              <select id="sheet_sort_col" name="sheet_sort_col" style="flex:1 1 120px; margin-bottom:0;">
                {% for h in sheet_headers %}
                  <option value="{{ loop.index0 }}" {% if sheet_sort_col == loop.index0 %}selected{% endif %}>{{ col_letras[loop.index0] }} ({{ h }})</option>
                {% endfor %}
              </select>
              <select id="sheet_sort_dir" name="sheet_sort_dir" style="flex:1 1 110px; margin-bottom:0;">
                <option value="asc" {% if sheet_sort_dir == 'asc' %}selected{% endif %}>Ascendente</option>
                <option value="desc" {% if sheet_sort_dir == 'desc' %}selected{% endif %}>Descendente</option>
              </select>
              <button type="submit" name="accion" value="sheet_sort" class="btn-secondary">Ordenar</button>
            </div>
          </div>
        </div>

        <div class="stat-mini-row">
          <div class="stat-mini-item"><span class="stat-mini-lbl">Selección:</span><span id="selRangeLabel" class="stat-mini-val">A1</span></div>
          <div class="stat-mini-item"><span class="stat-mini-lbl">Celdas:</span><span class="stat-mini-val">{{ row_max_num * (col_letras | length) }}</span></div>
          <div class="stat-mini-item"><span class="stat-mini-lbl">Filas:</span><span class="stat-mini-val">{{ row_max_num }}</span></div>
          <div class="stat-mini-item"><span class="stat-mini-lbl">Cols:</span><span class="stat-mini-val">{{ col_letras | length }}</span></div>
        </div>

        <div class="table-wrap" style="margin-bottom:16px;" id="excelGridWrap">
          <table id="excelGrid">
            <thead>
              <tr>
                <th class="row-num"></th>
                {% for h in sheet_headers %}
                  <th>
                    <div style="font-size:0.74rem; color:#fda4af; text-align:center;">{{ col_letras[loop.index0] }}</div>
                    <input class="sheet-cell" style="font-weight:700; text-align:center;" type="text" name="sh_{{ loop.index0 }}" value="{{ h }}" />
                  </th>
                {% endfor %}
              </tr>
            </thead>
            <tbody>
              {% for fila in sheet_raw %}
                {% set r_idx = loop.index0 %}
                <tr>
                  <td class="row-num">{{ loop.index }}</td>
                  {% for celda in fila %}
                    {% set c_idx = loop.index0 %}
                    <td id="td_{{ r_idx }}_{{ c_idx }}" data-r="{{ r_idx }}" data-c="{{ c_idx }}" data-ref="{{ col_letras[c_idx] }}{{ r_idx + 1 }}">
                      <input id="inp_{{ r_idx }}_{{ c_idx }}" class="sheet-cell" type="text" name="c_{{ r_idx }}_{{ c_idx }}" value="{{ celda }}" placeholder="{{ col_letras[c_idx] }}{{ r_idx + 1 }}" />
                      {% set eval_val = sheet_eval[r_idx][c_idx] %}
                      {% if celda.startswith('=') %}
                        <small style="color:#6ee7b7; display:block; padding:0 6px 3px;">= {{ eval_val }}</small>
                      {% endif %}
                    </td>
                  {% endfor %}
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </form>

      {% if mostrar_grafico_hoja %}
        <canvas id="chartSheet" height="95"></canvas>
      {% endif %}
    </section>

    <!-- 5. 30 NOTICIAS -->
    <section id="m5" class="mod-panel {% if active_mod != 'm5' %}hidden{% endif %}">
      <h2>5. Noticias (30)</h2>
      <p style="color:var(--muted)">Filtra las 30 noticias con la lupita o abre los enlaces.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m5" />
        <input type="hidden" name="accion" value="buscar_noticias" />
        <input type="text" name="news_query" value="{{ news_query }}" placeholder="🔍 Buscar noticia..." />
        <button type="submit" class="btn-primary" style="width:auto;">🔍 Buscar</button>
      </form>

      <div style="margin-bottom:12px;">
        <a class="btn-secondary" href="https://news.google.com/search?q={{ news_query_encoded }}" target="_blank" rel="noopener noreferrer">
          Google Noticias →
        </a>
      </div>

      <div class="grid-3">
        {% for n in noticias_lista %}
          <article class="card">
            <div class="news-head">
              <span class="news-logo">{{ n.logo }}</span>
              <span class="badge">{{ n.categoria }} · {{ n.fecha }}</span>
            </div>
            <h3 style="margin:4px 0 6px; font-size:0.96rem;">{{ n.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.83rem;">{{ n.resena }}</p>
            <a href="{{ n.url }}" target="_blank" rel="noopener noreferrer">Abrir enlace →</a>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- 6. 30 VIDEOS -->
    <section id="m6" class="mod-panel {% if active_mod != 'm6' %}hidden{% endif %}">
      <h2>6. Videos (30)</h2>
      <p style="color:var(--muted)">Filtra los 30 videos o abre enlaces en YouTube, TikTok e Instagram.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m6" />
        <input type="hidden" name="accion" value="buscar_videos" />
        <input type="text" name="video_query" value="{{ video_query }}" placeholder="🎬 Buscar video..." />
        <button type="submit" class="btn-primary" style="width:auto;">Buscar</button>
      </form>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
        <a class="btn-secondary" href="https://www.youtube.com/results?search_query={{ video_query_encoded }}" target="_blank" rel="noopener noreferrer">YouTube →</a>
        <a class="btn-secondary" href="https://www.tiktok.com/search?q={{ video_query_encoded }}" target="_blank" rel="noopener noreferrer">TikTok →</a>
        <a class="btn-secondary" href="https://www.instagram.com/explore/" target="_blank" rel="noopener noreferrer">Instagram →</a>
      </div>

      <div class="grid-3">
        {% for v in videos_lista %}
          <article class="card">
            <span class="badge">{{ v.plataforma }} · {{ v.categoria }}</span>
            <h3 style="margin:8px 0 6px; font-size:0.96rem;">{{ v.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.83rem;">{{ v.resena }}</p>
            <a href="{{ v.url }}" target="_blank" rel="noopener noreferrer">Ir al video →</a>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- 7. BUSCADOR WEB -->
    <section id="m7" class="mod-panel {% if active_mod != 'm7' %}hidden{% endif %}">
      <h2>7. Buscador web</h2>
      <p style="color:var(--muted)">Consulta un tema o persona (ej: <em>Messi</em>, <em>tecnología</em>, <em>programación</em>, <em>petróleo</em>, <em>Excel</em>).</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m7" />
        <input type="hidden" name="accion" value="buscar_web" />
        <input type="text" name="web_query" value="{{ web_query }}" placeholder="Buscar en la web..." />
        <button type="submit" class="btn-primary" style="width:auto;">Buscar</button>
      </form>

      <div class="card" style="margin-bottom:14px;">
        <span class="badge">{{ web_def_titulo }}</span>
        <p style="margin:10px 0; line-height:1.6;">{{ web_def_texto }}</p>
        <div style="background:var(--bg); border-left:3px solid var(--accent); padding:10px 12px; border-radius:8px; font-size:0.88rem; line-height:1.5;">
          {{ web_def_ejemplo }}
        </div>
        <div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:12px; font-size:0.86rem;">
          <a href="https://www.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Google →</a>
          <a href="https://news.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Noticias →</a>
          <a href="https://www.youtube.com/results?search_query={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">YouTube →</a>
        </div>
      </div>
    </section>

    <!-- 8. AJUSTES -->
    <section id="m8" class="mod-panel {% if active_mod != 'm8' %}hidden{% endif %}">
      <h2>8. Ajustes</h2>
      <p style="color:var(--muted)">Idioma (20 principales) y ajustes de la aplicación sin crear cuenta.</p>

      <form method="POST" class="grid-2">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m8" />
        <input type="hidden" name="accion" value="guardar_ajustes" />

        <div class="card">
          <h3 style="margin-top:0">Idioma (Top 20)</h3>
          <label for="idioma_sel">Idioma de interfaz</label>
          <select id="idioma_sel" name="idioma_sel">
            {% for code_lang, label_lang in idiomas_20 %}
              <option value="{{ code_lang }}" {% if idioma == code_lang %}selected{% endif %}>{{ label_lang }}</option>
            {% endfor %}
          </select>

          <label for="decimales_sel">Decimales en fórmulas</label>
          <select id="decimales_sel" name="decimales_sel">
            <option value="0" {% if decimales == 0 %}selected{% endif %}>0</option>
            <option value="2" {% if decimales == 2 %}selected{% endif %}>2</option>
            <option value="4" {% if decimales == 4 %}selected{% endif %}>4</option>
          </select>
        </div>

        <div class="card">
          <h3 style="margin-top:0">Visualización</h3>
          <label for="acento_sel">Color de acento</label>
          <select id="acento_sel" name="acento_sel">
            <option value="#e11d48" {% if acento_hex == '#e11d48' %}selected{% endif %}>Carmesí</option>
            <option value="#2563eb" {% if acento_hex == '#2563eb' %}selected{% endif %}>Azul</option>
            <option value="#059669" {% if acento_hex == '#059669' %}selected{% endif %}>Esmeralda</option>
            <option value="#d97706" {% if acento_hex == '#d97706' %}selected{% endif %}>Ámbar</option>
          </select>

          <label for="grafico_hoja_sel">Gráfico en hoja de cálculo</label>
          <select id="grafico_hoja_sel" name="grafico_hoja_sel">
            <option value="si" {% if mostrar_grafico_hoja %}selected{% endif %}>Visible</option>
            <option value="no" {% if not mostrar_grafico_hoja %}selected{% endif %}>Oculto</option>
          </select>

          <button type="submit" class="btn-primary" style="margin-top:6px;">Guardar ajustes</button>
        </div>
      </form>

      <div class="stat-mini-row">
        <div class="stat-mini-item"><span class="stat-mini-lbl">App:</span><span class="stat-mini-val">C-PRE2</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Estado:</span><span class="stat-mini-val" style="color:var(--ok)">OK</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Idioma:</span><span class="stat-mini-val">{{ idioma_nombre }}</span></div>
        <div class="stat-mini-item"><span class="stat-mini-lbl">Uso:</span><span class="stat-mini-val">{{ uso }}/{{ limite }}</span></div>
      </div>
    </section>
  {% endif %}
</div>

<script>
  function openMod(id, btn) {
    document.querySelectorAll('.mod-panel').forEach(p => p.classList.add('hidden'));
    document.querySelectorAll('.mod-btn').forEach(b => b.classList.remove('active'));
    const panel = document.getElementById(id);
    if (panel) panel.classList.remove('hidden');
    if (btn) btn.classList.add('active');
    document.querySelectorAll('input[name="active_mod"]').forEach(inp => inp.value = id);
  }

  {% if autorizado %}
  // Selección de celdas y rango tipo Excel
  let anchorCell = { r: 0, c: 0 };
  let focusCell = { r: 0, c: 0 };
  let isDragging = false;
  let clipboardBlock = null;

  function colToLetterJS(idx) {
    let s = '';
    let n = idx + 1;
    while (n > 0) {
      const rem = (n - 1) % 26;
      s = String.fromCharCode(65 + rem) + s;
      n = Math.floor((n - 1) / 26);
    }
    return s;
  }

  function updateExcelSelectionUI() {
    const rMin = Math.min(anchorCell.r, focusCell.r);
    const rMax = Math.max(anchorCell.r, focusCell.r);
    const cMin = Math.min(anchorCell.c, focusCell.c);
    const cMax = Math.max(anchorCell.c, focusCell.c);

    document.querySelectorAll('#excelGrid td[data-r]').forEach(td => {
      td.classList.remove('selected-cell', 'active-cell');
      const r = parseInt(td.dataset.r, 10);
      const c = parseInt(td.dataset.c, 10);
      if (r >= rMin && r <= rMax && c >= cMin && c <= cMax) {
        td.classList.add('selected-cell');
      }
      if (r === focusCell.r && c === focusCell.c) {
        td.classList.add('active-cell');
      }
    });

    const refActive = colToLetterJS(focusCell.c) + (focusCell.r + 1);
    const refStart = colToLetterJS(cMin) + (rMin + 1);
    const refEnd = colToLetterJS(cMax) + (rMax + 1);
    const refBadge = document.getElementById('activeCellRef');
    const rangeBadge = document.getElementById('selRangeLabel');
    const fBar = document.getElementById('formulaBarInput');
    const activeInp = document.getElementById(`inp_${focusCell.r}_${focusCell.c}`);

    if (refBadge) refBadge.textContent = refActive;
    if (rangeBadge) rangeBadge.textContent = (refStart === refEnd) ? refStart : `${refStart}:${refEnd}`;
    if (fBar && activeInp && document.activeElement !== fBar) {
      fBar.value = activeInp.value;
    }
  }

  function aplicarFormulaBar() {
    const fBar = document.getElementById('formulaBarInput');
    const activeInp = document.getElementById(`inp_${focusCell.r}_${focusCell.c}`);
    if (fBar && activeInp) {
      activeInp.value = fBar.value;
    }
  }

  function copiarSeleccion() {
    const rMin = Math.min(anchorCell.r, focusCell.r);
    const rMax = Math.max(anchorCell.r, focusCell.r);
    const cMin = Math.min(anchorCell.c, focusCell.c);
    const cMax = Math.max(anchorCell.c, focusCell.c);
    const rows = [];
    for (let r = rMin; r <= rMax; r++) {
      const rowVals = [];
      for (let c = cMin; c <= cMax; c++) {
        const inp = document.getElementById(`inp_${r}_${c}`);
        rowVals.push(inp ? inp.value : '');
      }
      rows.push(rowVals);
    }
    clipboardBlock = rows;
  }

  function pegarSeleccion() {
    if (!clipboardBlock || !clipboardBlock.length) return;
    for (let dr = 0; dr < clipboardBlock.length; dr++) {
      for (let dc = 0; dc < clipboardBlock[dr].length; dc++) {
        const inp = document.getElementById(`inp_${focusCell.r + dr}_${focusCell.c + dc}`);
        if (inp) inp.value = clipboardBlock[dr][dc];
      }
    }
    updateExcelSelectionUI();
  }

  document.querySelectorAll('#excelGrid td[data-r]').forEach(td => {
    td.addEventListener('mousedown', () => {
      isDragging = true;
      anchorCell = { r: parseInt(td.dataset.r, 10), c: parseInt(td.dataset.c, 10) };
      focusCell = { ...anchorCell };
      updateExcelSelectionUI();
    });
    td.addEventListener('mouseenter', () => {
      if (!isDragging) return;
      focusCell = { r: parseInt(td.dataset.r, 10), c: parseInt(td.dataset.c, 10) };
      updateExcelSelectionUI();
    });
    const innerInp = td.querySelector('input.sheet-cell');
    if (innerInp) {
      innerInp.addEventListener('focus', () => {
        if (!isDragging) {
          anchorCell = { r: parseInt(td.dataset.r, 10), c: parseInt(td.dataset.c, 10) };
          focusCell = { ...anchorCell };
        }
        updateExcelSelectionUI();
      });
      innerInp.addEventListener('input', () => {
        const fBar = document.getElementById('formulaBarInput');
        if (fBar && parseInt(td.dataset.r, 10) === focusCell.r && parseInt(td.dataset.c, 10) === focusCell.c) {
          fBar.value = innerInp.value;
        }
      });
    }
  });

  document.addEventListener('mouseup', () => {
    isDragging = false;
  });

  updateExcelSelectionUI();

  const ctxCustom = document.getElementById('chartCustom');
  if (ctxCustom) {
    new Chart(ctxCustom, {
      type: 'bar',
      data: {
        labels: {{ custom_labels | tojson }},
        datasets: [{
          label: 'Serie ordenada',
          data: {{ custom_values | tojson }},
          backgroundColor: 'rgba(225, 29, 72, 0.55)',
          borderColor: '{{ acento_hex }}',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f4f4fa' } } },
        scales: {
          x: { ticks: { color: '#9e9eb4' }, grid: { color: '#282838' } },
          y: { ticks: { color: '#9e9eb4' }, grid: { color: '#282838' } }
        }
      }
    });
  }

  {% if mostrar_grafico_hoja %}
  const ctxSheet = document.getElementById('chartSheet');
  if (ctxSheet) {
    new Chart(ctxSheet, {
      type: 'line',
      data: {
        labels: {{ sheet_chart_labels | tojson }},
        datasets: [{
          label: 'Valores de la hoja',
          data: {{ sheet_chart_values | tojson }},
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.18)',
          tension: 0.25,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f4f4fa' } } },
        scales: {
          x: { ticks: { color: '#9e9eb4' }, grid: { color: '#282838' } },
          y: { ticks: { color: '#9e9eb4' }, grid: { color: '#282838' } }
        }
      }
    });
  }
  {% endif %}
  {% endif %}
</script>
</body>
</html>
"""

ESTADO_SESIONES = {}


def _crear_hoja_inicial():
    cols = 10
    rows = 20
    headers = ["Concepto", "Cantidad", "Valor", "Subtotal", "Meta", "Diferencia", "Estado", "Nota", "Extra 1", "Extra 2"]
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    base = [
        ("Item A", "10", "25", "=B1*C1", "220", "=D1-E1", '=SI(D1>=E1;"Cumple";"Ajustar")', "Base", "", ""),
        ("Item B", "8", "30", "=B2*C2", "200", "=D2-E2", '=SI(D2>=E2;"Cumple";"Ajustar")', "Base", "", ""),
        ("Item C", "12", "18", "=B3*C3", "210", "=D3-E3", '=SI(D3>=E3;"Cumple";"Ajustar")', "Base", "", ""),
        ("Item D", "6", "45", "=B4*C4", "250", "=D4-E4", '=SI(D4>=E4;"Cumple";"Ajustar")', "Base", "", ""),
        ("Item E", "15", "20", "=B5*C5", "280", "=D5-E5", '=SI(D5>=E5;"Cumple";"Ajustar")', "Base", "", ""),
        ("Total", "=SUMA(B1:B5)", "=PROMEDIO(C1:C5)", "=SUMA(D1:D5)", "=SUMA(E1:E5)", "=SUMA(F1:F5)", "", "Resumen", "", ""),
    ]
    for r_i, fila_d in enumerate(base):
        for c_i, val_d in enumerate(fila_d):
            grid[r_i][c_i] = val_d
    return headers, grid


def obtener_estado(codigo):
    code = (codigo or "").strip().upper()
    if code not in CODIGOS_ACCESO:
        return None
    if code not in ESTADO_SESIONES:
        sh_h, sh_r = _crear_hoja_inicial()
        ESTADO_SESIONES[code] = {
            "uso": 0,
            "active_mod": "m1",
            "idioma": "es",
            "acento_hex": "#e11d48",
            "decimales": 2,
            "mostrar_grafico_hoja": True,
            "registros": [
                {"nombre": "Producto Alfa", "valor": 45, "categoria": "Inventario", "fecha": "2026-11-18"},
                {"nombre": "Producto Beta", "valor": 120, "categoria": "Ventas", "fecha": "2026-11-20"},
                {"nombre": "Producto Gamma", "valor": 75, "categoria": "Inventario", "fecha": "2026-11-15"},
            ],
            "code_input": (
                "numeros = [15, 42, 8, 90, 27, 63]\n"
                "print('Ordenados:', sorted(numeros))\n"
                "print('Suma:', sum(numeros), '| Promedio:', round(statistics.mean(numeros), 2))"
            ),
            "code_output": None,
            "custom_items": "",
            "custom_tipo": "auto",
            "custom_dir": "asc",
            "sheet_headers": sh_h,
            "sheet_raw": sh_r,
            "sheet_sort_col": 0,
            "sheet_sort_dir": "asc",
            "news_query": "",
            "video_query": "",
            "web_query": "Messi",
        }
    return ESTADO_SESIONES[code]


def _col_to_idx(col_str):
    col_str = col_str.upper().strip()
    idx = 0
    for ch in col_str:
        if "A" <= ch <= "Z":
            idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def _parse_rango_coords(rango_str, grid_raw):
    m = re.match(r"^([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)$", rango_str.strip())
    if not m:
        return []
    c1, r1, c2, r2 = _col_to_idx(m.group(1)), int(m.group(2)) - 1, _col_to_idx(m.group(3)), int(m.group(4)) - 1
    coords = []
    for r in range(min(r1, r2), max(r1, r2) + 1):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            if 0 <= r < len(grid_raw) and 0 <= c < len(grid_raw[r]):
                coords.append((r, c))
    return coords


def _expand_range(rango_str, grid_raw, decimales=2):
    vals = []
    for r, c in _parse_rango_coords(rango_str, grid_raw):
        v = evaluar_celda(grid_raw[r][c], grid_raw, visitadas=set(), decimales=decimales)
        try:
            vals.append(float(v))
        except (TypeError, ValueError):
            pass
    return vals


def _expand_text_range(rango_str, grid_raw, decimales=2):
    items = []
    for r, c in _parse_rango_coords(rango_str, grid_raw):
        v = str(evaluar_celda(grid_raw[r][c], grid_raw, visitadas=set(), decimales=decimales)).strip()
        if v:
            items.append(v)
    return items


def _resolver_token_celda(token, grid_raw, visitadas, decimales=2):
    t = token.strip().strip('"')
    ref = re.match(r"^([A-Za-z]{1,2})(\d{1,3})$", t)
    if ref:
        ci, ri = _col_to_idx(ref.group(1)), int(ref.group(2)) - 1
        if 0 <= ri < len(grid_raw) and 0 <= ci < len(grid_raw[ri]):
            return str(evaluar_celda(grid_raw[ri][ci], grid_raw, set(visitadas), decimales=decimales))
        return ""
    return t


def _fmt_num(val_num, decimales=2):
    if isinstance(val_num, float) and val_num.is_integer():
        return str(int(val_num))
    if isinstance(val_num, float):
        return str(round(val_num, decimales))
    return str(val_num)


def evaluar_celda(val, grid_raw, visitadas=None, decimales=2):
    if visitadas is None:
        visitadas = set()
    s = str(val or "").strip()
    if not s.startswith("="):
        return s

    expr = s[1:].strip()

    if expr.upper() in ("HOY()", "TODAY()"):
        return datetime.now().strftime("%Y-%m-%d")

    m_mayus = re.match(r"^MAYUS\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_mayus:
        return _resolver_token_celda(m_mayus.group(1), grid_raw, visitadas, decimales).upper()

    m_minus = re.match(r"^MINUS\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_minus:
        return _resolver_token_celda(m_minus.group(1), grid_raw, visitadas, decimales).lower()

    m_conc = re.match(r"^CONCATENAR\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_conc:
        partes = re.split(r"[;,]", m_conc.group(1))
        return "".join(_resolver_token_celda(p, grid_raw, visitadas, decimales) for p in partes)

    m_cs = re.match(r"^CONTAR\.SI\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_cs:
        partes_cs = [p.strip() for p in re.split(r"[;,]", m_cs.group(1))]
        if len(partes_cs) >= 2:
            criterio = partes_cs[1].strip('"')
            items = _expand_text_range(partes_cs[0], grid_raw, decimales)
            return str(sum(1 for it in items if it == criterio))

    m_ss = re.match(r"^SUMAR\.SI\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_ss:
        partes_ss = [p.strip() for p in re.split(r"[;,]", m_ss.group(1))]
        if len(partes_ss) >= 3:
            criterio = partes_ss[1].strip('"')
            crit_coords = _parse_rango_coords(partes_ss[0], grid_raw)
            sum_coords = _parse_rango_coords(partes_ss[2], grid_raw)
            total_ss = 0.0
            for idx_p, (rc, cc) in enumerate(crit_coords):
                val_c = str(evaluar_celda(grid_raw[rc][cc], grid_raw, set(visitadas), decimales)).strip()
                if val_c == criterio and idx_p < len(sum_coords):
                    sr, sc = sum_coords[idx_p]
                    try:
                        total_ss += float(evaluar_celda(grid_raw[sr][sc], grid_raw, set(visitadas), decimales))
                    except (TypeError, ValueError):
                        pass
            return _fmt_num(total_ss, decimales)

    m_si = re.match(r"^SI\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_si:
        partes_si = [p.strip() for p in re.split(r"[;,]", m_si.group(1))]
        if len(partes_si) >= 3:
            cond_raw, v_true, v_false = partes_si[0], partes_si[1].strip('"'), partes_si[2].strip('"')
            cond_eval = re.sub(
                r"\b([A-Za-z]{1,2})(\d{1,3})\b",
                lambda mm: str(float(evaluar_celda(grid_raw[int(mm.group(2)) - 1][_col_to_idx(mm.group(1))], grid_raw, set(visitadas), decimales))),
                cond_raw,
            )
            try:
                if re.match(r"^[0-9+\-*/().<>=!\s]+$", cond_eval) and eval(cond_eval, {"__builtins__": {}}, {}):
                    return v_true
                return v_false
            except Exception:
                return v_false

    m_red = re.match(r"^REDONDEAR\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_red:
        partes_r = [p.strip() for p in re.split(r"[;,]", m_red.group(1))]
        if len(partes_r) >= 2:
            v_num = float(evaluar_celda("=" + partes_r[0], grid_raw, set(visitadas), decimales))
            dec = int(float(partes_r[1]))
            return str(round(v_num, max(0, dec)))

    def repl_func(match):
        fname = match.group(1).upper()
        arg = match.group(2).strip()
        if fname in ("CONTARA", "COUNTA"):
            rango_items = _expand_text_range(arg, grid_raw, decimales)
            if rango_items:
                return str(len(rango_items))
            partes_t = [_resolver_token_celda(p, grid_raw, visitadas, decimales) for p in re.split(r"[;,]", arg)]
            return str(len([x for x in partes_t if x != ""]))
        nums = _expand_range(arg, grid_raw, decimales)
        if not nums:
            for part in re.split(r"[;,]", arg):
                part = part.strip()
                ref = re.match(r"^([A-Za-z]+)(\d+)$", part)
                if ref:
                    ci, ri = _col_to_idx(ref.group(1)), int(ref.group(2)) - 1
                    if 0 <= ri < len(grid_raw) and 0 <= ci < len(grid_raw[ri]):
                        try:
                            nums.append(float(evaluar_celda(grid_raw[ri][ci], grid_raw, set(visitadas), decimales)))
                        except (TypeError, ValueError):
                            pass
                else:
                    try:
                        nums.append(float(part))
                    except ValueError:
                        pass
        if fname in ("CONTAR", "COUNT"):
            return str(len(nums))
        if not nums:
            return "0"
        if fname in ("SUMA", "SUM"):
            return str(sum(nums))
        if fname in ("PROMEDIO", "AVG", "AVERAGE"):
            return str(sum(nums) / len(nums))
        if fname in ("MEDIANA", "MEDIAN"):
            return str(statistics.median(nums))
        if fname in ("MODA", "MODE"):
            try:
                return str(statistics.mode(nums))
            except statistics.StatisticsError:
                return str(nums[0])
        if fname == "MAX":
            return str(max(nums))
        if fname == "MIN":
            return str(min(nums))
        return "0"

    expr = re.sub(
        r"\b(SUMA|SUM|PROMEDIO|AVG|AVERAGE|MEDIANA|MEDIAN|MODA|MODE|MAX|MIN|CONTAR|COUNT|CONTARA|COUNTA)\(([^()]+)\)",
        repl_func,
        expr,
        flags=re.IGNORECASE,
    )
    expr = re.sub(r"\bPOTENCIA\(([^,;\s]+)[,;]([^)]+)\)", r"((\1)**(\2))", expr, flags=re.IGNORECASE)
    expr = re.sub(r"\bRAIZ\(([^)]+)\)", r"((\1)**0.5)", expr, flags=re.IGNORECASE)

    def repl_cell(match):
        ci, ri = _col_to_idx(match.group(1)), int(match.group(2)) - 1
        key = (ri, ci)
        if key in visitadas or ri < 0 or ci < 0 or ri >= len(grid_raw) or ci >= len(grid_raw[ri]):
            return "0"
        visitadas.add(key)
        res = evaluar_celda(grid_raw[ri][ci], grid_raw, visitadas, decimales)
        try:
            return str(float(res))
        except (TypeError, ValueError):
            return "0"

    expr = re.sub(r"\b([A-Za-z]{1,2})(\d{1,3})\b", repl_cell, expr)

    try:
        if re.match(r"^[0-9+\-*/().\s]+$", expr):
            val_num = eval(expr, {"__builtins__": {}}, {})
            return _fmt_num(val_num, decimales)
    except Exception:
        return "ERR"
    return expr


def evaluar_hoja(sheet_raw, decimales=2):
    return [[evaluar_celda(c, sheet_raw, set(), decimales=decimales) for c in fila] for fila in sheet_raw]


def parsear_lineas_db(texto):
    nuevos = []
    for idx, linea in enumerate((texto or "").splitlines(), start=1):
        linea = linea.strip()
        if not linea:
            continue
        partes = [p.strip() for p in linea.split(",")]
        nombre = partes[0]
        try:
            valor = float(partes[1]) if len(partes) > 1 and partes[1] != "" else float(idx)
        except ValueError:
            valor = 0.0
        val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
        cat = partes[2] if len(partes) > 2 and partes[2] else "General"
        fecha = partes[3] if len(partes) > 3 and partes[3] else datetime.now().strftime("%Y-%m-%d")
        nuevos.append({"nombre": nombre, "valor": val_fmt, "categoria": cat, "fecha": fecha})
    return nuevos


def parsear_archivo_subido(file_storage):
    filename = (file_storage.filename or "").lower()
    texto = file_storage.read().decode("utf-8", errors="ignore").strip()
    if not texto:
        return []
    if filename.endswith(".json") or texto.startswith("[") or texto.startswith("{"):
        data = json.loads(texto)
        items = data if isinstance(data, list) else data.get("registros", [])
        nuevos = []
        for idx, item in enumerate(items, start=1):
            if isinstance(item, dict):
                nombre = str(item.get("nombre") or item.get("producto") or f"Item {idx}").strip()
                try:
                    valor = float(item.get("valor", 0))
                except (TypeError, ValueError):
                    valor = 0.0
                val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
                cat = str(item.get("categoria") or "JSON").strip()
                fecha = str(item.get("fecha") or datetime.now().strftime("%Y-%m-%d")).strip()
                nuevos.append({"nombre": nombre, "valor": val_fmt, "categoria": cat, "fecha": fecha})
        return nuevos
    return parsear_lineas_db(texto)


def ordenar_elementos_custom(raw_text, tipo="auto", direccion="asc"):
    partes = [p.strip() for p in (raw_text or "").replace("\n", ",").split(",") if p.strip()]
    if not partes:
        return ["Sin datos"], [0]
    rev = (direccion == "desc")

    def es_numero(v):
        try:
            float(v)
            return True
        except ValueError:
            return False

    def es_fecha(v):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(v, fmt)
                return True
            except ValueError:
                continue
        return False

    def clave_fecha(v):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(v, fmt)
            except ValueError:
                continue
        return datetime.min

    if tipo == "numero":
        nums = [float(p) for p in partes if es_numero(p)]
        if nums:
            ord_n = sorted(nums, reverse=rev)
            limpios = [int(x) if float(x).is_integer() else round(float(x), 4) for x in ord_n]
            return [str(x) for x in limpios], limpios
    elif tipo == "fecha":
        ord_f = sorted(partes, key=clave_fecha, reverse=rev)
        return ord_f, [i + 1 for i in range(len(ord_f))]
    elif tipo == "texto":
        ord_t = sorted(partes, key=lambda s: s.lower(), reverse=rev)
        return ord_t, [float(x) if es_numero(x) else (i + 1) for i, x in enumerate(ord_t)]

    if all(es_numero(p) for p in partes):
        nums = sorted([float(p) for p in partes], reverse=rev)
        limpios = [int(x) if float(x).is_integer() else round(float(x), 4) for x in nums]
        return [str(x) for x in limpios], limpios
    if all(es_fecha(p) for p in partes):
        ord_f = sorted(partes, key=clave_fecha, reverse=rev)
        return ord_f, [i + 1 for i in range(len(ord_f))]

    ord_a = sorted(partes, key=lambda s: s.lower(), reverse=rev)
    return ord_a, [float(x) if es_numero(x) else (i + 1) for i, x in enumerate(ord_a)]


def calcular_stats(registros):
    if not registros:
        return {"count": 0, "total": 0, "avg": 0, "max_val": 0}
    vals = [float(r.get("valor", 0) or 0) for r in registros]
    fmt = lambda v: int(v) if float(v).is_integer() else round(float(v), 2)
    return {
        "count": len(vals),
        "total": fmt(sum(vals)),
        "avg": fmt(statistics.mean(vals)),
        "max_val": fmt(max(vals)),
    }


def ejecutar_codigo_python(codigo_fuente):
    bloqueados = ["__import__", "open(", "exec(", "eval(", "compile(", "input("]
    bajo = (codigo_fuente or "").lower()
    for b in bloqueados:
        if b in bajo:
            return f"Bloqueado: '{b}'."
    buf = io.StringIO()
    entorno = {
        "__builtins__": {
            "print": lambda *args, **kwargs: print(*args, file=buf, **kwargs),
            "len": len, "sum": sum, "min": min, "max": max, "sorted": sorted,
            "reversed": reversed, "enumerate": enumerate, "zip": zip, "round": round,
            "abs": abs, "pow": pow, "range": range, "int": int, "float": float,
            "str": str, "bool": bool, "list": list, "dict": dict, "set": set, "tuple": tuple,
        },
        "math": math,
        "statistics": statistics,
        "datetime": datetime,
    }
    try:
        exec(codigo_fuente, entorno, {})
        out = buf.getvalue().strip()
        return out if out else "Script ejecutado sin salida impresa."
    except Exception as e:
        return f"Error: {e}"


def responder_busqueda_natural(query):
    q_raw = (query or "Messi").strip()
    q_norm = (
        q_raw.lower()
        .replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )
    for clave, info in RESPUESTAS_NATURALES.items():
        if clave in q_norm or q_norm in clave:
            return info["titulo"], info["concepto"], info["ejemplo"]

    tema = q_raw.capitalize()
    return (
        tema,
        f"{tema} se refiere a un tema, persona o concepto que conviene revisar desde su idea "
        f"central, su funcionamiento práctico y los resultados o noticias disponibles.",
        f"Usa los enlaces de abajo para ver resultados directos en Google, Noticias o YouTube sobre {q_raw}.",
    )


def _nombre_idioma(code):
    for c, lbl in IDIOMAS_20:
        if c == code:
            return lbl
    return "Español"


def render_panel(codigo, estado, error_msg=None, aviso_msg=None):
    info = CODIGOS_ACCESO[codigo]
    custom_labels, custom_values = ordenar_elementos_custom(
        estado["custom_items"], estado["custom_tipo"], estado["custom_dir"]
    )
    decimales = estado.get("decimales", 2)
    sheet_eval = evaluar_hoja(estado["sheet_raw"], decimales=decimales)

    col_letras = [_col_letra(i) for i in range(len(estado["sheet_headers"]))]
    sheet_labels = []
    sheet_vals = []
    for idx, fila_ev in enumerate(sheet_eval):
        lbl = fila_ev[0] if fila_ev and fila_ev[0] else f"Fila {idx + 1}"
        num_encontrado = None
        for cell in reversed(fila_ev):
            try:
                num_encontrado = float(cell)
                break
            except (TypeError, ValueError):
                continue
        if num_encontrado is not None:
            sheet_labels.append(str(lbl))
            sheet_vals.append(int(num_encontrado) if num_encontrado.is_integer() else round(num_encontrado, decimales))

    nq = (estado["news_query"] or "").strip()
    if nq:
        noticias_lista = [
            n for n in NOTICIAS_30
            if nq.lower() in n["titulo"].lower()
            or nq.lower() in n["categoria"].lower()
            or nq.lower() in n["resena"].lower()
        ] or NOTICIAS_30
    else:
        noticias_lista = NOTICIAS_30

    vq = (estado["video_query"] or "").strip()
    if vq:
        videos_lista = [
            v for v in VIDEOS_30
            if vq.lower() in v["titulo"].lower()
            or vq.lower() in v["categoria"].lower()
            or vq.lower() in v["plataforma"].lower()
            or vq.lower() in v["resena"].lower()
        ] or VIDEOS_30
    else:
        videos_lista = VIDEOS_30

    wq = (estado["web_query"] or "Messi").strip()
    web_t, web_def, web_ej = responder_busqueda_natural(wq)

    return render_template_string(
        HTML_TEMPLATE,
        autorizado=True,
        error=error_msg,
        aviso=aviso_msg,
        codigo=codigo,
        plan=info["plan"],
        limite=info["limite"],
        uso=estado["uso"],
        idioma=estado["idioma"],
        idioma_nombre=_nombre_idioma(estado["idioma"]),
        idiomas_20=IDIOMAS_20,
        acento_hex=estado["acento_hex"],
        decimales=decimales,
        mostrar_grafico_hoja=estado.get("mostrar_grafico_hoja", True),
        active_mod=estado.get("active_mod", "m1"),
        code_input=estado["code_input"],
        code_output=estado["code_output"],
        registros=estado["registros"],
        stats=calcular_stats(estado["registros"]),
        custom_items=estado["custom_items"],
        custom_tipo=estado["custom_tipo"],
        custom_dir=estado["custom_dir"],
        custom_resultado_str=", ".join(str(x) for x in custom_labels),
        custom_labels=custom_labels,
        custom_values=custom_values,
        sheet_headers=estado["sheet_headers"],
        sheet_raw=estado["sheet_raw"],
        sheet_eval=sheet_eval,
        col_letras=col_letras,
        col_max_letra=col_letras[-1] if col_letras else "A",
        row_max_num=len(estado["sheet_raw"]),
        sheet_sort_col=estado["sheet_sort_col"],
        sheet_sort_dir=estado["sheet_sort_dir"],
        sheet_chart_labels=sheet_labels or ["Sin datos"],
        sheet_chart_values=sheet_vals or [0],
        news_query=nq,
        news_query_encoded=urllib.parse.quote_plus(nq or "noticias hoy"),
        noticias_lista=noticias_lista,
        video_query=vq,
        video_query_encoded=urllib.parse.quote_plus(vq or "tendencias"),
        videos_lista=videos_lista,
        web_query=wq,
        web_query_encoded=urllib.parse.quote_plus(wq),
        web_def_titulo=web_t,
        web_def_texto=web_def,
        web_def_ejemplo=web_ej,
    )


def leer_hoja_desde_form(estado):
    n_cols = len(estado["sheet_headers"])
    n_rows = len(estado["sheet_raw"])
    nuevos_headers = [
        (request.form.get(f"sh_{c}") if request.form.get(f"sh_{c}") is not None else estado["sheet_headers"][c])
        for c in range(n_cols)
    ]
    nueva_tabla = []
    for r in range(n_rows):
        fila = []
        for c in range(n_cols):
            val = request.form.get(f"c_{r}_{c}")
            fila.append(val if val is not None else estado["sheet_raw"][r][c])
        nueva_tabla.append(fila)
    estado["sheet_headers"] = nuevos_headers
    estado["sheet_raw"] = nueva_tabla


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        codigo = (request.form.get("codigo") or "").strip().upper()
        estado = obtener_estado(codigo)
        if not estado:
            return render_template_string(
                HTML_TEMPLATE,
                autorizado=False,
                idioma="es",
                acento_hex="#e11d48",
                error="Código no válido. Usa DEMO2026, VIP100 o EXCELSO99.",
            )

        mod_sel = request.form.get("active_mod")
        if mod_sel in ("m1", "m2", "m3", "m4", "m5", "m6", "m7", "m8"):
            estado["active_mod"] = mod_sel

        limite = CODIGOS_ACCESO[codigo]["limite"]
        accion = request.form.get("accion")
        aviso = None
        error = None

        if accion:
            if estado["uso"] >= limite:
                return render_panel(codigo, estado, error_msg="Límite de uso alcanzado.")
            estado["uso"] += 1

        if accion == "ejecutar_codigo":
            src = request.form.get("code_input") or ""
            estado["code_input"] = src
            estado["code_output"] = ejecutar_codigo_python(src)
            estado["active_mod"] = "m1"

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
                    aviso = f"Registro '{nombre}' guardado."
            except (TypeError, ValueError):
                error = "Ingresa un valor numérico válido."
            estado["active_mod"] = "m2"

        elif accion == "cargar_lote_db":
            lote = parsear_lineas_db(request.form.get("lote_db_texto") or "")
            modo = request.form.get("modo_carga_db") or "agregar"
            if lote:
                if modo == "reemplazar":
                    estado["registros"] = lote
                else:
                    estado["registros"].extend(lote)
                aviso = f"Cargados {len(lote)} registro(s)."
            else:
                error = "Escriba o pegue al menos una fila."
            estado["active_mod"] = "m2"

        elif accion == "importar_archivo":
            archivo = request.files.get("archivo_db")
            if archivo and archivo.filename:
                try:
                    nuevos = parsear_archivo_subido(archivo)
                    if nuevos:
                        estado["registros"].extend(nuevos)
                        aviso = f"Importados {len(nuevos)} registro(s) desde '{archivo.filename}'."
                    else:
                        error = "Archivo sin filas válidas."
                except Exception as e:
                    error = f"Error al importar archivo: {e}"
            estado["active_mod"] = "m2"

        elif accion == "borrar_fila":
            try:
                idx = int(request.form.get("fila_idx", -1))
                if 0 <= idx < len(estado["registros"]):
                    estado["registros"].pop(idx)
                    aviso = "Registro eliminado."
            except Exception:
                error = "No se pudo eliminar el registro."
            estado["active_mod"] = "m2"

        elif accion == "ordenar_custom":
            estado["custom_items"] = request.form.get("custom_items") or ""
            estado["custom_tipo"] = request.form.get("custom_tipo") or "auto"
            estado["custom_dir"] = request.form.get("custom_dir") or "asc"
            estado["active_mod"] = "m3"

        elif accion in (
            "sheet_calcular", "sheet_add_row", "sheet_del_row",
            "sheet_add_col", "sheet_del_col", "sheet_sort", "sheet_import"
        ):
            leer_hoja_desde_form(estado)
            n_cols = len(estado["sheet_headers"])
            dec = estado.get("decimales", 2)
            if accion == "sheet_add_row":
                estado["sheet_raw"].append(["" for _ in range(n_cols)])
                aviso = "Fila agregada."
            elif accion == "sheet_del_row":
                if len(estado["sheet_raw"]) > 1:
                    estado["sheet_raw"].pop()
                    aviso = "Última fila eliminada."
                else:
                    error = "Debe quedar al menos 1 fila."
            elif accion == "sheet_add_col":
                estado["sheet_headers"].append(f"Col {_col_letra(n_cols)}")
                for f in estado["sheet_raw"]:
                    f.append("")
                aviso = "Columna agregada."
            elif accion == "sheet_del_col":
                if n_cols > 1:
                    estado["sheet_headers"].pop()
                    for f in estado["sheet_raw"]:
                        f.pop()
                    aviso = "Última columna eliminada."
                else:
                    error = "Debe quedar al menos 1 columna."
            elif accion == "sheet_import":
                arch = request.files.get("archivo_sheet")
                if arch and arch.filename:
                    txt = arch.read().decode("utf-8", errors="ignore").strip()
                    filas_csv = [list(r) for r in csv.reader(io.StringIO(txt)) if any(c.strip() for c in r)]
                    if filas_csv:
                        max_c = max(len(r) for r in filas_csv)
                        estado["sheet_headers"] = [f"Col {_col_letra(i)}" for i in range(max_c)]
                        estado["sheet_raw"] = [r + [""] * (max_c - len(r)) for r in filas_csv]
                        aviso = f"Hoja cargada desde '{arch.filename}'."
                    else:
                        error = "Archivo vacío."
            elif accion == "sheet_sort":
                col_i = int(request.form.get("sheet_sort_col", 0))
                s_dir = request.form.get("sheet_sort_dir", "asc")
                estado["sheet_sort_col"] = max(0, min(col_i, n_cols - 1))
                estado["sheet_sort_dir"] = s_dir
                rev = (s_dir == "desc")
                evaluada_pairs = list(zip(estado["sheet_raw"], evaluar_hoja(estado["sheet_raw"], decimales=dec)))

                def clave_fila(par):
                    _, ev_f = par
                    v = ev_f[estado["sheet_sort_col"]] if estado["sheet_sort_col"] < len(ev_f) else ""
                    try:
                        return (0, float(v), "")
                    except ValueError:
                        return (1, 0.0, str(v).lower())

                evaluada_pairs.sort(key=clave_fila, reverse=rev)
                estado["sheet_raw"] = [p[0] for p in evaluada_pairs]
                aviso = f"Hoja ordenada por columna {_col_letra(estado['sheet_sort_col'])}."
            else:
                aviso = "Hoja calculada."
            estado["active_mod"] = "m4"

        elif accion == "buscar_noticias":
            estado["news_query"] = (request.form.get("news_query") or "").strip()
            estado["active_mod"] = "m5"

        elif accion == "buscar_videos":
            estado["video_query"] = (request.form.get("video_query") or "").strip()
            estado["active_mod"] = "m6"

        elif accion == "buscar_web":
            estado["web_query"] = (request.form.get("web_query") or "Messi").strip()
            estado["active_mod"] = "m7"

        elif accion == "guardar_ajustes":
            sel_lang = (request.form.get("idioma_sel") or "es").strip()
            if any(c == sel_lang for c, _ in IDIOMAS_20):
                estado["idioma"] = sel_lang
            sel_acc = (request.form.get("acento_sel") or "#e11d48").strip()
            if sel_acc in ("#e11d48", "#2563eb", "#059669", "#d97706"):
                estado["acento_hex"] = sel_acc
            try:
                dec_val = int(request.form.get("decimales_sel", 2))
                if dec_val in (0, 2, 4):
                    estado["decimales"] = dec_val
            except ValueError:
                pass
            estado["mostrar_grafico_hoja"] = (request.form.get("grafico_hoja_sel") != "no")
            aviso = "Ajustes guardados."
            estado["active_mod"] = "m8"

        return render_panel(codigo, estado, error_msg=error, aviso_msg=aviso)

    return render_template_string(
        HTML_TEMPLATE,
        autorizado=False,
        idioma="es",
        acento_hex="#e11d48",
        error=None,
    )


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
        headers={"Content-Disposition": "attachment; filename=c_pre2_base_datos.csv"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

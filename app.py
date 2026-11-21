import csv
import io
import json
import math
import os
import statistics
import urllib.parse
from datetime import datetime
from flask import Flask, Response, render_template_string, request

app = Flask(__name__)

CODIGOS_ACCESO = {
    "DEMO2026": {"plan": "DEMO", "limite": 100},
    "VIP100": {"plan": "VIP", "limite": 500},
    "EXCELSO99": {"plan": "PRO", "limite": 9999},
}

NOTICIAS_BASE = [
    {
        "titulo": "Últimas noticias de tecnología e inteligencia artificial",
        "categoria": "Tecnología",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Explora las novedades tecnológicas, software, hardware y tendencias globales del momento.",
        "url": "https://news.google.com/search?q=tecnologia+inteligencia+artificial",
    },
    {
        "titulo": "Energía, petróleo, geología y cuencas sedimentarias",
        "categoria": "Geología",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Seguimiento de producción energética, exploración, gravedad API y dinámica de cuencas.",
        "url": "https://news.google.com/search?q=petroleo+geologia+energia",
    },
    {
        "titulo": "Programación, desarrollo web y ciberseguridad",
        "categoria": "Programación",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Novedades en Python, Flask, desarrollo móvil, bases de datos y herramientas de software.",
        "url": "https://news.google.com/search?q=programacion+python+desarrollo+web",
    },
    {
        "titulo": "Ciencia, espacio, física y astronomía",
        "categoria": "Ciencia",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Descubrimientos científicos, astrofísica, experimentos y avances en investigación.",
        "url": "https://news.google.com/search?q=ciencia+astronomia+fisica",
    },
    {
        "titulo": "Deportes internacionales y fútbol mundial",
        "categoria": "Deportes",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Resultados, análisis, fichajes y noticias destacadas del fútbol y deportes globales.",
        "url": "https://news.google.com/search?q=futbol+deportes+internacional",
    },
    {
        "titulo": "Economía, mercados y negocios digitales",
        "categoria": "Economía",
        "fuente": "Google Noticias",
        "fecha": "Hoy",
        "resumen": "Movimientos del mercado, emprendimiento, criptomonedas y finanzas globales.",
        "url": "https://news.google.com/search?q=economia+negocios+finanzas",
    },
]

VIDEOS_BASE = [
    {
        "titulo": "Tendencias y videos virales en TikTok",
        "plataforma": "TikTok",
        "categoria": "Viral / TikTok",
        "url": "https://www.tiktok.com/search?q=tendencias%20virales",
        "descripcion": "Abre búsquedas y videos populares en TikTok al instante.",
    },
    {
        "titulo": "Reels y videos destacados en Instagram",
        "plataforma": "Instagram",
        "categoria": "Reels / Instagram",
        "url": "https://www.instagram.com/explore/",
        "descripcion": "Explora reels, creadores y contenido visual en Instagram.",
    },
    {
        "titulo": "Videos populares y tutoriales en YouTube",
        "plataforma": "YouTube",
        "categoria": "Videos / YouTube",
        "url": "https://www.youtube.com/results?search_query=tendencias+programacion+ciencia",
        "descripcion": "Busca y mira videos largos o cortos directamente en YouTube.",
    },
    {
        "titulo": "Python y Flask desde cero a proyectos reales",
        "plataforma": "YouTube",
        "categoria": "Programación",
        "url": "https://www.youtube.com/results?search_query=python+flask+tutorial+completo",
        "descripcion": "Videotutoriales prácticos de Python, web y automatización.",
    },
    {
        "titulo": "Geología del petróleo y yacimientos explicados",
        "plataforma": "YouTube",
        "categoria": "Geología",
        "url": "https://www.youtube.com/results?search_query=geologia+del+petroleo+yacimientos",
        "descripcion": "Videos sobre trampas petroleras, estratigrafía y análisis de cuencas.",
    },
    {
        "titulo": "Clips virales de tecnología y ciencia en TikTok",
        "plataforma": "TikTok",
        "categoria": "Tech / TikTok",
        "url": "https://www.tiktok.com/search?q=tecnologia%20ciencia%20programacion",
        "descripcion": "Clips rápidos sobre tecnología, trucos y curiosidades en TikTok.",
    },
]

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>C-PRE2 // Plataforma Digital</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #07070a;
      --panel: #111118;
      --panel-2: #181822;
      --border: #292938;
      --text: #f5f5fa;
      --muted: #a3a3b8;
      --accent: #e11d48;
      --accent-soft: rgba(225, 29, 72, 0.16);
      --ok: #10b981;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top, #1d0810 0%, var(--bg) 52%);
      color: var(--text);
      min-height: 100vh;
    }
    .wrap { max-width: 1080px; margin: 0 auto; padding: 16px 14px 52px; }
    .login-box {
      max-width: 420px;
      margin: 54px auto;
      background: var(--panel);
      border: 1px solid var(--accent);
      box-shadow: 0 0 34px rgba(225, 29, 72, 0.22);
      border-radius: 16px;
      padding: 24px;
      text-align: center;
    }
    .brand-title { margin: 0; font-size: 1.9rem; letter-spacing: 0.08em; }
    .brand-sub { margin: 6px 0 18px; font-size: 0.8rem; color: var(--muted); letter-spacing: 0.14em; }
    label { display: block; text-align: left; font-size: 0.83rem; color: var(--muted); margin-bottom: 5px; }
    input, select, textarea {
      width: 100%;
      background: var(--bg);
      color: var(--text);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 10px 12px;
      font-size: 0.94rem;
      margin-bottom: 11px;
    }
    input:focus, select:focus, textarea:focus { outline: none; border-color: var(--accent); }
    button {
      cursor: pointer;
      border: none;
      border-radius: 10px;
      padding: 10px 14px;
      font-weight: 600;
      font-size: 0.88rem;
      transition: transform 0.1s ease, background 0.15s ease;
    }
    button:active { transform: scale(0.98); }
    .btn-primary { width: 100%; background: var(--accent); color: #fff; padding: 11px 14px; }
    .btn-secondary {
      background: var(--panel-2);
      color: var(--text);
      border: 1px solid var(--border);
      display: inline-flex;
      align-items: center;
      gap: 6px;
    }
    .btn-small { padding: 6px 10px; font-size: 0.8rem; border-radius: 8px; }
    .topbar {
      display: flex;
      flex-wrap: wrap;
      justify-content: space-between;
      align-items: center;
      gap: 10px;
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 13px 16px;
      margin-bottom: 12px;
    }
    .badge {
      display: inline-block;
      padding: 3px 9px;
      border-radius: 999px;
      font-size: 0.76rem;
      background: var(--accent-soft);
      color: #fda4af;
      border: 1px solid rgba(225, 29, 72, 0.38);
    }
    .nav-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(135px, 1fr));
      gap: 8px;
      margin-bottom: 14px;
    }
    .mod-btn {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      text-align: left;
      padding: 10px 12px;
    }
    .mod-btn.active { background: var(--accent-soft); border-color: var(--accent); color: #fff; }
    .mod-panel {
      background: var(--panel);
      border: 1px solid var(--border);
      border-radius: 14px;
      padding: 18px;
    }
    .hidden { display: none !important; }
    .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(265px, 1fr)); gap: 14px; }
    .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 12px; }
    .card {
      background: var(--panel-2);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 14px;
    }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 10px; margin: 12px 0; }
    .stat-box { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 11px; }
    .stat-label { font-size: 0.75rem; color: var(--muted); }
    .stat-val { font-size: 1.2rem; font-weight: 700; margin-top: 4px; }
    pre {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      overflow-x: auto;
      font-size: 0.85rem;
      color: #e2e8f0;
    }
    .table-wrap { overflow-x: auto; }
    table { width: 100%; border-collapse: collapse; font-size: 0.86rem; }
    th, td { border-bottom: 1px solid var(--border); padding: 8px 10px; text-align: left; }
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
        <strong>C-PRE2</strong> <span class="badge">Código: {{ codigo }} · {{ plan }}</span>
      </div>
      <div style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
        <span class="badge">Uso: {{ uso }} / {{ limite }}</span>
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
      <button type="button" class="mod-btn {% if active_mod == 'm2' %}active{% endif %}" onclick="openMod('m2', this)">2. Base de datos</button>
      <button type="button" class="mod-btn {% if active_mod == 'm3' %}active{% endif %}" onclick="openMod('m3', this)">3. Ordenar y graficar</button>
      <button type="button" class="mod-btn {% if active_mod == 'm4' %}active{% endif %}" onclick="openMod('m4', this)">4. Noticias 🔍</button>
      <button type="button" class="mod-btn {% if active_mod == 'm5' %}active{% endif %}" onclick="openMod('m5', this)">5. Videos</button>
      <button type="button" class="mod-btn {% if active_mod == 'm6' %}active{% endif %}" onclick="openMod('m6', this)">6. Buscador / Web</button>
      <button type="button" class="mod-btn {% if active_mod == 'm7' %}active{% endif %}" onclick="openMod('m7', this)">7. Estado</button>
    </div>

    <!-- 1. PROGRAMAR -->
    <section id="m1" class="mod-panel {% if active_mod != 'm1' %}hidden{% endif %}">
      <h2>1. Programar en Python</h2>
      <p style="color:var(--muted)">Escribe scripts completos en Python (listas, funciones, cálculos, texto, fechas, estadísticas) y ejecútalos.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m1" />
        <input type="hidden" name="accion" value="ejecutar_codigo" />
        <label for="code_input">Código Python</label>
        <textarea id="code_input" name="code_input" rows="8">{{ code_input }}</textarea>
        <button type="submit" class="btn-primary">Ejecutar script</button>
      </form>
      {% if code_output is not none %}
        <h3>Salida</h3>
        <pre>{{ code_output }}</pre>
      {% endif %}
    </section>

    <!-- 2. BASE DE DATOS ORDENable + ARCHIVOS + EDITAR -->
    <section id="m2" class="mod-panel {% if active_mod != 'm2' %}hidden{% endif %}">
      <h2>2. Base de datos ordenable y compatible con archivos</h2>
      <p style="color:var(--muted)">Agrega registros, sube un archivo compatible (<strong>.csv</strong>, <strong>.txt</strong> o <strong>.json</strong>), ordena por el campo que elijas (producto/nombre, fecha, valor, categoría), edita o borra filas y descarga CSV.</p>

      <div class="grid-2">
        <form method="POST" class="card">
          <h3 style="margin-top:0">Agregar / Cambiar registro</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="agregar_registro" />
          <label for="db_nombre">Producto / Nombre / Etiqueta</label>
          <input id="db_nombre" name="db_nombre" type="text" placeholder="Ej: Producto A / Pozo 01" required />
          <label for="db_valor">Valor numérico</label>
          <input id="db_valor" name="db_valor" type="number" step="any" placeholder="Ej: 120.5" required />
          <label for="db_categoria">Categoría</label>
          <input id="db_categoria" name="db_categoria" type="text" placeholder="Ej: Ventas / Operación" />
          <label for="db_fecha">Fecha</label>
          <input id="db_fecha" name="db_fecha" type="date" />
          <button type="submit" class="btn-primary">Guardar registro</button>
        </form>

        <div class="card">
          <h3 style="margin-top:0">Cargar archivo o cambiar orden</h3>
          <form method="POST" enctype="multipart/form-data">
            <input type="hidden" name="codigo" value="{{ codigo }}" />
            <input type="hidden" name="active_mod" value="m2" />
            <input type="hidden" name="accion" value="importar_archivo" />
            <label for="archivo_db">Subir archivo (.csv, .txt, .json)</label>
            <input id="archivo_db" name="archivo_db" type="file" accept=".csv,.txt,.json" required />
            <button type="submit" class="btn-secondary" style="width:100%; justify-content:center; margin-bottom:12px;">Importar archivo a la base</button>
          </form>

          <form method="POST">
            <input type="hidden" name="codigo" value="{{ codigo }}" />
            <input type="hidden" name="active_mod" value="m2" />
            <input type="hidden" name="accion" value="ordenar_db" />
            <label for="db_sort_by">Ordenar base de datos por</label>
            <select id="db_sort_by" name="db_sort_by">
              <option value="nombre" {% if db_sort_by == 'nombre' %}selected{% endif %}>Producto / Nombre (A-Z)</option>
              <option value="fecha" {% if db_sort_by == 'fecha' %}selected{% endif %}>Fecha</option>
              <option value="valor" {% if db_sort_by == 'valor' %}selected{% endif %}>Valor numérico</option>
              <option value="categoria" {% if db_sort_by == 'categoria' %}selected{% endif %}>Categoría</option>
            </select>
            <label for="db_sort_dir">Dirección</label>
            <select id="db_sort_dir" name="db_sort_dir">
              <option value="asc" {% if db_sort_dir == 'asc' %}selected{% endif %}>Ascendente</option>
              <option value="desc" {% if db_sort_dir == 'desc' %}selected{% endif %}>Descendente</option>
            </select>
            <button type="submit" class="btn-primary">Ordenar base de datos</button>
          </form>
        </div>
      </div>

      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Registros</div><div class="stat-val">{{ stats.count }}</div></div>
        <div class="stat-box"><div class="stat-label">Suma total</div><div class="stat-val">{{ stats.total }}</div></div>
        <div class="stat-box"><div class="stat-label">Promedio</div><div class="stat-val">{{ stats.avg }}</div></div>
        <div class="stat-box"><div class="stat-label">Máximo</div><div class="stat-val">{{ stats.max_val }}</div></div>
      </div>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
        <a class="btn-secondary" style="padding:8px 12px; border-radius:10px;" href="/descargar-csv?codigo={{ codigo }}">Descargar CSV</a>
        <form method="POST" style="display:inline; margin:0;">
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="limpiar_db" />
          <button type="submit" class="btn-secondary">Vaciar registros</button>
        </form>
      </div>

      <div class="table-wrap">
        <table>
          <thead>
            <tr><th>#</th><th>Producto / Nombre</th><th>Valor</th><th>Categoría</th><th>Fecha</th><th>Acción</th></tr>
          </thead>
          <tbody>
            {% for r in registros %}
              <tr>
                <td>{{ loop.index }}</td>
                <td>{{ r.nombre }}</td>
                <td>{{ r.valor }}</td>
                <td>{{ r.categoria }}</td>
                <td>{{ r.fecha }}</td>
                <td>
                  <form method="POST" style="display:inline; margin:0;">
                    <input type="hidden" name="codigo" value="{{ codigo }}" />
                    <input type="hidden" name="active_mod" value="m2" />
                    <input type="hidden" name="accion" value="borrar_fila" />
                    <input type="hidden" name="fila_idx" value="{{ loop.index0 }}" />
                    <button type="submit" class="btn-secondary btn-small">Eliminar</button>
                  </form>
                </td>
              </tr>
            {% else %}
              <tr><td colspan="6" style="color:var(--muted)">Sin registros aún. Agrega uno o sube un archivo .csv / .txt / .json.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 3. ORDENAR LO QUE DESEES + GRAFICAR -->
    <section id="m3" class="mod-panel {% if active_mod != 'm3' %}hidden{% endif %}">
      <h2>3. Ordenar lo que escribas y graficar</h2>
      <p style="color:var(--muted)">Escribe lo que deseas ordenar (productos, fechas, palabras o números separados por coma o salto de línea) y elige cómo ordenarlo.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m3" />
        <input type="hidden" name="accion" value="ordenar_custom" />
        <label for="custom_items">¿Qué deseas ordenar? (Ej: Arroz, Azúcar, Café o 2026-11-10, 2026-11-01, 2026-11-21)</label>
        <textarea id="custom_items" name="custom_items" rows="3">{{ custom_items }}</textarea>
        <div class="grid-2">
          <div>
            <label for="custom_tipo">Tipo de orden</label>
            <select id="custom_tipo" name="custom_tipo">
              <option value="auto" {% if custom_tipo == 'auto' %}selected{% endif %}>Automático (Producto/Texto, Fecha o Número)</option>
              <option value="texto" {% if custom_tipo == 'texto' %}selected{% endif %}>Producto / Nombre / Texto (A-Z)</option>
              <option value="fecha" {% if custom_tipo == 'fecha' %}selected{% endif %}>Fecha cronológica</option>
              <option value="numero" {% if custom_tipo == 'numero' %}selected{% endif %}>Numérico</option>
            </select>
          </div>
          <div>
            <label for="custom_dir">Dirección</label>
            <select id="custom_dir" name="custom_dir">
              <option value="asc" {% if custom_dir == 'asc' %}selected{% endif %}>Ascendente (A-Z / más antigua / menor)</option>
              <option value="desc" {% if custom_dir == 'desc' %}selected{% endif %}>Descendente (Z-A / más reciente / mayor)</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn-primary">Ordenar y graficar</button>
      </form>

      <p><strong>Resultado ordenado:</strong> {{ custom_resultado_str }}</p>
      <canvas id="chartCustom" height="105"></canvas>
    </section>

    <!-- 4. NOTICIAS CON LUPITA 🔍 -->
    <section id="m4" class="mod-panel {% if active_mod != 'm4' %}hidden{% endif %}">
      <h2>4. Noticias con lupita de búsqueda</h2>
      <p style="color:var(--muted)">Usa la lupita para buscar noticias de cualquier tema y abre los enlaces directos.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m4" />
        <input type="hidden" name="accion" value="buscar_noticias" />
        <input type="text" name="news_query" value="{{ news_query }}" placeholder="🔍 Buscar noticias (ej: tecnología, fútbol, petróleo, ciencia)..." />
        <button type="submit" class="btn-primary" style="width:auto;">🔍 Buscar</button>
      </form>

      <div style="margin-bottom:14px;">
        <a class="btn-secondary" href="https://news.google.com/search?q={{ news_query_encoded }}" target="_blank" rel="noopener noreferrer">
          Abrir "{{ news_query }}" en Google Noticias →
        </a>
      </div>

      <div class="grid-3">
        {% for n in noticias_filtradas %}
          <article class="card">
            <span class="badge">{{ n.categoria }} · {{ n.fecha }}</span>
            <h3 style="margin:8px 0 6px; font-size:1rem;">{{ n.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.85rem;">{{ n.resumen }}</p>
            <div style="display:flex; justify-content:space-between; align-items:center; margin-top:8px;">
              <small style="color:var(--muted)">{{ n.fuente }}</small>
              <a href="{{ n.url }}" target="_blank" rel="noopener noreferrer">Leer noticia →</a>
            </div>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- 5. VIDEOS (YOUTUBE, TIKTOK, INSTAGRAM) -->
    <section id="m5" class="mod-panel {% if active_mod != 'm5' %}hidden{% endif %}">
      <h2>5. Videos · YouTube, TikTok e Instagram</h2>
      <p style="color:var(--muted)">Escribe lo que quieras ver y abre los enlaces directos en <strong>YouTube</strong>, <strong>TikTok</strong> o <strong>Instagram</strong>.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m5" />
        <input type="hidden" name="accion" value="buscar_videos" />
        <input type="text" name="video_query" value="{{ video_query }}" placeholder="🎬 Buscar videos (ej: música, programación, fútbol, geología)..." />
        <button type="submit" class="btn-primary" style="width:auto;">Buscar videos</button>
      </form>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:14px;">
        <a class="btn-secondary" href="https://www.youtube.com/results?search_query={{ video_query_encoded }}" target="_blank" rel="noopener noreferrer">▶ Buscar en YouTube →</a>
        <a class="btn-secondary" href="https://www.tiktok.com/search?q={{ video_query_encoded }}" target="_blank" rel="noopener noreferrer">♪ Buscar en TikTok →</a>
        <a class="btn-secondary" href="https://www.instagram.com/explore/" target="_blank" rel="noopener noreferrer">◎ Abrir Instagram →</a>
      </div>

      <div class="grid-3">
        {% for v in videos_filtrados %}
          <article class="card">
            <span class="badge">{{ v.plataforma }} · {{ v.categoria }}</span>
            <h3 style="margin:8px 0 6px; font-size:1rem;">{{ v.titulo }}</h3>
            <p style="color:var(--muted); font-size:0.85rem;">{{ v.descripcion }}</p>
            <a href="{{ v.url }}" target="_blank" rel="noopener noreferrer">Ir al enlace de video →</a>
          </article>
        {% endfor %}
      </div>
    </section>

    <!-- 6. BUSCADOR / NAVEGADOR RÁPIDO -->
    <section id="m6" class="mod-panel {% if active_mod != 'm6' %}hidden{% endif %}">
      <h2>6. Buscador y acceso web</h2>
      <p style="color:var(--muted)">Escribe cualquier cosa que quieras buscar y lánzala directo a Google, YouTube, TikTok o Wikipedia.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m6" />
        <input type="hidden" name="accion" value="buscar_web" />
        <input type="text" name="web_query" value="{{ web_query }}" placeholder="🌐 Escribe lo que deseas buscar..." />
        <button type="submit" class="btn-primary" style="width:auto;">Buscar</button>
      </form>

      <div class="grid-2" style="margin-top:10px;">
        <div class="card">
          <h3 style="margin-top:0">Resultados rápidos para: "{{ web_query }}"</h3>
          <ul style="padding-left:18px; line-height:1.9;">
            <li><a href="https://www.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Buscar en Google →</a></li>
            <li><a href="https://news.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Buscar noticias en Google Noticias →</a></li>
            <li><a href="https://www.youtube.com/results?search_query={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Buscar videos en YouTube →</a></li>
            <li><a href="https://www.tiktok.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Buscar en TikTok →</a></li>
            <li><a href="https://es.wikipedia.org/wiki/Especial:Buscar?search={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Consultar en Wikipedia →</a></li>
          </ul>
        </div>
        <div class="card">
          <h3 style="margin-top:0">Accesos directos</h3>
          <p style="color:var(--muted); font-size:0.86rem;">Abre tus plataformas principales en una pestaña nueva:</p>
          <div style="display:flex; gap:8px; flex-wrap:wrap;">
            <a class="btn-secondary" href="https://www.google.com" target="_blank" rel="noopener noreferrer">Google</a>
            <a class="btn-secondary" href="https://www.youtube.com" target="_blank" rel="noopener noreferrer">YouTube</a>
            <a class="btn-secondary" href="https://www.tiktok.com" target="_blank" rel="noopener noreferrer">TikTok</a>
            <a class="btn-secondary" href="https://www.instagram.com" target="_blank" rel="noopener noreferrer">Instagram</a>
          </div>
        </div>
      </div>
    </section>

    <!-- 7. ESTADO -->
    <section id="m7" class="mod-panel {% if active_mod != 'm7' %}hidden{% endif %}">
      <h2>7. Estado del sistema C-PRE2</h2>
      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Plataforma</div><div class="stat-val">C-PRE2</div></div>
        <div class="stat-box"><div class="stat-label">Estado</div><div class="stat-val" style="color:var(--ok)">OPERATIVO</div></div>
        <div class="stat-box"><div class="stat-label">Registros en DB</div><div class="stat-val">{{ stats.count }}</div></div>
        <div class="stat-box"><div class="stat-label">Uso actual</div><div class="stat-val">{{ uso }} / {{ limite }}</div></div>
      </div>
      <p style="color:var(--muted)">Los 7 renglones están activos con ordenamiento por campo, importación de archivos, buscador con lupita y enlaces a noticias y videos.</p>
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
    const hiddenInputs = document.querySelectorAll('input[name="active_mod"]');
    hiddenInputs.forEach(inp => inp.value = id);
  }

  {% if autorizado %}
  const ctx = document.getElementById('chartCustom');
  if (ctx) {
    new Chart(ctx, {
      type: 'bar',
      data: {
        labels: {{ custom_labels | tojson }},
        datasets: [{
          label: 'Valores / Posición ordenada',
          data: {{ custom_values | tojson }},
          backgroundColor: 'rgba(225, 29, 72, 0.58)',
          borderColor: '#e11d48',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f5f5fa' } } },
        scales: {
          x: { ticks: { color: '#a3a3b8' }, grid: { color: '#292938' } },
          y: { ticks: { color: '#a3a3b8' }, grid: { color: '#292938' } }
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
            "active_mod": "m1",
            "registros": [
                {"nombre": "Producto Alfa", "valor": 45, "categoria": "Inventario", "fecha": "2026-11-18"},
                {"nombre": "Producto Beta", "valor": 120, "categoria": "Ventas", "fecha": "2026-11-20"},
                {"nombre": "Producto Gamma", "valor": 75, "categoria": "Inventario", "fecha": "2026-11-15"},
            ],
            "db_sort_by": "nombre",
            "db_sort_dir": "asc",
            "code_input": (
                "productos = ['Teclado', 'Monitor', 'Mouse', 'Audifonos']\n"
                "precios = [35, 180, 18, 50]\n"
                "for p, pr in zip(productos, precios):\n"
                "    print(f'{p}: ${pr}')\n"
                "print('Total:', sum(precios), '| Promedio:', round(statistics.mean(precios), 2))"
            ),
            "code_output": None,
            "custom_items": "Teclado, Monitor, Mouse, 2026-11-21, 2026-11-05, 85, 25",
            "custom_tipo": "auto",
            "custom_dir": "asc",
            "news_query": "tecnología",
            "video_query": "programación python",
            "web_query": "C-PRE2 tecnología",
        }
    return ESTADO_SESIONES[code]


def ordenar_registros(registros, campo="nombre", direccion="asc"):
    rev = (direccion == "desc")
    if campo == "valor":
        return sorted(registros, key=lambda x: float(x.get("valor", 0) or 0), reverse=rev)
    if campo == "fecha":
        return sorted(registros, key=lambda x: str(x.get("fecha", "")), reverse=rev)
    if campo == "categoria":
        return sorted(registros, key=lambda x: str(x.get("categoria", "")).lower(), reverse=rev)
    return sorted(registros, key=lambda x: str(x.get("nombre", "")).lower(), reverse=rev)


def ordenar_elementos_custom(raw_text, tipo="auto", direccion="asc"):
    partes = [p.strip() for p in (raw_text or "").replace("\n", ",").split(",") if p.strip()]
    if not partes:
        partes = ["Elemento A", "Elemento B", "Elemento C"]
    rev = (direccion == "desc")

    def es_numero(val):
        try:
            float(val)
            return True
        except ValueError:
            return False

    def es_fecha(val):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                datetime.strptime(val, fmt)
                return True
            except ValueError:
                continue
        return False

    def clave_fecha(val):
        for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%Y/%m/%d"):
            try:
                return datetime.strptime(val, fmt)
            except ValueError:
                continue
        return datetime.min

    if tipo == "numero":
        nums = [float(p) for p in partes if es_numero(p)]
        if nums:
            ordenados = sorted(nums, reverse=rev)
            limpios = [int(x) if float(x).is_integer() else round(float(x), 4) for x in ordenados]
            return [str(x) for x in limpios], limpios
        ordenados = sorted(partes, key=lambda s: s.lower(), reverse=rev)
        return ordenados, [i + 1 for i in range(len(ordenados))]

    if tipo == "fecha":
        ordenados = sorted(partes, key=clave_fecha, reverse=rev)
        return ordenados, [i + 1 for i in range(len(ordenados))]

    if tipo == "texto":
        ordenados = sorted(partes, key=lambda s: s.lower(), reverse=rev)
        vals = [float(x) if es_numero(x) else (i + 1) for i, x in enumerate(ordenados)]
        return ordenados, vals

    # Modo automático
    if all(es_numero(p) for p in partes):
        nums = sorted([float(p) for p in partes], reverse=rev)
        limpios = [int(x) if float(x).is_integer() else round(float(x), 4) for x in nums]
        return [str(x) for x in limpios], limpios

    if all(es_fecha(p) for p in partes):
        ordenados = sorted(partes, key=clave_fecha, reverse=rev)
        return ordenados, [i + 1 for i in range(len(ordenados))]

    ordenados = sorted(partes, key=lambda s: s.lower(), reverse=rev)
    vals = [float(x) if es_numero(x) else (i + 1) for i, x in enumerate(ordenados)]
    return ordenados, vals


def calcular_stats(registros):
    if not registros:
        return {"count": 0, "total": 0, "avg": 0, "max_val": 0}
    vals = [float(r.get("valor", 0) or 0) for r in registros]
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


def parsear_archivo_subido(file_storage):
    filename = (file_storage.filename or "").lower()
    raw_bytes = file_storage.read()
    texto = raw_bytes.decode("utf-8", errors="ignore").strip()
    nuevos = []

    if not texto:
        return nuevos

    if filename.endswith(".json") or texto.startswith("[") or texto.startswith("{"):
        data = json.loads(texto)
        items = data if isinstance(data, list) else data.get("registros", [])
        for idx, item in enumerate(items, start=1):
            if isinstance(item, dict):
                nombre = str(item.get("nombre") or item.get("producto") or f"Item {idx}").strip()
                try:
                    valor = float(item.get("valor", 0))
                except (TypeError, ValueError):
                    valor = 0.0
                val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
                cat = str(item.get("categoria") or "Archivo JSON").strip()
                fecha = str(item.get("fecha") or datetime.now().strftime("%Y-%m-%d")).strip()
                nuevos.append({"nombre": nombre, "valor": val_fmt, "categoria": cat, "fecha": fecha})
    else:
        reader = csv.DictReader(io.StringIO(texto))
        if reader.fieldnames and any(h and h.strip().lower() in ("nombre", "producto", "valor") for h in reader.fieldnames):
            for idx, row in enumerate(reader, start=1):
                lower_row = {(k or "").strip().lower(): (v or "").strip() for k, v in row.items()}
                nombre = lower_row.get("nombre") or lower_row.get("producto") or f"Fila {idx}"
                try:
                    valor = float(lower_row.get("valor", "0"))
                except ValueError:
                    valor = 0.0
                val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
                cat = lower_row.get("categoria") or "Archivo CSV"
                fecha = lower_row.get("fecha") or datetime.now().strftime("%Y-%m-%d")
                nuevos.append({"nombre": nombre, "valor": val_fmt, "categoria": cat, "fecha": fecha})
        else:
            for idx, linea in enumerate(texto.splitlines(), start=1):
                partes = [p.strip() for p in linea.split(",")]
                if not partes or not partes[0]:
                    continue
                nombre = partes[0]
                try:
                    valor = float(partes[1]) if len(partes) > 1 else float(idx)
                except ValueError:
                    valor = float(idx)
                val_fmt = int(valor) if valor.is_integer() else round(valor, 4)
                cat = partes[2] if len(partes) > 2 and partes[2] else "Archivo"
                fecha = partes[3] if len(partes) > 3 and partes[3] else datetime.now().strftime("%Y-%m-%d")
                nuevos.append({"nombre": nombre, "valor": val_fmt, "categoria": cat, "fecha": fecha})

    return nuevos


def ejecutar_codigo_python(codigo_fuente):
    bloqueados = ["__import__", "open(", "exec(", "eval(", "compile(", "input("]
    bajo = (codigo_fuente or "").lower()
    for b in bloqueados:
        if b in bajo:
            return f"Bloqueado por seguridad: '{b}'."
    buf = io.StringIO()
    entorno = {
        "__builtins__": {
            "print": lambda *args, **kwargs: print(*args, file=buf, **kwargs),
            "len": len,
            "sum": sum,
            "min": min,
            "max": max,
            "sorted": sorted,
            "reversed": reversed,
            "enumerate": enumerate,
            "zip": zip,
            "map": map,
            "filter": filter,
            "round": round,
            "abs": abs,
            "pow": pow,
            "range": range,
            "int": int,
            "float": float,
            "str": str,
            "bool": bool,
            "list": list,
            "dict": dict,
            "set": set,
            "tuple": tuple,
        },
        "math": math,
        "statistics": statistics,
        "datetime": datetime,
    }
    try:
        exec(codigo_fuente, entorno, {})
        out = buf.getvalue().strip()
        return out if out else "Código ejecutado sin salida impresa."
    except Exception as e:
        return f"Error: {e}"


def render_panel(codigo, estado, error_msg=None, aviso_msg=None):
    info = CODIGOS_ACCESO[codigo]
    registros_ordenados = ordenar_registros(
        estado["registros"], estado["db_sort_by"], estado["db_sort_dir"]
    )
    custom_labels, custom_values = ordenar_elementos_custom(
        estado["custom_items"], estado["custom_tipo"], estado["custom_dir"]
    )

    nq = (estado["news_query"] or "").strip()
    if nq and nq.lower() not in ("todo", "todos", "tecnología"):
        noticias_filtradas = [
            n for n in NOTICIAS_BASE
            if nq.lower() in n["titulo"].lower()
            or nq.lower() in n["categoria"].lower()
            or nq.lower() in n["resumen"].lower()
        ] or NOTICIAS_BASE
    else:
        noticias_filtradas = NOTICIAS_BASE

    vq = (estado["video_query"] or "").strip()
    if vq and vq.lower() not in ("todo", "todos"):
        videos_filtrados = [
            v for v in VIDEOS_BASE
            if vq.lower() in v["titulo"].lower()
            or vq.lower() in v["categoria"].lower()
            or vq.lower() in v["plataforma"].lower()
            or vq.lower() in v["descripcion"].lower()
        ] or VIDEOS_BASE
    else:
        videos_filtrados = VIDEOS_BASE

    return render_template_string(
        HTML_TEMPLATE,
        autorizado=True,
        error=error_msg,
        aviso=aviso_msg,
        codigo=codigo,
        plan=info["plan"],
        limite=info["limite"],
        uso=estado["uso"],
        active_mod=estado.get("active_mod", "m1"),
        code_input=estado["code_input"],
        code_output=estado["code_output"],
        registros=registros_ordenados,
        db_sort_by=estado["db_sort_by"],
        db_sort_dir=estado["db_sort_dir"],
        stats=calcular_stats(registros_ordenados),
        custom_items=estado["custom_items"],
        custom_tipo=estado["custom_tipo"],
        custom_dir=estado["custom_dir"],
        custom_resultado_str=", ".join(str(x) for x in custom_labels),
        custom_labels=custom_labels,
        custom_values=custom_values,
        news_query=nq,
        news_query_encoded=urllib.parse.quote_plus(nq or "noticias hoy"),
        noticias_filtradas=noticias_filtradas,
        video_query=vq,
        video_query_encoded=urllib.parse.quote_plus(vq or "videos tendencias"),
        videos_filtrados=videos_filtrados,
        web_query=estado["web_query"],
        web_query_encoded=urllib.parse.quote_plus(estado["web_query"] or "C-PRE2"),
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

        mod_sel = request.form.get("active_mod")
        if mod_sel in ("m1", "m2", "m3", "m4", "m5", "m6", "m7"):
            estado["active_mod"] = mod_sel

        limite = CODIGOS_ACCESO[codigo]["limite"]
        accion = request.form.get("accion")
        aviso = None
        error = None

        if accion:
            if estado["uso"] >= limite:
                return render_panel(codigo, estado, error_msg="Límite de uso alcanzado para este código.")
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

        elif accion == "importar_archivo":
            archivo = request.files.get("archivo_db")
            if archivo and archivo.filename:
                try:
                    nuevos = parsear_archivo_subido(archivo)
                    if nuevos:
                        estado["registros"].extend(nuevos)
                        aviso = f"Se importaron {len(nuevos)} registro(s) desde '{archivo.filename}'."
                    else:
                        error = "No se encontraron datos válidos en el archivo."
                except Exception as e:
                    error = f"Error al leer el archivo: {e}"
            else:
                error = "Selecciona un archivo .csv, .txt o .json."
            estado["active_mod"] = "m2"

        elif accion == "ordenar_db":
            estado["db_sort_by"] = request.form.get("db_sort_by") or "nombre"
            estado["db_sort_dir"] = request.form.get("db_sort_dir") or "asc"
            aviso = f"Base de datos ordenada por {estado['db_sort_by']} ({estado['db_sort_dir']})."
            estado["active_mod"] = "m2"

        elif accion == "borrar_fila":
            try:
                idx = int(request.form.get("fila_idx", -1))
                ordenadas = ordenar_registros(
                    estado["registros"], estado["db_sort_by"], estado["db_sort_dir"]
                )
                if 0 <= idx < len(ordenadas):
                    objetivo = ordenadas[idx]
                    estado["registros"].remove(objetivo)
                    aviso = "Registro eliminado."
            except Exception:
                error = "No se pudo eliminar el registro."
            estado["active_mod"] = "m2"

        elif accion == "limpiar_db":
            estado["registros"] = []
            aviso = "Base de datos vaciada."
            estado["active_mod"] = "m2"

        elif accion == "ordenar_custom":
            estado["custom_items"] = request.form.get("custom_items") or ""
            estado["custom_tipo"] = request.form.get("custom_tipo") or "auto"
            estado["custom_dir"] = request.form.get("custom_dir") or "asc"
            estado["active_mod"] = "m3"

        elif accion == "buscar_noticias":
            estado["news_query"] = (request.form.get("news_query") or "").strip()
            estado["active_mod"] = "m4"

        elif accion == "buscar_videos":
            estado["video_query"] = (request.form.get("video_query") or "").strip()
            estado["active_mod"] = "m5"

        elif accion == "buscar_web":
            estado["web_query"] = (request.form.get("web_query") or "").strip()
            estado["active_mod"] = "m6"

        return render_panel(codigo, estado, error_msg=error, aviso_msg=aviso)

    return render_template_string(HTML_TEMPLATE, autorizado=False, error=None)


@app.route("/descargar-csv")
def descargar_csv():
    codigo = (request.args.get("codigo") or "").strip().upper()
    estado = obtener_estado(codigo)
    if not estado:
        return "Código no autorizado", 403

    ordenadas = ordenar_registros(
        estado["registros"], estado["db_sort_by"], estado["db_sort_dir"]
    )
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Nombre", "Valor", "Categoria", "Fecha"])
    for r in ordenadas:
        writer.writerow([r["nombre"], r["valor"], r["categoria"], r["fecha"]])

    return Response(
        output.getvalue(),
        mimetype="text/csv",
        headers={"Content-Disposition": "attachment; filename=c_pre2_base_datos.csv"},
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

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

ENCICLOPEDIA_COMPLETA = {
    "tecnologia": {
        "titulo": "Tecnología",
        "definicion": (
            "La tecnología es el conjunto de conocimientos científicos, técnicas, métodos, herramientas "
            "y sistemas creados por el ser humano para resolver problemas prácticos, mejorar procesos, "
            "optimizar recursos y transformar la forma en que trabajamos, nos comunicamos y producimos. "
            "Abarca desde el hardware y el software hasta la ingeniería energética, las telecomunicaciones "
            "y la automatización industrial."
        ),
        "ejemplo": (
            "Ejemplo práctico: Reestructurar un programa para que consuma menos memoria y energía "
            "mientras procesa miles de datos más rápido, o usar sensores automatizados en una planta "
            "para detectar fallas antes de que ocurran."
        ),
    },
    "programacion": {
        "titulo": "Programación",
        "definicion": (
            "La programación es el proceso de escribir, estructurar, probar y mantener instrucciones "
            "lógicas mediante un lenguaje de programación (como Python) para que un sistema informático "
            "procese información, tome decisiones condicionales, repita tareas, maneje bases de datos y "
            "construya aplicaciones web, móviles o de escritorio."
        ),
        "ejemplo": (
            "Ejemplo práctico: Crear un script en Python que reciba una lista de precios o registros, "
            "calcule totales, promedios y máximos, ordene los resultados y los guarde en un archivo CSV."
        ),
    },
    "petroleo": {
        "titulo": "Petróleo y Geología del Hidrocarburo",
        "definicion": (
            "El petróleo es una mezcla compleja de hidrocarburos (compuestos principalmente de carbono "
            "e hidrógeno) formada en el subsuelo durante millones de años a partir de materia orgánica "
            "bajo condiciones específicas de presión y temperatura. En geología petrolera se estudia "
            "la cuenca sedimentaria, la roca generadora, la migración, la roca reservorio (porosidad y "
            "permeabilidad), la roca sello, las trampas estructurales o estratigráficas y propiedades "
            "como la gravedad API y la viscosidad."
        ),
        "ejemplo": (
            "Ejemplo práctico: Comparar un crudo liviano o mediano con un crudo pesado o extrapesado "
            "mediante su gravedad API para determinar su flujo en tuberías, dilución o refinación."
        ),
    },
    "base de datos": {
        "titulo": "Base de datos",
        "definicion": (
            "Una base de datos es un conjunto organizado y estructurado de registros o información "
            "almacenada de manera que pueda consultarse, ordenarse, filtrarse, actualizarse, "
            "eliminarse o exportarse de forma rápida y ordenada según distintos criterios (nombre, "
            "fecha, valor, categoría o código)."
        ),
        "ejemplo": (
            "Ejemplo práctico: Reunir 100 filas con producto, valor y fecha y ordenarlas de mayor a "
            "menor valor o por fecha para detectar los picos de movimiento."
        ),
    },
    "hoja de calculo": {
        "titulo": "Hoja de cálculo",
        "definicion": (
            "Una hoja de cálculo es una cuadrícula interactiva formada por columnas (A, B, C...) y "
            "filas (1, 2, 3...) que se intersectan en celdas. Cada celda puede almacenar texto, "
            "números o fórmulas que recalculan valores automáticamente cuando cambian los datos de "
            "entrada, además de permitir ordenar tablas, graficar series e imprimir reportes."
        ),
        "ejemplo": (
            "Ejemplo práctico: En la columna B poner cantidades, en la C precios unitarios, en D "
            "multiplicar =B1*C1 y en una celda final escribir =SUMA(D1:D10) para obtener el total."
        ),
    },
    "inteligencia artificial": {
        "titulo": "Inteligencia Artificial",
        "definicion": (
            "La inteligencia artificial es el campo de la informática dedicado a crear sistemas capaces "
            "de realizar tareas que normalmente requieren razonamiento, reconocimiento de patrones, "
            "análisis de datos, clasificación, predicción o procesamiento de lenguaje."
        ),
        "ejemplo": (
            "Ejemplo práctico: Un modelo que analiza patrones repetitivos en datos o texto para "
            "clasificar información, resumir contenidos o detectar anomalías."
        ),
    },
    "futbol": {
        "titulo": "Fútbol",
        "definicion": (
            "El fútbol es un deporte colectivo en el que dos equipos de once jugadores compiten por "
            "marcar más goles en la portería contraria usando principalmente los pies y el cuerpo "
            "(excepto el portero dentro de su área). Combina técnica individual, resistencia física, "
            "lectura espacial y organización táctica en ataque y defensa."
        ),
        "ejemplo": (
            "Ejemplo práctico: Alternar posesión paciente para atraer la presión rival con pases "
            "verticales rápidos hacia los espacios libres cuando el bloque contrario se desordena."
        ),
    },
    "economia": {
        "titulo": "Economía",
        "definicion": (
            "La economía es la ciencia social que estudia cómo las personas, empresas y gobiernos "
            "administran recursos limitados para producir, distribuir y consumir bienes y servicios, "
            "analizando precios, oferta, demanda, costos, inversión y crecimiento."
        ),
        "ejemplo": (
            "Ejemplo práctico: Calcular el costo unitario, el margen de ganancia y el punto de "
            "equilibrio de un producto antes de fijar su precio de venta."
        ),
    },
    "ciencia": {
        "titulo": "Ciencia",
        "definicion": (
            "La ciencia es el sistema ordenado de conocimiento basado en la observación, la medición, "
            "la experimentación y la comprobación lógica para explicar cómo funcionan los fenómenos "
            "naturales, físicos, químicos, biológicos o matemáticos."
        ),
        "ejemplo": (
            "Ejemplo práctico: Formular una hipótesis sobre cómo influye una variable en un proceso, "
            "probarla con mediciones controladas y analizar los resultados obtenidos."
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
        ("Tecnología", "N-Tech", "Eficiencia energética y cálculo computacional", "Reseña: Avances en optimización de software, hardware y ahorro energético en procesamiento de datos.", "eficiencia energetica computacion software"),
        ("Geología", "N-Geo", "Cuencas sedimentarias, trampas y gravedad API", "Reseña: Análisis sobre sistemas petroleros, yacimientos, porosidad y comportamiento del crudo.", "geologia petroleo cuencas sedimentarias"),
        ("Programación", "N-Dev", "Python, Flask y sistemas web rápidos", "Reseña: Aplicaciones web, scripts automatizados, manejo de datos y desarrollo ágil.", "python flask programacion web"),
        ("Deportes", "N-Fut", "Fútbol mundial, marcas históricas y táctica", "Reseña: Cobertura de partidos, récords goleadores, rendimiento y análisis de equipos.", "futbol internacional goles tactica"),
        ("Ciencia", "N-Sci", "Física, astronomía y experimentos actuales", "Reseña: Novedades científicas, astrofísica, energía y descubrimientos recientes.", "ciencia astronomia fisica"),
        ("Economía", "N-Eco", "Mercados, producción y tecnología aplicada", "Reseña: Movimientos económicos, productividad, inversión y transformación digital.", "economia mercados tecnologia"),
    ]
    enfoques = [
        "análisis principal",
        "reporte actual",
        "claves técnicas",
        "panorama general",
        "resumen del día",
    ]
    out = []
    for i in range(30):
        cat, logo, tit, res, q = temas[i % len(temas)]
        enf = enfoques[i % len(enfoques)]
        num = i + 1
        out.append({
            "num": num,
            "logo": logo,
            "titulo": f"#{num:02d} · {tit} — {enf}",
            "categoria": cat,
            "fuente": f"Google Noticias · {cat}",
            "fecha": "Hoy",
            "resena": f"{res} ({enf.capitalize()}).",
            "url": f"https://news.google.com/search?q={urllib.parse.quote_plus(q + ' ' + enf)}",
        })
    return out


def construir_30_videos():
    plataformas = [
        ("TikTok", "Viral / TikTok", "https://www.tiktok.com/search?q="),
        ("YouTube", "Videos / YouTube", "https://www.youtube.com/results?search_query="),
        ("Instagram", "Reels / Instagram", "https://www.instagram.com/explore/"),
    ]
    temas = [
        ("Tendencias virales y clips destacados", "tendencias virales"),
        ("Programación en Python y desarrollo web", "python programacion web"),
        ("Geología del petróleo y yacimientos", "geologia petroleo"),
        ("Fútbol, goles y análisis táctico", "futbol goles analisis"),
        ("Matemática y lógica práctica", "matematicas logica"),
        ("Ciencia y astronomía", "ciencia astronomia"),
        ("Bases de datos y hojas de cálculo", "bases de datos hoja de calculo"),
        ("Tecnología y productividad", "tecnologia productividad"),
        ("Diseño y estética oscura", "diseño oscuro ui"),
        ("Emprendimiento y software", "emprendimiento software"),
    ]
    out = []
    for i in range(30):
        plat, cat, base_u = plataformas[i % len(plataformas)]
        tit, q = temas[i % len(temas)]
        num = i + 1
        url = base_u if plat == "Instagram" else f"{base_u}{urllib.parse.quote_plus(q + ' ' + str(num))}"
        out.append({
            "num": num,
            "titulo": f"#{num:02d} · {tit}",
            "plataforma": plat,
            "categoria": cat,
            "resena": f"Acceso directo a {plat} para '{q}'.",
            "url": url,
        })
    return out


NOTICIAS_30 = construir_30_noticias()
VIDEOS_30 = construir_30_videos()

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1.0" />
  <title>C-PRE2 // Plataforma Digital</title>
  <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
  <style>
    :root {
      --bg: #07070c;
      --panel: #11111a;
      --panel-2: #181826;
      --border: #2a2a3e;
      --text: #f5f5fc;
      --muted: #a4a4ba;
      --accent: #e11d48;
      --accent-soft: rgba(225, 29, 72, 0.16);
      --ok: #10b981;
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
      background: radial-gradient(circle at top, #1f0812 0%, var(--bg) 52%);
      color: var(--text);
      min-height: 100vh;
    }
    .wrap { max-width: 1200px; margin: 0 auto; padding: 14px 12px 56px; }
    .login-box {
      max-width: 420px;
      margin: 56px auto;
      background: var(--panel);
      border: 1px solid var(--accent);
      box-shadow: 0 0 34px rgba(225, 29, 72, 0.22);
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
      font-size: 0.85rem;
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
      border: 1px solid rgba(225, 29, 72, 0.38);
    }
    .nav-grid {
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(128px, 1fr));
      gap: 7px;
      margin-bottom: 14px;
    }
    .mod-btn {
      background: var(--panel);
      color: var(--text);
      border: 1px solid var(--border);
      text-align: left;
      padding: 9px 11px;
      font-size: 0.83rem;
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
      background: linear-gradient(135deg, #e11d48, #9f1239);
      color: #fff;
      font-weight: 800;
      font-size: 0.75rem;
    }
    .stat-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(135px, 1fr)); gap: 10px; margin: 12px 0; }
    .stat-box { background: var(--bg); border: 1px solid var(--border); border-radius: 10px; padding: 11px; }
    .stat-label { font-size: 0.75rem; color: var(--muted); }
    .stat-val { font-size: 1.18rem; font-weight: 700; margin-top: 4px; }
    pre {
      background: var(--bg);
      border: 1px solid var(--border);
      border-radius: 10px;
      padding: 12px;
      overflow-x: auto;
      font-size: 0.85rem;
      color: #e2e8f0;
    }
    .table-wrap { overflow-x: auto; max-height: 460px; overflow-y: auto; border: 1px solid var(--border); border-radius: 10px; }
    table { width: 100%; border-collapse: collapse; font-size: 0.82rem; }
    th, td { border: 1px solid var(--border); padding: 5px 6px; text-align: left; }
    th { background: var(--panel-2); position: sticky; top: 0; z-index: 2; }
    .row-num { background: var(--panel-2); font-weight: 700; text-align: center; min-width: 38px; color: var(--muted); }
    .sheet-input {
      width: 100%;
      min-width: 96px;
      margin-bottom: 0;
      padding: 5px 7px;
      font-size: 0.82rem;
      border-radius: 6px;
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
      .topbar, .nav-grid, .btn-secondary, .btn-primary, form { display: none !important; }
      body { background: #fff; color: #000; }
      .mod-panel { border: none; background: #fff; color: #000; padding: 0; }
      .table-wrap { max-height: none; overflow: visible; border: none; }
      table, th, td { border: 1px solid #444; color: #000; }
      input.sheet-input { border: none; color: #000; background: transparent; }
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
      <button type="button" class="mod-btn {% if active_mod == 'm4' %}active{% endif %}" onclick="openMod('m4', this)">4. Hoja de cálculo</button>
      <button type="button" class="mod-btn {% if active_mod == 'm5' %}active{% endif %}" onclick="openMod('m5', this)">5. Noticias (30)</button>
      <button type="button" class="mod-btn {% if active_mod == 'm6' %}active{% endif %}" onclick="openMod('m6', this)">6. Videos (30)</button>
      <button type="button" class="mod-btn {% if active_mod == 'm7' %}active{% endif %}" onclick="openMod('m7', this)">7. Enciclopedia / Web</button>
      <button type="button" class="mod-btn {% if active_mod == 'm8' %}active{% endif %}" onclick="openMod('m8', this)">8. Estado</button>
    </div>

    <!-- 1. PROGRAMAR -->
    <section id="m1" class="mod-panel {% if active_mod != 'm1' %}hidden{% endif %}">
      <h2>1. Programar en Python</h2>
      <p style="color:var(--muted)">Escribe tu script en Python y ejecuta para ver los resultados en pantalla.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m1" />
        <input type="hidden" name="accion" value="ejecutar_codigo" />
        <label for="code_input">Escribe tu código Python aquí</label>
        <textarea id="code_input" name="code_input" rows="9">{{ code_input }}</textarea>
        <button type="submit" class="btn-primary">Ejecutar código</button>
      </form>
      {% if code_output is not none %}
        <h3>Resultados</h3>
        <pre>{{ code_output }}</pre>
      {% endif %}
    </section>

    <!-- 2. BASE DE DATOS GRANDE + ESPACIO AMPLIO DE TEXTO + AUTOMÁTICO / MANUAL -->
    <section id="m2" class="mod-panel {% if active_mod != 'm2' %}hidden{% endif %}">
      <h2>2. Base de datos grande (Manual y Automática)</h2>
      <p style="color:var(--muted)">Escribe o pega tu texto o base de datos amplia aquí abajo, sube un archivo o ordénala en modo <strong>Manual</strong> o <strong>Automático</strong>.</p>

      <form method="POST" class="card" style="margin-bottom:14px;">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m2" />
        <input type="hidden" name="accion" value="cargar_lote_db" />
        <label for="lote_db_texto">Escriba o pegue su texto o base de datos aquí (una fila por línea: Producto/Nombre, Valor, Categoría, Fecha)</label>
        <textarea id="lote_db_texto" name="lote_db_texto" rows="9" placeholder="Escriba o pegue su texto aquí...&#10;Ejemplo:&#10;Producto A, 120, Ventas, 2026-11-20&#10;Producto B, 85, Inventario, 2026-11-18&#10;Producto C, 240, Ventas, 2026-11-21"></textarea>
        <div class="grid-2">
          <div>
            <label for="modo_carga_db">Modo de carga</label>
            <select id="modo_carga_db" name="modo_carga_db">
              <option value="reemplazar">Reemplazar base actual</option>
              <option value="agregar">Agregar a la base actual</option>
            </select>
          </div>
          <div>
            <label for="autollenar_n">Generar lote de prueba</label>
            <select id="autollenar_n" name="autollenar_n">
              <option value="0">No generar</option>
              <option value="30">Generar 30 registros</option>
              <option value="80">Generar 80 registros</option>
            </select>
          </div>
        </div>
        <button type="submit" class="btn-primary">Cargar en base de datos</button>
      </form>

      <div class="grid-2">
        <form method="POST" enctype="multipart/form-data" class="card">
          <h3 style="margin-top:0">Importar archivo</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="importar_archivo" />
          <label for="archivo_db">Archivo (.csv, .txt, .json)</label>
          <input id="archivo_db" name="archivo_db" type="file" accept=".csv,.txt,.json" required />
          <button type="submit" class="btn-secondary" style="width:100%; justify-content:center;">Subir e importar</button>
        </form>

        <form method="POST" class="card">
          <h3 style="margin-top:0">Ordenar base de datos</h3>
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="ordenar_db" />
          <label for="db_modo_orden">Modo</label>
          <select id="db_modo_orden" name="db_modo_orden">
            <option value="manual" {% if db_modo_orden == 'manual' %}selected{% endif %}>Manual</option>
            <option value="auto" {% if db_modo_orden == 'auto' %}selected{% endif %}>Automático</option>
          </select>
          <label for="db_sort_by">Campo (modo manual)</label>
          <select id="db_sort_by" name="db_sort_by">
            <option value="nombre" {% if db_sort_by == 'nombre' %}selected{% endif %}>Producto / Nombre</option>
            <option value="fecha" {% if db_sort_by == 'fecha' %}selected{% endif %}>Fecha</option>
            <option value="valor" {% if db_sort_by == 'valor' %}selected{% endif %}>Valor numérico</option>
            <option value="categoria" {% if db_sort_by == 'categoria' %}selected{% endif %}>Categoría</option>
          </select>
          <label for="db_sort_dir">Sentido (modo manual)</label>
          <select id="db_sort_dir" name="db_sort_dir">
            <option value="asc" {% if db_sort_dir == 'asc' %}selected{% endif %}>Ascendente</option>
            <option value="desc" {% if db_sort_dir == 'desc' %}selected{% endif %}>Descendente</option>
          </select>
          <button type="submit" class="btn-primary">Ordenar ahora</button>
        </form>
      </div>

      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Registros</div><div class="stat-val">{{ stats.count }}</div></div>
        <div class="stat-box"><div class="stat-label">Suma</div><div class="stat-val">{{ stats.total }}</div></div>
        <div class="stat-box"><div class="stat-label">Promedio</div><div class="stat-val">{{ stats.avg }}</div></div>
        <div class="stat-box"><div class="stat-label">Máximo</div><div class="stat-val">{{ stats.max_val }}</div></div>
      </div>

      <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:10px;">
        <a class="btn-secondary" style="padding:8px 12px; border-radius:10px;" href="/descargar-csv?codigo={{ codigo }}">Descargar CSV</a>
        <form method="POST" style="display:inline; margin:0;">
          <input type="hidden" name="codigo" value="{{ codigo }}" />
          <input type="hidden" name="active_mod" value="m2" />
          <input type="hidden" name="accion" value="limpiar_db" />
          <button type="submit" class="btn-secondary">Vaciar base</button>
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
              <tr><td colspan="6" style="color:var(--muted)">Sin registros cargados.</td></tr>
            {% endfor %}
          </tbody>
        </table>
      </div>
    </section>

    <!-- 3. ORDENAR Y GRAFICAR -->
    <section id="m3" class="mod-panel {% if active_mod != 'm3' %}hidden{% endif %}">
      <h2>3. Ordenar y graficar</h2>
      <p style="color:var(--muted)">Escriba o pegue aquí lo que desea ordenar (productos, fechas, palabras o números) y vea la gráfica.</p>
      <form method="POST">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m3" />
        <input type="hidden" name="accion" value="ordenar_custom" />
        <label for="custom_items">Escriba o pegue su lista aquí</label>
        <textarea id="custom_items" name="custom_items" rows="5" placeholder="Escriba aquí lo que desea ordenar...">{{ custom_items }}</textarea>
        <div class="grid-2">
          <div>
            <label for="custom_tipo">Tipo</label>
            <select id="custom_tipo" name="custom_tipo">
              <option value="auto" {% if custom_tipo == 'auto' %}selected{% endif %}>Automático</option>
              <option value="texto" {% if custom_tipo == 'texto' %}selected{% endif %}>Producto / Texto (A-Z)</option>
              <option value="fecha" {% if custom_tipo == 'fecha' %}selected{% endif %}>Fecha</option>
              <option value="numero" {% if custom_tipo == 'numero' %}selected{% endif %}>Numérico</option>
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
      <p><strong>Resultado ordenado:</strong> {{ custom_resultado_str }}</p>
      <canvas id="chartCustom" height="105"></canvas>
    </section>

    <!-- 4. HOJA DE CÁLCULO AMPLIA (COLUMNAS A-H, FILAS 1-15) -->
    <section id="m4" class="mod-panel {% if active_mod != 'm4' %}hidden{% endif %}">
      <h2>4. Hoja de cálculo (Columnas A–{{ col_max_letra }} · Filas 1–{{ row_max_num }})</h2>
      <p style="color:var(--muted)">Fórmulas soportadas: <code>=SUMA(B1:B10)</code>, <code>=PROMEDIO(B1:B10)</code>, <code>=MAX(B1:B10)</code>, <code>=MIN(B1:B10)</code>, <code>=CONTAR(B1:B10)</code>, <code>=REDONDEAR(C1;2)</code>, <code>=POTENCIA(B1;2)</code>, <code>=RAIZ(C1)</code>, <code>=SI(B1&gt;5;"Alto";"Bajo")</code> o <code>=B1*C1</code>.</p>

      <form method="POST" enctype="multipart/form-data">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m4" />

        <div style="display:flex; gap:8px; flex-wrap:wrap; margin-bottom:12px;">
          <button type="submit" name="accion" value="sheet_calcular" class="btn-primary" style="width:auto;">Calcular fórmulas</button>
          <button type="submit" name="accion" value="sheet_add_row" class="btn-secondary">+ Fila</button>
          <button type="submit" name="accion" value="sheet_del_row" class="btn-secondary">- Fila</button>
          <button type="submit" name="accion" value="sheet_add_col" class="btn-secondary">+ Columna</button>
          <button type="submit" name="accion" value="sheet_del_col" class="btn-secondary">- Columna</button>
          <button type="button" onclick="window.print()" class="btn-secondary">Imprimir</button>
        </div>

        <div class="card" style="margin-bottom:12px;">
          <label for="archivo_sheet">Cargar archivo a la hoja (.csv o .txt)</label>
          <div style="display:flex; gap:8px; flex-wrap:wrap; align-items:center;">
            <input id="archivo_sheet" name="archivo_sheet" type="file" accept=".csv,.txt" style="flex:1 1 220px; margin-bottom:0;" />
            <button type="submit" name="accion" value="sheet_import" class="btn-secondary">Cargar archivo</button>
          </div>
        </div>

        <div class="grid-2" style="margin-bottom:10px;">
          <div>
            <label for="sheet_sort_col">Ordenar por columna</label>
            <select id="sheet_sort_col" name="sheet_sort_col">
              {% for h in sheet_headers %}
                <option value="{{ loop.index0 }}" {% if sheet_sort_col == loop.index0 %}selected{% endif %}>{{ col_letras[loop.index0] }} ({{ h }})</option>
              {% endfor %}
            </select>
          </div>
          <div>
            <label for="sheet_sort_dir">Orden</label>
            <select id="sheet_sort_dir" name="sheet_sort_dir">
              <option value="asc" {% if sheet_sort_dir == 'asc' %}selected{% endif %}>Ascendente</option>
              <option value="desc" {% if sheet_sort_dir == 'desc' %}selected{% endif %}>Descendente</option>
            </select>
          </div>
        </div>
        <button type="submit" name="accion" value="sheet_sort" class="btn-secondary" style="margin-bottom:12px;">Ordenar hoja</button>

        <div class="table-wrap" style="margin-bottom:16px;">
          <table>
            <thead>
              <tr>
                <th class="row-num">#</th>
                {% for h in sheet_headers %}
                  <th>
                    <div style="font-size:0.72rem; color:#fda4af; margin-bottom:2px;">Columna {{ col_letras[loop.index0] }}</div>
                    <input class="sheet-input" type="text" name="sh_{{ loop.index0 }}" value="{{ h }}" />
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
                    <td>
                      <input class="sheet-input" type="text" name="c_{{ r_idx }}_{{ c_idx }}" value="{{ celda }}" placeholder="{{ col_letras[c_idx] }}{{ loop.index if false else (r_idx + 1) }}" />
                      {% set eval_val = sheet_eval[r_idx][c_idx] %}
                      {% if celda.startswith('=') %}
                        <small style="color:#6ee7b7; display:block; margin-top:2px;">= {{ eval_val }}</small>
                      {% endif %}
                    </td>
                  {% endfor %}
                </tr>
              {% endfor %}
            </tbody>
          </table>
        </div>
      </form>

      <canvas id="chartSheet" height="95"></canvas>
    </section>

    <!-- 5. 30 NOTICIAS -->
    <section id="m5" class="mod-panel {% if active_mod != 'm5' %}hidden{% endif %}">
      <h2>5. Noticias (30 disponibles)</h2>
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
          Buscar "{{ news_query }}" en Google Noticias →
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
      <h2>6. Videos (30 disponibles)</h2>
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

    <!-- 7. ENCICLOPEDIA CON DEFINICIONES COMPLETAS Y EJEMPLOS -->
    <section id="m7" class="mod-panel {% if active_mod != 'm7' %}hidden{% endif %}">
      <h2>7. Enciclopedia y consulta</h2>
      <p style="color:var(--muted)">Escribe un tema (ej: <em>tecnología</em>, <em>programación</em>, <em>petróleo</em>, <em>base de datos</em>, <em>hoja de cálculo</em>, <em>inteligencia artificial</em>, <em>fútbol</em>, <em>economía</em>, <em>ciencia</em>) para leer su definición completa y ejemplo.</p>

      <form method="POST" class="search-row">
        <input type="hidden" name="codigo" value="{{ codigo }}" />
        <input type="hidden" name="active_mod" value="m7" />
        <input type="hidden" name="accion" value="buscar_web" />
        <input type="text" name="web_query" value="{{ web_query }}" placeholder="Escriba un concepto o tema..." />
        <button type="submit" class="btn-primary" style="width:auto;">Consultar</button>
      </form>

      <div class="card" style="margin-bottom:14px;">
        <span class="badge">{{ web_def_titulo }}</span>
        <p style="margin:10px 0; line-height:1.6;">{{ web_def_texto }}</p>
        <div style="background:var(--bg); border-left:3px solid var(--accent); padding:10px 12px; border-radius:8px; font-size:0.88rem; line-height:1.5;">
          {{ web_def_ejemplo }}
        </div>
        <div style="display:flex; gap:14px; flex-wrap:wrap; margin-top:12px; font-size:0.86rem;">
          <a href="https://www.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Google →</a>
          <a href="https://es.wikipedia.org/wiki/Especial:Buscar?search={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Wikipedia →</a>
          <a href="https://news.google.com/search?q={{ web_query_encoded }}" target="_blank" rel="noopener noreferrer">Noticias →</a>
        </div>
      </div>
    </section>

    <!-- 8. ESTADO -->
    <section id="m8" class="mod-panel {% if active_mod != 'm8' %}hidden{% endif %}">
      <h2>8. Estado del sistema C-PRE2</h2>
      <div class="stat-grid">
        <div class="stat-box"><div class="stat-label">Plataforma</div><div class="stat-val">C-PRE2</div></div>
        <div class="stat-box"><div class="stat-label">Estado</div><div class="stat-val" style="color:var(--ok)">ACTIVO</div></div>
        <div class="stat-box"><div class="stat-label">Registros DB</div><div class="stat-val">{{ stats.count }}</div></div>
        <div class="stat-box"><div class="stat-label">Uso</div><div class="stat-val">{{ uso }} / {{ limite }}</div></div>
      </div>
      <p style="color:var(--muted)">Hoja de cálculo con columnas A–H y filas 1–15, enciclopedia con definiciones y ejemplos, base de datos amplia y 30 noticias / 30 videos.</p>
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
  const ctxCustom = document.getElementById('chartCustom');
  if (ctxCustom) {
    new Chart(ctxCustom, {
      type: 'bar',
      data: {
        labels: {{ custom_labels | tojson }},
        datasets: [{
          label: 'Serie ordenada',
          data: {{ custom_values | tojson }},
          backgroundColor: 'rgba(225, 29, 72, 0.58)',
          borderColor: '#e11d48',
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f5f5fc' } } },
        scales: {
          x: { ticks: { color: '#a4a4ba' }, grid: { color: '#2a2a3e' } },
          y: { ticks: { color: '#a4a4ba' }, grid: { color: '#2a2a3e' } }
        }
      }
    });
  }

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
          backgroundColor: 'rgba(16, 185, 129, 0.22)',
          tension: 0.25,
          fill: true
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { labels: { color: '#f5f5fc' } } },
        scales: {
          x: { ticks: { color: '#a4a4ba' }, grid: { color: '#2a2a3e' } },
          y: { ticks: { color: '#a4a4ba' }, grid: { color: '#2a2a3e' } }
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


def _crear_hoja_inicial():
    cols = 8
    rows = 15
    headers = ["Concepto / Item", "Cantidad", "Valor", "Subtotal", "Meta", "Desviación", "Estado", "Nota"]
    grid = [["" for _ in range(cols)] for _ in range(rows)]
    datos_ejemplo = [
        ("Item A", "10", "25", "=B1*C1", "220", "=D1-E1", '=SI(D1>=E1;"Cumple";"Ajustar")', "Base"),
        ("Item B", "8", "30", "=B2*C2", "200", "=D2-E2", '=SI(D2>=E2;"Cumple";"Ajustar")', "Base"),
        ("Item C", "12", "18", "=B3*C3", "210", "=D3-E3", '=SI(D3>=E3;"Cumple";"Ajustar")', "Base"),
        ("Item D", "6", "45", "=B4*C4", "250", "=D4-E4", '=SI(D4>=E4;"Cumple";"Ajustar")', "Base"),
        ("Item E", "15", "20", "=B5*C5", "280", "=D5-E5", '=SI(D5>=E5;"Cumple";"Ajustar")', "Base"),
        ("Total", "=SUMA(B1:B5)", "=PROMEDIO(C1:C5)", "=SUMA(D1:D5)", "=SUMA(E1:E5)", "=SUMA(F1:F5)", "", "Resumen"),
    ]
    for r_i, fila_d in enumerate(datos_ejemplo):
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
            "registros": [
                {"nombre": "Producto Alfa", "valor": 45, "categoria": "Inventario", "fecha": "2026-11-18"},
                {"nombre": "Producto Beta", "valor": 120, "categoria": "Ventas", "fecha": "2026-11-20"},
                {"nombre": "Producto Gamma", "valor": 75, "categoria": "Inventario", "fecha": "2026-11-15"},
            ],
            "db_modo_orden": "manual",
            "db_sort_by": "nombre",
            "db_sort_dir": "asc",
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
            "web_query": "tecnología",
        }
    return ESTADO_SESIONES[code]


def _col_to_idx(col_str):
    col_str = col_str.upper().strip()
    idx = 0
    for ch in col_str:
        if "A" <= ch <= "Z":
            idx = idx * 26 + (ord(ch) - ord("A") + 1)
    return idx - 1


def _expand_range(rango_str, grid_raw):
    m = re.match(r"^([A-Za-z]+)(\d+):([A-Za-z]+)(\d+)$", rango_str.strip())
    if not m:
        return []
    c1, r1, c2, r2 = _col_to_idx(m.group(1)), int(m.group(2)) - 1, _col_to_idx(m.group(3)), int(m.group(4)) - 1
    vals = []
    for r in range(min(r1, r2), max(r1, r2) + 1):
        for c in range(min(c1, c2), max(c1, c2) + 1):
            if 0 <= r < len(grid_raw) and 0 <= c < len(grid_raw[r]):
                v = evaluar_celda(grid_raw[r][c], grid_raw, visitadas=set())
                try:
                    vals.append(float(v))
                except (TypeError, ValueError):
                    pass
    return vals


def evaluar_celda(val, grid_raw, visitadas=None):
    if visitadas is None:
        visitadas = set()
    s = str(val or "").strip()
    if not s.startswith("="):
        return s

    expr = s[1:].strip()

    m_si = re.match(r"^SI\((.+)\)$", expr, flags=re.IGNORECASE)
    if m_si:
        partes_si = [p.strip() for p in re.split(r"[;,]", m_si.group(1))]
        if len(partes_si) >= 3:
            cond_raw, v_true, v_false = partes_si[0], partes_si[1].strip('"'), partes_si[2].strip('"')
            cond_eval = re.sub(
                r"\b([A-Za-z]{1,2})(\d{1,3})\b",
                lambda mm: str(float(evaluar_celda(grid_raw[int(mm.group(2)) - 1][_col_to_idx(mm.group(1))], grid_raw, set(visitadas)))),
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
            v_num = float(evaluar_celda("=" + partes_r[0], grid_raw, set(visitadas)))
            dec = int(float(partes_r[1]))
            return str(round(v_num, max(0, dec)))

    def repl_func(match):
        fname = match.group(1).upper()
        arg = match.group(2).strip()
        nums = _expand_range(arg, grid_raw)
        if not nums:
            for part in re.split(r"[;,]", arg):
                part = part.strip()
                ref = re.match(r"^([A-Za-z]+)(\d+)$", part)
                if ref:
                    ci, ri = _col_to_idx(ref.group(1)), int(ref.group(2)) - 1
                    if 0 <= ri < len(grid_raw) and 0 <= ci < len(grid_raw[ri]):
                        try:
                            nums.append(float(evaluar_celda(grid_raw[ri][ci], grid_raw, set(visitadas))))
                        except (TypeError, ValueError):
                            pass
                else:
                    try:
                        nums.append(float(part))
                    except ValueError:
                        pass
        if fname in ("CONTAR", "COUNT", "CONTARA"):
            return str(len(nums))
        if not nums:
            return "0"
        if fname in ("SUMA", "SUM"):
            return str(sum(nums))
        if fname in ("PROMEDIO", "AVG", "AVERAGE"):
            return str(sum(nums) / len(nums))
        if fname == "MAX":
            return str(max(nums))
        if fname == "MIN":
            return str(min(nums))
        return "0"

    expr = re.sub(
        r"\b(SUMA|SUM|PROMEDIO|AVG|AVERAGE|MAX|MIN|CONTAR|COUNT|CONTARA)\(([^()]+)\)",
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
        res = evaluar_celda(grid_raw[ri][ci], grid_raw, visitadas)
        try:
            return str(float(res))
        except (TypeError, ValueError):
            return "0"

    expr = re.sub(r"\b([A-Za-z]{1,2})(\d{1,3})\b", repl_cell, expr)

    try:
        if re.match(r"^[0-9+\-*/().\s]+$", expr):
            val_num = eval(expr, {"__builtins__": {}}, {})
            if isinstance(val_num, float) and val_num.is_integer():
                return str(int(val_num))
            if isinstance(val_num, float):
                return str(round(val_num, 4))
            return str(val_num)
    except Exception:
        return "ERR"
    return expr


def evaluar_hoja(sheet_raw):
    return [[evaluar_celda(c, sheet_raw, set()) for c in fila] for fila in sheet_raw]


def ordenar_registros(registros, modo="manual", campo="nombre", direccion="asc"):
    if modo == "auto":
        if not registros:
            return []
        vals = [float(r.get("valor", 0) or 0) for r in registros]
        if len(set(vals)) > 1:
            return sorted(registros, key=lambda x: float(x.get("valor", 0) or 0), reverse=True)
        return sorted(registros, key=lambda x: str(x.get("nombre", "")).lower())

    rev = (direccion == "desc")
    if campo == "valor":
        return sorted(registros, key=lambda x: float(x.get("valor", 0) or 0), reverse=rev)
    if campo == "fecha":
        return sorted(registros, key=lambda x: str(x.get("fecha", "")), reverse=rev)
    if campo == "categoria":
        return sorted(registros, key=lambda x: str(x.get("categoria", "")).lower(), reverse=rev)
    return sorted(registros, key=lambda x: str(x.get("nombre", "")).lower(), reverse=rev)


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
        return out if out else "Código ejecutado sin salida impresa."
    except Exception as e:
        return f"Error: {e}"


def consultar_enciclopedia(query):
    q_raw = (query or "tecnología").strip()
    q = q_raw.lower()
    # Normalizar acentos básicos para buscar mejor
    q_norm = (
        q.replace("á", "a").replace("é", "e").replace("í", "i")
        .replace("ó", "o").replace("ú", "u")
    )
    for clave, info in ENCICLOPEDIA_COMPLETA.items():
        if clave in q_norm or q_norm in clave:
            return info["titulo"], info["definicion"], info["ejemplo"]

    nombre = q_raw.capitalize()
    return (
        nombre,
        f"{nombre} es un concepto o ámbito que puede estudiarse desde sus fundamentos teóricos, "
        f"sus componentes principales, sus aplicaciones prácticas y su impacto real. Comprender "
        f"cómo funciona {q_raw} implica identificar sus elementos clave, cómo interactúan entre sí "
        f"y en qué situaciones resulta más útil aplicarlo.",
        f"Ejemplo práctico: Si trabajas con '{q_raw}', define primero el objetivo concreto, "
        f"reúne los datos o elementos involucrados, aplica un método ordenado de análisis y "
        f"comprueba el resultado obtenido.",
    )


def render_panel(codigo, estado, error_msg=None, aviso_msg=None):
    info = CODIGOS_ACCESO[codigo]
    registros_ordenados = ordenar_registros(
        estado["registros"], estado["db_modo_orden"], estado["db_sort_by"], estado["db_sort_dir"]
    )
    custom_labels, custom_values = ordenar_elementos_custom(
        estado["custom_items"], estado["custom_tipo"], estado["custom_dir"]
    )
    sheet_eval = evaluar_hoja(estado["sheet_raw"])

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
            sheet_vals.append(int(num_encontrado) if num_encontrado.is_integer() else round(num_encontrado, 2))

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

    wq = (estado["web_query"] or "tecnología").strip()
    web_t, web_def, web_ej = consultar_enciclopedia(wq)

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
        db_modo_orden=estado["db_modo_orden"],
        db_sort_by=estado["db_sort_by"],
        db_sort_dir=estado["db_sort_dir"],
        stats=calcular_stats(registros_ordenados),
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

        elif accion == "cargar_lote_db":
            lote = parsear_lineas_db(request.form.get("lote_db_texto") or "")
            autog = int(request.form.get("autollenar_n") or 0)
            modo = request.form.get("modo_carga_db") or "reemplazar"
            if autog > 0:
                extra = [
                    {
                        "nombre": f"Registro {i}",
                        "valor": (i * 15) % 300 + 10,
                        "categoria": "Lote" if i % 2 == 0 else "Operación",
                        "fecha": f"2026-11-{(i % 28) + 1:02d}",
                    }
                    for i in range(1, autog + 1)
                ]
                lote.extend(extra)
            if lote:
                if modo == "reemplazar":
                    estado["registros"] = lote
                else:
                    estado["registros"].extend(lote)
                aviso = f"Base actualizada: {len(lote)} fila(s) cargadas."
            else:
                error = "Escriba o pegue filas o seleccione generar registros."
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

        elif accion == "ordenar_db":
            estado["db_modo_orden"] = request.form.get("db_modo_orden") or "manual"
            estado["db_sort_by"] = request.form.get("db_sort_by") or "nombre"
            estado["db_sort_dir"] = request.form.get("db_sort_dir") or "asc"
            aviso = f"Base ordenada ({estado['db_modo_orden']})."
            estado["active_mod"] = "m2"

        elif accion == "borrar_fila":
            try:
                idx = int(request.form.get("fila_idx", -1))
                ordenadas = ordenar_registros(
                    estado["registros"], estado["db_modo_orden"], estado["db_sort_by"], estado["db_sort_dir"]
                )
                if 0 <= idx < len(ordenadas):
                    estado["registros"].remove(ordenadas[idx])
                    aviso = "Fila eliminada."
            except Exception:
                error = "No se pudo eliminar la fila."
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

        elif accion in (
            "sheet_calcular", "sheet_add_row", "sheet_del_row",
            "sheet_add_col", "sheet_del_col", "sheet_sort", "sheet_import"
        ):
            leer_hoja_desde_form(estado)
            n_cols = len(estado["sheet_headers"])
            if accion == "sheet_add_row":
                estado["sheet_raw"].append(["" for _ in range(n_cols)])
                aviso = "Fila añadida."
            elif accion == "sheet_del_row":
                if len(estado["sheet_raw"]) > 1:
                    estado["sheet_raw"].pop()
                    aviso = "Última fila eliminada."
                else:
                    error = "Debe quedar al menos 1 fila."
            elif accion == "sheet_add_col":
                estado["sheet_headers"].append(f"Col {n_cols + 1}")
                for f in estado["sheet_raw"]:
                    f.append("")
                aviso = "Columna añadida."
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
                evaluada_pairs = list(zip(estado["sheet_raw"], evaluar_hoja(estado["sheet_raw"])))

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
                aviso = "Fórmulas calculadas."
            estado["active_mod"] = "m4"

        elif accion == "buscar_noticias":
            estado["news_query"] = (request.form.get("news_query") or "").strip()
            estado["active_mod"] = "m5"

        elif accion == "buscar_videos":
            estado["video_query"] = (request.form.get("video_query") or "").strip()
            estado["active_mod"] = "m6"

        elif accion == "buscar_web":
            estado["web_query"] = (request.form.get("web_query") or "tecnología").strip()
            estado["active_mod"] = "m7"

        return render_panel(codigo, estado, error_msg=error, aviso_msg=aviso)

    return render_template_string(HTML_TEMPLATE, autorizado=False, error=None)


@app.route("/descargar-csv")
def descargar_csv():
    codigo = (request.args.get("codigo") or "").strip().upper()
    estado = obtener_estado(codigo)
    if not estado:
        return "Código no autorizado", 403
    ordenadas = ordenar_registros(
        estado["registros"], estado["db_modo_orden"], estado["db_sort_by"], estado["db_sort_dir"]
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

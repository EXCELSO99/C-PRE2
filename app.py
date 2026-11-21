import ast
import csv
import io
import json
import math
import statistics
from datetime import datetime
from urllib.parse import quote_plus
from flask import Flask, render_template_string, request, redirect, url_for, session, Response

app = Flask(__name__)
app.secret_key = "cipres2_crimson_core_2026"

CODIGOS_ACCESO = {
    "DEMO2026": {"nombre": "Invitado Demo", "plan": "DEMO", "limite": 50},
    "VIP100": {"nombre": "Director Ejecutivo", "plan": "PRO ULTRA", "limite": 10000},
    "EXCELSO99": {"nombre": "Fundador Cipres 2", "plan": "PRO ULTRA", "limite": 10000},
}

NOTICIAS_BASE = [
    {
        "titulo": "Avances en eficiencia energética y cómputo en la nube",
        "categoria": "Tecnología",
        "resumen": "Nuevos enfoques de software buscan reducir el consumo de recursos en centros de datos y sistemas distribuidos manteniendo alta velocidad de respuesta.",
        "fuente": "TechCrunch",
        "url": "https://techcrunch.com/"
    },
    {
        "titulo": "Panorama global de mercados energéticos y crudo",
        "categoria": "Economía",
        "resumen": "Analistas revisan inventarios, rutas marítimas, producción y demanda industrial en los principales mercados energéticos internacionales.",
        "fuente": "Reuters Business",
        "url": "https://www.reuters.com/business/energy/"
    },
    {
        "titulo": "Resumen del fútbol internacional y torneos de élite",
        "categoria": "Deportes",
        "resumen": "Resultados recientes, análisis táctico, rendimiento de figuras clave y tabla de posiciones en las principales ligas y competiciones.",
        "fuente": "ESPN Fútbol",
        "url": "https://www.espn.com/soccer/"
    },
    {
        "titulo": "Exploración espacial y fenómenos de alta energía",
        "categoria": "Ciencia",
        "resumen": "Observatorios y equipos científicos continúan estudiando estrellas compactas, supernovas y dinámicas astrofísicas extremas.",
        "fuente": "NASA Science",
        "url": "https://science.nasa.gov/"
    },
]

VIDEOS_BASE = [
    {
        "titulo": "Análisis de Datos y Automatización en Python",
        "tema": "Programación y Datos",
        "previa": "Revisa cómo limpiar tablas, detectar patrones y automatizar tareas repetitivas que en hojas de cálculo manuales toman mucho más tiempo.",
        "url": "https://www.youtube.com/results?search_query=python+data+analysis+tutorial"
    },
    {
        "titulo": "Geología del Petróleo y Sistemas Petroleros",
        "tema": "Hidrocarburos",
        "previa": "Explicación visual sobre roca generadora, roca yacimiento, trampas estructurales y estratigráficas y gravedad API.",
        "url": "https://www.youtube.com/results?search_query=petroleum+geology+reservoir+traps"
    },
    {
        "titulo": "Táctica y Análisis de Fútbol Moderno",
        "tema": "Deportes",
        "previa": "Desglose de movimientos colectivos, presión alta, transiciones rápidas y toma de decisiones en el último tercio.",
        "url": "https://www.youtube.com/results?search_query=football+tactics+analysis"
    },
    {
        "titulo": "Contabilidad Práctica y Control Financiero",
        "tema": "Contabilidad",
        "previa": "Repaso de registros, conciliaciones, flujo de caja y organización de información financiera para negocios.",
        "url": "https://www.youtube.com/results?search_query=accounting+basics+financial+statements"
    },
]

WEBS_RECOMENDADAS = [
    {
        "nombre": "IFAC / Normas y Recursos Contables",
        "area": "Contabilidad",
        "descripcion": "Portal de referencia para estándares internacionales de contabilidad, auditoría y práctica profesional.",
        "url": "https://www.ifac.org/"
    },
    {
        "nombre": "PubMed / Biblioteca Médica",
        "area": "Medicina",
        "descripcion": "Buscador de literatura biomédica, artículos científicos y revisiones clínicas revisadas por pares.",
        "url": "https://pubmed.ncbi.nlm.nih.gov/"
    },
    {
        "nombre": "AAPG Wiki / Geología del Petróleo",
        "area": "Hidrocarburos",
        "descripcion": "Enciclopedia técnica sobre cuencas sedimentarias, yacimientos, exploración y geociencias aplicadas a hidrocarburos.",
        "url": "https://wiki.aapg.org/"
    },
    {
        "nombre": "Documentación Oficial de Python",
        "area": "Programación",
        "descripcion": "Guía de referencia del lenguaje Python, estructuras de datos, módulos estándar y buenas prácticas.",
        "url": "https://docs.python.org/3/"
    },
    {
        "nombre": "MDN Web Docs",
        "area": "Programación",
        "descripcion": "Documentación clara y completa sobre HTML, CSS, JavaScript y desarrollo web.",
        "url": "https://developer.mozilla.org/"
    },
]

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CIPRES 2 // C-PRE2 CRIMSON SUITE</title>
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
<style>
  :root {
    --bg: #050507;
    --card: #0c0c11;
    --card-2: #13131b;
    --red: #ff1e38;
    --red-bright: #ff596d;
    --red-glow: rgba(255, 30, 56, 0.5);
    --red-dim: rgba(255, 30, 56, 0.14);
    --text: #f5f5f8;
    --muted: #9b9ba8;
    --line: #26141a;
  }

  * { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Segoe UI', system-ui, sans-serif; }

  body {
    background: radial-gradient(circle at 50% 0%, #22060c 0%, var(--bg) 52%);
    color: var(--text);
    min-height: 100vh;
    overflow-x: hidden;
  }

  .top-flash {
    height: 3px;
    width: 100%;
    background: linear-gradient(90deg, transparent, var(--red), var(--red-bright), var(--red), transparent);
    box-shadow: 0 0 22px var(--red), 0 0 45px var(--red);
  }

  .wrap {
    max-width: 1220px;
    margin: 0 auto;
    padding: 20px 16px 64px;
  }

  .hero {
    display: flex;
    flex-wrap: wrap;
    justify-content: space-between;
    align-items: center;
    gap: 14px;
    padding: 20px 24px;
    background: rgba(12, 12, 17, 0.94);
    border: 1px solid var(--line);
    border-left: 4px solid var(--red);
    border-radius: 16px;
    margin-bottom: 20px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.7), 0 0 24px rgba(255, 30, 56, 0.14);
  }

  .hero h1 {
    font-size: 1.75rem;
    letter-spacing: 2px;
    font-weight: 800;
    background: linear-gradient(90deg, #ffffff, var(--red-bright));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
  }

  .hero p { color: var(--muted); font-size: 0.88rem; margin-top: 4px; }

  .pill {
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    color: var(--red-bright);
    background: var(--red-dim);
    border: 1px solid var(--red);
    box-shadow: 0 0 14px rgba(255, 30, 56, 0.28);
  }

  /* 7 Renglones / Módulos */
  .modules-nav {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
    gap: 10px;
    margin-bottom: 24px;
  }

  .mod-btn {
    position: relative;
    overflow: hidden;
    background: var(--card);
    color: var(--text);
    border: 1px solid var(--line);
    border-radius: 13px;
    padding: 13px 15px;
    text-align: left;
    cursor: pointer;
    transition: all 0.22s ease;
  }

  .mod-btn::after {
    content: "";
    position: absolute;
    top: 0; left: -100%;
    width: 100%; height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255, 30, 56, 0.35), transparent);
    transition: left 0.45s ease;
  }

  .mod-btn:hover::after { left: 100%; }

  .mod-btn:hover, .mod-btn.active {
    border-color: var(--red);
    background: linear-gradient(135deg, #1d080d 0%, #0e0e14 100%);
    box-shadow: 0 0 22px rgba(255, 30, 56, 0.32);
    transform: translateY(-2px);
  }

  .mod-num {
    font-size: 0.72rem;
    font-weight: 800;
    color: var(--red-bright);
    letter-spacing: 1px;
    text-transform: uppercase;
  }

  .mod-title {
    font-size: 0.98rem;
    font-weight: 700;
    margin-top: 2px;
  }

  .card {
    background: var(--card);
    border: 1px solid var(--line);
    border-radius: 18px;
    padding: 22px;
    margin-bottom: 22px;
    box-shadow: 0 12px 32px rgba(0, 0, 0, 0.65);
  }

  .card h2 {
    font-size: 1.25rem;
    margin-bottom: 8px;
    display: flex;
    align-items: center;
    gap: 10px;
  }

  .card h2::before {
    content: "";
    width: 10px; height: 10px;
    border-radius: 50%;
    background: var(--red);
    box-shadow: 0 0 12px var(--red);
  }

  .sub { color: var(--muted); font-size: 0.9rem; margin-bottom: 16px; line-height: 1.45; }

  .grid-2 { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; margin-bottom: 14px; }
  .grid-3 { display: grid; grid-template-columns: repeat(auto-fit, minmax(190px, 1fr)); gap: 12px; margin-bottom: 14px; }

  label { display: block; font-size: 0.82rem; color: #d5d5e0; margin-bottom: 6px; font-weight: 600; }

  input[type="text"], input[type="file"], select, textarea {
    width: 100%;
    background: #07070a;
    color: var(--text);
    border: 1px solid #2b2630;
    border-radius: 11px;
    padding: 11px 13px;
    font-size: 0.92rem;
    transition: all 0.22s ease;
  }

  input:focus, select:focus, textarea:focus {
    outline: none;
    border-color: var(--red);
    box-shadow: 0 0 18px rgba(255, 30, 56, 0.38);
    background: #0d0709;
  }

  textarea.code-box {
    min-height: 170px;
    font-family: 'Consolas', 'Courier New', monospace;
    line-height: 1.45;
  }

  .btn-red {
    width: 100%;
    padding: 13px 18px;
    background: linear-gradient(90deg, #bd0b22, var(--red));
    color: #fff;
    border: none;
    border-radius: 11px;
    font-weight: 800;
    font-size: 0.95rem;
    cursor: pointer;
    box-shadow: 0 0 22px rgba(255, 30, 56, 0.4);
    transition: all 0.2s ease;
  }

  .btn-red:hover {
    transform: translateY(-1px);
    box-shadow: 0 0 34px rgba(255, 30, 56, 0.75);
  }

  .btn-ghost {
    display: inline-block;
    padding: 9px 14px;
    background: var(--card-2);
    color: #fff;
    border: 1px solid var(--red);
    border-radius: 10px;
    text-decoration: none;
    font-weight: 700;
    font-size: 0.86rem;
    cursor: pointer;
    transition: 0.2s;
  }

  .btn-ghost:hover { background: var(--red); box-shadow: 0 0 16px var(--red); }

  .out-box {
    margin-top: 14px;
    padding: 14px;
    border-radius: 12px;
    background: #070709;
    border: 1px solid rgba(255, 30, 56, 0.35);
    font-family: 'Consolas', monospace;
    font-size: 0.88rem;
    white-space: pre-wrap;
    color: #ffd6dc;
  }

  .item-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(260px, 1fr));
    gap: 14px;
    margin-top: 14px;
  }

  .mini-card {
    background: #08080c;
    border: 1px solid var(--line);
    border-radius: 14px;
    padding: 16px;
    transition: all 0.22s ease;
  }

  .mini-card:hover {
    border-color: var(--red);
    box-shadow: 0 0 20px rgba(255, 30, 56, 0.22);
    transform: translateY(-2px);
  }

  .tag {
    display: inline-block;
    font-size: 0.72rem;
    font-weight: 700;
    color: var(--red-bright);
    background: var(--red-dim);
    padding: 3px 9px;
    border-radius: 999px;
    margin-bottom: 8px;
  }

  .mini-card h3 { font-size: 1rem; margin-bottom: 8px; }
  .mini-card p { font-size: 0.86rem; color: var(--muted); line-height: 1.4; margin-bottom: 12px; }

  .table-wrap { overflow-x: auto; margin-top: 14px; border: 1px solid var(--line); border-radius: 12px; }
  table { width: 100%; border-collapse: collapse; font-size: 0.88rem; }
  th { background: #19080d; color: var(--red-bright); padding: 11px 13px; text-align: left; border-bottom: 2px solid var(--red); }
  td { padding: 10px 13px; border-bottom: 1px solid #191922; transition: 0.2s; }

  tbody tr { animation: rowGlow 0.6s ease-out; }
  tbody tr:hover {
    background: linear-gradient(90deg, rgba(255, 30, 56, 0.22), transparent);
    box-shadow: inset 3px 0 0 var(--red);
  }

  @keyframes rowGlow {
    0% { background-color: rgba(255, 30, 56, 0.42); }
    100% { background-color: transparent; }
  }

  .chart-box {
    background: #07070a;
    border: 1px solid rgba(255, 30, 56, 0.35);
    border-radius: 14px;
    padding: 16px;
    height: 360px;
    margin-top: 16px;
  }

  .kpi-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
    gap: 12px;
    margin: 14px 0;
  }

  .kpi {
    background: #09090e;
    border: 1px solid rgba(255, 30, 56, 0.3);
    border-radius: 12px;
    padding: 14px;
    text-align: center;
  }

  .kpi .v { font-size: 1.6rem; font-weight: 800; color: var(--red-bright); }
  .kpi .k { font-size: 0.76rem; color: var(--muted); margin-top: 3px; }

  .alert {
    padding: 12px 15px;
    border-radius: 11px;
    background: rgba(255, 30, 56, 0.16);
    border: 1px solid var(--red);
    color: #ff94a2;
    margin-bottom: 14px;
    font-size: 0.88rem;
  }

  .login-card {
    max-width: 430px;
    margin: 65px auto;
    padding: 30px 24px;
    background: var(--card);
    border: 1px solid var(--red);
    border-radius: 18px;
    box-shadow: 0 0 40px rgba(255, 30, 56, 0.25);
    text-align: center;
  }

  .hidden { display: none; }
</style>
</head>
<body>
<div class="top-flash"></div>

{% if not user %}
  <div class="wrap">
    <div class="login-card">
      <div class="hero" style="justify-content:center; text-align:center; border-left:none; border-bottom:3px solid var(--red);">
        <div>
          <h1>CIPRES 2</h1>
          <p>PLATAFORMA DIGITAL // C-PRE2</p>
        </div>
      </div>
      {% if error %}<div class="alert">{{ error }}</div>{% endif %}
      <form method="POST" action="/login">
        <label style="text-align:left;">Código de acceso</label>
        <input type="text" name="codigo" placeholder="DEMO2026 o VIP100" required autocomplete="off">
        <br><br>
        <button type="submit" class="btn-red">ENTRAR A CIPRES 2</button>
      </form>
    </div>
  </div>
{% else %}
  <div class="wrap">
    <div class="hero">
      <div>
        <h1>CIPRES 2</h1>
        <p>Usuario: <strong>{{ user.nombre }}</strong> · Límite de filas: <strong>{{ user.limite }}</strong></p>
      </div>
      <div style="display:flex; gap:10px; align-items:center;">
        <span class="pill">{{ user.plan }}</span>
        <a href="/logout" class="btn-ghost">Salir</a>
      </div>
    </div>

    <!-- LOS 7 RENGLONES DE CIPRES 2 -->
    <div class="modules-nav">
      <button class="mod-btn {% if active_tab=='m1' %}active{% endif %}" onclick="openMod('m1', this)">
        <div class="mod-num">Renglón 1</div>
        <div class="mod-title">Programar</div>
      </button>
      <button class="mod-btn {% if active_tab=='m2' %}active{% endif %}" onclick="openMod('m2', this)">
        <div class="mod-num">Renglón 2</div>
        <div class="mod-title">Crear base de datos</div>
      </button>
      <button class="mod-btn {% if active_tab=='m3' %}active{% endif %}" onclick="openMod('m3', this)">
        <div class="mod-num">Renglón 3</div>
        <div class="mod-title">Ordenar base de datos</div>
      </button>
      <button class="mod-btn {% if active_tab=='m4' %}active{% endif %}" onclick="openMod('m4', this)">
        <div class="mod-num">Renglón 4</div>
        <div class="mod-title">Noticias del día</div>
      </button>
      <button class="mod-btn {% if active_tab=='m5' %}active{% endif %}" onclick="openMod('m5', this)">
        <div class="mod-num">Renglón 5</div>
        <div class="mod-title">Videos del día</div>
      </button>
      <button class="mod-btn {% if active_tab=='m6' %}active{% endif %}" onclick="openMod('m6', this)">
        <div class="mod-num">Renglón 6</div>
        <div class="mod-title">Páginas web recomendadas</div>
      </button>
      <button class="mod-btn {% if active_tab=='m7' %}active{% endif %}" onclick="openMod('m7', this)">
        <div class="mod-num">Renglón 7</div>
        <div class="mod-title">Ajustes y estadísticas de la app</div>
      </button>
    </div>

    <!-- 1. PROGRAMAR -->
    <section id="m1" class="mod-panel {% if active_tab!='m1' %}hidden{% endif %}">
      <div class="card">
        <h2>1. Programar (Laboratorio Python y Librerías)</h2>
        <p class="sub">Selecciona librerías de referencia, escribe tu código Python y obtén el resultado al instante.</p>
        <div class="grid-2">
          <div>
            <label>Librería / Módulo de referencia</label>
            <select id="libSelect" onchange="cargarPlantillaLib()">
              <option value="math">math (cálculos matemáticos y raíces)</option>
              <option value="statistics">statistics (promedio, mediana y análisis)</option>
              <option value="pandas">pandas (referencia para tablas y DataFrames)</option>
              <option value="numpy">numpy (referencia para arreglos numéricos)</option>
              <option value="requests">requests (referencia para peticiones HTTP)</option>
              <option value="beautifulsoup4">beautifulsoup4 (referencia para extracción HTML)</option>
            </select>
          </div>
          <div>
            <label>Librerías marcadas para tu script</label>
            <input type="text" id="libsActivas" value="math, statistics" readonly>
          </div>
        </div>
        <form method="POST" action="/ejecutar_codigo">
          <label>Editor de código Python</label>
          <textarea id="pyCode" name="codigo_py" class="code-box">{{ py_code or "datos = [12, 45, 23, 89, 34]\nprint('Total:', sum(datos))\nprint('Promedio:', statistics.mean(datos))\nprint('Raiz del mayor:', round(math.sqrt(max(datos)), 2))" }}</textarea>
          <br><br>
          <button type="submit" class="btn-red">▶ EJECUTAR SCRIPT Y VER RESULTADO</button>
        </form>
        {% if py_salida is not none %}
          <div class="out-box">{{ py_salida }}</div>
        {% endif %}
      </div>
    </section>

    <!-- 2. CREAR BASE DE DATOS -->
    <section id="m2" class="mod-panel {% if active_tab!='m2' %}hidden{% endif %}">
      <div class="card">
        <h2>2. Crear base de datos</h2>
        <p class="sub">Añade registros fila por fila con destello luminoso y descárgalos en formato CSV listo para Excel.</p>
        <div class="grid-3">
          <div>
            <label>Campo 1</label>
            <input type="text" id="newC1" placeholder="Ej: Producto / Nombre">
          </div>
          <div>
            <label>Campo 2</label>
            <input type="text" id="newC2" placeholder="Ej: 2026-11-21 o Área">
          </div>
          <div>
            <label>Campo 3</label>
            <input type="text" id="newC3" placeholder="Ej: 150">
          </div>
        </div>
        <button type="button" class="btn-red" onclick="addRowFlash()">+ AGREGAR FILA CON DESTELLO</button>
        <div class="table-wrap">
          <table id="creatorTbl">
            <thead><tr><th>Campo 1</th><th>Campo 2</th><th>Campo 3</th></tr></thead>
            <tbody></tbody>
          </table>
        </div>
        <br>
        <button type="button" class="btn-ghost" onclick="exportCreatorCSV()">⬇ Descargar base creada (.CSV)</button>
      </div>
    </section>

    <!-- 3. ORDENAR BASE DE DATOS -->
    <section id="m3" class="mod-panel {% if active_tab!='m3' %}hidden{% endif %}">
      <div class="card">
        <h2>3. Ordenar base de datos (Automático con "Nuevo intento" y Manual)</h2>
        <p class="sub">Elige <strong>Orden Automático</strong> para que Cipres 2 proponga un orden (y toca <strong>Nuevo intento</strong> o <strong>Automático por fecha</strong> si quieres cambiarlo), o elige <strong>Orden Manual</strong> para decidirlo tú mismo.</p>

        {% if error and active_tab=='m3' %}<div class="alert">{{ error }}</div>{% endif %}

        <form method="POST" action="/ordenar_datos" enctype="multipart/form-data">
          <div class="grid-3">
            <div>
              <label>Modo principal</label>
              <select

import ast
import csv
import io
import json
import math
import statistics
from datetime import datetime
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

    <section id="m3" class="mod-panel {% if active_tab!='m3' %}hidden{% endif %}">
      <div class="card">
        <h2>3. Ordenar base de datos (Automático con "Nuevo intento" y Manual)</h2>
        <p class="sub">Elige <strong>Orden Automático</strong> para que Cipres 2 proponga un orden (y toca <strong>Nuevo intento</strong> o <strong>Automático por fecha</strong> si quieres cambiarlo), o elige <strong>Orden Manual</strong> para decidirlo tú mismo.</p>

        {% if error and active_tab=='m3' %}<div class="alert">{{ error }}</div>{% endif %}

        <form method="POST" action="/ordenar_datos" enctype="multipart/form-data">
          <div class="grid-3">
            <div>
              <label>Modo principal</label>
              <select name="modo_principal" id="modoPrincipal" onchange="toggleOrdenUI()">
                <option value="auto" {% if modo_principal=='auto' %}selected{% endif %}>Automático (Cipres 2 propone el orden)</option>
                <option value="manual" {% if modo_principal=='manual' %}selected{% endif %}>Manual (Tú eliges columna y criterio)</option>
              </select>
            </div>
            <div>
              <label>Intento automático / Enfoque</label>
              <select name="intento_auto">
                <option value="inteligente" {% if intento_auto=='inteligente' %}selected{% endif %}>Propuesta automática general</option>
                <option value="fecha" {% if intento_auto=='fecha' %}selected{% endif %}>Automático por fecha / hora</option>
                <option value="numerico" {% if intento_auto=='numerico' %}selected{% endif %}>Automático por mayor valor numérico</option>
                <option value="alfabetico" {% if intento_auto=='alfabetico' %}selected{% endif %}>Automático alfabético (A → Z)</option>
              </select>
            </div>
            <div>
              <label>Contador de "Nuevo intento"</label>
              <input type="text" name="num_intento" id="numIntento" value="{{ num_intento or 1 }}" readonly>
            </div>
          </div>

          <div id="manualBox" class="grid-3 {% if modo_principal!='manual' %}hidden{% endif %}">
            <div>
              <label>Columna manual (1, 2, 3...)</label>
              <input type="text" name="col_manual" value="{{ col_manual or '1' }}">
            </div>
            <div>
              <label>Criterio manual</label>
              <select name="criterio_manual">
                <option value="az" {% if criterio_manual=='az' %}selected{% endif %}>Alfabético (A → Z)</option>
                <option value="za" {% if criterio_manual=='za' %}selected{% endif %}>Alfabético inverso (Z → A)</option>
                <option value="num_desc" {% if criterio_manual=='num_desc' %}selected{% endif %}>Numérico: Mayor a menor</option>
                <option value="num_asc" {% if criterio_manual=='num_asc' %}selected{% endif %}>Numérico: Menor a mayor</option>
                <option value="fecha_asc" {% if criterio_manual=='fecha_asc' %}selected{% endif %}>Fecha: Más antigua a reciente</option>
                <option value="fecha_desc" {% if criterio_manual=='fecha_desc' %}selected{% endif %}>Fecha: Más reciente a antigua</option>
              </select>
            </div>
            <div>
              <label>Formato de texto</label>
              <select name="formato_texto">
                <option value="normal" {% if formato_texto=='normal' %}selected{% endif %}>Normal</option>
                <option value="upper" {% if formato_texto=='upper' %}selected{% endif %}>MAYÚSCULAS</option>
                <option value="title" {% if formato_texto=='title' %}selected{% endif %}>Tipo Título</option>
              </select>
            </div>
          </div>

          <div class="grid-2">
            <div>
              <label>Subir archivo .CSV</label>
              <input type="file" name="archivo_csv" accept=".csv,.txt">
            </div>
            <div>
              <label>Limpiar duplicados</label>
              <select name="quitar_dup">
                <option value="si" {% if quitar_dup=='si' %}selected{% endif %}>Sí, eliminar duplicados</option>
                <option value="no" {% if quitar_dup=='no' %}selected{% endif %}>No, mantener todos</option>
              </select>
            </div>
          </div>

          <label>O pega aquí tu base de datos desordenada</label>
          <textarea name="datos_csv" class="code-box" placeholder="Producto,Fecha,Monto&#10;Crudo Liviano,2026-11-18,320&#10;Gas Natural,2026-11-12,180&#10;Crudo Liviano,2026-11-18,320&#10;Diesel,2026-11-20,250">{{ datos_csv or '' }}</textarea>
          <br><br>
          <div class="grid-2">
            <button type="submit" name="accion_btn" value="aplicar" class="btn-red">⚡ APLICAR ORDEN Y MOSTRAR GRÁFICO</button>
            <button type="submit" name="accion_btn" value="nuevo_intento" onclick="sumarIntento()" class="btn-ghost" style="text-align:center; padding:13px;">↻ NUEVO INTENTO (NO ME CONVENCE)</button>
          </div>
        </form>

        {% if res_orden %}
          <hr style="border-color:var(--line); margin:20px 0;">
          <p class="sub"><strong>Criterio aplicado:</strong> {{ res_orden.criterio_usado }}</p>
          <div class="kpi-row">
            <div class="kpi"><div class="v">{{ res_orden.filas }}</div><div class="k">Filas procesadas</div></div>
            <div class="kpi"><div class="v">{{ res_orden.dups }}</div><div class="k">Duplicados quitados</div></div>
            <div class="kpi"><div class="v">{{ res_orden.suma }}</div><div class="k">Suma numérica</div></div>
          </div>

          <form method="POST" action="/descargar_csv" style="margin-bottom:12px;">
            <input type="hidden" name="csv_data" value="{{ res_orden.csv_out }}">
            <button type="submit" class="btn-ghost">⬇ Descargar CSV ordenado para Excel</button>
          </form>

          <div class="chart-box">
            <canvas id="cipresChart"></canvas>
          </div>

          <div class="table-wrap">
            <table>
              <thead>
                <tr>{% for h in res_orden.headers %}<th>{{ h }}</th>{% endfor %}</tr>
              </thead>
              <tbody>
                {% for r in res_orden.rows %}
                  <tr>{% for c in r %}<td>{{ c }}</td>{% endfor %}</tr>
                {% endfor %}
              </tbody>
            </table>
          </div>

          <script>
            new Chart(document.getElementById('cipresChart'), {
              type: 'bar',
              data: {
                labels: {{ res_orden.labels | safe }},
                datasets: [{
                  label: {{ res_orden.metric | safe }},
                  data: {{ res_orden.values | safe }},
                  backgroundColor: 'rgba(255, 30, 56, 0.72)',
                  borderColor: '#ff1e38',
                  borderWidth: 2,
                  borderRadius: 6
                }]
              },
              options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                  legend: { labels: { color: '#f5f5f8', font: { size: 14 } } },
                  title: { display: true, text: 'VISUALIZACIÓN CIPRES 2', color: '#ff596d', font: { size: 16 } }
                },
                scales: {
                  x: { ticks: { color: '#d5d5e0' }, grid: { color: 'rgba(255,255,255,0.05)' } },
                  y: { ticks: { color: '#d5d5e0' }, grid: { color: 'rgba(255,30,56,0.14)' } }
                }
              }
            });
          </script>
        {% endif %}
      </div>
    </section>

    <section id="m4" class="mod-panel {% if active_tab!='m4' %}hidden{% endif %}">
      <div class="card">
        <h2>4. Noticias del día</h2>
        <p class="sub">Busca noticias, filtra por tema, lee la síntesis aquí mismo o abre el portal de origen.</p>
        <div class="grid-2">
          <div>
            <label>Buscar noticia</label>
            <input type="text" id="newsSearch" onkeyup="filterNews()" placeholder="Ej: fútbol, energía, ciencia, tecnología...">
          </div>
          <div>
            <label>Categoría</label>
            <select id="newsCat" onchange="filterNews()">
              <option value="ALL">Todas las categorías</option>
              <option value="Deportes">Deportes</option>
              <option value="Tecnología">Tecnología</option>
              <option value="Economía">Economía</option>
              <option value="Ciencia">Ciencia</option>
            </select>
          </div>
        </div>
        <div style="margin-bottom:14px;">
          <button type="button" class="btn-ghost" onclick="openGoogleNewsSearch()">🔎 Buscar término en noticias web</button>
        </div>
        <div id="newsList" class="item-grid">
          {% for n in noticias %}
            <article class="mini-card news-card" data-cat="{{ n.categoria }}" data-txt="{{ (n.titulo ~ ' ' ~ n.resumen ~ ' ' ~ n.categoria)|lower }}">
              <span class="tag">{{ n.categoria }} · {{ n.fuente }}</span>
              <h3>{{ n.titulo }}</h3>
              <p>{{ n.resumen }}</p>
              <a href="{{ n.url }}" target="_blank" rel="noopener" class="btn-ghost">Leer en el sitio web ↗</a>
            </article>
          {% endfor %}
        </div>
      </div>
    </section>

    <section id="m5" class="mod-panel {% if active_tab!='m5' %}hidden{% endif %}">
      <div class="card">
        <h2>5. Videos del día</h2>
        <p class="sub">Consulta una breve previa de lo que trata cada video y abre el enlace directo para verlo.</p>
        <div class="item-grid">
          {% for v in videos %}
            <article class="mini-card">
              <span class="tag">{{ v.tema }}</span>
              <h3>{{ v.titulo }}</h3>
              <p><strong>Previa:</strong> {{ v.previa }}</p>
              <a href="{{ v.url }}" target="_blank" rel="noopener" class="btn-ghost">Ir al video ▶</a>
            </article>
          {% endfor %}
        </div>
      </div>
    </section>

    <section id="m6" class="mod-panel {% if active_tab!='m6' %}hidden{% endif %}">
      <div class="card">
        <h2>6. Páginas web recomendadas</h2>
        <p class="sub">Usa la lupa para filtrar sitios útiles de contabilidad, medicina, hidrocarburos, programación y más.</p>
        <div class="grid-2">
          <div>
            <label>🔍 Buscar por área o palabra clave</label>
            <input type="text" id="webSearch" onkeyup="filterWebs()" placeholder="Ej: contabilidad, medicina, hidrocarburos, python...">
          </div>
          <div>
            <label>Filtro rápido de área</label>
            <select id="webArea" onchange="filterWebs()">
              <option value="ALL">Todas las áreas</option>
              <option value="Contabilidad">Contabilidad</option>
              <option value="Medicina">Medicina</option>
              <option value="Hidrocarburos">Hidrocarburos</option>
              <option value="Programación">Programación</option>
            </select>
          </div>
        </div>
        <div id="webList" class="item-grid">
          {% for w in webs %}
            <article class="mini-card web-card" data-area="{{ w.area }}" data-txt="{{ (w.nombre ~ ' ' ~ w.area ~ ' ' ~ w.descripcion)|lower }}">
              <span class="tag">{{ w.area }}</span>
              <h3>{{ w.nombre }}</h3>
              <p>{{ w.descripcion }}</p>
              <a href="{{ w.url }}" target="_blank" rel="noopener" class="btn-ghost">Visitar sitio ↗</a>
            </article>
          {% endfor %}
        </div>
      </div>
    </section>

    <section id="m7" class="mod-panel {% if active_tab!='m7' %}hidden{% endif %}">
      <div class="card">
        <h2>7. Ajustes y estadísticas de la aplicación</h2>
        <p class="sub">Métricas de rendimiento y uso de Cipres 2 en esta sesión junto con ajustes visuales rápidos.</p>
        <div class="kpi-row">
          <div class="kpi"><div class="v">{{ stats.operaciones }}</div><div class="k">Operaciones ejecutadas</div></div>
          <div class="kpi"><div class="v">{{ stats.scripts_corridos }}</div><div class="k">Scripts corridos</div></div>
          <div class="kpi"><div class="v">{{ stats.filas_totales }}</div><div class="k">Filas procesadas</div></div>
          <div class="kpi"><div class="v">99.9%</div><div class="k">Estabilidad de sesión</div></div>
        </div>
        <div class="grid-2">
          <div>
            <label>Intensidad de destello rojo</label>
            <select id="glowLevel" onchange="changeGlow()">
              <option value="normal">Estándar (Negro + Rojo)</option>
              <option value="alto">Alto impacto (Destello intenso)</option>
            </select>
          </div>
          <div>
            <label>Estado del motor</label>
            <input type="text" value="Cipres 2 Activo // Nube Render" readonly>
          </div>
        </div>
      </div>
    </section>
  </div>

  <script>
    function openMod(id, btn) {
      document.querySelectorAll('.mod-panel').forEach(p => p.classList.add('hidden'));
      document.querySelectorAll('.mod-btn').forEach(b => b.classList.remove('active'));
      document.getElementById(id).classList.remove('hidden');
      if (btn) btn.classList.add('active');
    }

    function cargarPlantillaLib() {
      const lib = document.getElementById('libSelect').value;
      const box = document.getElementById('pyCode');
      const libsInput = document.getElementById('libsActivas');
      const actuales = libsInput.value.split(',').map(s => s.trim()).filter(Boolean);
      if (!actuales.includes(lib)) {
        actuales.push(lib);
        libsInput.value = actuales.join(', ');
      }
      const plantillas = {
        math: "import math\nprint('Potencia 2^10:', math.pow(2, 10))\nprint('Raiz de 144:', math.sqrt(144))",
        statistics: "import statistics\nvalores = [10, 20, 30, 40, 100]\nprint('Media:', statistics.mean(valores))\nprint('Mediana:', statistics.median(valores))",
        pandas: "# Ejemplo de estructura tabular tipo pandas\nfilas = [{'item': 'A', 'valor': 10}, {'item': 'B', 'valor': 25}]\nprint('Total filas:', len(filas))\nprint('Suma valores:', sum(x['valor'] for x in filas))",
        numpy: "# Ejemplo de arreglo numérico\narr = [2, 4, 6, 8]\ndobles = [x * 2 for x in arr]\nprint('Dobles:', dobles)",
        requests: "# Ejemplo de preparación de consulta HTTP\nendpoint = 'https://api.ejemplo.com/datos'\nprint('Endpoint listo:', endpoint)",
        beautifulsoup4: "# Ejemplo de limpieza de etiquetas de texto\ntexto = '<p><b>Dato limpio</b> en Cipres 2</p>'\nlimpio = texto.replace('<p>', '').replace('<b>', '').replace('</b>', '').replace('</p>', '')\nprint(limpio)"
      };
      box.value = plantillas[lib] || box.value;
    }

    function addRowFlash() {
      const c1 = document.getElementById('newC1').value.trim();
      const c2 = document.getElementById('newC2').value.trim();
      const c3 = document.getElementById('newC3').value.trim();
      if (!c1 && !c2 && !c3) return;
      const tr = document.createElement('tr');
      tr.innerHTML = `<td>${c1}</td><td>${c2}</td><td>${c3}</td>`;
      document.querySelector('#creatorTbl tbody').appendChild(tr);
      document.getElementById('newC1').value = '';
      document.getElementById('newC2').value = '';
      document.getElementById('newC3').value = '';
      document.getElementById('newC1').focus();
    }

    function exportCreatorCSV() {
      const lines = ['Campo_1,Campo_2,Campo_3'];
      document.querySelectorAll('#creatorTbl tbody tr').forEach(tr => {
        const cols = Array.from(tr.querySelectorAll('td')).map(td => td.innerText.replace(/,/g, ' '));
        lines.push(cols.join(','));
      });
      const blob = new Blob(['\\uFEFF' + lines.join('\\n')], { type: 'text/csv;charset=utf-8;' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'cipres2_base_creada.csv';
      a.click();
    }

    function toggleOrdenUI() {
      const m = document.getElementById('modoPrincipal').value;
      document.getElementById('manualBox').classList.toggle('hidden', m !== 'manual');
    }

    function sumarIntento() {
      const inp = document.getElementById('numIntento');
      inp.value = (parseInt(inp.value || '1', 10) + 1);
    }

    function filterNews() {
      const q = document.getElementById('newsSearch').value.toLowerCase().trim();
      const cat = document.getElementById('newsCat').value;
      document.querySelectorAll('.news-card').forEach(card => {
        const okCat = (cat === 'ALL' || card.dataset.cat === cat);
        const okTxt = (!q || card.dataset.txt.includes(q));
        card.classList.toggle('hidden', !(okCat && okTxt));
      });
    }

    function openGoogleNewsSearch() {
      const q = encodeURIComponent(document.getElementById('newsSearch').value.trim() || 'noticias del dia');
      window.open(`https://news.google.com/search?q=${q}`, '_blank');
    }

    function filterWebs() {
      const q = document.getElementById('webSearch').value.toLowerCase().trim();
      const area = document.getElementById('webArea').value;
      document.querySelectorAll('.web-card').forEach(card => {
        const okArea = (area === 'ALL' || card.dataset.area === area);
        const okTxt = (!q || card.dataset.txt.includes(q));
        card.classList.toggle('hidden', !(okArea && okTxt));
      });
    }

    function changeGlow() {
      const lvl = document.getElementById('glowLevel').value;
      document.querySelector('.top-flash').style.height = (lvl === 'alto') ? '6px' : '3px';
    }
  </script>
{% endif %}
</body>
</html>
"""

def get_stats():
    if "stats" not in session:
        session["stats"] = {"operaciones": 0, "scripts_corridos": 0, "filas_totales": 0}
    return session["stats"]

def to_num(val):
    try:
        s = str(val).replace("$", "").replace("€", "").replace(" ", "").replace(",", ".")
        return float(s)
    except ValueError:
        return None

def to_date(val):
    for fmt in ("%Y-%m-%d", "%d/%m/%Y", "%d-%m-%Y", "%Y/%m/%d", "%H:%M", "%H:%M:%S"):
        try:
            return datetime.strptime(str(val).strip(), fmt)
        except ValueError:
            continue
    return None

def render_app(user, active_tab="m1", **ctx):
    stats = get_stats()
    return render_template_string(
        HTML_TEMPLATE,
        user=user,
        active_tab=active_tab,
        noticias=NOTICIAS_BASE,
        videos=VIDEOS_BASE,
        webs=WEBS_RECOMENDADAS,
        stats=stats,
        **ctx
    )

@app.route("/")
def index():
    user = session.get("user")
    return render_app(user, active_tab="m1")

@app.route("/login", methods=["POST"])
def login():
    codigo = request.form.get("codigo", "").strip().upper()
    if codigo in CODIGOS_ACCESO:
        session["user"] = CODIGOS_ACCESO[codigo]
        return redirect(url_for("index"))
    return render_app(None, active_tab="m1", error="Código inválido. Usa DEMO2026 o VIP100.")

@app.route("/logout")
def logout():
    session.pop("user", None)
    return redirect(url_for("index"))

@app.route("/ejecutar_codigo", methods=["POST"])
def ejecutar_codigo():
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))

    codigo = request.form.get("codigo_py", "")
    salida_lines = []

    def fake_print(*args, **kwargs):
        sep = kwargs.get("sep", " ")
        salida_lines.append(sep.join(str(a) for a in args))

    safe_builtins = {
        "abs": abs, "round": round, "min": min, "max": max,
        "sum": sum, "len": len, "range": range, "enumerate": enumerate,
        "sorted": sorted, "list": list, "dict": dict, "set": set,
        "str": str, "int": int, "float": float, "bool": bool,
        "print": fake_print,
    }
    safe_globals = {
        "__builtins__": safe_builtins,
        "math": math,
        "statistics": statistics,
    }

    try:
        tree = ast.parse(codigo, mode="exec")
        for node in ast.walk(tree):
            if isinstance(node, (ast.Import, ast.ImportFrom, ast.While)):
                if isinstance(node, ast.While):
                    raise RuntimeError("Bucles 'while' desactivados por seguridad en la nube; usa 'for' o listas.")
        exec(compile(tree, filename="<cipres2_script>", mode="exec"), safe_globals, {})
        st = get_stats()
        st["scripts_corridos"] += 1
        st["operaciones"] += 1
        session["stats"] = st
        salida = "\n".join(salida_lines) if salida_lines else "Script ejecutado sin salida impresa (usa print(...) para ver resultados)."
    except Exception as exc:
        salida = f"Error al ejecutar: {exc}"

    return render_app(user, active_tab="m1", py_code=codigo, py_salida=salida)

@app.route("/ordenar_datos", methods=["GET", "POST"])
def ordenar_datos():
    if request.method == "GET":
        return redirect(url_for("index"))
    user = session.get("user")
    if not user:
        return redirect(url_for("index"))

    raw_text = request.form.get("datos_csv", "").strip()
    archivo = request.files.get("archivo_csv")
    if archivo and archivo.filename:
        raw_bytes = archivo.read()
        try:
            raw_text = raw_bytes.decode("utf-8-sig")
        except UnicodeDecodeError:
            raw_text = raw_bytes.decode("latin-1")

    modo_principal = request.form.get("modo_principal", "auto")
    intento_auto = request.form.get("intento_auto", "inteligente")
    num_intento = int(request.form.get("num_intento", "1") or "1")
    accion_btn = request.form.get("accion_btn", "aplicar")
    col_manual = request.form.get("col_manual", "1")
    criterio_manual = request.form.get("criterio_manual", "az")
    formato_texto = request.form.get("formato_texto", "normal")
    quitar_dup = request.form.get("quitar_dup", "si")

    if not raw_text:
        return render_app(
            user, active_tab="m3",
            error="Pega datos o sube un archivo .CSV para ordenar.",
            modo_principal=modo_principal, intento_auto=intento_auto, num_intento=num_intento
        )

    primera = raw_text.splitlines()[0]
    delim = ";" if primera.count(";") > primera.count(",") else ","
    reader = csv.reader(io.StringIO(raw_text), delimiter=delim)
    filas = [[c.strip() for c in r] for r in reader if any(c.strip() for c in r)]

    if len(filas) < 2:
        return render_app(
            user, active_tab="m3",
            error="Necesitas una fila de encabezados y al menos una fila de datos.",
            datos_csv=raw_text, modo_principal=modo_principal, intento_auto=intento_auto, num_intento=num_intento
        )

    headers = filas[0]
    rows = filas[1:user["limite"] + 1]

    if formato_texto == "upper":
        rows = [[c.upper() for c in r] for r in rows]
    elif formato_texto == "title":
        rows = [[c.title() for c in r] for r in rows]

    dups = 0
    if quitar_dup == "si":
        vistos = set()
        limpias = []
        for r in rows:
            t = tuple(r)
            if t not in vistos:
                vistos.add(t)
                limpias.append(r)
            else:
                dups += 1
        rows = limpias

    def cell(r, idx):
        return r[idx] if 0 <= idx < len(r) else ""

    if modo_principal == "auto":
        fecha_cols = [i for i in range(len(headers)) if any(to_date(cell(r, i)) is not None for r in rows)]
        num_cols = [i for i in range(len(headers)) if any(to_num(cell(r, i)) is not None for r in rows)]

        if accion_btn == "nuevo_intento" and intento_auto == "inteligente":
            ciclo = ["alfabetico", "fecha", "numerico", "inverso"]
            enfoque = ciclo[(num_intento - 1) % len(ciclo)]
        else:
            enfoque = intento_auto

        if enfoque == "fecha" and fecha_cols:
            c_idx = fecha_cols[0]
            rows.sort(key=lambda r: to_date(cell(r, c_idx)) or datetime.min)
            criterio_usado = f"Automático por fecha en columna '{headers[c_idx]}' (Intento #{num_intento})"
        elif enfoque == "numerico" and num_cols:
            c_idx = num_cols[0]
            rows.sort(key=lambda r: to_num(cell(r, c_idx)) if to_num(cell(r, c_idx)) is not None else -1e18, reverse=True)
            criterio_usado = f"Automático numérico mayor a menor en '{headers[c_idx]}' (Intento #{num_intento})"
        elif enfoque == "inverso":
            rows.sort(key=lambda r: cell(r, 0).lower(), reverse=True)
            criterio_usado = f"Automático inverso (Z → A) en '{headers[0]}' (Intento #{num_intento})"
        else:
            rows.sort(key=lambda r: cell(r, 0).lower())
            criterio_usado = f"Automático alfabético (A → Z) en '{headers[0]}' (Intento #{num_intento})"
    else:
        try:
            idx = max(0, int(col_manual) - 1)
        except ValueError:
            idx = 0
        col_nombre = headers[idx] if idx < len(headers) else f"Columna {idx+1}"
        if criterio_manual == "za":
            rows.sort(key=lambda r: cell(r, idx).lower(), reverse=True)
        elif criterio_manual == "num_desc":
            rows.sort(key=lambda r: to_num(cell(r, idx)) if to_num(cell(r, idx)) is not None else -1e18, reverse=True)
        elif criterio_manual == "num_asc":
            rows.sort(key=lambda r: to_num(cell(r, idx)) if to_num(cell(r, idx)) is not None else 1e18)
        elif criterio_manual == "fecha_asc":
            rows.sort(key=lambda r: to_date(cell(r, idx)) or datetime.min)
        elif criterio_manual == "fecha_desc":
            rows.sort(key=lambda r: to_date(cell(r, idx)) or datetime.min, reverse=True)
        else:
            rows.sort(key=lambda r: cell(r, idx).lower())
        criterio_usado = f"Manual en '{col_nombre}' ({criterio_manual})"

    num_col = next((i for i in range(len(headers)) if rows and to_num(cell(rows[0], i)) is not None), None)
    labels, values, suma = [], [], 0.0
    if num_col is not None:
        metric = headers[num_col]
        for r in rows[:20]:
            labels.append(cell(r, 0) or "Fila")
            val = to_num(cell(r, num_col)) or 0.0
            values.append(val)
        for r in rows:
            suma += (to_num(cell(r, num_col)) or 0.0)
    else:
        metric = "Conteo de registros"
        labels = [cell(r, 0) or f"Fila {i+1}" for i, r in enumerate(rows[:20])]
        values = [1 for _ in labels]
        suma = float(len(rows))

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(headers)
    w.writerows(rows)

    st = get_stats()
    st["operaciones"] += 1
    st["filas_totales"] += len(rows)
    session["stats"] = st

    res = {
        "criterio_usado": criterio_usado,
        "headers": headers,
        "rows": rows,
        "filas": len(rows),
        "dups": dups,
        "suma": round(suma, 2),
        "csv_out": buf.getvalue(),
        "labels": json.dumps(labels),
        "values": json.dumps(values),
        "metric": json.dumps(metric),
    }

    return render_app(
        user, active_tab="m3",
        res_orden=res, datos_csv=raw_text,
        modo_principal=modo_principal, intento_auto=intento_auto,
        num_intento=num_intento, col_manual=col_manual,
        criterio_manual=criterio_manual, formato_texto=formato_texto, quitar_dup=quitar_dup
    )

@app.route("/descargar_csv", methods=["POST"])
def descargar_csv():
    data = request.form.get("csv_data", "")
    return Response(
        "\ufeff" + data,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": "attachment;filename=cipres2_ordenado.csv"}
    )

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)

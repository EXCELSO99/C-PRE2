import os
import json
import re
from datetime import datetime
from flask import Flask, request, jsonify

app = Flask(__name__)

PORT = int(os.environ.get("PORT", 5000))
HOST = os.environ.get("HOST", "0.0.0.0")
CLAVES_VALIDAS = {"VIP100", "Celso2026"}
ARCHIVO_DB = os.environ.get("CPRE2_DB_FILE", "cpre2_datos.json")
MAX_FILAS_HOJA = 8
MAX_COLS_HOJA = 4


def construir_entrada_diccionario(
    termino,
    categoria,
    definicion,
    ejemplo,
    sinonimo="",
    antonimo="",
    nota_uso="",
):
    return {
        "termino": termino.strip(),
        "categoria": categoria.strip(),
        "definicion": definicion.strip(),
        "ejemplo": ejemplo.strip(),
        "sinonimo": sinonimo.strip(),
        "antonimo": antonimo.strip(),
        "nota_uso": nota_uso.strip(),
    }


ENTRADAS_DICCIONARIO_BASE = [
    construir_entrada_diccionario(
        "abaco",
        "Sustantivo",
        "Instrumento manual de calculo formado por cuentas ensartadas en varillas para sumar, restar y realizar operaciones aritmeticas.",
        "Antes de usar calculadoras electronicas, el abaco permitia resolver cuentas con rapidez.",
        "contador",
        "computadora",
        "Se asocia al origen historico del calculo ordenado.",
    ),
    construir_entrada_diccionario(
        "acceso",
        "Sustantivo",
        "Accion o facultad de entrar, consultar o utilizar un sistema, espacio o informacion autorizada.",
        "Ingresa la clave valida para habilitar el acceso a la aplicacion.",
        "entrada",
        "bloqueo",
        "Clave en el control de inicio de sesion.",
    ),
    construir_entrada_diccionario(
        "acierto",
        "Sustantivo",
        "Resultado correcto o decision acertada al resolver una tarea, calculo o consulta.",
        "Cada acierto en la hoja de calculo confirma que la formula esta bien planteada.",
        "exito",
        "error",
        "Util en evaluacion y validacion de resultados.",
    ),
    construir_entrada_diccionario(
        "acumular",
        "Verbo",
        "Reunir o ir sumando elementos, valores o avances de forma progresiva con el tiempo.",
        "Guardar cada sesion permite acumular el progreso sin perder registros.",
        "reunir",
        "dispersar",
        "Aplicable tanto a datos numericos como a historial de trabajo.",
    ),
    construir_entrada_diccionario(
        "adaptar",
        "Verbo",
        "Ajustar o modificar algo para que responda mejor a un entorno, dispositivo o necesidad concreta.",
        "La interfaz se adapta para tocar botones y celdas con comodidad en pantalla movil.",
        "ajustar",
        "desajustar",
        "Clave en el diseno responsivo y modular.",
    ),
    construir_entrada_diccionario(
        "agua",
        "Sustantivo",
        "Liquido transparente, incoloro, inodoro e insipido en estado puro, esencial para la vida y multiples procesos.",
        "El agua es fundamental para la vida y para numerosos procesos industriales.",
        "liquido",
        "sequia",
        "Termino basico del vocabulario general y cientifico.",
    ),
    construir_entrada_diccionario(
        "aire",
        "Sustantivo",
        "Mezcla de gases que rodea la Tierra y compone la atmosfera respirable.",
        "El aire limpio es indispensable para el bienestar diario.",
        "atmosfera",
        "vacio",
        "Sustantivo comun de uso cotidiano.",
    ),
    construir_entrada_diccionario(
        "ajuste",
        "Sustantivo",
        "Modificacion precisa realizada para corregir un detalle o calibrar un funcionamiento.",
        "Hicimos un ajuste en el ancho de las columnas para ver mejor los numeros.",
        "correccion",
        "desarreglo",
        "Muy usado al afinar parametros y vistas.",
    ),
    construir_entrada_diccionario(
        "algebra",
        "Sustantivo",
        "Rama de las matematicas que trabaja con cantidades generales representadas por letras y simbolos.",
        "El algebra ayuda a expresar relaciones y formulas de forma general.",
        "calculo",
        "azar",
        "Base para modelos y formulas estructuradas.",
    ),
    construir_entrada_diccionario(
        "algoritmo",
        "Sustantivo",
        "Conjunto ordenado y finito de pasos o reglas definidas para resolver un problema o ejecutar una tarea.",
        "El algoritmo de ordenamiento acomoda la lista de menor a mayor o de la A a la Z.",
        "procedimiento",
        "improvisacion",
        "Fundamento de cualquier proceso repetible.",
    ),
    construir_entrada_diccionario(
        "alinear",
        "Verbo",
        "Colocar elementos, textos o columnas en una direccion o margen comun para dar claridad visual.",
        "Alinear bien los numeros en una tabla facilita leer los totales.",
        "ordenar",
        "desalinear",
        "Mejora la legibilidad de tablas y paneles.",
    ),
    construir_entrada_diccionario(
        "almacenar",
        "Verbo",
        "Guardar informacion o recursos en un soporte o archivo para recuperarla mas adelante.",
        "El sistema almacena el progreso vinculado al correo electronico.",
        "guardar",
        "borrar",
        "Evita perder cambios al cerrar o recargar.",
    ),
    construir_entrada_diccionario(
        "alternativa",
        "Sustantivo",
        "Opcion distinta entre dos o mas posibilidades para resolver una situacion.",
        "Si una clave no se usa, existe la otra clave valida como alternativa.",
        "opcion",
        "imposicion",
        "Util para rutas y decisiones flexibles.",
    ),
    construir_entrada_diccionario(
        "ambiente",
        "Sustantivo",
        "Condiciones o entorno en el que se ejecuta un trabajo, sistema o actividad.",
        "Cada entorno de ejecucion puede configurar su puerto y archivo de datos.",
        "entorno",
        "aislamiento",
        "Aplica a configuracion de servidor y uso diario.",
    ),
    construir_entrada_diccionario(
        "amigo",
        "Sustantivo",
        "Persona con quien se mantiene afecto, confianza mutua y trato cercano.",
        "Un buen amigo apoya en los momentos importantes.",
        "companero",
        "enemigo",
        "Sustantivo de uso frecuente en comunicacion diaria.",
    ),
    construir_entrada_diccionario(
        "analisis",
        "Sustantivo",
        "Examen detallado de las partes o datos de un asunto para comprenderlo y sacar conclusiones.",
        "El analisis de las filas muestra cual columna aporta mas al total.",
        "estudio",
        "descuido",
        "Paso clave antes de tomar decisiones.",
    ),
    construir_entrada_diccionario(
        "anotar",
        "Verbo",
        "Registrar por escrito una idea, cifra o recordatorio para no olvidarlo.",
        "Anota cada cifra en su celda antes de pulsar calcular.",
        "registrar",
        "omitir",
        "Habito practico en trabajo con datos.",
    ),
    construir_entrada_diccionario(
        "aprender",
        "Verbo",
        "Adquirir conocimientos, destrezas o criterio mediante el estudio, la observacion y la practica.",
        "Practicar todos los dias ayuda a aprender con mayor firmeza.",
        "asimilar",
        "olvidar",
        "Eje central del estudio continuo.",
    ),
    construir_entrada_diccionario(
        "archivo",
        "Sustantivo",
        "Conjunto organizado de datos o documento guardado con un nombre para conservar o exportar informacion.",
        "Puedes exportar tus registros ordenados en un archivo de texto.",
        "documento",
        "vacio",
        "Permite respaldar y compartir listas de datos.",
    ),
    construir_entrada_diccionario(
        "armonia",
        "Sustantivo",
        "Equilibrio y correspondencia conveniente entre las partes que forman un conjunto.",
        "Una distribucion limpia por pestanas da armonia al recorrido de la app.",
        "equilibrio",
        "caos",
        "Importante en diseno de interfaces y estructuras.",
    ),
    construir_entrada_diccionario(
        "ascendente",
        "Adjetivo",
        "Que sube o avanza de menor a mayor valor, nivel o posicion alfabetica.",
        "El orden ascendente coloca primero los numeros menores o la letra A.",
        "creciente",
        "descendente",
        "Criterio estandar para ordenar listas y tablas.",
    ),
    construir_entrada_diccionario(
        "asignar",
        "Verbo",
        "Senalar o destinar un valor, funcion o dato a un elemento o usuario.",
        "El progreso guardado se asigna al correo electronico indicado.",
        "atribuir",
        "quitar",
        "Relaciona cada registro con su identificador.",
    ),
    construir_entrada_diccionario(
        "atencion",
        "Sustantivo",
        "Concentracion de la mente en una actividad, detalle o instruccion especifica.",
        "Presta atencion a los valores decimales al sumar filas.",
        "concentracion",
        "distraccion",
        "Reduce errores al ingresar datos.",
    ),
    construir_entrada_diccionario(
        "autenticar",
        "Verbo",
        "Comprobar que una clave o credencial corresponde a una entrada permitida.",
        "Al entrar se autentica la clave antes de mostrar la pantalla de bienvenida.",
        "validar",
        "rechazar",
        "Primer filtro de acceso del sistema.",
    ),
    construir_entrada_diccionario(
        "avance",
        "Sustantivo",
        "Progreso o desplazamiento hacia adelante en una tarea, etapa o proyecto.",
        "Cada registro guardado representa un avance concreto en tu trabajo.",
        "progreso",
        "retroceso",
        "Mide el recorrido realizado.",
    ),
    construir_entrada_diccionario(
        "base",
        "Sustantivo",
        "Fundamento, apoyo principal o conjunto inicial de datos sobre el que se construye algo.",
        "Este diccionario cuenta con una base amplia de palabras listas para consultar.",
        "fundamento",
        "cima",
        "Punto de partida de un sistema o concepto.",
    ),
    construir_entrada_diccionario(
        "bitacora",
        "Sustantivo",
        "Registro cronologico de hechos, observaciones o pasos realizados en un proyecto.",
        "Usa la seccion de archivos como bitacora diaria de tus anotaciones.",
        "registro",
        "olvido",
        "Util para llevar seguimiento ordenado.",
    ),
    construir_entrada_diccionario(
        "bloque",
        "Sustantivo",
        "Conjunto unitario de elementos o panel independiente dentro de una estructura mayor.",
        "Cada modulo funciona como un bloque claro al navegar de izquierda a derecha.",
        "modulo",
        "fragmento",
        "Organiza la interfaz en partes manejables.",
    ),
    construir_entrada_diccionario(
        "buscar",
        "Verbo",
        "Hacer diligencias o consultas para encontrar un termino, dato o definicion.",
        "Escribe la palabra y pulsa buscar para ver su definicion y ejemplo.",
        "consultar",
        "ignorar",
        "Accion principal en el modulo de diccionario.",
    ),
    construir_entrada_diccionario(
        "calculo",
        "Sustantivo",
        "Operacion o conjunto de operaciones matematicas para hallar un resultado a partir de datos.",
        "La hoja de calculo suma las columnas de cada fila y obtiene el total general.",
        "computo",
        "adivinanza",
        "Nucleo funcional de la hoja de calculo.",
    ),
    construir_entrada_diccionario(
        "camino",
        "Sustantivo",
        "Via, ruta o secuencia de pasos que conduce hacia una meta o resultado.",
        "Seguir un orden claro hace mas directo el camino hacia el objetivo.",
        "ruta",
        "desvio",
        "Metafora habitual para procesos y recorridos.",
    ),
    construir_entrada_diccionario(
        "campo",
        "Sustantivo",
        "Espacio o casilla destinado a recibir un tipo especifico de informacion.",
        "Completa el campo de correo electronico para guardar tu progreso.",
        "casilla",
        "vacio",
        "Presente en formularios y tablas.",
    ),
    construir_entrada_diccionario(
        "capacidad",
        "Sustantivo",
        "Aptitud o facultad para realizar una funcion, contener datos o soportar carga.",
        "La tabla amplia ofrece mayor capacidad visual para trabajar varias columnas.",
        "aptitud",
        "incapacidad",
        "Describe alcance funcional o de espacio.",
    ),
    construir_entrada_diccionario(
        "categoria",
        "Sustantivo",
        "Clase o division en la que se agrupan elementos segun caracteristicas comunes.",
        "Cada entrada del diccionario indica su categoria gramatical.",
        "clasificacion",
        "mezcla",
        "Ordena la informacion por tipo.",
    ),
    construir_entrada_diccionario(
        "celda",
        "Sustantivo",
        "Interseccion de una fila y una columna en una hoja de calculo donde se introduce un valor.",
        "Escribe un numero en cada celda de las columnas A, B, C o D.",
        "casilla",
        "margen",
        "Unidad basica de una hoja de calculo.",
    ),
    construir_entrada_diccionario(
        "ciencia",
        "Sustantivo",
        "Rama del saber humano constituida por conocimientos verificables obtenidos mediante metodo y observacion.",
        "La ciencia avanza probando hipotesis y registrando resultados claros.",
        "conocimiento",
        "ignorancia",
        "Sustantivo fundamental en formacion academica.",
    ),
    construir_entrada_diccionario(
        "cifra",
        "Sustantivo",
        "Signo o numero con el que se representa una cantidad o valor.",
        "Revisa cada cifra antes de calcular el total de la fila.",
        "numero",
        "letra",
        "Elemento habitual en hojas de calculo.",
    ),
    construir_entrada_diccionario(
        "claridad",
        "Sustantivo",
        "Cualidad de lo que se entiende con facilidad, sin confusion ni ambiguedad.",
        "Las definiciones breves y los ejemplos aportan claridad al estudio.",
        "nitidez",
        "confusion",
        "Prioridad en textos, menus y herramientas.",
    ),
    construir_entrada_diccionario(
        "clave",
        "Sustantivo",
        "Codigo o palabra secreta que permite verificar el acceso a un sistema o seccion.",
        "Introduce una clave valida para desbloquear la aplicacion.",
        "codigo",
        "desconocimiento",
        "Requisito inicial para ingresar.",
    ),
    construir_entrada_diccionario(
        "codigo",
        "Sustantivo",
        "Conjunto de reglas o instrucciones escritas que determinan como opera un programa.",
        "Todo el servidor y la interfaz web estan reunidos en este codigo.",
        "programa",
        "caos",
        "Base tecnica de la aplicacion.",
    ),
    construir_entrada_diccionario(
        "columna",
        "Sustantivo",
        "Serie vertical de celdas o elementos alineados de arriba abajo en una tabla.",
        "La hoja cuenta con cuatro columnas principales de entrada numerica.",
        "hilera",
        "fila",
        "Eje vertical de una tabla.",
    ),
    construir_entrada_diccionario(
        "combinar",
        "Verbo",
        "Unir o integrar distintos elementos o fuentes para formar un conjunto completo.",
        "Al iniciar se combinan las palabras base con las palabras agregadas por el usuario.",
        "unir",
        "separar",
        "Permite enriquecer datos existentes.",
    ),
    construir_entrada_diccionario(
        "comprobar",
        "Verbo",
        "Verificar mediante revision o prueba que un dato o resultado es exacto.",
        "Comprueba el total general despues de modificar alguna celda.",
        "verificar",
        "ignorar",
        "Buena practica al trabajar con numeros.",
    ),
    construir_entrada_diccionario(
        "concepto",
        "Sustantivo",
        "Idea general o definicion abstracta que resume las caracteristicas esenciales de algo.",
        "Comprender el concepto facilita aplicar la herramienta sin memorizar a ciegas.",
        "nocion",
        "ambiguedad",
        "Elemento clave de aprendizaje.",
    ),
    construir_entrada_diccionario(
        "conexion",
        "Sustantivo",
        "Enlace o comunicacion establecida entre el navegador y el servidor de la aplicacion.",
        "Las acciones de guardar y cargar progreso usan la conexion con el servidor.",
        "enlace",
        "desconexion",
        "Necesaria para persistir datos en disco.",
    ),
    construir_entrada_diccionario(
        "confirmar",
        "Verbo",
        "Ratificar o dar por valido un paso, dato o decision antes de avanzar.",
        "Pulsa ACEPTAR para confirmar la entrada y abrir los modulos.",
        "validar",
        "anular",
        "Marca el paso de la guia inicial al panel principal.",
    ),
    construir_entrada_diccionario(
        "constancia",
        "Sustantivo",
        "Firmeza y perseverancia en mantener un habito o trabajo a lo largo del tiempo.",
        "La constancia diaria es la que consolida el dominio de cualquier tema.",
        "perseverancia",
        "inconstancia",
        "Clave para avanzar en cualquier proyecto.",
    ),
    construir_entrada_diccionario(
        "consulta",
        "Sustantivo",
        "Accion de buscar informacion, revisar una definicion o pedir un dato concreto.",
        "Cada consulta en el diccionario muestra el significado y un ejemplo de uso.",
        "busqueda",
        "omision",
        "Operacion habitual al estudiar.",
    ),
    construir_entrada_diccionario(
        "contenido",
        "Sustantivo",
        "Lo que esta incluido dentro de un texto, archivo, modulo o espacio.",
        "El contenido de la seccion de archivos puede ordenarse y descargarse.",
        "materia",
        "vacio",
        "Representa la informacion trabajada.",
    ),
    construir_entrada_diccionario(
        "control",
        "Sustantivo",
        "Dominio, supervision o mecanismo de regulacion sobre un proceso o estado.",
        "Tienes control sobre tu progreso al guardarlo y cargarlo con tu correo.",
        "dominio",
        "descontrol",
        "Da seguridad al manejar informacion.",
    ),
    construir_entrada_diccionario(
        "coordinar",
        "Verbo",
        "Disponer cosas o acciones de manera ordenada para que funcionen en conjunto.",
        "Las pestanas superiores coordinan el cambio limpio entre modulos.",
        "organizar",
        "desordenar",
        "Favorece una experiencia fluida.",
    ),
    construir_entrada_diccionario(
        "correo",
        "Sustantivo",
        "Direccion o sistema de correo electronico usado para identificar el progreso del usuario.",
        "Escribe tu correo electronico para guardar y recuperar tu sesion.",
        "email",
        "anonimato",
        "Llave para persistir el progreso por usuario.",
    ),
    construir_entrada_diccionario(
        "crear",
        "Verbo",
        "Producir, elaborar o dar origen a algo nuevo a partir de una idea o necesidad.",
        "Puedes crear nuevas definiciones cuando busques una palabra aun no registrada.",
        "generar",
        "destruir",
        "Amplia el diccionario con uso real.",
    ),
    construir_entrada_diccionario(
        "criterio",
        "Sustantivo",
        "Regla o norma establecida para juzgar, clasificar o decidir algo.",
        "El ordenamiento aplica criterio numerico cuando los valores son numeros y alfabetico en texto.",
        "norma",
        "capricho",
        "Define como se comportan las funciones.",
    ),
    construir_entrada_diccionario(
        "cronologia",
        "Sustantivo",
        "Orden o sucesion de fechas y tiempos en que ocurren los hechos.",
        "Las noticias y videos diarios rotan segun el dia del calendario.",
        "secuencia",
        "anacronismo",
        "Ordena la rotacion diaria de contenidos.",
    ),
    construir_entrada_diccionario(
        "cuadricula",
        "Sustantivo",
        "Conjunto de lineas horizontales y verticales que forman casillas o celdas.",
        "La hoja de calculo presenta una cuadricula amplia de 8 filas por 4 columnas.",
        "tabla",
        "bloque",
        "Estructura visual de la hoja de calculo.",
    ),
    construir_entrada_diccionario(
        "cultura",
        "Sustantivo",
        "Conjunto de saberes, costumbres, lenguajes y expresiones de una sociedad.",
        "Conocer palabras y conceptos amplios enriquece la cultura general.",
        "tradicion",
        "ignorancia",
        "Sustantivo de amplio alcance.",
    ),
    construir_entrada_diccionario(
        "dato",
        "Sustantivo",
        "Informacion concreta, valor o registro minimo que sirve para operar o analizar.",
        "Cada dato ingresado en la tabla se toma en cuenta al calcular los totales.",
        "valor",
        "incognita",
        "Materia prima de tablas y archivos.",
    ),
    construir_entrada_diccionario(
        "definicion",
        "Sustantivo",
        "Explicacion clara y precisa del significado de una palabra o expresion.",
        "Al buscar una palabra aparece su definicion y un ejemplo de aplicacion.",
        "significado",
        "confusion",
        "Elemento central de cada entrada del diccionario.",
    ),
    construir_entrada_diccionario(
        "descarga",
        "Sustantivo",
        "Accion de guardar o exportar un archivo desde la aplicacion hacia el dispositivo.",
        "Usa el boton de descargar archivo para guardar tus registros en un documento.",
        "exportacion",
        "carga",
        "Permite sacar los datos fuera de la pagina.",
    ),
    construir_entrada_diccionario(
        "descendente",
        "Adjetivo",
        "Que baja o va de mayor a menor valor o en sentido inverso al alfabetico.",
        "El orden descendente pone primero los valores mas altos o de la Z hacia la A.",
        "decreciente",
        "ascendente",
        "Complementa al orden ascendente.",
    ),
    construir_entrada_diccionario(
        "detalle",
        "Sustantivo",
        "Parte pequena o dato particular que completa la comprension de un conjunto.",
        "Cada video del dia muestra su titulo y un detalle breve de su contenido.",
        "pormenor",
        "conjunto",
        "Aporta precision a la informacion.",
    ),
    construir_entrada_diccionario(
        "diccionario",
        "Sustantivo",
        "Obra o herramienta de consulta que reune palabras con sus definiciones y ejemplos.",
        "En el modulo de diccionario puedes buscar terminos y sumar definiciones nuevas.",
        "lexico",
        "vacio",
        "Modulo principal de consulta de palabras.",
    ),
    construir_entrada_diccionario(
        "dinamico",
        "Adjetivo",
        "Que cambia, responde o se actualiza segun condiciones, acciones o fechas.",
        "Las noticias y videos cambian automaticamente segun el dia.",
        "cambiante",
        "estatico",
        "Describe contenidos que evolucionan.",
    ),
    construir_entrada_diccionario(
        "diseno",
        "Sustantivo",
        "Planificacion y estructura visual o funcional de una obra, objeto o interfaz.",
        "Un buen diseno facilita encontrar cada funcion sin perder tiempo.",
        "trazado",
        "improvisacion",
        "Une estetica y usabilidad.",
    ),
    construir_entrada_diccionario(
        "disponible",
        "Adjetivo",
        "Que esta listo, habilitado o al alcance para ser utilizado en ese momento.",
        "Una vez aceptada la entrada, todos los modulos quedan disponibles.",
        "habilitado",
        "bloqueado",
        "Indica operatividad de una funcion.",
    ),
    construir_entrada_diccionario(
        "documento",
        "Sustantivo",
        "Escrito o archivo que contiene informacion registrada de forma ordenada.",
        "Puedes darle un nombre propio a tu documento antes de descargarlo.",
        "archivo",
        "borrador",
        "Formato habitual para guardar notas o listas.",
    ),
    construir_entrada_diccionario(
        "ejemplo",
        "Sustantivo",
        "Caso concreto o frase ilustrativa que ayuda a entender como se aplica una regla o palabra.",
        "Cada palabra del diccionario incluye un ejemplo para verla en contexto.",
        "muestra",
        "abstraccion",
        "Refuerza la comprension practica.",
    ),
    construir_entrada_diccionario(
        "elemento",
        "Sustantivo",
        "Cada una de las partes o unidades que integran un conjunto, lista o sistema.",
        "Cada linea escrita en el area de texto se trata como un elemento al ordenar.",
        "componente",
        "totalidad",
        "Unidad dentro de una coleccion.",
    ),
    construir_entrada_diccionario(
        "energia",
        "Sustantivo",
        "Capacidad de un sistema para realizar trabajo o producir transformaciones.",
        "La energia se transforma y aprovecha en distintos procesos fisicos y tecnicos.",
        "potencia",
        "inercia",
        "Concepto clave en ciencias y tecnologia.",
    ),
    construir_entrada_diccionario(
        "enlace",
        "Sustantivo",
        "Conexion o vinculo que une dos elementos, datos o puntos.",
        "El correo electronico sirve como enlace para recuperar tu progreso guardado.",
        "vinculo",
        "separacion",
        "Conecta la identidad del usuario con sus datos.",
    ),
    construir_entrada_diccionario(
        "entrada",
        "Sustantivo",
        "Pantalla inicial o dato introducido en un sistema para iniciar o procesar algo.",
        "En la pantalla de entrada ves como funciona la app, pones tu correo y tocas ACEPTAR.",
        "ingreso",
        "salida",
        "Primer paso hacia el uso de los modulos.",
    ),
    construir_entrada_diccionario(
        "entorno",
        "Sustantivo",
        "Conjunto de circunstancias o ajustes que rodean la ejecucion de un programa.",
        "Variables de entorno permiten cambiar puerto o archivo sin tocar el codigo.",
        "contexto",
        "aislamiento",
        "Facilita el despliegue en distintos servidores.",
    ),
    construir_entrada_diccionario(
        "error",
        "Sustantivo",
        "Fallo, equivocacion o desviacion respecto a lo esperado o correcto.",
        "Si escribes una clave incorrecta, el sistema te avisa para que intentes de nuevo.",
        "fallo",
        "acierto",
        "Señal util para corregir entradas.",
    ),
    construir_entrada_diccionario(
        "esquema",
        "Sustantivo",
        "Representacion ordenada y resumida de las partes principales de un tema o sistema.",
        "El esquema de modulos divide el trabajo en pestanas claras.",
        "estructura",
        "desorden",
        "Organiza la vision general.",
    ),
    construir_entrada_diccionario(
        "estado",
        "Sustantivo",
        "Situacion o conjunto de valores que tiene un sistema o dato en un momento dado.",
        "Guardar el progreso conserva el estado actual de tu tabla, notas y palabra.",
        "condicion",
        "cambio",
        "Refleja los datos activos de la sesion.",
    ),
    construir_entrada_diccionario(
        "estructura",
        "Sustantivo",
        "Distribucion y orden de las partes que componen un sistema o construccion.",
        "Una estructura limpia hace que cada modulo cumpla su funcion sin estorbar a los demas.",
        "armazon",
        "desconcierto",
        "Soporte organizativo de la aplicacion.",
    ),
    construir_entrada_diccionario(
        "estudio",
        "Sustantivo",
        "Esfuerzo intelectual dedicado a comprender, analizar y aprender un tema.",
        "El estudio diario con herramientas claras hace mas sencillo avanzar.",
        "aprendizaje",
        "abandono",
        "Actividad principal de formacion.",
    ),
    construir_entrada_diccionario(
        "evidencia",
        "Sustantivo",
        "Certeza clara y manifiesta de que algo ocurre o es verdadero.",
        "El total calculado ofrece evidencia inmediata de la suma de cada fila.",
        "prueba",
        "duda",
        "Confirma resultados de forma objetiva.",
    ),
    construir_entrada_diccionario(
        "exactitud",
        "Sustantivo",
        "Precision y fidelidad al obtener un dato o realizar una operacion.",
        "La exactitud en los calculos evita diferencias en los totales finales.",
        "precision",
        "inexactitud",
        "Meta importante al manejar cifras.",
    ),
    construir_entrada_diccionario(
        "exportar",
        "Verbo",
        "Enviar o guardar datos desde el programa hacia un archivo externo.",
        "Exporta tu lista ordenada cuando quieras tenerla en un archivo independiente.",
        "extraer",
        "importar",
        "Facilita guardar copias de registros.",
    ),
    construir_entrada_diccionario(
        "fila",
        "Sustantivo",
        "Linea horizontal de celdas o elementos dispuestos de izquierda a derecha en una tabla.",
        "La hoja de calculo dispone de ocho filas numeradas del 1 al 8.",
        "linea",
        "columna",
        "Eje horizontal de una tabla.",
    ),
    construir_entrada_diccionario(
        "flujo",
        "Sustantivo",
        "Movimiento continuo y ordenado de informacion, pasos o acciones.",
        "El flujo empieza en la clave, sigue en la entrada con correo y pasa a los modulos.",
        "secuencia",
        "bloqueo",
        "Define el recorrido natural del usuario.",
    ),
    construir_entrada_diccionario(
        "formato",
        "Sustantivo",
        "Conjunto de caracteristicas de presentacion o estructura de un texto o archivo.",
        "Los registros se guardan en texto plano limpio para facil lectura.",
        "disposicion",
        "informe",
        "Determina como se presenta la informacion.",
    ),
    construir_entrada_diccionario(
        "formula",
        "Sustantivo",
        "Expresion o regla que calcula un resultado a partir de valores dados.",
        "Cada fila suma los valores de sus cuatro columnas para mostrar el total de fila.",
        "regla",
        "azar",
        "Automatiza el calculo en la tabla.",
    ),
    construir_entrada_diccionario(
        "funcion",
        "Sustantivo",
        "Tarea o capacidad especifica que realiza una parte de un programa o sistema.",
        "Cada boton cumple una funcion concreta: buscar, ordenar, calcular o guardar.",
        "operacion",
        "inactividad",
        "Define lo que hace cada control.",
    ),
    construir_entrada_diccionario(
        "futuro",
        "Sustantivo",
        "Tiempo que viene despues del presente y en el que se proyectan planes o metas.",
        "Guardar tu progreso hoy te permite retomarlo en el futuro sin empezar de cero.",
        "porvenir",
        "pasado",
        "Perspectiva temporal de planificacion.",
    ),
    construir_entrada_diccionario(
        "general",
        "Adjetivo",
        "Que abarca la totalidad o el conjunto de un grupo o calculo.",
        "El total general suma todos los resultados obtenidos en las ocho filas.",
        "global",
        "particular",
        "Resume el resultado completo.",
    ),
    construir_entrada_diccionario(
        "gestion",
        "Sustantivo",
        "Administracion y manejo ordenado de recursos, datos o tareas.",
        "La gestion clara de tus datos evita extravios y confusiones.",
        "administracion",
        "abandono",
        "Organiza el uso diario de la herramienta.",
    ),
    construir_entrada_diccionario(
        "guardar",
        "Verbo",
        "Conservar o registrar datos en memoria o archivo para usarlos despues.",
        "Guarda tu progreso con tu correo electronico cada vez que actualices tus datos.",
        "conservar",
        "descartar",
        "Accion esencial para no perder avances.",
    ),
    construir_entrada_diccionario(
        "guia",
        "Sustantivo",
        "Indicacion o orientacion practica que muestra como utilizar algo de forma sencilla.",
        "En la entrada inicial tienes una guia directa de como funciona la aplicacion.",
        "orientacion",
        "confusion",
        "Ayuda a entender el sistema al instante.",
    ),
    construir_entrada_diccionario(
        "herramienta",
        "Sustantivo",
        "Instrumento o recurso util creado para facilitar un trabajo o resolver una tarea.",
        "Cada modulo es una herramienta enfocada en un tipo de tarea.",
        "instrumento",
        "obstaculo",
        "Enfoque practico de la aplicacion.",
    ),
    construir_entrada_diccionario(
        "historial",
        "Sustantivo",
        "Conjunto de registros o estados guardados previamente en el sistema.",
        "Cargar por correo recupera el historial guardado para esa direccion.",
        "registro",
        "olvido",
        "Permite retomar trabajo anterior.",
    ),
    construir_entrada_diccionario(
        "horizonte",
        "Sustantivo",
        "Limite visual o meta hacia donde se proyecta un trabajo o avance.",
        "Trabajar por etapas claras amplía el horizonte de lo que puedes construir.",
        "meta",
        "limite",
        "Representa proyeccion y alcance.",
    ),
    construir_entrada_diccionario(
        "identidad",
        "Sustantivo",
        "Conjunto de rasgos o datos que distinguen y permiten reconocer a alguien o algo.",
        "Tu correo electronico identifica tu espacio de progreso guardado.",
        "caracteristica",
        "anonimato",
        "Asocia el progreso a un usuario.",
    ),
    construir_entrada_diccionario(
        "idioma",
        "Sustantivo",
        "Sistema de comunicacion verbal o escrito propio de una comunidad o pueblo.",
        "El diccionario permite consultar y ampliar palabras en espanol con definiciones claras.",
        "lengua",
        "silencio",
        "Medio de expresion y comprension.",
    ),
    construir_entrada_diccionario(
        "indice",
        "Sustantivo",
        "Lista ordenada o indicador que senala la ubicacion de elementos o posiciones.",
        "Cada fila de la hoja de calculo tiene su numero de indice del 1 al 8.",
        "indicador",
        "desorden",
        "Facilita ubicar cada fila.",
    ),
    construir_entrada_diccionario(
        "informacion",
        "Sustantivo",
        "Conjunto de datos organizados que comunican un hecho, concepto o noticia.",
        "Las noticias diarias entregan informacion actualizada en cada jornada.",
        "dato",
        "desconocimiento",
        "Sustancia de consultas y registros.",
    ),
    construir_entrada_diccionario(
        "inicio",
        "Sustantivo",
        "Comienzo o punto de partida de un proceso, sesion o recorrido.",
        "El inicio valida tu clave y te lleva a la pantalla de entrada con correo y guia.",
        "comienzo",
        "fin",
        "Primera fase al abrir la aplicacion.",
    ),
    construir_entrada_diccionario(
        "interfaz",
        "Sustantivo",
        "Parte visible con la que interactua el usuario para manejar botones, campos y vistas.",
        "La interfaz organiza los modulos de izquierda a derecha para tocar y avanzar.",
        "vista",
        "nucleo",
        "Puente visual entre el usuario y el codigo.",
    ),
    construir_entrada_diccionario(
        "leer",
        "Verbo",
        "Comprender el significado de palabras o cifras escritas.",
        "Lee con calma cada definicion y ejemplo para asimilar mejor el termino.",
        "comprender",
        "ignorar",
        "Base de consulta textual.",
    ),
    construir_entrada_diccionario(
        "lenguaje",
        "Sustantivo",
        "Capacidad humana de expresar pensamientos y sentimientos mediante palabras o signos.",
        "El lenguaje claro evita malentendidos tanto en textos como en instrucciones.",
        "expresion",
        "mudez",
        "Presente en toda comunicacion.",
    ),
    construir_entrada_diccionario(
        "limpiar",
        "Verbo",
        "Quitar impurezas, espacios sobrantes o errores de un texto o conjunto de datos.",
        "Limpiar los espacios en blanco ayuda a ordenar mejor cada linea.",
        "depurar",
        "ensuciar",
        "Mejora la calidad de los datos.",
    ),
    construir_entrada_diccionario(
        "linea",
        "Sustantivo",
        "Sucesion continua de puntos o trazo que delimita, separa o agrupa elementos.",
        "Cada linea en el area de archivos representa un registro independiente.",
        "renglon",
        "punto",
        "Unidad de texto en listas.",
    ),
    construir_entrada_diccionario(
        "logica",
        "Sustantivo",
        "Principio o coherencia interna que hace que un razonamiento o regla tenga sentido.",
        "La logica de navegacion muestra un modulo a la vez desde la barra superior.",
        "coherencia",
        "contradiccion",
        "Sustenta el orden de funcionamiento.",
    ),
    construir_entrada_diccionario(
        "manual",
        "Adjetivo",
        "Que se ejecuta o maneja con las manos o mediante instruccion directa.",
        "Puedes editar cualquier celda de forma manual antes de calcular los totales.",
        "directo",
        "automatico",
        "Contrasta con el calculo automatico de totales.",
    ),
    construir_entrada_diccionario(
        "memoria",
        "Sustantivo",
        "Capacidad de retener y recordar informacion o de conservar datos en un sistema.",
        "El archivo JSON guarda en disco los datos y palabras agregadas.",
        "recuerdo",
        "olvido",
        "Permite conservar informacion entre sesiones.",
    ),
    construir_entrada_diccionario(
        "metodo",
        "Sustantivo",
        "Modo ordenado y sistematico de hacer algo para conseguir un fin.",
        "Tener un metodo para guardar y ordenar evita perder tiempo buscando datos.",
        "procedimiento",
        "azar",
        "Organiza la forma de trabajar.",
    ),
    construir_entrada_diccionario(
        "modulo",
        "Sustantivo",
        "Cada una de las partes o secciones independientes que forman una aplicacion.",
        "C-Pre 2 separa sus funciones en cinco modulos accesibles de izquierda a derecha.",
        "seccion",
        "bloque",
        "Facilita el uso enfocado sin saturar.",
    ),
    construir_entrada_diccionario(
        "mundo",
        "Sustantivo",
        "Conjunto de todo lo existente o el planeta Tierra y la vida que alberga.",
        "El diccionario busca reunir palabras utiles de distintos ambitos del mundo.",
        "universo",
        "nada",
        "Termino amplio y universal.",
    ),
    construir_entrada_diccionario(
        "navegar",
        "Verbo",
        "Desplazarse o moverse por distintas secciones o vistas de una aplicacion.",
        "Toca cada boton de la barra superior para navegar entre modulos.",
        "recorrer",
        "estancarse",
        "Accion central de la interfaz.",
    ),
    construir_entrada_diccionario(
        "noticia",
        "Sustantivo",
        "Informacion o aviso relevante que se actualiza periodicamente.",
        "La seccion diaria presenta una noticia distinta segun el dia del ano.",
        "aviso",
        "rumor",
        "Parte del bloque diario de novedades.",
    ),
    construir_entrada_diccionario(
        "numero",
        "Sustantivo",
        "Signo o conjunto de signos que expresa cantidad, medida o posicion en una serie.",
        "Los numeros escritos en la hoja de calculo se suman fila por fila.",
        "cifra",
        "letra",
        "Base de los calculos en la tabla.",
    ),
    construir_entrada_diccionario(
        "objetivo",
        "Sustantivo",
        "Meta o proposito que se pretende alcanzar mediante una accion o proyecto.",
        "El objetivo es tener una herramienta clara, completa y sin perdida de datos.",
        "meta",
        "desproposito",
        "Orienta el uso del sistema.",
    ),
    construir_entrada_diccionario(
        "operacion",
        "Sustantivo",
        "Ejecucion de un calculo, accion o proceso sobre uno o mas valores.",
        "Cada fila ejecuta una operacion de suma sobre sus cuatro columnas.",
        "calculo",
        "pausa",
        "Accion matematica o logica.",
    ),
    construir_entrada_diccionario(
        "orden",
        "Sustantivo",
        "Colocacion o disposicion organizada de cosas o datos segun un criterio.",
        "Ordenar tus registros facilita localizar cualquier elemento rapidamente.",
        "organizacion",
        "desorden",
        "Principio clave en datos y menus.",
    ),
    construir_entrada_diccionario(
        "palabra",
        "Sustantivo",
        "Unidad del lenguaje formada por letras o sonidos que transmite un significado.",
        "Busca cualquier palabra en el diccionario para ver su definicion y ejemplo.",
        "termino",
        "silencio",
        "Elemento central del diccionario.",
    ),
    construir_entrada_diccionario(
        "panel",
        "Sustantivo",
        "Superficie o recuadro donde se agrupan controles e informacion de un modulo.",
        "Cada seccion se muestra en un panel claro y facil de leer.",
        "tablero",
        "borde",
        "Contenedor visual de cada funcion.",
    ),
    construir_entrada_diccionario(
        "pasado",
        "Sustantivo",
        "Tiempo que ya transcurrio o conjunto de hechos anteriores al momento presente.",
        "Lo que guardaste en sesiones pasadas se recupera al cargar tu correo.",
        "ayer",
        "futuro",
        "Referencia temporal de datos previos.",
    ),
    construir_entrada_diccionario(
        "practica",
        "Sustantivo",
        "Ejercicio continuo y aplicacion real de un conocimiento o herramienta.",
        "Usar la hoja de calculo y el diccionario en la practica fija su manejo.",
        "ejercicio",
        "teoria",
        "Refuerza el aprendizaje activo.",
    ),
    construir_entrada_diccionario(
        "precision",
        "Sustantivo",
        "Exactitud y cuidado al realizar una medicion, calculo o definicion.",
        "Definiciones precisas evitan confusiones al consultar terminos.",
        "exactitud",
        "imprecision",
        "Cualidad deseable en datos y textos.",
    ),
    construir_entrada_diccionario(
        "progreso",
        "Sustantivo",
        "Avance o mejoria gradual en una tarea, estudio o proyecto.",
        "Vincular tu correo permite conservar tu progreso en el servidor.",
        "avance",
        "estancamiento",
        "Seguimiento continuo del trabajo.",
    ),
    construir_entrada_diccionario(
        "proyecto",
        "Sustantivo",
        "Conjunto organizado de ideas y acciones para construir o desarrollar algo.",
        "C-Pre 2 forma parte de tu serie de proyectos de aplicaciones.",
        "plan",
        "improvisacion",
        "Marco de desarrollo de la app.",
    ),
    construir_entrada_diccionario(
        "registro",
        "Sustantivo",
        "Anotacion o conjunto de datos guardados de forma estructurada.",
        "Cada linea del bloque de archivos funciona como un registro.",
        "anotacion",
        "olvido",
        "Unidad de informacion guardada.",
    ),
    construir_entrada_diccionario(
        "respaldo",
        "Sustantivo",
        "Copia o resguardo de informacion para evitar perderla ante cualquier cierre o cambio.",
        "Guardar por correo funciona como respaldo de tu progreso.",
        "copia",
        "perdida",
        "Protege el trabajo realizado.",
    ),
    construir_entrada_diccionario(
        "resultado",
        "Sustantivo",
        "Efecto o cifra final obtenida tras realizar un calculo o proceso.",
        "El resultado de cada fila aparece en su columna de total.",
        "consecuencia",
        "causa",
        "Salida visible de una operacion.",
    ),
    construir_entrada_diccionario(
        "rutina",
        "Sustantivo",
        "Costumbre o practica que se realiza de forma habitual y ordenada.",
        "Revisar noticias, diccionario y registros cada dia forma una buena rutina.",
        "habito",
        "excepcion",
        "Favorece la constancia diaria.",
    ),
    construir_entrada_diccionario(
        "sesion",
        "Sustantivo",
        "Periodo de tiempo en el que se utiliza una aplicacion desde que se entra hasta que se sale.",
        "Al iniciar sesion con tu correo puedes cargar lo que dejaste pendiente.",
        "jornada",
        "interrupcion",
        "Lapso activo de uso de la app.",
    ),
    construir_entrada_diccionario(
        "sistema",
        "Sustantivo",
        "Conjunto ordenado de partes o reglas interrelacionadas que cumplen una funcion.",
        "El sistema valida la clave, gestiona la entrada y guarda el progreso.",
        "estructura",
        "aislamiento",
        "Conjunto integrado de funciones.",
    ),
    construir_entrada_diccionario(
        "tabla",
        "Sustantivo",
        "Disposicion de datos en filas y columnas para facilitar su lectura y calculo.",
        "La tabla de la hoja de calculo tiene ocho filas y cuatro columnas de entrada.",
        "cuadricula",
        "texto",
        "Formato ideal para cifras ordenadas.",
    ),
    construir_entrada_diccionario(
        "termino",
        "Sustantivo",
        "Palabra o expresion que designa un concepto o elemento dentro de un tema.",
        "Cada entrada del diccionario explica un termino con claridad.",
        "palabra",
        "frase",
        "Sinonimo habitual en diccionarios.",
    ),
    construir_entrada_diccionario(
        "tiempo",
        "Sustantivo",
        "Magnitud en la que se suceden los hechos y que marca la rotacion diaria de contenidos.",
        "Con el paso de cada dia cambian las noticias y videos mostrados.",
        "duracion",
        "eternidad",
        "Factor que actualiza los contenidos diarios.",
    ),
    construir_entrada_diccionario(
        "total",
        "Sustantivo",
        "Cantidad o suma resultante de reunir todas las partes de un conjunto.",
        "Se muestra tanto el total por fila como el total general de toda la hoja.",
        "suma",
        "parte",
        "Resumen numerico final.",
    ),
    construir_entrada_diccionario(
        "trabajo",
        "Sustantivo",
        "Actividad o esfuerzo aplicado para crear, organizar o completar algo.",
        "Guardar tu correo protege todo el trabajo hecho en la hoja y en tus archivos.",
        "esfuerzo",
        "descanso",
        "Resultado de dedicar tiempo y orden.",
    ),
    construir_entrada_diccionario(
        "validar",
        "Verbo",
        "Comprobar que un dato o clave cumple con las condiciones establecidas.",
        "Se valida la clave de acceso y el formato del correo electronico.",
        "confirmar",
        "rechazar",
        "Evita entradas incorrectas.",
    ),
    construir_entrada_diccionario(
        "valor",
        "Sustantivo",
        "Importe, cifra o cualidad asignada a un elemento o celda.",
        "Ingresa valores numericos en las celdas para sumar cada fila.",
        "cifra",
        "nulo",
        "Dato numerico o conceptual.",
    ),
    construir_entrada_diccionario(
        "verdad",
        "Sustantivo",
        "Conformidad de lo que se dice o calcula con lo que es real y exacto.",
        "La verificacion directa de los datos da certeza sobre el resultado.",
        "certeza",
        "error",
        "Valor fundamental en cualquier consulta.",
    ),
    construir_entrada_diccionario(
        "vida",
        "Sustantivo",
        "Existencia y actividad continua de los seres vivos.",
        "La vida cotidiana combina aprendizaje, trabajo y crecimiento constante.",
        "existencia",
        "inexistencia",
        "Sustantivo esencial del vocabulario.",
    ),
    construir_entrada_diccionario(
        "video",
        "Sustantivo",
        "Secuencia audiovisual o guia tematica presentada en la seccion diaria.",
        "Cada dia aparece un video recomendado distinto con su tema y descripcion.",
        "grabacion",
        "texto",
        "Complementa las noticias diarias.",
    ),
]


def construir_mapa_diccionario():
    mapa = {}
    for item in ENTRADAS_DICCIONARIO_BASE:
        clave = normalizar_clave_py(item["termino"])
        mapa[clave] = item
    return mapa


def normalizar_clave_py(texto):
    limpio = (texto or "").strip().lower()
    reemplazos = {
        "á": "a",
        "é": "e",
        "í": "i",
        "ó": "o",
        "ú": "u",
        "ü": "u",
        "ñ": "n",
    }
    for orig, dest in reemplazos.items():
        limpio = limpio.replace(orig, dest)
    limpio = re.sub(r"\s+", " ", limpio)
    return limpio


DICCIONARIO_BASE = construir_mapa_diccionario()

NOTICIAS_DIARIAS = [
    "Noticia del dia: Guarda tu progreso con tu correo electronico para conservar tu hoja de calculo, diccionario y registros.",
    "Noticia del dia: La hoja de calculo ampliada permite trabajar 8 filas y 4 columnas con totales por fila y total general.",
    "Noticia del dia: Si buscas una palabra que aun no figura en el diccionario, puedes agregar su definicion al instante.",
    "Noticia del dia: Ordena tus listas de forma ascendente o descendente antes de exportarlas como archivo.",
    "Noticia del dia: Navega de izquierda a derecha entre modulos para mantener cada tarea enfocada.",
    "Noticia del dia: Revisar tus datos y respaldarlos por correo evita perder avances entre sesiones.",
    "Noticia del dia: Cada dia se actualizan las noticias y videos recomendados dentro de C-Pre 2.",
    "Noticia del dia: Usa el ordenamiento numerico o alfabetico segun lo que contenga tu lista de registros.",
    "Noticia del dia: Mantener la estructura limpia facilita encontrar informacion sin perder tiempo.",
    "Noticia del dia: Un buen respaldo de progreso te permite retomar tu trabajo desde cualquier momento.",
]

VIDEOS_DIARIOS = [
    {
        "titulo": "Guia 1: Hoja de calculo de 8 filas x 4 columnas",
        "detalle": "Escribe cifras en las columnas A, B, C y D y pulsa calcular para ver el total de cada fila y el total general.",
    },
    {
        "titulo": "Guia 2: Guardar y cargar progreso por correo",
        "detalle": "Ingresa tu correo en la pantalla de entrada o en el modulo Correo para guardar y recuperar tu sesion.",
    },
    {
        "titulo": "Guia 3: Diccionario y nuevas definiciones",
        "detalle": "Consulta palabras y ejemplos; si falta algun termino, anade su definicion para enriquecer el diccionario.",
    },
    {
        "titulo": "Guia 4: Ordenamiento y exportacion de archivos",
        "detalle": "Ordena lineas en sentido ascendente o descendente y descarga el archivo con el nombre que elijas.",
    },
    {
        "titulo": "Guia 5: Navegacion modular de izquierda a derecha",
        "detalle": "Cambia de modulo tocando cada pestana superior sin amontonar todo en una sola columna vertical.",
    },
    {
        "titulo": "Guia 6: Buenas practicas al registrar datos",
        "detalle": "Revisa numeros, textos y nombres de archivo antes de guardar o exportar para evitar confusiones.",
    },
    {
        "titulo": "Guia 7: Rutina diaria con noticias y videos",
        "detalle": "Consulta cada dia las novedades del panel diario y mantente al dia con tus registros.",
    },
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


def obtener_diccionario_combinado():
    db = cargar_db()
    combinado = dict(DICCIONARIO_BASE)
    extras = db.get("diccionario_extra", {})
    if isinstance(extras, dict):
        for clave, entrada in extras.items():
            c_norm = normalizar_clave_py(clave)
            if isinstance(entrada, dict):
                combinado[c_norm] = {
                    "termino": entrada.get("termino") or clave,
                    "categoria": entrada.get("categoria") or "Personalizada",
                    "definicion": entrada.get("definicion") or "",
                    "ejemplo": entrada.get("ejemplo") or "",
                    "sinonimo": entrada.get("sinonimo") or "",
                    "antonimo": entrada.get("antonimo") or "",
                    "nota_uso": entrada.get("nota_uso") or "",
                }
            elif isinstance(entrada, str):
                combinado[c_norm] = construir_entrada_diccionario(
                    clave,
                    "Personalizada",
                    entrada,
                    f"Ejemplo de uso con '{clave}'.",
                )
    return combinado


def validar_correo_simple(correo):
    limpio = (correo or "").strip().lower()
    if not limpio or "@" not in limpio or "." not in limpio.split("@")[-1]:
        return ""
    return limpio


def normalizar_tabla_progreso(tabla):
    resultado = []
    if not isinstance(tabla, list):
        tabla = []
    for idx_f in range(MAX_FILAS_HOJA):
        fila_orig = tabla[idx_f] if idx_f < len(tabla) and isinstance(tabla[idx_f], list) else []
        fila_limpia = []
        for idx_c in range(MAX_COLS_HOJA):
            val = fila_orig[idx_c] if idx_c < len(fila_orig) else ""
            fila_limpia.append(str(val if val is not None else ""))
        resultado.append(fila_limpia)
    return resultado


HTML_PAGE = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>C-PRE 2</title>
<style>
* {
  box-sizing: border-box;
}
html, body {
  margin: 0;
  padding: 0;
  background: #140507;
  color: #fff5f5;
  font-family: system-ui, -apple-system, Arial, sans-serif;
  font-size: 16px;
}
body {
  padding-bottom: 64px;
}
header {
  background: #2a060b;
  border-bottom: 2px solid #991b1b;
  padding: 14px 14px 10px;
  position: sticky;
  top: 0;
  z-index: 30;
}
.top-head {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 10px;
}
header h1 {
  margin: 0;
  font-size: 21px;
  font-weight: 900;
  letter-spacing: 0.6px;
  color: #ffffff;
}
header .fecha-sub {
  font-size: 12.5px;
  color: #fca5a5;
  margin-top: 3px;
}
.correo-badge {
  font-size: 12.5px;
  font-weight: 700;
  color: #fee2e2;
  background: #140507;
  border: 1px solid #991b1b;
  padding: 5px 10px;
  border-radius: 999px;
  max-width: 52%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.nav-h {
  display: flex;
  gap: 8px;
  overflow-x: auto;
  padding: 10px 0 4px;
  -webkit-overflow-scrolling: touch;
}
.nav-btn {
  flex: 0 0 auto;
  width: auto;
  margin: 0;
  padding: 9px 14px;
  font-size: 13.5px;
  font-weight: 800;
  border-radius: 999px;
  background: #22070b;
  color: #fecaca;
  border: 1px solid #991b1b;
  cursor: pointer;
}
.nav-btn.activo {
  background: #ef4444;
  color: #ffffff;
  border-color: #fca5a5;
}
.wrap {
  max-width: 960px;
  margin: 0 auto;
  padding: 14px;
}
.card {
  background: #22070b;
  border: 1px solid #7f1d1d;
  border-radius: 10px;
  padding: 16px;
  margin-bottom: 14px;
}
h2 {
  margin: 0 0 10px;
  font-size: 19px;
  color: #fecaca;
}
h3 {
  margin: 12px 0 6px;
  font-size: 16px;
  color: #fecaca;
}
label {
  display: block;
  font-size: 14px;
  font-weight: 700;
  color: #fee2e2;
  margin-top: 10px;
}
input[type="text"],
input[type="password"],
input[type="email"],
textarea,
select {
  width: 100%;
  padding: 12px 13px;
  font-size: 15.5px;
  border-radius: 8px;
  border: 1px solid #991b1b;
  background: #120305;
  color: #ffffff;
  margin-top: 6px;
}
textarea {
  min-height: 130px;
  font-family: monospace;
  line-height: 1.45;
}
button {
  width: 100%;
  padding: 12px 14px;
  font-size: 15px;
  font-weight: 800;
  border-radius: 8px;
  border: none;
  background: #dc2626;
  color: #ffffff;
  cursor: pointer;
  margin-top: 9px;
}
button:hover {
  background: #ef4444;
}
button.sec {
  background: #3b0a11;
  color: #fecaca;
  border: 1px solid #991b1b;
}
.row-2 {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 8px;
}
.box {
  background: #120305;
  border-left: 4px solid #ef4444;
  border-radius: 0 8px 8px 0;
  padding: 12px 13px;
  margin-top: 10px;
  font-size: 14.5px;
  line-height: 1.5;
  white-space: pre-line;
  color: #fff5f5;
}
.guia-pasos {
  background: #120305;
  border: 1px solid #7f1d1d;
  border-radius: 8px;
  padding: 12px 14px;
  margin-top: 8px;
  font-size: 14px;
  line-height: 1.55;
  color: #ffe4e6;
}
.guia-pasos div {
  margin: 5px 0;
}
.hoja-scroll {
  width: 100%;
  overflow-x: auto;
  margin-top: 10px;
  -webkit-overflow-scrolling: touch;
}
table.hoja-grande {
  width: 100%;
  min-width: 660px;
  border-collapse: collapse;
}
table.hoja-grande th,
table.hoja-grande td {
  border: 1px solid #991b1b;
  padding: 8px;
  text-align: center;
}
table.hoja-grande th {
  background: #33080f;
  font-size: 14px;
  color: #fecaca;
  padding: 11px 8px;
}
table.hoja-grande td input {
  width: 100%;
  min-width: 102px;
  height: 48px;
  margin: 0;
  padding: 8px 10px;
  font-size: 16px;
  font-weight: 600;
  background: #120305;
  color: #ffffff;
  border: 1px solid #7f1d1d;
  border-radius: 6px;
}
.cel-fila-tot {
  font-weight: 900;
  font-size: 15.5px;
  color: #ffffff;
  background: #24060b;
  min-width: 92px;
}
.resumen-cols {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 8px;
  margin-top: 10px;
}
.mini-stat {
  background: #120305;
  border: 1px solid #7f1d1d;
  border-radius: 8px;
  padding: 9px 8px;
  text-align: center;
}
.mini-stat span {
  display: block;
  font-size: 11.5px;
  color: #fca5a5;
}
.mini-stat strong {
  display: block;
  font-size: 15px;
  color: #ffffff;
  margin-top: 3px;
}
.estado-msg {
  font-size: 13.5px;
  color: #fca5a5;
  margin-top: 8px;
  line-height: 1.4;
}
.pantalla-fija {
  position: fixed;
  inset: 0;
  background: #140507;
  z-index: 100;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 16px;
  overflow-y: auto;
}
.oculto {
  display: none !important;
}
</style>
</head>
<body>

<div id="pantallaClave" class="pantalla-fija">
  <div class="card" style="max-width:430px;width:100%;">
    <h2>Clave de Acceso</h2>
    <p style="margin:6px 0 10px;font-size:14px;color:#fca5a5;">Ingresa tu clave de acceso para continuar a C-Pre 2.</p>
    <label for="inpClave">Clave:</label>
    <input type="password" id="inpClave" placeholder="Escribe la clave de acceso...">
    <button type="button" onclick="verificarClave()">ENTRAR</button>
    <div id="msgClave" class="estado-msg"></div>
  </div>
</div>

<div id="pantallaEntrada" class="pantalla-fija oculto">
  <div class="card" style="max-width:560px;width:100%;">
    <h2>Bienvenido a C-Pre 2</h2>
    <div class="guia-pasos">
      <div><strong>Como funciona la aplicacion:</strong></div>
      <div>1. Escribe tu <strong>correo electronico</strong> para guardar y recuperar tu progreso sin perder datos.</div>
      <div>2. Al pulsar <strong>ACEPTAR</strong> entraras a los modulos y podras moverte de izquierda a derecha en la barra superior.</div>
      <div>3. <strong>Diccionario:</strong> consulta definiciones y ejemplos o agrega palabras nuevas.</div>
      <div>4. <strong>Noticias y Videos:</strong> revisa la actualizacion diaria de noticias y videos.</div>
      <div>5. <strong>Archivos y Orden:</strong> ordena tus registros de forma ascendente o descendente y descargalos.</div>
      <div>6. <strong>Hoja de Calculo:</strong> trabaja en la tabla amplia de 8 filas por 4 columnas con calculo automatico.</div>
    </div>
    <label for="inpCorreoEntrada">Correo electronico:</label>
    <input type="email" id="inpCorreoEntrada" placeholder="tu_correo@ejemplo.com">
    <button type="button" onclick="aceptarEntrada()">ACEPTAR</button>
    <div id="msgEntrada" class="estado-msg"></div>
  </div>
</div>

<header id="cabeceraApp" class="oculto">
  <div class="top-head">
    <div>
      <h1>C-PRE 2</h1>
      <div class="fecha-sub" id="lblFechaSub"></div>
    </div>
    <div class="correo-badge" id="lblCorreoActivo">Sin correo</div>
  </div>
  <nav class="nav-h" aria-label="Modulos de izquierda a derecha">
    <button type="button" class="nav-btn activo" data-sec="secCorreo" onclick="irModulo('secCorreo', this)">1. Correo y Progreso</button>
    <button type="button" class="nav-btn" data-sec="secDiccionario" onclick="irModulo('secDiccionario', this)">2. Diccionario</button>
    <button type="button" class="nav-btn" data-sec="secDiarios" onclick="irModulo('secDiarios', this)">3. Noticias y Videos</button>
    <button type="button" class="nav-btn" data-sec="secArchivos" onclick="irModulo('secArchivos', this)">4. Archivos y Orden</button>
    <button type="button" class="nav-btn" data-sec="secHoja" onclick="irModulo('secHoja', this)">5. Hoja de Calculo</button>
  </nav>
</header>

<main id="contenedorModulos" class="wrap oculto">
  <section id="secCorreo" class="card modulo-panel">
    <h2>Correo Electronico y Progreso</h2>
    <p style="margin:0 0 8px;font-size:14px;color:#fca5a5;">Guarda o carga el estado de tu diccionario actual, registros de archivo y hoja de calculo vinculado a tu correo.</p>
    <label for="inpCorreo">Correo electronico:</label>
    <input type="email" id="inpCorreo" placeholder="tu_correo@ejemplo.com">
    <div class="row-2">
      <button type="button" onclick="cargarProgreso()">CARGAR PROGRESO</button>
      <button type="button" class="sec" onclick="guardarProgreso()">GUARDAR PROGRESO</button>
    </div>
    <div id="msgProgreso" class="estado-msg">Listo para guardar o cargar tu progreso.</div>
  </section>

  <section id="secDiccionario" class="card modulo-panel oculto">
    <h2>Diccionario</h2>
    <label for="inpPalabra">Palabra a buscar:</label>
    <input type="text" id="inpPalabra" placeholder="Escribe una palabra...">
    <button type="button" onclick="buscarPalabra()">BUSCAR EN DICCIONARIO</button>
    <div id="resDiccionario" class="box">Escribe una palabra para consultar su definicion, categoria y ejemplo.</div>

    <div id="bloqueNuevaPalabra" class="oculto" style="margin-top:12px;">
      <h3>Agregar palabra al diccionario</h3>
      <label for="inpCatNueva">Categoria:</label>
      <input type="text" id="inpCatNueva" value="Sustantivo">
      <label for="inpDefNueva">Definicion:</label>
      <input type="text" id="inpDefNueva" placeholder="Escribe la definicion de la palabra...">
      <label for="inpEjNueva">Ejemplo de uso:</label>
      <input type="text" id="inpEjNueva" placeholder="Escribe un ejemplo en oracion...">
      <button type="button" class="sec" onclick="agregarPalabra()">GUARDAR PALABRA</button>
    </div>
  </section>

  <section id="secDiarios" class="card modulo-panel oculto">
    <h2>Noticias y Videos (Actualizacion Diaria)</h2>
    <div id="boxNoticia" class="box"></div>
    <div id="boxVideo" class="box"></div>
  </section>

  <section id="secArchivos" class="card modulo-panel oculto">
    <h2>Archivos y Ordenamiento</h2>
    <label for="inpNombreArchivo">Nombre del archivo:</label>
    <input type="text" id="inpNombreArchivo" value="registros_cpre2.txt">
    <label for="txtDatos">Registros o lineas (uno por linea):</label>
    <textarea id="txtDatos" placeholder="Escribe tus registros o numeros, uno por linea..."></textarea>
    <div class="row-2">
      <button type="button" onclick="ordenarDatos('asc')">ORDENAR ASCENDENTE</button>
      <button type="button" class="sec" onclick="ordenarDatos('desc')">ORDENAR DESCENDENTE</button>
    </div>
    <button type="button" class="sec" onclick="exportarArchivo()">DESCARGAR ARCHIVO</button>
    <div id="msgArchivo" class="estado-msg"></div>
  </section>

  <section id="secHoja" class="card modulo-panel oculto">
    <h2>Hoja de Calculo (8 Filas x 4 Columnas)</h2>
    <div class="hoja-scroll">
      <table class="hoja-grande">
        <thead>
          <tr>
            <th>Fila</th>
            <th>Col A</th>
            <th>Col B</th>
            <th>Col C</th>
            <th>Col D</th>
            <th>Total Fila</th>
          </tr>
        </thead>
        <tbody id="tablaCuerpo"></tbody>
      </table>
    </div>
    <div class="resumen-cols">
      <div class="mini-stat"><span>Total Col A</span><strong id="totColA">0</strong></div>
      <div class="mini-stat"><span>Total Col B</span><strong id="totColB">0</strong></div>
      <div class="mini-stat"><span>Total Col C</span><strong id="totColC">0</strong></div>
      <div class="mini-stat"><span>Total Col D</span><strong id="totColD">0</strong></div>
    </div>
    <button type="button" onclick="recalcularTabla()">CALCULAR FILAS Y COLUMNAS</button>
    <div id="resTabla" class="box">Total general: 0</div>
  </section>
</main>

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
    .replace(/[\\u0300-\\u036f]/g, "")
    .replace(/\\s+/g, " ");
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
      document.getElementById("pantallaEntrada").classList.remove("oculto");
    } else {
      msg.textContent = "Clave incorrecta. Verifica e intenta de nuevo.";
    }
  } catch (e) {
    msg.textContent = "Error al validar la clave.";
  }
}

async function aceptarEntrada() {
  const correo = document.getElementById("inpCorreoEntrada").value.trim().toLowerCase();
  const msg = document.getElementById("msgEntrada");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Ingresa un correo electronico valido antes de pulsar ACEPTAR.";
    return;
  }
  document.getElementById("inpCorreo").value = correo;
  document.getElementById("lblCorreoActivo").textContent = correo;
  document.getElementById("pantallaEntrada").classList.add("oculto");
  document.getElementById("cabeceraApp").classList.remove("oculto");
  document.getElementById("contenedorModulos").classList.remove("oculto");
  await cargarProgreso();
}

function irModulo(idSeccion, boton) {
  document.querySelectorAll(".modulo-panel").forEach(sec => sec.classList.add("oculto"));
  const destino = document.getElementById(idSeccion);
  if (destino) destino.classList.remove("oculto");
  document.querySelectorAll(".nav-btn").forEach(b => b.classList.remove("activo"));
  if (boton) boton.classList.add("activo");
}

function cargarDiarios() {
  const hoy = new Date();
  document.getElementById("lblFechaSub").textContent = "Fecha: " + hoy.toLocaleDateString("es-VE");
  const inicio = new Date(hoy.getFullYear(), 0, 0);
  const diaAno = Math.floor((hoy - inicio) / 86400000);

  document.getElementById("boxNoticia").textContent = NOTICIAS[diaAno % NOTICIAS.length];
  const vid = VIDEOS[diaAno % VIDEOS.length];
  document.getElementById("boxVideo").textContent = vid.titulo + "\\n" + vid.detalle;
}

function escaparAtributo(valor) {
  return String(valor || "")
    .replace(/&/g, "&amp;")
    .replace(/"/g, "&quot;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");
}

function montarTabla(filas) {
  const tbody = document.getElementById("tablaCuerpo");
  tbody.innerHTML = "";
  for (let i = 0; i < 8; i++) {
    const f = (filas && filas[i]) ? filas[i] : ["", "", "", ""];
    const tr = document.createElement("tr");
    tr.innerHTML =
      `<td><strong>${i + 1}</strong></td>` +
      `<td><input type="text" class="c-a" value="${escaparAtributo(f[0])}"></td>` +
      `<td><input type="text" class="c-b" value="${escaparAtributo(f[1])}"></td>` +
      `<td><input type="text" class="c-c" value="${escaparAtributo(f[2])}"></td>` +
      `<td><input type="text" class="c-d" value="${escaparAtributo(f[3])}"></td>` +
      `<td class="cel-fila-tot">0</td>`;
    tbody.appendChild(tr);
  }
  recalcularTabla();
}

function leerNumeroCelda(inputEl) {
  if (!inputEl) return 0;
  const limpio = String(inputEl.value || "").trim().replace(",", ".");
  const n = parseFloat(limpio);
  return isNaN(n) ? 0 : n;
}

function recalcularTabla() {
  let sumA = 0;
  let sumB = 0;
  let sumC = 0;
  let sumD = 0;
  let totalGeneral = 0;

  document.querySelectorAll("#tablaCuerpo tr").forEach(tr => {
    const a = leerNumeroCelda(tr.querySelector(".c-a"));
    const b = leerNumeroCelda(tr.querySelector(".c-b"));
    const c = leerNumeroCelda(tr.querySelector(".c-c"));
    const d = leerNumeroCelda(tr.querySelector(".c-d"));
    const sumaFila = a + b + c + d;

    sumA += a;
    sumB += b;
    sumC += c;
    sumD += d;
    totalGeneral += sumaFila;

    tr.querySelector(".cel-fila-tot").textContent = sumaFila;
  });

  document.getElementById("totColA").textContent = sumA;
  document.getElementById("totColB").textContent = sumB;
  document.getElementById("totColC").textContent = sumC;
  document.getElementById("totColD").textContent = sumD;
  document.getElementById("resTabla").textContent = "Total general: " + totalGeneral;
}

function leerTabla() {
  const filas = [];
  document.querySelectorAll("#tablaCuerpo tr").forEach(tr => {
    filas.push([
      tr.querySelector(".c-a").value,
      tr.querySelector(".c-b").value,
      tr.querySelector(".c-c").value,
      tr.querySelector(".c-d").value
    ]);
  });
  return filas;
}

function formatearEntradaDiccionario(entry) {
  if (!entry) return "";
  if (typeof entry === "string") return entry;
  let texto = `${entry.termino} (${entry.categoria})\\nDefinicion: ${entry.definicion}`;
  if (entry.ejemplo) texto += `\\nEjemplo: ${entry.ejemplo}`;
  if (entry.sinonimo) texto += `\\nSinonimo: ${entry.sinonimo}`;
  if (entry.antonimo) texto += `\\nAntonimo: ${entry.antonimo}`;
  return texto;
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
    box.textContent = formatearEntradaDiccionario(DICCIONARIO[clave]);
    bloqueNueva.classList.add("oculto");
  } else {
    box.textContent = `La palabra "${raw}" no esta en el diccionario todavia. Puedes agregarla abajo.`;
    bloqueNueva.classList.remove("oculto");
  }
}

async function agregarPalabra() {
  const raw = document.getElementById("inpPalabra").value.trim();
  const cat = document.getElementById("inpCatNueva").value.trim() || "Sustantivo";
  const def = document.getElementById("inpDefNueva").value.trim();
  const ej = document.getElementById("inpEjNueva").value.trim();
  if (!raw || !def) return;

  const clave = normalizar(raw);
  const nuevaEntrada = {
    termino: raw,
    categoria: cat,
    definicion: def,
    ejemplo: ej,
    sinonimo: "",
    antonimo: "",
    nota_uso: ""
  };
  DICCIONARIO[clave] = nuevaEntrada;
  document.getElementById("resDiccionario").textContent = formatearEntradaDiccionario(nuevaEntrada);
  document.getElementById("bloqueNuevaPalabra").classList.add("oculto");
  document.getElementById("inpDefNueva").value = "";
  document.getElementById("inpEjNueva").value = "";

  try {
    await fetch("/api/diccionario", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ palabra: clave, entrada: nuevaEntrada })
    });
  } catch (e) {}
}

function ordenarDatos(sentido) {
  const items = document.getElementById("txtDatos").value
    .split("\\n")
    .map(x => x.trim())
    .filter(x => x.length > 0);
  items.sort((a, b) => {
    const na = parseFloat(a.replace(",", "."));
    const nb = parseFloat(b.replace(",", "."));
    if (!isNaN(na) && !isNaN(nb)) {
      return sentido === "asc" ? na - nb : nb - na;
    }
    return sentido === "asc" ? a.localeCompare(b, "es") : b.localeCompare(a, "es");
  });
  document.getElementById("txtDatos").value = items.join("\\n");
  document.getElementById("msgArchivo").textContent =
    `Registros ordenados (${sentido === "asc" ? "ascendente" : "descendente"}): ${items.length} lineas.`;
}

function exportarArchivo() {
  const nombre = (document.getElementById("inpNombreArchivo").value || "registros_cpre2.txt").trim();
  const contenido = document.getElementById("txtDatos").value;
  const blob = new Blob([contenido], { type: "text/plain;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = nombre;
  a.click();
  URL.revokeObjectURL(url);
  document.getElementById("msgArchivo").textContent = `Archivo "${nombre}" listo para descargar.`;
}

async function guardarProgreso() {
  const correo = document.getElementById("inpCorreo").value.trim().toLowerCase();
  const msg = document.getElementById("msgProgreso");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo electronico valido.";
    return;
  }
  document.getElementById("lblCorreoActivo").textContent = correo;
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
    msg.textContent = d.mensaje || "Progreso guardado.";
  } catch (e) {
    msg.textContent = "Error al guardar el progreso.";
  }
}

async function cargarProgreso() {
  const correo = document.getElementById("inpCorreo").value.trim().toLowerCase();
  const msg = document.getElementById("msgProgreso");
  if (!correo || !correo.includes("@")) {
    msg.textContent = "Escribe un correo electronico valido.";
    return;
  }
  document.getElementById("lblCorreoActivo").textContent = correo;
  try {
    const r = await fetch("/api/progreso/cargar?correo=" + encodeURIComponent(correo));
    const d = await r.json();
    if (!d.encontrado) {
      msg.textContent = "No hay progreso previo para " + correo + ". Puedes guardar tus cambios actuales.";
      return;
    }
    const p = d.progreso || {};
    if (p.nombre_archivo) document.getElementById("inpNombreArchivo").value = p.nombre_archivo;
    if (typeof p.datos === "string") document.getElementById("txtDatos").value = p.datos;
    if (Array.isArray(p.tabla)) montarTabla(p.tabla);
    if (p.palabra) document.getElementById("inpPalabra").value = p.palabra;
    msg.textContent = "Progreso cargado para " + correo + ".";
  } catch (e) {
    msg.textContent = "Error al cargar el progreso.";
  }
}

document.getElementById("inpClave").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    verificarClave();
  }
});

document.getElementById("inpCorreoEntrada").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    aceptarEntrada();
  }
});

document.getElementById("inpPalabra").addEventListener("keydown", function(ev) {
  if (ev.key === "Enter") {
    ev.preventDefault();
    buscarPalabra();
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
    diccionario_total = obtener_diccionario_combinado()
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
    return jsonify({"ok": clave in CLAVES_VALIDAS})


@app.route("/api/diccionario", methods=["POST"])
def api_diccionario():
    datos = request.get_json(silent=True) or {}
    palabra = normalizar_clave_py(datos.get("palabra") or "")
    entrada = datos.get("entrada")
    definicion_texto = (datos.get("definicion") or "").strip()

    if palabra and isinstance(entrada, dict):
        db = cargar_db()
        db["diccionario_extra"][palabra] = {
            "termino": (entrada.get("termino") or palabra).strip(),
            "categoria": (entrada.get("categoria") or "Personalizada").strip(),
            "definicion": (entrada.get("definicion") or "").strip(),
            "ejemplo": (entrada.get("ejemplo") or "").strip(),
            "sinonimo": (entrada.get("sinonimo") or "").strip(),
            "antonimo": (entrada.get("antonimo") or "").strip(),
            "nota_uso": (entrada.get("nota_uso") or "").strip(),
        }
        guardar_db(db)
    elif palabra and definicion_texto:
        db = cargar_db()
        db["diccionario_extra"][palabra] = construir_entrada_diccionario(
            palabra,
            "Personalizada",
            definicion_texto,
            f"Ejemplo con {palabra}.",
        )
        guardar_db(db)

    return jsonify({"ok": True})


@app.route("/api/progreso/guardar", methods=["POST"])
def api_guardar_progreso():
    datos = request.get_json(silent=True) or {}
    correo = validar_correo_simple(datos.get("correo"))
    progreso = datos.get("progreso") or {}
    if not correo:
        return jsonify({"ok": False, "mensaje": "Correo electronico invalido."}), 400

    progreso_limpio = {
        "nombre_archivo": str(progreso.get("nombre_archivo") or "registros_cpre2.txt").strip() or "registros_cpre2.txt",
        "datos": str(progreso.get("datos") if progreso.get("datos") is not None else ""),
        "tabla": normalizar_tabla_progreso(progreso.get("tabla")),
        "palabra": str(progreso.get("palabra") if progreso.get("palabra") is not None else ""),
    }

    db = cargar_db()
    db["usuarios"][correo] = {
        "actualizado": datetime.utcnow().isoformat(),
        "datos": progreso_limpio,
    }
    guardar_db(db)
    return jsonify({"ok": True, "mensaje": f"Progreso guardado para {correo}."})


@app.route("/api/progreso/cargar", methods=["GET"])
def api_cargar_progreso():
    correo = validar_correo_simple(request.args.get("correo"))
    if not correo:
        return jsonify({"encontrado": False, "mensaje": "Correo invalido."})
    db = cargar_db()
    registro = db.get("usuarios", {}).get(correo)
    if not registro:
        return jsonify({"encontrado": False})
    datos_guardados = registro.get("datos", {})
    if isinstance(datos_guardados, dict) and "tabla" in datos_guardados:
        datos_guardados["tabla"] = normalizar_tabla_progreso(datos_guardados.get("tabla"))
    return jsonify({"encontrado": True, "progreso": datos_guardados})


if __name__ == "__main__":
    app.run(host=HOST, port=PORT)

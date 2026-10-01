// En la app de escritorio la UI la sirve el mismo backend (/ui/), así que se usa su
// mismo origen. Si se abre de otra forma (archivo suelto, otro servidor), se usa
// el backend por defecto (python -m uvicorn servidor:app / Docker).
const API_BASE = location.pathname.startsWith("/ui/") ? location.origin : "http://127.0.0.1:8000";
const PALABRAS_CLAVE = ["coordenada", "validar", "distancia", "hemisferio", "ubicacion"];

const NOMBRE_FASE = {
  lexico: "Error léxico",
  sintactico: "Error sintáctico",
  interno: "Error interno",
};

// Resultado del último análisis (lista de instrucciones devuelta por el backend)
let instrucciones = [];
let lineaActiva = null;

// ─── Referencias al DOM ───────────────────────────────────────────────────────
const $ = (id) => document.getElementById(id);

const editorInput     = $("editor-input");
const editorResaltado = $("editor-resaltado");
const editorLineas    = $("editor-lineas");
const editorPos       = $("editor-pos");

const btnEjecutar = $("btn-ejecutar");
const btnTexto    = $("btn-texto");
const btnLimpiar  = $("btn-limpiar");

const servidor      = $("servidor");
const servidorTexto = $("servidor-texto");
const estado        = $("estado");
const fases         = $("fases");
const leyenda       = $("mapa-leyenda");

// ─── EDITOR: resaltado de sintaxis, números de línea y cursor ────────────────
const PATRON_SINTAXIS = /(#[^\n]*)|('[^'\n]*'?)|(\d+(?:\.\d+)?)|([A-Za-zÁÉÍÓÚáéíóúÑñ_][\wÁÉÍÓÚáéíóúÑñ]*)|([(),\-])|(\s+)|(.)/g;

function resaltar(texto) {
  let html = "";
  for (const m of texto.matchAll(PATRON_SINTAXIS)) {
    const [lexema, comentario, cadena, numero, palabra, puntuacion, espacio] = m;
    const seguro = escapeHTML(lexema);
    if (comentario)      html += `<span class="syn-comentario">${seguro}</span>`;
    else if (cadena)     html += `<span class="syn-cadena">${seguro}</span>`;
    else if (numero)     html += `<span class="syn-numero">${seguro}</span>`;
    else if (palabra)    html += PALABRAS_CLAVE.includes(palabra.toLowerCase())
                                   ? `<span class="syn-clave">${seguro}</span>` : seguro;
    else if (puntuacion) html += lexema === "-"
                                   ? `<span class="syn-numero">-</span>`
                                   : `<span class="syn-puntuacion">${seguro}</span>`;
    else if (espacio)    html += seguro;
    else                 html += `<span class="syn-invalido">${seguro}</span>`;
  }
  // El salto final evita que la última línea vacía quede desalineada con el textarea
  return html + "\n";
}

function actualizarEditor() {
  editorResaltado.innerHTML = resaltar(editorInput.value);
  renderNumerosLinea();
  sincronizarScroll();
  actualizarPosicion();
}

// Números de línea; las líneas con error del último análisis se marcan en rojo
function renderNumerosLinea(errores = new Map()) {
  const total = editorInput.value.split("\n").length;
  editorLineas.innerHTML = Array.from({ length: total }, (_, i) => {
    const n = i + 1;
    const error = errores.get(n);
    return error
      ? `<span class="linea-error" title="${escapeHTML(error)}">${n}</span>`
      : String(n);
  }).join("\n");
}

function sincronizarScroll() {
  editorResaltado.scrollTop  = editorInput.scrollTop;
  editorResaltado.scrollLeft = editorInput.scrollLeft;
  editorLineas.scrollTop     = editorInput.scrollTop;
}

function actualizarPosicion() {
  const antes = editorInput.value.slice(0, editorInput.selectionStart).split("\n");
  editorPos.textContent = `Ln ${antes.length}, Col ${antes[antes.length - 1].length + 1}`;
}

// Al editar, las marcas de error del análisis anterior ya no corresponden a las líneas
editorInput.addEventListener("input", actualizarEditor);
editorInput.addEventListener("scroll", sincronizarScroll);
editorInput.addEventListener("keyup", actualizarPosicion);
editorInput.addEventListener("click", actualizarPosicion);

editorInput.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
    e.preventDefault();
    ejecutar();
  }
});

function seleccionarLinea(n) {
  const lineas = editorInput.value.split("\n");
  const inicio = lineas.slice(0, n - 1).reduce((acc, l) => acc + l.length + 1, 0);
  editorInput.focus();
  editorInput.setSelectionRange(inicio, inicio + lineas[n - 1].length);
  actualizarPosicion();
}

// ─── REFERENCIA: insertar instrucción en la línea actual ─────────────────────
document.querySelectorAll("#referencia button").forEach((btn) => {
  btn.addEventListener("click", () => insertarInstruccion(btn.dataset.cmd));
});

function insertarInstruccion(cmd) {
  const texto = editorInput.value;
  const cursor = editorInput.selectionStart;
  const inicioLinea = texto.lastIndexOf("\n", cursor - 1) + 1;
  let finLinea = texto.indexOf("\n", cursor);
  if (finLinea === -1) finLinea = texto.length;

  const lineaVacia = texto.slice(inicioLinea, finLinea).trim() === "";
  const nuevo = lineaVacia
    ? texto.slice(0, inicioLinea) + cmd + texto.slice(finLinea)
    : texto.slice(0, finLinea) + "\n" + cmd + texto.slice(finLinea);
  const posFinal = (lineaVacia ? inicioLinea : finLinea + 1) + cmd.length;

  editorInput.value = nuevo;
  actualizarEditor();
  editorInput.focus();
  editorInput.setSelectionRange(posFinal, posFinal);
  actualizarPosicion();
}

// ─── PESTAÑAS ─────────────────────────────────────────────────────────────────
document.querySelectorAll(".pestana").forEach((pestana) => {
  pestana.addEventListener("click", () => activarPestana(pestana.dataset.tab));
});

function activarPestana(nombre) {
  document.querySelectorAll(".pestana").forEach((p) => {
    const activa = p.dataset.tab === nombre;
    p.classList.toggle("activa", activa);
    p.setAttribute("aria-selected", activa);
  });
  document.querySelectorAll(".tab-contenido").forEach((t) => {
    t.hidden = t.id !== `tab-${nombre}`;
  });
}

// ─── ESTADO DEL SERVIDOR ─────────────────────────────────────────────────────
async function verificarServidor() {
  try {
    const r = await fetch(`${API_BASE}/`, { cache: "no-store" });
    if (!r.ok) throw new Error();
    const info = await r.json();
    servidor.dataset.estado = "conectado";
    servidorTexto.textContent = `Servidor v${info.version ?? "?"}`;
  } catch {
    servidor.dataset.estado = "desconectado";
    servidorTexto.textContent = "Servidor no disponible";
  }
  setTimeout(verificarServidor, servidor.dataset.estado === "conectado" ? 15000 : 3000);
}

// ─── EJECUTAR ─────────────────────────────────────────────────────────────────
btnEjecutar.addEventListener("click", ejecutar);
btnLimpiar.addEventListener("click", limpiarTodo);

async function ejecutar() {
  if (!editorInput.value.trim()) { editorInput.focus(); return; }

  setCargando(true);
  const inicio = performance.now();

  try {
    const r = await fetch(`${API_BASE}/iniciar`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo: editorInput.value }),
    });
    if (!r.ok) throw new Error(`HTTP ${r.status}`);
    const data = await r.json();
    if (!Array.isArray(data.instrucciones)) {
      mostrarErrorServidor(
        "Sin respuesta compatible",
        `El servidor en ${API_BASE} respondió en un formato que esta interfaz no reconoce ` +
        "(probablemente es una versión anterior del backend).\n" +
        "Cierra las instancias abiertas de GeoQuery o reinicia el servidor."
      );
      return;
    }
    mostrarAnalisis(data.instrucciones, Math.round(performance.now() - inicio));
  } catch {
    mostrarErrorServidor(
      "Sin conexión",
      `No se pudo conectar con el servidor de análisis (${API_BASE}).\n` +
      "Verifica que el backend esté en ejecución."
    );
  } finally {
    setCargando(false);
  }
}

function setCargando(activo) {
  btnEjecutar.disabled = activo;
  btnEjecutar.classList.toggle("cargando", activo);
  btnTexto.textContent = activo ? "Analizando" : "Ejecutar";
}

// ─── MOSTRAR ANÁLISIS ────────────────────────────────────────────────────────
function mostrarAnalisis(lista, ms) {
  instrucciones = lista;
  lineaActiva = null;

  const errores = lista.filter((i) => !i.exito);
  const tokens = lista.flatMap((i) => i.tokens ?? []);

  renderNumerosLinea(new Map(errores.map((i) => [i.linea, limpiarMensaje(i.error)])));
  renderInstrucciones();
  renderTokens(tokens);
  renderArbol();
  marcarFases(errores);
  dibujarEnMapa();

  if (!lista.length) {
    setEstado("listo", "No hay instrucciones para analizar");
  } else if (errores.length) {
    const e = errores[0];
    setEstado("error",
      `${errores.length} ${errores.length === 1 ? "error" : "errores"} · ` +
      `línea ${e.linea}: ${limpiarMensaje(e.error)}`);
  } else {
    setEstado("ok",
      `${lista.length} ${lista.length === 1 ? "instrucción correcta" : "instrucciones correctas"} · ` +
      `${tokens.length} tokens · ${ms} ms`);
  }
  activarPestana("resultado");
}

// Los mensajes del parser ya traen "Error:" / "Error Sintáctico:"; la fase se muestra aparte
function limpiarMensaje(mensaje) {
  return String(mensaje ?? "Error desconocido").replace(/^Error(?: \p{L}+)?:\s*/u, "");
}

// ─── RESULTADO: lista de instrucciones ───────────────────────────────────────
function renderInstrucciones() {
  const cuerpo = $("resultado-cuerpo");
  $("resultado-vacio").hidden = instrucciones.length > 0;
  cuerpo.hidden = instrucciones.length === 0;
  if (!instrucciones.length) return;

  const correctas = instrucciones.filter((i) => i.exito).length;
  const conError = instrucciones.length - correctas;

  cuerpo.innerHTML = `
    <div class="resumen">
      <span>${instrucciones.length} ${instrucciones.length === 1 ? "instrucción" : "instrucciones"}</span>
      <span class="resumen-ok">${correctas} ${correctas === 1 ? "correcta" : "correctas"}</span>
      ${conError ? `<span class="resumen-error">${conError} con error</span>` : ""}
    </div>
    <ol class="instrucciones">
      ${instrucciones.map(renderFilaInstruccion).join("")}
    </ol>`;

  cuerpo.querySelectorAll(".instr").forEach((fila) => {
    fila.addEventListener("click", () => seleccionarInstruccion(Number(fila.dataset.linea)));
  });
}

function renderFilaInstruccion(i) {
  if (!i.exito) {
    return `
      <li class="instr instr-error" data-linea="${i.linea}" title="${escapeHTML(i.codigo)}">
        <span class="instr-linea">${i.linea}</span>
        <span class="instr-cmd">${escapeHTML(NOMBRE_FASE[i.fase] ?? "Error")}</span>
        <span class="instr-datos">${escapeHTML(limpiarMensaje(i.error))}</span>
      </li>`;
  }
  const { comando, argumentos } = i.resultado;
  return `
    <li class="instr" data-linea="${i.linea}">
      <span class="instr-linea">${i.linea}</span>
      <span class="instr-cmd">${escapeHTML(comando.toUpperCase())}</span>
      <span class="instr-datos">${escapeHTML(describirArgumentos(comando, argumentos))}</span>
    </li>`;
}

function describirArgumentos(comando, args) {
  if (comando === "ubicacion") return `'${args}'`;
  if (comando === "distancia") return `A (${args[0][0]}, ${args[0][1]})  →  B (${args[1][0]}, ${args[1][1]})`;
  return `${args[0]}, ${args[1]}`;
}

// Clic en una instrucción: se resalta en el mapa y se selecciona en el editor.
// Un segundo clic sobre la misma vuelve a mostrar todas.
function seleccionarInstruccion(linea) {
  lineaActiva = lineaActiva === linea ? null : linea;
  document.querySelectorAll(".instr").forEach((f) => {
    f.classList.toggle("activa", Number(f.dataset.linea) === lineaActiva);
  });
  Mapa.enfocar(lineaActiva);
  actualizarLeyenda();
  if (lineaActiva !== null) seleccionarLinea(lineaActiva);
}

// ─── MAPA ────────────────────────────────────────────────────────────────────
let puntosOmitidos = 0;

function dibujarEnMapa() {
  const puntos = [];
  const rutas = [];
  const correctas = instrucciones.filter((i) => i.exito);
  // Con una sola instrucción se etiqueta con sus coordenadas; con varias, con su línea
  const etiquetaCorta = correctas.length > 1;

  for (const i of correctas) {
    const { comando, argumentos } = i.resultado;
    const grupo = i.linea;

    if (comando === "ubicacion") continue;

    if (comando === "distancia") {
      const [[la1, lo1], [la2, lo2]] = argumentos;
      const desde = { lat: la1, lon: lo1 };
      const hasta = { lat: la2, lon: lo2 };
      puntos.push({ ...desde, grupo, etiqueta: etiquetaCorta ? `L${grupo} A` : "A" });
      puntos.push({ ...hasta, grupo, etiqueta: etiquetaCorta ? `L${grupo} B` : "B" });
      rutas.push({ grupo, desde, hasta });
    } else {
      const [lat, lon] = argumentos;
      puntos.push({ lat, lon, grupo, etiqueta: etiquetaCorta ? `L${grupo}` : `${lat}, ${lon}` });
    }
  }

  puntosOmitidos = Mapa.mostrar({ puntos, rutas });
  actualizarLeyenda();
}

function actualizarLeyenda() {
  const correctas = instrucciones.filter((i) => i.exito);
  if (!correctas.length) { leyenda.hidden = true; return; }

  let titulo, detalle;
  const activa = correctas.find((i) => i.linea === lineaActiva) ??
                 (correctas.length === 1 ? correctas[0] : null);

  if (activa) {
    const { comando, argumentos } = activa.resultado;
    titulo = correctas.length > 1 ? `Línea ${activa.linea} · ${comando.toUpperCase()}` : comando.toUpperCase();
    detalle = comando === "ubicacion"
      ? `'${argumentos}' — búsqueda de lugares aún no disponible`
      : describirArgumentos(comando, argumentos);
  } else {
    titulo = "Consulta";
    detalle = `${correctas.length} instrucciones en el mapa · clic en una para enfocarla`;
  }
  if (puntosOmitidos && !activa) detalle += `\n${puntosOmitidos} punto(s) fuera de rango no se dibujan`;

  leyenda.hidden = false;
  leyenda.innerHTML = `
    <div class="mapa-leyenda-titulo">${escapeHTML(titulo)}</div>
    <div class="mapa-leyenda-dato">${escapeHTML(detalle).replace(/\n/g, "<br>")}</div>`;
}

// ─── ERROR DEL SERVIDOR (sin conexión o respuesta incompatible) ──────────────
function mostrarErrorServidor(titulo, mensaje) {
  instrucciones = [];
  renderNumerosLinea();
  renderTokens([]);
  renderArbol();
  marcarFases(null);

  $("resultado-vacio").hidden = true;
  const cuerpo = $("resultado-cuerpo");
  cuerpo.hidden = false;
  cuerpo.innerHTML = `
    <div class="resultado-error">
      <div class="resultado-error-fase">${escapeHTML(titulo)}</div>
      <div class="resultado-error-msg">${escapeHTML(mensaje)}</div>
    </div>`;

  setEstado("error", `${titulo}: ${mensaje.split("\n")[0]}`);
  leyenda.hidden = true;
  Mapa.mostrar({});
  activarPestana("resultado");
}

// ─── TOKENS ──────────────────────────────────────────────────────────────────
function renderTokens(tokens) {
  $("cuenta-tokens").textContent = tokens.length ? tokens.length : "";
  $("tokens-vacio").hidden = tokens.length > 0;
  $("tabla-tokens").hidden = tokens.length === 0;

  $("tokens-cuerpo").innerHTML = tokens.map((t, i) => {
    const tipo = String(t.tipo ?? "?");
    return `<tr>
      <td>${i + 1}</td>
      <td>${t.linea ?? ""}</td>
      <td>${escapeHTML(tipo)}</td>
      <td class="${claseToken(tipo)}">${escapeHTML(String(t.valor ?? ""))}</td>
    </tr>`;
  }).join("");
}

function claseToken(tipo) {
  switch (tipo) {
    case "IDENTIFICADOR": return "tok-identificador";
    case "NUMERO":
    case "NEGATIVO":      return "tok-numero";
    case "STRING":        return "tok-string";
    default:              return "tok-puntuacion";
  }
}

// ─── ÁRBOL SINTÁCTICO ────────────────────────────────────────────────────────
// Nodo: { texto (HTML ya escapado), hijos: [] }
function nodoInstruccion(i) {
  const n = (texto, hijos = []) => ({ texto, hijos });
  const hoja = (clave, valor, clase = "ast-valor") =>
    n(`<span class="ast-clave">${clave}</span>  <span class="${clase}">${escapeHTML(String(valor))}</span>`);
  const coord = ([lat, lon]) => [hoja("latitud ", lat), hoja("longitud", lon)];
  const etiquetaLinea = `<span class="ast-rama">línea ${i.linea}</span>`;

  if (!i.exito) {
    return n(`${etiquetaLinea}  <span class="ast-error">${escapeHTML(NOMBRE_FASE[i.fase] ?? "Error")}</span>`);
  }

  const { comando, argumentos } = i.resultado;
  const raiz = `<span class="ast-nodo">${escapeHTML(comando)}</span>  ${etiquetaLinea}`;
  if (comando === "ubicacion") return n(raiz, [hoja("lugar", `'${argumentos}'`, "ast-texto")]);
  if (comando === "distancia") {
    return n(raiz, [
      n(`<span class="ast-nodo">coordenada A</span>`, coord(argumentos[0])),
      n(`<span class="ast-nodo">coordenada B</span>`, coord(argumentos[1])),
    ]);
  }
  return n(raiz, coord(argumentos));
}

function dibujarArbol(nodo, prefijo = "", ultimo = true, raiz = true) {
  const rama = (t) => `<span class="ast-rama">${t}</span>`;
  let salida = raiz ? nodo.texto : `${prefijo}${rama(ultimo ? "└─" : "├─")} ${nodo.texto}`;
  const prefijoHijos = raiz ? "" : prefijo + (ultimo ? "   " : `${rama("│")}  `);
  nodo.hijos.forEach((hijo, k) => {
    salida += "\n" + dibujarArbol(hijo, prefijoHijos, k === nodo.hijos.length - 1, false);
  });
  return salida;
}

function renderArbol() {
  const hay = instrucciones.length > 0;
  $("ast-vacio").hidden = hay;
  $("ast-cuerpo").hidden = !hay;
  if (!hay) return;
  const programa = {
    texto: `<span class="ast-nodo">programa</span>`,
    hijos: instrucciones.map(nodoInstruccion),
  };
  $("ast-cuerpo").innerHTML = dibujarArbol(programa);
}

// ─── ESTADO GENERAL ──────────────────────────────────────────────────────────
// Léxico falla si alguna línea tuvo error léxico; sintáctico, si alguna tuvo error
// sintáctico. Si solo hubo errores léxicos, el sintáctico queda pendiente.
function marcarFases(errores) {
  const estados = {};
  if (errores) {
    const hay = (fase) => errores.some((e) => e.fase === fase);
    estados.lexico = hay("lexico") ? "error" : "ok";
    estados.sintactico = hay("sintactico") ? "error" : (hay("lexico") ? undefined : "ok");
  }
  fases.querySelectorAll("li").forEach((li) => {
    const e = estados[li.dataset.fase];
    if (e) li.dataset.estado = e;
    else   delete li.dataset.estado;
  });
}

function setEstado(tipo, texto) {
  estado.dataset.tipo = tipo;
  estado.textContent = texto;
}

function limpiarTodo() {
  editorInput.value = "";
  instrucciones = [];
  lineaActiva = null;
  actualizarEditor();
  editorInput.focus();

  renderTokens([]);
  renderArbol();
  $("resultado-cuerpo").hidden = true;
  $("resultado-vacio").hidden = false;

  marcarFases(null);
  setEstado("listo", "Listo");
  leyenda.hidden = true;
  Mapa.limpiar();
  activarPestana("resultado");
}

// ─── MAPA: controles ─────────────────────────────────────────────────────────
$("mapa-acercar").addEventListener("click", () => Mapa.acercar(1.6));
$("mapa-alejar").addEventListener("click", () => Mapa.acercar(1 / 1.6));
$("mapa-encuadrar").addEventListener("click", () => Mapa.encuadrar());

// ─── UTILIDAD ────────────────────────────────────────────────────────────────
function escapeHTML(str) {
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

// ─── INICIO ──────────────────────────────────────────────────────────────────
Mapa.iniciar($("mapa-svg"));
actualizarEditor();
verificarServidor();

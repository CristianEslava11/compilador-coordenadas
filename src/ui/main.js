const API_URL = "http://127.0.0.1:8000/iniciar";

// ─── Referencias al DOM ───────────────────────────────────────────────────────
const inputCodigo    = document.getElementById("input-codigo");
const btnEjecutar    = document.getElementById("btn-ejecutar");
const btnLimpiar     = document.getElementById("btn-limpiar");
const btnIcon        = document.getElementById("btn-icon");
const btnText        = document.getElementById("btn-text");
const spinnerEl      = document.getElementById("spinner");

const estadoInicial  = document.getElementById("estado-inicial");
const bloqueTokens   = document.getElementById("bloque-tokens");
const bloqueResultado= document.getElementById("bloque-resultado");
const bloqueError    = document.getElementById("bloque-error");

const zonaTokens     = document.getElementById("zona-tokens");
const zonaResultado  = document.getElementById("zona-resultado");
const zonaError      = document.getElementById("zona-error");
const tokensCount    = document.getElementById("tokens-count");
const lineNumbers    = document.getElementById("line-numbers");

// ─── Números de línea dinámicos ───────────────────────────────────────────────
inputCodigo.addEventListener("input", actualizarLineNumbers);
inputCodigo.addEventListener("scroll", () => {
  lineNumbers.scrollTop = inputCodigo.scrollTop;
});

function actualizarLineNumbers() {
  const lineas = inputCodigo.value.split("\n").length;
  lineNumbers.textContent = Array.from({ length: lineas }, (_, i) => i + 1).join("\n");
}

// ─── Comandos rápidos ─────────────────────────────────────────────────────────
document.querySelectorAll(".quick-btn").forEach(btn => {
  btn.addEventListener("click", () => {
    const cmd = btn.dataset.cmd;
    inputCodigo.value = cmd;
    actualizarLineNumbers();
    inputCodigo.focus();
  });
});

// ─── Ejecutar con Ctrl+Enter ──────────────────────────────────────────────────
inputCodigo.addEventListener("keydown", (e) => {
  if (e.key === "Enter" && e.ctrlKey) {
    e.preventDefault();
    ejecutar();
  }
});

// ─── Botones principales ──────────────────────────────────────────────────────
btnEjecutar.addEventListener("click", ejecutar);
btnLimpiar.addEventListener("click", limpiarTodo);

// ─── FUNCIÓN PRINCIPAL: EJECUTAR ──────────────────────────────────────────────
async function ejecutar() {
  const codigo = inputCodigo.value.trim();
  if (!codigo) return;

  setCargando(true);

  try {
    const respuesta = await fetch(API_URL, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ codigo })
    });

    if (!respuesta.ok) {
      throw new Error(`HTTP ${respuesta.status}: ${respuesta.statusText}`);
    }

    const data = await respuesta.json();

    if (data.exito) {
      mostrarExito(data.tokens, data.resultado);
    } else {
      mostrarError(data.error);
    }
  } catch (err) {
    if (err.message.includes("fetch") || err.message.includes("Failed")) {
      mostrarError("No se pudo conectar con el servidor.\nAsegúrate de que el backend está corriendo en el puerto 8000.");
    } else {
      mostrarError(`Error de red: ${err.message}`);
    }
  } finally {
    setCargando(false);
  }
}

// ─── ESTADO: CARGANDO ─────────────────────────────────────────────────────────
function setCargando(activo) {
  btnEjecutar.disabled = activo;
  spinnerEl.classList.toggle("visible", activo);
  btnIcon.classList.toggle("oculto", activo);
  btnText.textContent = activo ? "Ejecutando..." : "Ejecutar";
}

// ─── ESTADO: ÉXITO ───────────────────────────────────────────────────────────
function mostrarExito(tokens, resultado) {
  estadoInicial.classList.add("oculto");
  bloqueError.classList.add("oculto");

  const header = `<div class="token-list-header"><span>Tipo</span><span>Valor</span></div>`;
  zonaTokens.innerHTML = header + tokens.map(t => renderTokenRow(t)).join("");
  tokensCount.textContent = `${tokens.length} token${tokens.length !== 1 ? "s" : ""}`;
  bloqueTokens.classList.remove("oculto");

  zonaResultado.innerHTML = renderResultado(resultado);
  bloqueResultado.classList.remove("oculto");
}

// ─── ESTADO: ERROR ────────────────────────────────────────────────────────────
function mostrarError(mensaje) {
  estadoInicial.classList.add("oculto");
  bloqueTokens.classList.add("oculto");
  bloqueResultado.classList.add("oculto");

  zonaError.textContent = mensaje;
  bloqueError.classList.remove("oculto");
}

// ─── LIMPIAR TODO ─────────────────────────────────────────────────────────────
function limpiarTodo() {
  inputCodigo.value = "";
  actualizarLineNumbers();
  inputCodigo.focus();

  bloqueTokens.classList.add("oculto");
  bloqueResultado.classList.add("oculto");
  bloqueError.classList.add("oculto");
  estadoInicial.classList.remove("oculto");

  zonaTokens.innerHTML = "";
  zonaResultado.innerHTML = "";
  zonaError.textContent = "";
}

// ─── RENDERIZADO: FILA DE TOKEN (LISTA) ──────────────────────────────────────
function renderTokenRow(token) {
  const tipo     = token.tipo  ?? token.type  ?? "?";
  const valor    = token.valor ?? token.value ?? "?";
  const valorStr = String(valor);
  const clseTipo = `token-tipo tipo-${tipo.toLowerCase()}`;

  return `
    <div class="token-row">
      <span class="${clseTipo}">${tipo}</span>
      <span class="token-valor">${escapeHTML(valorStr)}</span>
    </div>
  `;
}

// ─── RENDERIZADO: RESULTADO ESTRUCTURADO ─────────────────────────────────────
function renderResultado(resultado) {
  if (!resultado) return "<span style='color:var(--text-muted)'>Sin resultado</span>";

  const comando = resultado.comando ?? "—";
  const args    = resultado.argumentos ?? resultado.args ?? null;
  const argsStr = args !== null ? JSON.stringify(args, null, 2) : "—";

  return `
    <div class="resultado-grid">
      <span class="resultado-key">comando:</span>
      <span class="resultado-val">
        <span class="comando-tag">${escapeHTML(comando)}</span>
      </span>
      <span class="resultado-key">argumentos:</span>
      <span class="resultado-val args-val">${escapeHTML(argsStr)}</span>
    </div>
  `;
}

// ─── UTILIDAD: ESCAPAR HTML ───────────────────────────────────────────────────
function escapeHTML(str) {
  return str
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;");
}

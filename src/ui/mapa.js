// ─── MAPA MUNDIAL ─────────────────────────────────────────────────────────────
// Mapa vectorial con proyección Natural Earth (d3-geo) y datos de países
// de Natural Earth 1:50m (world-atlas). Funciona sin conexión.
//
// API pública (window.Mapa):
//   Mapa.iniciar(contenedor)          → dibuja el mapa
//   Mapa.mostrar({ puntos, rutas })   → puntos: [{ lat, lon, etiqueta, grupo }]
//                                        rutas:  [{ grupo, desde: {lat, lon}, hasta: {lat, lon} }]
//   Mapa.enfocar(grupo)               → resalta y encuadra un grupo (null = todos)
//   Mapa.limpiar()                    → quita puntos y rutas
//   Mapa.encuadrar()                  → ajusta la vista al grupo activo, a todos los puntos o al mundo

(function () {
  const ZOOM_MAX = 40;
  const MARGEN = 16;

  let svg, capaMundo, capaMarcas, proyeccion, zoom;
  let ancho = 0, alto = 0;
  let transformacion = d3.zoomIdentity;
  let marcas = { puntos: [], rutas: [] };
  let grupoActivo = null;

  const mundo = topojson.feature(GEO_MUNDO, GEO_MUNDO.objects.countries);
  const fronteras = topojson.mesh(GEO_MUNDO, GEO_MUNDO.objects.countries, (a, b) => a !== b);
  const reticula = d3.geoGraticule10();
  const ecuador = { type: "LineString", coordinates: [[-180, 0], [-90, 0], [0, 0], [90, 0], [180, 0]] };
  const esfera = { type: "Sphere" };

  function iniciar(contenedor) {
    svg = d3.select(contenedor);
    capaMundo = svg.append("g");
    capaMarcas = svg.append("g");
    proyeccion = d3.geoNaturalEarth1();

    capaMundo.append("path").attr("class", "mapa-esfera");
    capaMundo.append("path").attr("class", "mapa-reticula");
    capaMundo.append("path").attr("class", "mapa-ecuador");
    capaMundo.append("path").attr("class", "mapa-tierra");
    capaMundo.append("path").attr("class", "mapa-fronteras");
    capaMundo.selectAll("path").attr("vector-effect", "non-scaling-stroke");

    zoom = d3.zoom()
      .scaleExtent([1, ZOOM_MAX])
      .on("zoom", (evento) => {
        transformacion = evento.transform;
        capaMundo.attr("transform", transformacion);
        dibujarMarcas();
      });
    svg.call(zoom).on("dblclick.zoom", null);

    svg.on("mousemove", (evento) => mostrarCursor(d3.pointer(evento)));
    svg.on("mouseleave", () => mostrarCursor(null));

    new ResizeObserver(redimensionar).observe(contenedor);
    redimensionar();
  }

  function redimensionar() {
    const caja = svg.node().getBoundingClientRect();
    if (!caja.width || !caja.height) return;
    ancho = caja.width;
    alto = caja.height;

    proyeccion.fitExtent([[MARGEN, MARGEN], [ancho - MARGEN, alto - MARGEN]], esfera);
    const ruta = d3.geoPath(proyeccion);

    capaMundo.select(".mapa-esfera").attr("d", ruta(esfera));
    capaMundo.select(".mapa-reticula").attr("d", ruta(reticula));
    capaMundo.select(".mapa-ecuador").attr("d", ruta(ecuador));
    capaMundo.select(".mapa-tierra").attr("d", ruta(mundo));
    capaMundo.select(".mapa-fronteras").attr("d", ruta(fronteras));

    zoom.extent([[0, 0], [ancho, alto]]).translateExtent([[0, 0], [ancho, alto]]);
    dibujarMarcas();
    if (marcas.puntos.length) encuadrar(0);
  }

  // Proyección equivalente a la base pero con el zoom actual aplicado,
  // para que los marcadores conserven su tamaño en pantalla.
  function proyeccionConZoom() {
    const [tx, ty] = proyeccion.translate();
    const k = transformacion.k;
    return d3.geoNaturalEarth1()
      .scale(proyeccion.scale() * k)
      .translate([transformacion.x + tx * k, transformacion.y + ty * k]);
  }

  function dibujarMarcas() {
    if (!capaMarcas) return;
    const p = proyeccionConZoom();
    const { puntos, rutas } = marcas;
    const atenuado = (d) => grupoActivo !== null && d.grupo !== grupoActivo;

    capaMarcas.selectAll(".mapa-ruta")
      .data(rutas)
      .join("path")
      .attr("class", "mapa-ruta")
      .classed("atenuado", atenuado)
      .attr("d", (d) => d3.geoPath(p)(lineaDeRuta(d)));

    const grupos = capaMarcas.selectAll(".mapa-marca")
      .data(puntos)
      .join((entrar) => {
        const g = entrar.append("g").attr("class", "mapa-marca");
        g.append("circle").attr("class", "mapa-punto-halo").attr("r", 11);
        g.append("circle").attr("class", "mapa-punto").attr("r", 4.5);
        g.append("text").attr("class", "mapa-etiqueta").attr("x", 10).attr("y", -8);
        return g;
      })
      .classed("atenuado", atenuado)
      .attr("transform", (d) => `translate(${p([d.lon, d.lat])})`);

    grupos.select("text").text((d) => d.etiqueta ?? "");
    capaMarcas.selectAll(".mapa-ruta").lower();
  }

  function mostrarCursor(posicion) {
    const salida = document.getElementById("mapa-cursor");
    if (!posicion) { salida.hidden = true; return; }

    const [x, y] = transformacion.invert(posicion);
    const lonlat = proyeccion.invert([x, y]);
    const valido = lonlat && Number.isFinite(lonlat[0]) && Number.isFinite(lonlat[1])
      && d3.geoContains(esfera, lonlat)
      && Math.abs(lonlat[0]) <= 180 && Math.abs(lonlat[1]) <= 90
      && pareceDentroDeLaEsfera(x, y, lonlat);

    salida.hidden = !valido;
    if (valido) salida.textContent = formatearCoordenada(lonlat[1], lonlat[0]);
  }

  // Natural Earth invierte puntos fuera del contorno a coordenadas "válidas";
  // se reproyecta para comprobar que el punto corresponde al mismo píxel.
  function pareceDentroDeLaEsfera(x, y, lonlat) {
    const [px, py] = proyeccion(lonlat);
    return Math.hypot(px - x, py - y) < 1;
  }

  const enRango = (p) => Math.abs(p.lat) <= 90 && Math.abs(p.lon) <= 180;

  function lineaDeRuta(r) {
    return { type: "LineString", coordinates: [[r.desde.lon, r.desde.lat], [r.hasta.lon, r.hasta.lat]] };
  }

  function mostrar({ puntos = [], rutas = [] } = {}) {
    marcas = {
      puntos: puntos.filter(enRango),
      rutas: rutas.filter((r) => enRango(r.desde) && enRango(r.hasta)),
    };
    grupoActivo = null;
    dibujarMarcas();
    encuadrar();
    return puntos.length - marcas.puntos.length;   // puntos omitidos por estar fuera de rango
  }

  function enfocar(grupo) {
    grupoActivo = grupo;
    dibujarMarcas();
    encuadrar();
  }

  function limpiar() {
    marcas = { puntos: [], rutas: [] };
    grupoActivo = null;
    dibujarMarcas();
    svg.transition().duration(500).call(zoom.transform, d3.zoomIdentity);
  }

  function encuadrar(duracion = 650) {
    const puntos = marcas.puntos.filter((p) => grupoActivo === null || p.grupo === grupoActivo);
    const rutas = marcas.rutas.filter((r) => grupoActivo === null || r.grupo === grupoActivo);
    if (!puntos.length) {
      svg.transition().duration(duracion).call(zoom.transform, d3.zoomIdentity);
      return;
    }

    let objetivo;
    if (puntos.length === 1) {
      const [x, y] = proyeccion([puntos[0].lon, puntos[0].lat]);
      const k = 4;
      objetivo = d3.zoomIdentity.translate(ancho / 2 - x * k, alto / 2 - y * k).scale(k);
    } else {
      // Las rutas se incluyen porque el arco de círculo máximo puede salirse de los extremos
      const geometria = {
        type: "GeometryCollection",
        geometries: [
          { type: "MultiPoint", coordinates: puntos.map((p) => [p.lon, p.lat]) },
          ...rutas.map(lineaDeRuta),
        ],
      };
      const [[x0, y0], [x1, y1]] = d3.geoPath(proyeccion).bounds(geometria);
      const k = Math.min(20, 0.55 / Math.max((x1 - x0) / ancho, (y1 - y0) / alto, 1e-3));
      const cx = (x0 + x1) / 2, cy = (y0 + y1) / 2;
      objetivo = d3.zoomIdentity.translate(ancho / 2 - cx * k, alto / 2 - cy * k).scale(Math.max(1, k));
    }
    svg.transition().duration(duracion).call(zoom.transform, objetivo);
  }

  function acercar(factor) {
    svg.transition().duration(250).call(zoom.scaleBy, factor);
  }

  // Mismo formato que el lenguaje GEO: grados decimales con signo
  // (latitud negativa = Sur, longitud negativa = Oeste)
  function formatearCoordenada(lat, lon) {
    return `${Number(lat).toFixed(4)}, ${Number(lon).toFixed(4)}`;
  }

  window.Mapa = { iniciar, mostrar, enfocar, limpiar, encuadrar, acercar, formatearCoordenada };
})();

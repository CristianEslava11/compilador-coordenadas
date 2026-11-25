# Programa de ejemplo del lenguaje GEO
# Una instrucción por línea; las líneas que empiezan con # son comentarios.
# Ejecutar con: python src/main.py ProgramasCompilador/ejemplo.geo

# Lugar que corresponde a una coordenada (Tunja)
COORDENADA(5.5353, -73.3678)

# Punto en medio del océano Atlántico
COORDENADA(25.24, -60.14)

# Validación de rangos
VALIDAR(4.7110, -74.0721)
VALIDAR(95, -200)

# Distancia Bogotá - Medellín
DISTANCIA(4.7110, -74.0721), (6.2442, -75.5812)

# Hemisferios de Sídney
HEMISFERIO(-33.8688, 151.2093)

# Búsqueda de un lugar por nombre
UBICACION('San Andrés')

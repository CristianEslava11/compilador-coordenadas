import json
import os
import ReglasSintacticas

class parser:
    def __init__(self, tokens, ruta_reglas = None):
        self.tokens = tokens
        self.pos = 0
        self.reglas = self._cargar_reglas(ruta_reglas)
        self.acciones = {}

    def _cargar_reglas(self, ruta_reglas):
        if ruta_reglas is None:
            ruta_reglas = os.path.join(os.path.dirname(__file__), "persistencia", "reglas.json")
        with open(ruta_reglas, "r", encoding="utf-8") as f:
            return json.load(f)

    def actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    def consumir(self, tipo):
        token = self.actual()
        if token is None:
            raise SyntaxError("Fin inesperado de la entrada. No hay token disponible.")

        if token.tipo != tipo:
            raise SyntaxError(f"Error: Se esperaba {tipo}, se encontró {token.tipo}")

        self.pos += 1
        return token

    def buscar_regla(self):
        """
        Examina el token actual y consulta en el JSON de reglas la configuración
        asociada a dicha palabra clave. Retorna el diccionario de funciones a ejecutar.
        """
        token = self.actual()
        
        if token.valor != None:
            clave = str(token.valor).lower()
        else:
            raise SyntaxError("Error: No se encontró la palabra clave al inicio")

        return self.reglas.get(clave)

    def ejecucion_metodo(self, nombre_metodo):
        """Busca el método en ReglasSintacticas por su nombre en string y lo ejecuta pasándole self."""
        if not hasattr(ReglasSintacticas, nombre_metodo):
            raise SyntaxError(f"Error: El método '{nombre_metodo}' no existe en ReglasSintacticas.")
        
        metodo = getattr(ReglasSintacticas, nombre_metodo)
        return metodo(self)

    def analizador(self):
        token = self.actual()
        if token is None:
            raise SyntaxError("La secuencia de tokens está vacía.")

        config_regla = self.buscar_regla()
        
        if config_regla is None:
            raise SyntaxError(f"Error: No hay reglas definidas para el token actual: {token.tipo}, {token.valor}")

        # 1. Ejecutar la regla de inicio apuntada desde el JSON (ej. 'revisar_palabra_clave')
        comando = self.ejecucion_metodo(config_regla["funcion_clave"])
        
        # 2. Ejecutar la regla de argumentos apuntada desde el JSON (ej. 'revisar_validacion_coordenada', 'regla_distancia')
        argumentos = self.ejecucion_metodo(config_regla["funcion_argumentos"])

        return {
            "comando": comando,
            "argumentos": argumentos
        }

    
        

    

        
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
        Examina el token actual y busca en la lista de reglas cargadas desde el JSON
        cuál regla coincide con el valor o tipo de dicho token.
        Retorna el nombre del método/función a ejecutar en 'ReglasSintacticas.py'.
        """
        token = self.actual()
        if token is None:
            raise SyntaxError("Error: No se encontró la palabra clave al inicio")
        
        if token.valor is not None:
            valor_token = str(token.valor).lower()
        else: 
            valor_token = None

        tipo_token = token.tipo.upper()

        for reglas in self.reglas:
            regla_dict = reglas.get("Regla_1", {})
            for nombre_funcion, disparadores in regla_dict.items():
                if nombre_funcion == "revisar_palabra_clave":
                    # Si el valor o tipo coincide con los disparadores
                    disparadores_lower = [str(d).lower() for d in disparadores]
                    if valor_token in disparadores_lower or tipo_token in disparadores:
                        return nombre_funcion  # Retorna "revisar_palabra_clave"

        return None

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

        nombre_metodo = self.buscar_regla()
        
        if nombre_metodo is None:
            raise SyntaxError(f"Error: No hay reglas definidas para el token actual: {token.tipo}, {token.valor}")
        # 1. Ejecutar la primera regla (revisar palabra clave)
        comando = self.ejecucion_metodo(nombre_metodo)
        # 2. Ejecutar la siguiente regla para validar los argumentos de la coordenada
        coordenadas = self.ejecucion_metodo("revisar_validacion_coordenada")
        return {
            "comando": comando,
            "coordenadas": coordenadas
        }

    
        

    
        
                                

                
                

        
        
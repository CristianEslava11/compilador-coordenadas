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
            #json.load() para cargar el archivo
            return json.load(f)

    #funcion para obtener el token actual
    def actual(self):
        if self.pos < len(self.tokens):
            return self.tokens[self.pos]
        return None

    #funcion para consumir el token actual y avanzar a la siguiente posicion
    def consumir(self, tipo):
        token = self.actual()
        if token is None:
            raise SyntaxError("Fin inesperado de la entrada. No hay token disponible.")

        if token.tipo != tipo:
            raise SyntaxError(f"Error: Se esperaba {tipo}, se encontró {token.tipo}")

        self.pos += 1
        return token

    #funcion para buscar la regla
    
    def buscar_regla(self):
        """
        Examina el token actual y consulta en el JSON de reglas la configuración
        asociada a dicha palabra clave. Retorna el diccionario de funciones a ejecutar.
        """
        #se guarda eñ token actual en token
        token = self.actual()
        
        if token.valor != None:
    
            clave = str(token.valor).lower()
        else:
            raise SyntaxError("Error: No se encontró la palabra clave al inicio")

    
        return self.reglas.get(clave)

    #funcion para ejecutar el metodo
    def ejecucion_metodo(self, nombre_metodo):
        """Busca el método en ReglasSintacticas por su nombre en string y lo ejecuta pasándole self."""
        #hasattr() es una funcion que verifica si un objeto tiene un atributo
        if not hasattr(ReglasSintacticas, nombre_metodo):
            raise SyntaxError(f"Error: El método '{nombre_metodo}' no existe en ReglasSintacticas.")
        
        #getattr() es una funcion que obtiene un atributo de un objeto
        metodo = getattr(ReglasSintacticas, nombre_metodo)
        return metodo(self)

    #funcion para analizar el token
    def analizador(self):
        #se obtiene el token actual
        token = self.actual()
        #si el token es None, lanzar SyntaxError
        if token is None:
            raise SyntaxError("La secuencia de tokens está vacía.")
        #se busca la regla asociada al token
        config_regla = self.buscar_regla()
        
        #si la regla no existe, lanzar SyntaxError
        if config_regla is None:
            raise SyntaxError(f"Error: No hay reglas definidas para el token actual: {token.tipo}, {token.valor}")

        #se ejecuta la regla de inicio apuntada desde el JSON
        comando = self.ejecucion_metodo(config_regla["funcion_clave"])
        
        # 2. Ejecutar la regla de argumentos apuntada desde el JSON (ej. 'revisar_validacion_coordenada', 'regla_distancia')
        argumentos = self.ejecucion_metodo(config_regla["funcion_argumentos"])

        return {
            "comando": comando,
            "argumentos": argumentos
        }

    
        

    

        
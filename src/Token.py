class Token:
    #Se crea el constructor __init__
    # Representa una unidad reconocida por el analizador léxico.
    def __init__(self, token, valor): 
        self.token = token
        self.valor = valor

    def to_json(self):
        return self.__dict__

    def __repr__(self):
        return f"{self.token}, {self.valor!r}"
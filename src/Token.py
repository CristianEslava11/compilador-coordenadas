class Token:
    # Se crea el constructor __init__
    # Representa una unidad reconocida por el analizador léxico.
    def __init__(self, tipo, valor): 
        self.tipo = tipo
        self.valor = valor

    def to_json(self):
        return self.__dict__

    def __repr__(self):
        return f"{self.tipo}, {self.valor!r}"
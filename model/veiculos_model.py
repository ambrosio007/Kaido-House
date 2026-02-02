import uuid
from datetime import datetime

class VeiculoModel:
    def __init__(self, user_id, marca, modelo, ano, km, cor, estado, preco, descricao, fotos=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.marca = marca
        self.modelo = modelo
        self.ano = ano
        self.km = km
        self.cor = cor
        self.estado = estado  # ✅ NOVO: novo, seminovo ou usado
        self.preco = preco
        self.descricao = descricao
        self.fotos = fotos or ""
        self.data_cadastro = datetime.now()
        self.status = "ativo"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "marca": self.marca,
            "modelo": self.modelo,
            "ano": self.ano,
            "km": self.km,
            "cor": self.cor,
            "estado": self.estado,  # ✅ NOVO
            "preco": self.preco,
            "descricao": self.descricao,
            "fotos": self.fotos,
            "data_cadastro": self.data_cadastro,
            "status": self.status
        }
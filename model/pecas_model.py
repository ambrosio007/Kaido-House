import uuid
from datetime import datetime

class PecaModel:
    def __init__(self, user_id, nome, categoria, marca, modelo, estado, preco, descricao, fotos=None):
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.nome = nome
        self.categoria = categoria
        self.marca = marca
        self.modelo = modelo or ""
        self.estado = estado
        self.preco = preco
        self.descricao = descricao
        self.fotos = fotos or ""
        self.data_cadastro = datetime.now()
        self.status = "ativo"

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "nome": self.nome,
            "categoria": self.categoria,
            "marca": self.marca,
            "modelo": self.modelo,
            "estado": self.estado,
            "preco": self.preco,
            "descricao": self.descricao,
            "fotos": self.fotos,
            "data_cadastro": self.data_cadastro,
            "status": self.status
        }
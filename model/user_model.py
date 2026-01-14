import uuid
import bcrypt

class User:
    def __init__(self, nome, cdf, cep, idade, email, senha):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.cpf = cdf
        self.cep = cep
        self.idade = idade
        self.email = email
        self.senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "cep": self.cep,
            "idade": self.idade,
            "email": self.email
        }
import uuid
import bcrypt

class UserModel:
    def __init__(self, nome, cpf, cep, idade, email, senha, perfil='cliente', foto_perfil=None):
        self.id = str(uuid.uuid4())
        self.nome = nome
        self.cpf = cpf
        self.cep = cep
        self.idade = idade
        self.email = email
        self.senha_hash = bcrypt.hashpw(senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
        self.perfil = perfil
        self.foto_perfil = foto_perfil  # URL ou caminho da foto

    def to_dict(self):
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "cep": self.cep,
            "idade": self.idade,
            "email": self.email,
            "perfil": self.perfil,
            "foto_perfil": self.foto_perfil
        }
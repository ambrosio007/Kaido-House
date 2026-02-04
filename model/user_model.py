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
        # ✅ foto_perfil aceito como parâmetro mas não incluído no dict inicial
        # A foto será adicionada DEPOIS através do método atualizar_foto_perfil
        self._foto_perfil = foto_perfil

    def to_dict(self):
        """
        Retorna dicionário básico SEM foto_perfil
        A foto será adicionada depois do cadastro
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "cep": self.cep,
            "idade": self.idade,
            "email": self.email,
            "perfil": self.perfil,
            # ⚠️ foto_perfil NÃO incluída aqui - será NULL no banco inicialmente
        }
    
    def to_dict_completo(self):
        """
        Retorna dicionário completo COM foto_perfil
        Use este método quando precisar incluir a foto
        """
        return {
            "id": self.id,
            "nome": self.nome,
            "cpf": self.cpf,
            "cep": self.cep,
            "idade": self.idade,
            "email": self.email,
            "perfil": self.perfil,
            "foto_perfil": self._foto_perfil
        }
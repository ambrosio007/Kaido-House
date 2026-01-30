from model.user_model import UserModel
from repository.user_repository import UserRepository
import bcrypt

class UserService:

    @staticmethod
    def cadastrar_user(dados):
        try:
            user = UserModel(**dados)
            status = UserRepository.adicionar_user(user.__dict__)
        
            if status:
                return True, "Usuário cadastrado com sucesso"
            else:
                return False, "Erro ao salvar usuário no banco de dados"
            
        except TypeError as e:
        # Captura erros de campos incorretos no UserModel
            return False, f"Campo inválido: {str(e)}"
        except Exception as e:
        # Captura qualquer outro erro
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def autenticar_user(email, senha):
        user = UserRepository.buscar_por_email_e_senha(email, senha)
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha'].encode('utf-8')):
            return UserModel(**user)
        return None
    
    @staticmethod
    def atualizar(user_edits):
        return UserRepository.atualizar_user(user_edits['id'], user_edits)
    
    @staticmethod
    def deletar(user_id):
        return UserRepository.delet(user_id)
    
    @staticmethod
    def listar_users():
        users = UserRepository.lista_users()
        return [UserModel(**user) for user in users]
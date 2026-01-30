from model.user_model import UserModel
from repository.user_repository import UserRepository
import bcrypt

class UserService:

    @staticmethod
    def cadastrar_user(dados):
        try:
            print(f"========== CADASTRO DE USUÁRIO ==========")
            print(f"1. Dados recebidos no service:")
            for key, value in dados.items():
                if key == 'senha':
                    print(f"   {key}: ****** (oculto)")
                else:
                    print(f"   {key}: {value}")
            
            print(f"\n2. Criando UserModel...")
            user = UserModel(**dados)
            print(f"   ✅ UserModel criado com sucesso")
            print(f"   ID: {user.id}")
            print(f"   Perfil: {user.perfil}")
            
            print(f"\n3. Convertendo para dict...")
            user_dict = user.__dict__
            print(f"   Campos no dict: {list(user_dict.keys())}")
            
            print(f"\n4. Chamando UserRepository.adicionar_user...")
            status = UserRepository.adicionar_user(user_dict)
            
            print(f"\n5. Resultado do repository: {status}")
            print(f"==========================================\n")
            
            if status:
                return True, "Usuário cadastrado com sucesso"
            else:
                return False, "Erro ao salvar usuário no banco de dados"
                
        except TypeError as e:
            print(f"ERRO TypeError: {str(e)}")
            return False, f"Campo inválido: {str(e)}"
        except Exception as e:
            print(f"ERRO Exception: {str(e)}")
            import traceback
            traceback.print_exc()
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
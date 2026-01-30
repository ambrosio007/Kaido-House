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
            
            print(f"\n3. Chamando UserRepository.adicionar_user...")
            status = UserRepository.adicionar_user(user.__dict__)
            
            print(f"\n4. ✅ Usuário cadastrado com sucesso!")
            print(f"==========================================\n")
            
            return True, "Usuário cadastrado com sucesso"
                
        except Exception as e:
            erro_msg = str(e)
            print(f"\n❌ ERRO: {erro_msg}")
            print(f"==========================================\n")
            
            # Retorna a mensagem de erro específica
            if "já está cadastrado" in erro_msg or "already exists" in erro_msg:
                return False, erro_msg
            else:
                return False, f"Erro ao cadastrar: {erro_msg}"
    
    @staticmethod
    def autenticar_usuario(email, senha):
        """Autentica usuário por email e senha"""
        user = UserRepository.buscar_por_email_e_senha(email, senha)
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha'].encode('utf-8')):
            return user  # Retorna o dict do usuário
        return None
    
    @staticmethod
    def atualizar_usuario(user_id, user_edits):
        """Atualiza dados do usuário"""
        return UserRepository.atualizar_user(user_id, user_edits)
    
    @staticmethod
    def deletar_usuario(user_id):
        """Deleta um usuário"""
        return UserRepository.delet(user_id)
    
    @staticmethod
    def lista():
        """Lista todos os usuários"""
        users = UserRepository.lista_users()
        return users  # Retorna lista de dicts
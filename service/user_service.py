from model.user_model import UserModel
from repository.user_repository import UserRepository
from repository.redefinir_senha import PasswordResetRepository
from service.email_service import EmailService
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
            
            if "já está cadastrado" in erro_msg or "already exists" in erro_msg:
                return False, erro_msg
            else:
                return False, f"Erro ao cadastrar: {erro_msg}"
    
    @staticmethod
    def autenticar_usuario(email, senha):
        """Autentica usuário por email e senha"""
        user = UserRepository.buscar_por_email_e_senha(email, senha)
        if user and bcrypt.checkpw(senha.encode('utf-8'), user['senha'].encode('utf-8')):
            return user
        return None
    
    @staticmethod
    def solicitar_recuperacao_senha(email):
        """
        Inicia o processo de recuperação de senha
        
        Args:
            email (str): E-mail do usuário
        
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            print(f"\n========== RECUPERAÇÃO DE SENHA ==========")
            print(f"1. Buscando usuário com e-mail: {email}")
            
            # Buscar usuário pelo e-mail
            user = UserRepository.buscar_por_email_e_senha(email, None)
            
            if not user:
                print(f"❌ Usuário não encontrado")
                # Por segurança, não revele que o e-mail não existe
                return True, "Se o e-mail estiver cadastrado, você receberá um link de recuperação"
            
            print(f"✅ Usuário encontrado: {user['nome']}")
            
            # Criar token de recuperação
            print(f"\n2. Gerando token de recuperação...")
            token = PasswordResetRepository.criar_token_recuperacao(
                user_id=user['id'],
                email=email
            )
            
            if not token:
                print(f"❌ Erro ao gerar token")
                return False, "Erro ao processar solicitação. Tente novamente."
            
            # Enviar e-mail com o link
            print(f"\n3. Enviando e-mail de recuperação...")
            email_enviado = EmailService.enviar_email_recuperacao(
                destinatario=email,
                token=token,
                nome_usuario=user['nome']
            )
            
            if not email_enviado:
                print(f"❌ Erro ao enviar e-mail")
                return False, "Erro ao enviar e-mail. Tente novamente mais tarde."
            
            print(f"✅ Processo concluído com sucesso!")
            print(f"==========================================\n")
            
            return True, "E-mail de recuperação enviado com sucesso! Verifique sua caixa de entrada."
            
        except Exception as e:
            print(f"❌ Erro na recuperação de senha: {str(e)}")
            print(f"==========================================\n")
            return False, "Erro ao processar solicitação. Tente novamente."
    
    @staticmethod
    def validar_token_recuperacao(token):
        """
        Valida se o token de recuperação é válido
        
        Args:
            token (str): Token a validar
        
        Returns:
            dict: Dados do token se válido, None caso contrário
        """
        try:
            return PasswordResetRepository.validar_token(token)
        except Exception as e:
            print(f"❌ Erro ao validar token: {str(e)}")
            return None
    
    @staticmethod
    def redefinir_senha(token, nova_senha):
        """
        Redefine a senha do usuário usando o token
        
        Args:
            token (str): Token de recuperação
            nova_senha (str): Nova senha
        
        Returns:
            tuple: (sucesso: bool, mensagem: str)
        """
        try:
            print(f"\n========== REDEFINIÇÃO DE SENHA ==========")
            print(f"1. Validando token...")
            
            # Validar token
            token_data = PasswordResetRepository.validar_token(token)
            
            if not token_data:
                print(f"❌ Token inválido ou expirado")
                return False, "Link de recuperação inválido ou expirado. Solicite um novo."
            
            user_id = token_data['user_id']
            email = token_data['email']
            print(f"✅ Token válido para user_id: {user_id}")
            
            # Gerar hash da nova senha
            print(f"\n2. Gerando hash da nova senha...")
            senha_hash = bcrypt.hashpw(nova_senha.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            # Atualizar senha no banco
            print(f"\n3. Atualizando senha no banco...")
            sucesso = UserRepository.atualizar_senha(user_id, senha_hash)
            
            if not sucesso:
                print(f"❌ Erro ao atualizar senha")
                return False, "Erro ao atualizar senha. Tente novamente."
            
            # Marcar token como usado
            print(f"\n4. Marcando token como usado...")
            PasswordResetRepository.marcar_token_usado(token)
            
            # Buscar nome do usuário para o e-mail
            user = UserRepository.buscar_por_id(user_id)
            
            # Enviar e-mail de confirmação
            print(f"\n5. Enviando e-mail de confirmação...")
            EmailService.enviar_confirmacao_troca_senha(
                destinatario=email,
                nome_usuario=user['nome'] if user else 'Usuário'
            )
            
            print(f"✅ Senha redefinida com sucesso!")
            print(f"==========================================\n")
            
            return True, "Senha redefinida com sucesso! Você já pode fazer login."
            
        except Exception as e:
            print(f"❌ Erro ao redefinir senha: {str(e)}")
            print(f"==========================================\n")
            return False, "Erro ao redefinir senha. Tente novamente."
    
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
        return users

    @staticmethod
    def buscar_por_id(user_id):
        """
        Busca um usuário pelo ID e retorna seus dados completos
        ✅ VERSÃO CORRIGIDA - usando 'idade' ao invés de 'data_nascimento'
        """
        try:
            user = UserRepository.buscar_por_id(user_id)
            
            if not user:
                return None
            
            # Retorna um dicionário com os dados do usuário
            return {
                'id': user.get('id'),
                'nome': user.get('nome'),
                'email': user.get('email'),
                'cpf': user.get('cpf'),
                'idade': user.get('idade'),  # ✅ CORRIGIDO: usar 'idade' ao invés de 'data_nascimento'
                'cep': user.get('cep'),
                'foto_perfil': user.get('foto_perfil'),
                'created_at': user.get('created_at'),
                'data_cadastro': user.get('created_at'),
                # Estatísticas opcionais
                'total_pedidos': user.get('total_pedidos', 0),
                'avaliacao': user.get('avaliacao', 0.0),
                'total_favoritos': user.get('total_favoritos', 0)
            }
            
        except Exception as e:
            print(f'Erro ao buscar usuário por ID: {str(e)}')
            return None
    
    @staticmethod
    def atualizar_foto_perfil(user_id, foto_url):
        """
        Atualiza a foto de perfil do usuário
        """
        try:
            return UserRepository.atualizar_foto_perfil(user_id, foto_url)
        except Exception as e:
            print(f'Erro ao atualizar foto de perfil: {str(e)}')
            return False
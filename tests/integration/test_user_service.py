"""
Testes de integração para o serviço de usuários
"""
import pytest
from service.user_service import UserService

class TestUserService:
    
    def test_cadastrar_usuario_sucesso(self, clean_database, user_data):
        """Testa cadastro de usuário com sucesso"""
        status, mensagem = UserService.cadastrar_usuario(user_data)
        
        assert status is True
        assert "sucesso" in mensagem.lower()
    
    def test_cadastrar_usuario_email_duplicado(self, clean_database, user_data):
        """Testa cadastro com email duplicado"""
        # Primeiro cadastro
        UserService.cadastrar_usuario(user_data)
        
        # Segundo cadastro com mesmo email
        status, mensagem = UserService.cadastrar_usuario(user_data)
        
        assert status is False
    
    def test_autenticar_usuario_sucesso(self, clean_database, user_data):
        """Testa autenticação com credenciais corretas"""
        # Cadastrar usuário
        UserService.cadastrar_usuario(user_data)
        
        # Autenticar
        user = UserService.autenticar_usuario(
            user_data['email'], 
            user_data['senha']
        )
        
        assert user is not None
        assert user['email'] == user_data['email']
    
    def test_autenticar_usuario_senha_incorreta(self, clean_database, user_data):
        """Testa autenticação com senha incorreta"""
        # Cadastrar usuário
        UserService.cadastrar_usuario(user_data)
        
        # Tentar autenticar com senha errada
        user = UserService.autenticar_usuario(
            user_data['email'], 
            'senha_errada'
        )
        
        assert user is None
    
    def test_autenticar_usuario_inexistente(self, clean_database):
        """Testa autenticação de usuário que não existe"""
        user = UserService.autenticar_usuario(
            'naoexiste@test.com', 
            'senha123'
        )
        
        assert user is None
    
    def test_buscar_usuario_por_id(self, clean_database, user_data):
        """Testa busca de usuário por ID"""
        # Cadastrar usuário
        UserService.cadastrar_usuario(user_data)
        
        # Buscar por email para pegar o ID
        user = UserService.autenticar_usuario(
            user_data['email'], 
            user_data['senha']
        )
        
        # Buscar por ID
        user_encontrado = UserService.buscar_por_id(user['id'])
        
        assert user_encontrado is not None
        assert user_encontrado['email'] == user_data['email']
    
    def test_atualizar_usuario(self, clean_database, user_data):
        """Testa atualização de dados do usuário"""
        # Cadastrar usuário
        UserService.cadastrar_usuario(user_data)
        
        # Buscar usuário
        user = UserService.autenticar_usuario(
            user_data['email'], 
            user_data['senha']
        )
        
        # Atualizar dados
        novos_dados = {
            'id': user['id'],
            'nome': 'João Silva Santos',
            'cpf': user_data['cpf'],
            'cep': '57000-001',
            'idade': user_data['idade'],
            'email': user_data['email']
        }
        
        resultado = UserService.atualizar_usuario(novos_dados)
        
        assert resultado is True
        
        # Verificar se foi atualizado
        user_atualizado = UserService.buscar_por_id(user['id'])
        assert user_atualizado['nome'] == 'João Silva Santos'
        assert user_atualizado['cep'] == '57000-001'
    
    def test_listar_usuarios(self, clean_database, user_data):
        """Testa listagem de usuários"""
        # Cadastrar alguns usuários
        UserService.cadastrar_usuario(user_data)
        
        user_data2 = user_data.copy()
        user_data2['email'] = 'maria@test.com'
        user_data2['cpf'] = '987.654.321-00'
        UserService.cadastrar_usuario(user_data2)
        
        # Listar
        usuarios = UserService.lista()
        
        assert len(usuarios) >= 2
    
    def test_deletar_usuario(self, clean_database, user_data):
        """Testa deleção de usuário"""
        # Cadastrar usuário
        UserService.cadastrar_usuario(user_data)
        
        # Buscar usuário
        user = UserService.autenticar_usuario(
            user_data['email'], 
            user_data['senha']
        )
        
        # Deletar
        resultado = UserService.deletar_usuario(user['id'])
        
        assert resultado is True
        
        # Verificar se foi deletado
        user_deletado = UserService.buscar_por_id(user['id'])
        assert user_deletado is None
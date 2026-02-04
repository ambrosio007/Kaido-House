"""
Testes unitários para o modelo de usuário
"""
import pytest
import bcrypt
from model.user_model import UserModel

class TestUserModel:
    
    def test_create_user_model(self):
        """Testa criação de usuário"""
        user = UserModel(
            nome='João Silva',
            cpf='123.456.789-00',
            cep='57000-000',
            idade='1990-01-01',
            email='joao@test.com',
            senha='senha123'
        )
        
        assert user.nome == 'João Silva'
        assert user.cpf == '123.456.789-00'
        assert user.cep == '57000-000'
        assert user.idade == '1990-01-01'
        assert user.email == 'joao@test.com'
        assert user.id is not None
        assert len(user.id) == 36  # UUID
    
    def test_password_is_hashed(self):
        """Testa se a senha é criptografada"""
        user = UserModel(
            nome='João Silva',
            cpf='123.456.789-00',
            cep='57000-000',
            idade='1990-01-01',
            email='joao@test.com',
            senha='senha123'
        )
        
        # Senha deve estar hasheada
        assert user.senha_hash != 'senha123'
        
        # Deve poder verificar a senha
        assert bcrypt.checkpw('senha123'.encode('utf-8'), user.senha_hash.encode('utf-8'))
    
    def test_to_dict_excludes_password(self):
        """Testa se to_dict não inclui a senha"""
        user = UserModel(
            nome='João Silva',
            cpf='123.456.789-00',
            cep='57000-000',
            idade='1990-01-01',
            email='joao@test.com',
            senha='senha123'
        )
        
        user_dict = user.to_dict()
        
        assert 'senha' not in user_dict
        assert 'senha_hash' not in user_dict
        assert user_dict['nome'] == 'João Silva'
        assert user_dict['email'] == 'joao@test.com'
    
    def test_unique_ids(self):
        """Testa se cada usuário tem um ID único"""
        user1 = UserModel(
            nome='João',
            cpf='111.111.111-11',
            cep='57000-000',
            idade='1990-01-01',
            email='joao@test.com',
            senha='senha123'
        )
        
        user2 = UserModel(
            nome='Maria',
            cpf='222.222.222-22',
            cep='57000-000',
            idade='1995-05-05',
            email='maria@test.com',
            senha='senha456'
        )
        
        assert user1.id != user2.id
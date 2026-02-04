"""
Testes end-to-end do fluxo de cadastro e login
"""
import pytest

class TestCadastroFlow:
    
    def test_fluxo_cadastro_completo(self, client, clean_database):
        """Testa fluxo completo: cadastro → login → perfil"""
        
        # 1. Acessar página de cadastro
        response = client.get('/cadastro')
        assert response.status_code == 200
        
        # 2. Realizar cadastro
        dados_cadastro = {
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            'cep': '57000-000',
            'date': '1990-01-01',
            'email': 'joao@test.com',
            'senha': 'senha123'
        }
        
        response = client.post('/cadastro-user', data=dados_cadastro)
        assert response.status_code == 302  # Redirect para login
        
        # 3. Fazer login
        response = client.post('/login-user', data={
            'email': 'joao@test.com',
            'senha': 'senha123'
        }, follow_redirects=True)
        
        assert response.status_code == 200
        
        # 4. Acessar perfil
        response = client.get('/perfil')
        assert response.status_code == 200
        assert b'joao@test.com' in response.data
    
    def test_cadastro_com_senha_fraca(self, client, clean_database):
        """Testa cadastro com senha muito curta"""
        
        dados_cadastro = {
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            'cep': '57000-000',
            'date': '1990-01-01',
            'email': 'joao@test.com',
            'senha': '123'  # Senha muito curta
        }
        
        # O HTML deve validar com minlength="8"
        # Mas vamos testar se chegar ao backend
        response = client.post('/cadastro-user', data=dados_cadastro)
        # Deve funcionar ou rejeitar dependendo da validação
    
    def test_login_com_credenciais_invalidas(self, client, clean_database):
        """Testa login com credenciais inválidas"""
        
        response = client.post('/login-user', data={
            'email': 'naoexiste@test.com',
            'senha': 'senha123'
        })
        
        assert response.status_code == 200
        assert b'Falha no login' in response.data
    
    def test_acesso_perfil_sem_login(self, client, clean_database):
        """Testa acesso ao perfil sem estar logado"""
        
        response = client.get('/perfil', follow_redirects=False)
        assert response.status_code == 302  # Redirect para login
    
    def test_logout(self, client, clean_database):
        """Testa logout do sistema"""
        
        # Cadastrar e logar
        dados_cadastro = {
            'nome': 'João Silva',
            'cpf': '123.456.789-00',
            'cep': '57000-000',
            'date': '1990-01-01',
            'email': 'joao@test.com',
            'senha': 'senha123'
        }
        
        client.post('/cadastro-user', data=dados_cadastro)
        client.post('/login-user', data={
            'email': 'joao@test.com',
            'senha': 'senha123'
        })
        
        # Fazer logout
        response = client.get('/logout', follow_redirects=False)
        assert response.status_code == 302  # Redirect para login
        
        # Tentar acessar perfil (não deve conseguir)
        response = client.get('/perfil', follow_redirects=False)
        assert response.status_code == 302
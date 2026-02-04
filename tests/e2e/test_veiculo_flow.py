"""
Testes end-to-end do fluxo de veículos
"""
import pytest
import json

class TestVeiculoFlow:
    
    def test_cadastrar_veiculo_completo(self, client, clean_database, authenticated_user):
        """Testa cadastro completo de um veículo"""
        
        dados_veiculo = {
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2020,
            'km': 50000,
            'cor': 'Prata',
            'preco': 85000.00,
            'descricao': 'Veículo em ótimo estado'
        }
        
        response = client.post('/cadastro-veiculo', data=dados_veiculo)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_listar_meus_veiculos(self, client, clean_database, authenticated_user):
        """Testa listagem de veículos do usuário"""
        
        # Cadastrar um veículo
        dados_veiculo = {
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano': 2019,
            'km': 30000,
            'cor': 'Preto',
            'preco': 75000.00,
            'descricao': 'Veículo impecável'
        }
        
        client.post('/cadastro-veiculo', data=dados_veiculo)
        
        # Listar veículos
        response = client.get('/meus-veiculos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['marca'] == 'Honda'
    
    def test_listar_todos_veiculos(self, client, clean_database, authenticated_user):
        """Testa listagem pública de veículos"""
        
        # Cadastrar veículo
        dados_veiculo = {
            'marca': 'Ford',
            'modelo': 'Focus',
            'ano': 2018,
            'km': 40000,
            'cor': 'Branco',
            'preco': 55000.00,
            'descricao': 'Carro econômico'
        }
        
        client.post('/cadastro-veiculo', data=dados_veiculo)
        
        # Fazer logout
        client.get('/logout')
        
        # Listar todos (sem estar logado)
        response = client.get('/veiculos')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_cadastrar_veiculo_sem_autenticacao(self, client, clean_database):
        """Testa que não é possível cadastrar sem login"""
        
        dados_veiculo = {
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2020,
            'km': 50000,
            'cor': 'Prata',
            'preco': 85000.00,
            'descricao': 'Veículo em ótimo estado'
        }
        
        response = client.post('/cadastro-veiculo', data=dados_veiculo)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_deletar_veiculo_proprio(self, client, clean_database, authenticated_user):
        """Testa deleção do próprio veículo"""
        
        # Cadastrar veículo
        dados_veiculo = {
            'marca': 'Chevrolet',
            'modelo': 'Onix',
            'ano': 2021,
            'km': 15000,
            'cor': 'Vermelho',
            'preco': 60000.00,
            'descricao': 'Carro novo'
        }
        
        response = client.post('/cadastro-veiculo', data=dados_veiculo)
        
        # Pegar lista de veículos para obter o ID
        response = client.get('/meus-veiculos')
        veiculos = json.loads(response.data)
        veiculo_id = veiculos[0]['id']
        
        # Deletar veículo
        response = client.delete(f'/veiculo/{veiculo_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
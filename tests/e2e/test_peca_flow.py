"""
Testes end-to-end do fluxo de peças
"""
import pytest
import json


class TestPecaFlow:
    
    def test_cadastrar_peca_completo(self, client, clean_database, authenticated_user):
        """Testa cadastro completo de uma peça"""
        
        dados_peca = {
            'nome': 'Motor 1.8',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2020,
            'preco': 15000.00,
            'descricao': 'Motor completo revisado',
            'estado': 'usado'
        }
        
        response = client.post('/cadastro-peca', data=dados_peca)
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
    
    def test_listar_minhas_pecas(self, client, clean_database, authenticated_user):
        """Testa listagem de peças do usuário"""
        
        # Cadastrar uma peça
        dados_peca = {
            'nome': 'Câmbio Manual',
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano': 2019,
            'preco': 8000.00,
            'descricao': 'Câmbio 5 marchas',
            'estado': 'novo'
        }
        
        client.post('/cadastro-peca', data=dados_peca)
        
        # Listar peças
        response = client.get('/minhas-pecas')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
        assert data[0]['nome'] == 'Câmbio Manual'
    
    def test_listar_todas_pecas(self, client, clean_database, authenticated_user):
        """Testa listagem pública de peças"""
        
        # Cadastrar peça
        dados_peca = {
            'nome': 'Radiador',
            'marca': 'Ford',
            'modelo': 'Focus',
            'ano': 2018,
            'preco': 800.00,
            'descricao': 'Radiador original',
            'estado': 'usado'
        }
        
        client.post('/cadastro-peca', data=dados_peca)
        
        # Fazer logout
        client.get('/logout')
        
        # Listar todas (sem estar logado)
        response = client.get('/pecas')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert len(data) >= 1
    
    def test_cadastrar_peca_sem_autenticacao(self, client, clean_database):
        """Testa que não é possível cadastrar sem login"""
        
        dados_peca = {
            'nome': 'Motor 1.8',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2020,
            'preco': 15000.00,
            'descricao': 'Motor completo revisado',
            'estado': 'usado'
        }
        
        response = client.post('/cadastro-peca', data=dados_peca)
        
        assert response.status_code == 401
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_deletar_peca_propria(self, client, clean_database, authenticated_user):
        """Testa deleção da própria peça"""
        
        # Cadastrar peça
        dados_peca = {
            'nome': 'Farol',
            'marca': 'Chevrolet',
            'modelo': 'Onix',
            'ano': 2021,
            'preco': 500.00,
            'descricao': 'Farol dianteiro',
            'estado': 'novo'
        }
        
        response = client.post('/cadastro-peca', data=dados_peca)
        
        # Pegar lista de peças para obter o ID
        response = client.get('/minhas-pecas')
        pecas = json.loads(response.data)
        peca_id = pecas[0]['id']
        
        # Deletar peça
        response = client.delete(f'/peca/{peca_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'message' in data
    
    def test_buscar_peca_por_id(self, client, clean_database, authenticated_user):
        """Testa busca de peça específica por ID"""
        
        # Cadastrar peça
        dados_peca = {
            'nome': 'Volante',
            'marca': 'Fiat',
            'modelo': 'Uno',
            'ano': 2015,
            'preco': 300.00,
            'descricao': 'Volante esportivo',
            'estado': 'usado'
        }
        
        client.post('/cadastro-peca', data=dados_peca)
        
        # Pegar ID
        response = client.get('/minhas-pecas')
        pecas = json.loads(response.data)
        peca_id = pecas[0]['id']
        
        # Buscar por ID
        response = client.get(f'/peca/{peca_id}')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['nome'] == 'Volante'
        assert data['marca'] == 'Fiat'
    
    def test_atualizar_peca(self, client, clean_database, authenticated_user):
        """Testa atualização de peça"""
        
        # Cadastrar peça
        dados_peca = {
            'nome': 'Suspensão',
            'marca': 'Volkswagen',
            'modelo': 'Gol',
            'ano': 2016,
            'preco': 1200.00,
            'descricao': 'Suspensão dianteira',
            'estado': 'usado'
        }
        
        client.post('/cadastro-peca', data=dados_peca)
        
        # Pegar ID
        response = client.get('/minhas-pecas')
        pecas = json.loads(response.data)
        peca_id = pecas[0]['id']
        
        # Atualizar peça
        dados_atualizados = {
            'id': peca_id,
            'nome': 'Suspensão Completa',
            'marca': 'Volkswagen',
            'modelo': 'Gol',
            'ano': 2016,
            'preco': 1500.00,
            'descricao': 'Suspensão dianteira e traseira',
            'estado': 'recondicionado'
        }
        
        response = client.put(f'/peca/{peca_id}', 
                            data=json.dumps(dados_atualizados),
                            content_type='application/json')
        
        assert response.status_code == 200
    
    def test_filtrar_pecas_por_marca(self, client, clean_database, authenticated_user):
        """Testa filtro de peças por marca"""
        
        # Cadastrar peças de diferentes marcas
        dados_peca1 = {
            'nome': 'Motor',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2020,
            'preco': 15000.00,
            'descricao': 'Motor original',
            'estado': 'usado'
        }
        
        dados_peca2 = {
            'nome': 'Câmbio',
            'marca': 'Honda',
            'modelo': 'Civic',
            'ano': 2019,
            'preco': 8000.00,
            'descricao': 'Câmbio manual',
            'estado': 'usado'
        }
        
        client.post('/cadastro-peca', data=dados_peca1)
        client.post('/cadastro-peca', data=dados_peca2)
        
        # Filtrar por marca Toyota
        response = client.get('/pecas?marca=Toyota')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(p['marca'] == 'Toyota' for p in data)
    
    def test_filtrar_pecas_por_estado(self, client, clean_database, authenticated_user):
        """Testa filtro de peças por estado (novo/usado)"""
        
        # Cadastrar peças com diferentes estados
        dados_peca_nova = {
            'nome': 'Bateria',
            'marca': 'Moura',
            'modelo': 'Universal',
            'ano': 2023,
            'preco': 600.00,
            'descricao': 'Bateria 60Ah',
            'estado': 'novo'
        }
        
        dados_peca_usada = {
            'nome': 'Alternador',
            'marca': 'Bosch',
            'modelo': 'Universal',
            'ano': 2020,
            'preco': 400.00,
            'descricao': 'Alternador testado',
            'estado': 'usado'
        }
        
        client.post('/cadastro-peca', data=dados_peca_nova)
        client.post('/cadastro-peca', data=dados_peca_usada)
        
        # Filtrar por estado novo
        response = client.get('/pecas?estado=novo')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert all(p['estado'] == 'novo' for p in data)
    
    def test_cadastrar_multiplas_pecas(self, client, clean_database, authenticated_user):
        """Testa cadastro de múltiplas peças do mesmo usuário"""
        
        pecas = [
            {
                'nome': 'Motor',
                'marca': 'Fiat',
                'modelo': 'Palio',
                'ano': 2015,
                'preco': 5000.00,
                'descricao': 'Motor 1.0',
                'estado': 'usado'
            },
            {
                'nome': 'Câmbio',
                'marca': 'Fiat',
                'modelo': 'Palio',
                'ano': 2015,
                'preco': 3000.00,
                'descricao': 'Câmbio 5 marchas',
                'estado': 'usado'
            },
            {
                'nome': 'Radiador',
                'marca': 'Fiat',
                'modelo': 'Palio',
                'ano': 2015,
                'preco': 400.00,
                'descricao': 'Radiador original',
                'estado': 'usado'
            }
        ]
        
        # Cadastrar todas as peças
        for peca in pecas:
            response = client.post('/cadastro-peca', data=peca)
            assert response.status_code == 200
        
        # Verificar que todas foram cadastradas
        response = client.get('/minhas-pecas')
        data = json.loads(response.data)
        assert len(data) == 3
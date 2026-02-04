"""
Testes de integração para o serviço de peças
"""
import pytest
from service.pecas_service import PecaService
from service.user_service import UserService


class TestPecaService:
    
    def test_cadastrar_peca_sucesso(self, clean_database, user_data, peca_data):
        """Testa cadastro de peça com sucesso"""
        # Criar usuário primeiro
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Adicionar usuario_id aos dados da peça
        peca_data['usuario_id'] = user['id']
        
        # Cadastrar peça
        status, mensagem = PecaService.cadastrar_peca(peca_data)
        
        assert status is True
        assert "sucesso" in mensagem.lower()
    
    def test_listar_pecas_usuario(self, clean_database, user_data, peca_data):
        """Testa listagem de peças de um usuário"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar algumas peças
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        peca_data2 = peca_data.copy()
        peca_data2['nome'] = 'Câmbio Manual'
        peca_data2['preco'] = 8000.00
        PecaService.cadastrar_peca(peca_data2)
        
        # Listar peças do usuário
        pecas = PecaService.listar_por_usuario(user['id'])
        
        assert len(pecas) == 2
        assert any(p['nome'] == 'Motor 1.8' for p in pecas)
        assert any(p['nome'] == 'Câmbio Manual' for p in pecas)
    
    def test_listar_todas_pecas(self, clean_database, user_data, peca_data):
        """Testa listagem de todas as peças"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peça
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        # Listar todas
        pecas = PecaService.lista()
        
        assert len(pecas) >= 1
        assert any(p['nome'] == 'Motor 1.8' for p in pecas)
    
    def test_buscar_peca_por_id(self, clean_database, user_data, peca_data):
        """Testa busca de peça por ID"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peça
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        # Buscar peça
        pecas = PecaService.listar_por_usuario(user['id'])
        peca_id = pecas[0]['id']
        
        peca_encontrada = PecaService.buscar_por_id(peca_id)
        
        assert peca_encontrada is not None
        assert peca_encontrada['nome'] == 'Motor 1.8'
        assert peca_encontrada['marca'] == 'Toyota'
    
    def test_atualizar_peca(self, clean_database, user_data, peca_data):
        """Testa atualização de peça"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peça
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        # Buscar peça
        pecas = PecaService.listar_por_usuario(user['id'])
        peca_id = pecas[0]['id']
        
        # Atualizar dados
        novos_dados = {
            'id': peca_id,
            'nome': 'Motor 2.0',
            'marca': 'Toyota',
            'modelo': 'Corolla',
            'ano': 2021,
            'preco': 18000.00,
            'descricao': 'Motor atualizado',
            'estado': 'novo'
        }
        
        resultado = PecaService.atualizar_peca(novos_dados)
        
        assert resultado is True
        
        # Verificar atualização
        peca_atualizada = PecaService.buscar_por_id(peca_id)
        assert peca_atualizada['nome'] == 'Motor 2.0'
        assert peca_atualizada['preco'] == 18000.00
        assert peca_atualizada['estado'] == 'novo'
    
    def test_deletar_peca(self, clean_database, user_data, peca_data):
        """Testa deleção de peça"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peça
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        # Buscar peça
        pecas = PecaService.listar_por_usuario(user['id'])
        peca_id = pecas[0]['id']
        
        # Deletar
        resultado = PecaService.deletar_peca(peca_id)
        
        assert resultado is True
        
        # Verificar deleção
        peca_deletada = PecaService.buscar_por_id(peca_id)
        assert peca_deletada is None
    
    def test_buscar_pecas_por_marca(self, clean_database, user_data, peca_data):
        """Testa busca de peças por marca"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peças de diferentes marcas
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        peca_data2 = peca_data.copy()
        peca_data2['nome'] = 'Câmbio'
        peca_data2['marca'] = 'Honda'
        PecaService.cadastrar_peca(peca_data2)
        
        # Buscar por marca
        pecas_toyota = PecaService.buscar_por_marca('Toyota')
        
        assert len(pecas_toyota) >= 1
        assert all(p['marca'] == 'Toyota' for p in pecas_toyota)
    
    def test_buscar_pecas_por_modelo(self, clean_database, user_data, peca_data):
        """Testa busca de peças por modelo"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar peças
        peca_data['usuario_id'] = user['id']
        PecaService.cadastrar_peca(peca_data)
        
        # Buscar por modelo
        pecas_corolla = PecaService.buscar_por_modelo('Corolla')
        
        assert len(pecas_corolla) >= 1
        assert all(p['modelo'] == 'Corolla' for p in pecas_corolla)
    
    def test_cadastrar_peca_sem_usuario(self, clean_database, peca_data):
        """Testa que não é possível cadastrar peça sem usuário"""
        peca_data['usuario_id'] = 'usuario-inexistente'
        
        status, mensagem = PecaService.cadastrar_peca(peca_data)
        
        # Deve falhar devido à constraint de foreign key
        assert status is False
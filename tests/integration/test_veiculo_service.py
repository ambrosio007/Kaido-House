"""
Testes de integração para o serviço de veículos
"""
import pytest
from service.veiculos_service import VeiculoService
from service.user_service import UserService


class TestVeiculoService:
    
    def test_cadastrar_veiculo_sucesso(self, clean_database, user_data, veiculo_data):
        """Testa cadastro de veículo com sucesso"""
        # Criar usuário primeiro
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Adicionar usuario_id aos dados do veículo
        veiculo_data['usuario_id'] = user['id']
        
        # Cadastrar veículo
        status, mensagem = VeiculoService.cadastrar_veiculo(veiculo_data)
        
        assert status is True
        assert "sucesso" in mensagem.lower()
    
    def test_listar_veiculos_usuario(self, clean_database, user_data, veiculo_data):
        """Testa listagem de veículos de um usuário"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar alguns veículos
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        veiculo_data2 = veiculo_data.copy()
        veiculo_data2['marca'] = 'Honda'
        veiculo_data2['modelo'] = 'Civic'
        veiculo_data2['preco'] = 75000.00
        VeiculoService.cadastrar_veiculo(veiculo_data2)
        
        # Listar veículos do usuário
        veiculos = VeiculoService.listar_por_usuario(user['id'])
        
        assert len(veiculos) == 2
        assert any(v['marca'] == 'Toyota' for v in veiculos)
        assert any(v['marca'] == 'Honda' for v in veiculos)
    
    def test_listar_todos_veiculos(self, clean_database, user_data, veiculo_data):
        """Testa listagem de todos os veículos"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículo
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Listar todos
        veiculos = VeiculoService.lista()
        
        assert len(veiculos) >= 1
        assert any(v['marca'] == 'Toyota' for v in veiculos)
    
    def test_buscar_veiculo_por_id(self, clean_database, user_data, veiculo_data):
        """Testa busca de veículo por ID"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículo
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Buscar veículo
        veiculos = VeiculoService.listar_por_usuario(user['id'])
        veiculo_id = veiculos[0]['id']
        
        veiculo_encontrado = VeiculoService.buscar_por_id(veiculo_id)
        
        assert veiculo_encontrado is not None
        assert veiculo_encontrado['marca'] == 'Toyota'
        assert veiculo_encontrado['modelo'] == 'Corolla'
    
    def test_atualizar_veiculo(self, clean_database, user_data, veiculo_data):
        """Testa atualização de veículo"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículo
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Buscar veículo
        veiculos = VeiculoService.listar_por_usuario(user['id'])
        veiculo_id = veiculos[0]['id']
        
        # Atualizar dados
        novos_dados = {
            'id': veiculo_id,
            'marca': 'Toyota',
            'modelo': 'Corolla XEI',
            'ano': 2021,
            'km': 55000,
            'cor': 'Preto',
            'preco': 90000.00,
            'descricao': 'Veículo atualizado'
        }
        
        resultado = VeiculoService.atualizar_veiculo(novos_dados)
        
        assert resultado is True
        
        # Verificar atualização
        veiculo_atualizado = VeiculoService.buscar_por_id(veiculo_id)
        assert veiculo_atualizado['modelo'] == 'Corolla XEI'
        assert veiculo_atualizado['km'] == 55000
        assert veiculo_atualizado['preco'] == 90000.00
    
    def test_deletar_veiculo(self, clean_database, user_data, veiculo_data):
        """Testa deleção de veículo"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículo
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Buscar veículo
        veiculos = VeiculoService.listar_por_usuario(user['id'])
        veiculo_id = veiculos[0]['id']
        
        # Deletar
        resultado = VeiculoService.deletar_veiculo(veiculo_id)
        
        assert resultado is True
        
        # Verificar deleção
        veiculo_deletado = VeiculoService.buscar_por_id(veiculo_id)
        assert veiculo_deletado is None
    
    def test_buscar_veiculos_por_marca(self, clean_database, user_data, veiculo_data):
        """Testa busca de veículos por marca"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículos de diferentes marcas
        veiculo_data['usuario_id'] = user['id']
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        veiculo_data2 = veiculo_data.copy()
        veiculo_data2['marca'] = 'Honda'
        veiculo_data2['modelo'] = 'Civic'
        VeiculoService.cadastrar_veiculo(veiculo_data2)
        
        # Buscar por marca
        veiculos_toyota = VeiculoService.buscar_por_marca('Toyota')
        
        assert len(veiculos_toyota) >= 1
        assert all(v['marca'] == 'Toyota' for v in veiculos_toyota)
    
    def test_buscar_veiculos_por_faixa_preco(self, clean_database, user_data, veiculo_data):
        """Testa busca de veículos por faixa de preço"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículos com diferentes preços
        veiculo_data['usuario_id'] = user['id']
        veiculo_data['preco'] = 50000.00
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        veiculo_data2 = veiculo_data.copy()
        veiculo_data2['marca'] = 'Honda'
        veiculo_data2['preco'] = 100000.00
        VeiculoService.cadastrar_veiculo(veiculo_data2)
        
        # Buscar na faixa de 40k a 60k
        veiculos_faixa = VeiculoService.buscar_por_faixa_preco(40000, 60000)
        
        assert len(veiculos_faixa) >= 1
        assert all(40000 <= v['preco'] <= 60000 for v in veiculos_faixa)
    
    def test_buscar_veiculos_por_ano(self, clean_database, user_data, veiculo_data):
        """Testa busca de veículos por ano"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículos
        veiculo_data['usuario_id'] = user['id']
        veiculo_data['ano'] = 2020
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Buscar por ano
        veiculos_2020 = VeiculoService.buscar_por_ano(2020)
        
        assert len(veiculos_2020) >= 1
        assert all(v['ano'] == 2020 for v in veiculos_2020)
    
    def test_cadastrar_veiculo_sem_usuario(self, clean_database, veiculo_data):
        """Testa que não é possível cadastrar veículo sem usuário"""
        veiculo_data['usuario_id'] = 'usuario-inexistente'
        
        status, mensagem = VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Deve falhar devido à constraint de foreign key
        assert status is False
    
    def test_atualizar_km_veiculo(self, clean_database, user_data, veiculo_data):
        """Testa atualização específica da quilometragem"""
        # Criar usuário
        UserService.cadastrar_usuario(user_data)
        user = UserService.autenticar_usuario(user_data['email'], user_data['senha'])
        
        # Cadastrar veículo
        veiculo_data['usuario_id'] = user['id']
        veiculo_data['km'] = 50000
        VeiculoService.cadastrar_veiculo(veiculo_data)
        
        # Buscar veículo
        veiculos = VeiculoService.listar_por_usuario(user['id'])
        veiculo_id = veiculos[0]['id']
        
        # Atualizar km
        veiculo = VeiculoService.buscar_por_id(veiculo_id)
        veiculo['km'] = 60000
        
        resultado = VeiculoService.atualizar_veiculo(veiculo)
        assert resultado is True
        
        # Verificar atualização
        veiculo_atualizado = VeiculoService.buscar_por_id(veiculo_id)
        assert veiculo_atualizado['km'] == 60000
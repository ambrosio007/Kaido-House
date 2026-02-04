"""
Testes unitários para o modelo de Veículo
"""
import pytest
from model.veiculos_model import VeiculoModel


class TestVeiculoModel:
    
    def test_create_veiculo_model(self):
        """Testa criação de veículo"""
        veiculo = VeiculoModel(
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            km=50000,
            cor='Prata',
            preco=85000.00,
            descricao='Veículo em ótimo estado',
            usuario_id='user-123'
        )
        
        assert veiculo.marca == 'Toyota'
        assert veiculo.modelo == 'Corolla'
        assert veiculo.ano == 2020
        assert veiculo.km == 50000
        assert veiculo.cor == 'Prata'
        assert veiculo.preco == 85000.00
        assert veiculo.descricao == 'Veículo em ótimo estado'
        assert veiculo.usuario_id == 'user-123'
        assert veiculo.id is not None
        assert len(veiculo.id) == 36  # UUID
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        veiculo = VeiculoModel(
            marca='Honda',
            modelo='Civic',
            ano=2019,
            km=30000,
            cor='Preto',
            preco=75000.00,
            descricao='Veículo impecável',
            usuario_id='user-456'
        )
        
        veiculo_dict = veiculo.to_dict()
        
        assert veiculo_dict['marca'] == 'Honda'
        assert veiculo_dict['modelo'] == 'Civic'
        assert veiculo_dict['ano'] == 2019
        assert veiculo_dict['km'] == 30000
        assert veiculo_dict['cor'] == 'Preto'
        assert veiculo_dict['preco'] == 75000.00
        assert 'id' in veiculo_dict
        assert 'usuario_id' in veiculo_dict
    
    def test_unique_ids(self):
        """Testa se cada veículo tem um ID único"""
        veiculo1 = VeiculoModel(
            marca='Ford',
            modelo='Focus',
            ano=2018,
            km=40000,
            cor='Branco',
            preco=55000.00,
            descricao='Carro econômico',
            usuario_id='user-1'
        )
        
        veiculo2 = VeiculoModel(
            marca='Chevrolet',
            modelo='Onix',
            ano=2021,
            km=15000,
            cor='Vermelho',
            preco=60000.00,
            descricao='Carro novo',
            usuario_id='user-2'
        )
        
        assert veiculo1.id != veiculo2.id
    
    def test_preco_validation(self):
        """Testa validação de preço"""
        veiculo = VeiculoModel(
            marca='Fiat',
            modelo='Uno',
            ano=2015,
            km=80000,
            cor='Azul',
            preco=25000.00,
            descricao='Primeiro carro',
            usuario_id='user-789'
        )
        
        assert veiculo.preco > 0
        assert isinstance(veiculo.preco, float)
    
    def test_km_validation(self):
        """Testa validação de quilometragem"""
        veiculo = VeiculoModel(
            marca='Volkswagen',
            modelo='Gol',
            ano=2020,
            km=0,  # Carro zero km
            cor='Branco',
            preco=45000.00,
            descricao='Carro zero km',
            usuario_id='user-999'
        )
        
        assert veiculo.km >= 0
        assert isinstance(veiculo.km, int)
    
    def test_ano_validation(self):
        """Testa validação de ano"""
        veiculo = VeiculoModel(
            marca='Nissan',
            modelo='Versa',
            ano=2022,
            km=10000,
            cor='Cinza',
            preco=70000.00,
            descricao='Seminovo',
            usuario_id='user-555'
        )
        
        assert isinstance(veiculo.ano, int)
        assert veiculo.ano >= 1900
        assert veiculo.ano <= 2025
    
    def test_cores_validas(self):
        """Testa diferentes cores válidas"""
        cores = ['Preto', 'Branco', 'Prata', 'Vermelho', 'Azul', 'Cinza', 'Verde']
        
        for cor in cores:
            veiculo = VeiculoModel(
                marca='Test',
                modelo='Test',
                ano=2020,
                km=10000,
                cor=cor,
                preco=50000.00,
                descricao='Test',
                usuario_id='user-test'
            )
            assert veiculo.cor == cor
    
    def test_marcas_populares(self):
        """Testa criação com marcas populares brasileiras"""
        marcas = ['Fiat', 'Volkswagen', 'Chevrolet', 'Ford', 'Toyota', 'Honda', 'Hyundai']
        
        for marca in marcas:
            veiculo = VeiculoModel(
                marca=marca,
                modelo='Test Model',
                ano=2020,
                km=20000,
                cor='Prata',
                preco=60000.00,
                descricao='Test vehicle',
                usuario_id='user-test'
            )
            assert veiculo.marca == marca
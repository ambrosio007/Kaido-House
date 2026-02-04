"""
Testes unitários para o modelo de Peça
"""
import pytest
from model.pecas_model import PecaModel


class TestPecaModel:
    
    def test_create_peca_model(self):
        """Testa criação de peça"""
        peca = PecaModel(
            nome='Motor 1.8',
            marca='Toyota',
            modelo='Corolla',
            ano=2020,
            preco=15000.00,
            descricao='Motor completo revisado',
            estado='usado',
            usuario_id='user-123'
        )
        
        assert peca.nome == 'Motor 1.8'
        assert peca.marca == 'Toyota'
        assert peca.modelo == 'Corolla'
        assert peca.ano == 2020
        assert peca.preco == 15000.00
        assert peca.descricao == 'Motor completo revisado'
        assert peca.estado == 'usado'
        assert peca.usuario_id == 'user-123'
        assert peca.id is not None
        assert len(peca.id) == 36  # UUID
    
    def test_to_dict(self):
        """Testa conversão para dicionário"""
        peca = PecaModel(
            nome='Câmbio Manual',
            marca='Honda',
            modelo='Civic',
            ano=2019,
            preco=8000.00,
            descricao='Câmbio 5 marchas',
            estado='novo',
            usuario_id='user-456'
        )
        
        peca_dict = peca.to_dict()
        
        assert peca_dict['nome'] == 'Câmbio Manual'
        assert peca_dict['marca'] == 'Honda'
        assert peca_dict['modelo'] == 'Civic'
        assert peca_dict['ano'] == 2019
        assert peca_dict['preco'] == 8000.00
        assert peca_dict['estado'] == 'novo'
        assert 'id' in peca_dict
        assert 'usuario_id' in peca_dict
    
    def test_unique_ids(self):
        """Testa se cada peça tem um ID único"""
        peca1 = PecaModel(
            nome='Peça 1',
            marca='Marca A',
            modelo='Modelo A',
            ano=2020,
            preco=1000.00,
            descricao='Descrição 1',
            estado='novo',
            usuario_id='user-1'
        )
        
        peca2 = PecaModel(
            nome='Peça 2',
            marca='Marca B',
            modelo='Modelo B',
            ano=2021,
            preco=2000.00,
            descricao='Descrição 2',
            estado='usado',
            usuario_id='user-2'
        )
        
        assert peca1.id != peca2.id
    
    def test_preco_validation(self):
        """Testa validação de preço"""
        peca = PecaModel(
            nome='Radiador',
            marca='Chevrolet',
            modelo='Onix',
            ano=2021,
            preco=500.00,
            descricao='Radiador original',
            estado='novo',
            usuario_id='user-789'
        )
        
        assert peca.preco > 0
        assert isinstance(peca.preco, float)
    
    def test_estado_values(self):
        """Testa valores válidos de estado"""
        estados_validos = ['novo', 'usado', 'recondicionado']
        
        for estado in estados_validos:
            peca = PecaModel(
                nome='Teste',
                marca='Test',
                modelo='Test',
                ano=2020,
                preco=100.00,
                descricao='Test',
                estado=estado,
                usuario_id='user-test'
            )
            assert peca.estado == estado
    
    def test_ano_validation(self):
        """Testa validação de ano"""
        peca = PecaModel(
            nome='Farol',
            marca='Ford',
            modelo='Focus',
            ano=2018,
            preco=800.00,
            descricao='Farol dianteiro direito',
            estado='usado',
            usuario_id='user-999'
        )
        
        assert isinstance(peca.ano, int)
        assert peca.ano >= 1900
        assert peca.ano <= 2025
import uuid
from datetime import datetime

class CarrinhoItemModel:
    """
    Modelo de item do carrinho de compras
    """
    
    def __init__(self, user_id, tipo_item, item_id, quantidade, preco_unitario):
        """
        Inicializa um item do carrinho
        
        Args:
            user_id (str): ID do usuário
            tipo_item (str): 'veiculo' ou 'peca'
            item_id (str): ID do veículo ou peça
            quantidade (int): Quantidade do item
            preco_unitario (float): Preço unitário
        """
        self.id = str(uuid.uuid4())
        self.user_id = user_id
        self.tipo_item = tipo_item
        self.item_id = item_id
        self.quantidade = quantidade if tipo_item == 'peca' else 1  # Veículo sempre 1
        self.preco_unitario = float(preco_unitario)
        self.data_adicao = datetime.now()
    
    def to_dict(self):
        """
        Converte o modelo para dicionário
        
        Returns:
            dict: Dicionário com os dados do item
        """
        return {
            "id": self.id,
            "user_id": self.user_id,
            "tipo_item": self.tipo_item,
            "item_id": self.item_id,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "subtotal": self.calcular_subtotal(),
            "data_adicao": self.data_adicao
        }
    
    def calcular_subtotal(self):
        """
        Calcula o subtotal do item (quantidade × preço)
        
        Returns:
            float: Subtotal do item
        """
        return self.quantidade * self.preco_unitario
    
    def validar(self):
        """
        Valida os dados do item
        
        Returns:
            tuple: (bool, str) - (válido, mensagem de erro)
        """
        if self.tipo_item not in ['veiculo', 'peca']:
            return False, "Tipo de item inválido. Use 'veiculo' ou 'peca'"
        
        if self.quantidade < 1:
            return False, "Quantidade deve ser maior que zero"
        
        if self.tipo_item == 'veiculo' and self.quantidade > 1:
            return False, "Veículo só pode ter quantidade 1"
        
        if self.preco_unitario <= 0:
            return False, "Preço deve ser maior que zero"
        
        return True, "Válido"
    
    @staticmethod
    def from_dict(data):
        """
        Cria um CarrinhoItemModel a partir de um dicionário
        
        Args:
            data (dict): Dicionário com os dados
            
        Returns:
            CarrinhoItemModel: Instância do modelo
        """
        item = CarrinhoItemModel(
            user_id=data['user_id'],
            tipo_item=data['tipo_item'],
            item_id=data['item_id'],
            quantidade=data['quantidade'],
            preco_unitario=data['preco_unitario']
        )
        
        # Se o dicionário já tem ID e data, usa eles
        if 'id' in data:
            item.id = data['id']
        if 'data_adicao' in data:
            item.data_adicao = data['data_adicao']
        
        return item
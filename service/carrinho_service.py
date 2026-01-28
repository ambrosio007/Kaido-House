from model.carrinho_model import CarrinhoItemModel
from repository.carrinho_repository import CarrinhoRepository
from repository.veiculo_repository import VeiculoRepository
from repository.peca_repository import PecaRepository

class CarrinhoService:
    """
    Service para lógica de negócio do carrinho
    """
    
    @staticmethod
    def adicionar_item(user_id, tipo_item, item_id, quantidade=1):
        """
        Adiciona um item ao carrinho do usuário
        
        Args:
            user_id (str): ID do usuário
            tipo_item (str): 'veiculo' ou 'peca'
            item_id (str): ID do item
            quantidade (int): Quantidade (padrão 1)
            
        Returns:
            tuple: (bool, str) - (sucesso, mensagem)
        """
        try:
            # Validar tipo de item
            if tipo_item not in ['veiculo', 'peca']:
                return False, "Tipo de item inválido"
            
            # Buscar item para obter o preço
            if tipo_item == 'veiculo':
                item = VeiculoRepository.buscar_por_id(item_id)
                if not item:
                    return False, "Veículo não encontrado"
                if item.get('status') != 'ativo':
                    return False, "Veículo não está disponível"
                # Veículo sempre quantidade 1
                quantidade = 1
            else:  # peca
                item = PecaRepository.buscar_por_id(item_id)
                if not item:
                    return False, "Peça não encontrada"
                if item.get('status') != 'ativo':
                    return False, "Peça não está disponível"
            
            preco_unitario = item['preco']
            
            # Criar modelo do item
            carrinho_item = CarrinhoItemModel(
                user_id=user_id,
                tipo_item=tipo_item,
                item_id=item_id,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )
            
            # Validar item
            valido, mensagem = carrinho_item.validar()
            if not valido:
                return False, mensagem
            
            # Adicionar ao repositório
            sucesso = CarrinhoRepository.adicionar_item(carrinho_item.to_dict())
            
            if sucesso:
                return True, "Item adicionado ao carrinho com sucesso!"
            else:
                return False, "Erro ao adicionar item ao carrinho"
                
        except Exception as e:
            print(f"Erro no CarrinhoService.adicionar_item: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def listar_carrinho(user_id):
        """
        Lista todos os itens do carrinho do usuário
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            list: Lista de itens
        """
        try:
            return CarrinhoRepository.listar_por_usuario(user_id)
        except Exception as e:
            print(f"Erro ao listar carrinho: {e}")
            return []
    
    @staticmethod
    def obter_resumo_carrinho(user_id):
        """
        Obtém resumo do carrinho (itens, quantidade total, valor total)
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            dict: Resumo do carrinho
        """
        try:
            itens = CarrinhoRepository.listar_por_usuario(user_id)
            total_itens = CarrinhoRepository.contar_itens(user_id)
            total_valor = CarrinhoRepository.calcular_total(user_id)
            
            return {
                "itens": itens,
                "total_itens": total_itens,
                "total_valor": total_valor,
                "total_quantidade": sum(item['quantidade'] for item in itens)
            }
        except Exception as e:
            print(f"Erro ao obter resumo: {e}")
            return {
                "itens": [],
                "total_itens": 0,
                "total_valor": 0.0,
                "total_quantidade": 0
            }
    
    @staticmethod
    def atualizar_quantidade(item_id, user_id, nova_quantidade):
        """
        Atualiza a quantidade de um item
        
        Args:
            item_id (str): ID do item no carrinho
            user_id (str): ID do usuário
            nova_quantidade (int): Nova quantidade
            
        Returns:
            tuple: (bool, str) - (sucesso, mensagem)
        """
        try:
            if nova_quantidade < 1:
                return False, "Quantidade deve ser maior que zero"
            
            # TODO: Verificar se item pertence ao usuário
            
            sucesso = CarrinhoRepository.atualizar_quantidade(item_id, nova_quantidade)
            
            if sucesso:
                return True, "Quantidade atualizada com sucesso!"
            else:
                return False, "Erro ao atualizar quantidade"
                
        except Exception as e:
            print(f"Erro ao atualizar quantidade: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def remover_item(item_id, user_id):
        """
        Remove um item do carrinho
        
        Args:
            item_id (str): ID do item no carrinho
            user_id (str): ID do usuário
            
        Returns:
            tuple: (bool, str) - (sucesso, mensagem)
        """
        try:
            sucesso = CarrinhoRepository.remover_item(item_id, user_id)
            
            if sucesso:
                return True, "Item removido do carrinho!"
            else:
                return False, "Item não encontrado ou não pertence a você"
                
        except Exception as e:
            print(f"Erro ao remover item: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def limpar_carrinho(user_id):
        """
        Remove todos os itens do carrinho
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            tuple: (bool, str) - (sucesso, mensagem)
        """
        try:
            count = CarrinhoRepository.limpar_carrinho(user_id)
            
            if count > 0:
                return True, f"{count} item(ns) removido(s) do carrinho!"
            else:
                return True, "Carrinho já estava vazio"
                
        except Exception as e:
            print(f"Erro ao limpar carrinho: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def verificar_disponibilidade(user_id):
        """
        Verifica se todos os itens do carrinho ainda estão disponíveis
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            tuple: (bool, list) - (todos_disponiveis, itens_indisponiveis)
        """
        try:
            itens = CarrinhoRepository.listar_por_usuario(user_id)
            itens_indisponiveis = []
            
            for item in itens:
                if item['tipo_item'] == 'veiculo':
                    veiculo = VeiculoRepository.buscar_por_id(item['item_id'])
                    if not veiculo or veiculo.get('status') != 'ativo':
                        itens_indisponiveis.append(item)
                else:  # peca
                    peca = PecaRepository.buscar_por_id(item['item_id'])
                    if not peca or peca.get('status') != 'ativo':
                        itens_indisponiveis.append(item)
            
            return len(itens_indisponiveis) == 0, itens_indisponiveis
            
        except Exception as e:
            print(f"Erro ao verificar disponibilidade: {e}")
            return False, []
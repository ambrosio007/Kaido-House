"""
Service de Carrinho de Compras
✅ VERSÃO CORRIGIDA - Compatível com PostgreSQL + psycopg2
"""

from model.carrinho_model import CarrinhoItemModel
from repository.carrinho_repository import CarrinhoRepository
from repository.pecas_repository import PecasRepository
from repository.veiculo_repository import VeiculosRepository


class CarrinhoService:
    
    @staticmethod
    def obter_resumo_carrinho(user_id):
        """
        Obtém resumo completo do carrinho
        ✅ VERSÃO CORRIGIDA - Usa o repository com JOIN
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            dict: Resumo do carrinho com itens completos
        """
        try:
            print(f"\n{'='*60}")
            print(f"🛒 OBTENDO RESUMO DO CARRINHO")
            print(f"   User ID: {user_id}")
            print(f"{'='*60}")
            
            # ✅ Buscar itens usando o repository que já faz JOIN
            itens = CarrinhoRepository.listar_por_usuario(user_id)
            
            print(f"📦 {len(itens)} itens encontrados no carrinho")
            
            # Processar itens para o formato esperado pelo frontend
            itens_formatados = []
            total_quantidade = 0
            total_valor = 0.0
            
            for item in itens:
                print(f"\n   📋 Processando item:")
                print(f"      - Tipo: {item['tipo_item']}")
                print(f"      - Nome: {item.get('nome', 'N/A')}")
                print(f"      - Quantidade: {item['quantidade']}")
                print(f"      - Preço: R$ {item['preco_unitario']:.2f}")
                
                # Determinar nome do item baseado no tipo
                if item['tipo_item'] == 'veiculo':
                    nome = f"{item.get('marca', '')} {item.get('modelo', '')} {item.get('ano', '')}".strip()
                else:
                    nome = item.get('nome', 'Produto sem nome')
                
                # Processar fotos (pegar primeira foto)
                fotos = item.get('fotos', '')
                if fotos:
                    primeira_foto = fotos.split(',')[0].strip()
                else:
                    primeira_foto = '/static/img/placeholder.jpg'
                
                # Montar objeto formatado
                item_formatado = {
                    "id": item['id'],
                    "tipo_item": item['tipo_item'],
                    "item_id": item['item_id'],
                    "nome": nome,
                    "preco": float(item['preco_unitario']),
                    "quantidade": item['quantidade'],
                    "imagem": primeira_foto,
                    "subtotal": float(item['subtotal']),
                    "data_adicao": item['data_adicao'].isoformat() if hasattr(item['data_adicao'], 'isoformat') else str(item['data_adicao'])
                }
                
                # Adicionar campos específicos por tipo
                if item['tipo_item'] == 'peca':
                    item_formatado.update({
                        "categoria": item.get('categoria', 'N/A'),
                        "marca": item.get('peca_marca', 'N/A'),
                        "modelo": item.get('peca_modelo', ''),
                        "ano_compativel": item.get('ano_compativel', ''),
                        "status": item.get('status', 'ativo')
                    })
                else:  # veiculo
                    item_formatado.update({
                        "marca": item.get('marca', 'N/A'),
                        "modelo": item.get('modelo', 'N/A'),
                        "ano": item.get('ano', 'N/A'),
                        "km": item.get('km', 0),
                        "estado": item.get('estado', 'N/A'),
                        "status": item.get('status', 'disponivel')
                    })
                
                itens_formatados.append(item_formatado)
                total_quantidade += item['quantidade']
                total_valor += float(item['subtotal'])
            
            # Montar resumo final
            resumo = {
                "itens": itens_formatados,
                "total_itens": len(itens_formatados),
                "total_quantidade": total_quantidade,
                "total_valor": round(total_valor, 2)
            }
            
            print(f"\n{'='*60}")
            print(f"📊 RESUMO FINAL:")
            print(f"   Total de itens: {resumo['total_itens']}")
            print(f"   Quantidade total: {resumo['total_quantidade']}")
            print(f"   Valor total: R$ {resumo['total_valor']:.2f}")
            print(f"{'='*60}\n")
            
            return resumo
            
        except Exception as e:
            print(f"❌ ERRO ao obter resumo do carrinho: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return {
                "itens": [],
                "total_itens": 0,
                "total_quantidade": 0,
                "total_valor": 0.0
            }
    
    @staticmethod
    def adicionar_item(user_id, tipo_item, item_id, quantidade=1):
        """
        Adiciona um item ao carrinho
        
        Args:
            user_id (str): ID do usuário
            tipo_item (str): 'peca' ou 'veiculo'
            item_id (str): ID do item
            quantidade (int): Quantidade
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            print(f"\n{'='*60}")
            print(f"➕ ADICIONANDO ITEM AO CARRINHO")
            print(f"   User ID: {user_id}")
            print(f"   Tipo: {tipo_item}")
            print(f"   Item ID: {item_id}")
            print(f"   Quantidade: {quantidade}")
            print(f"{'='*60}")
            
            # Validações
            if quantidade <= 0:
                return False, "Quantidade deve ser maior que zero"
            
            if tipo_item not in ['peca', 'veiculo']:
                return False, "Tipo de item inválido"
            
            # Buscar informações do item para validação e preço
            if tipo_item == 'peca':
                item_info = PecasRepository.buscar_por_id(item_id)
                if not item_info:
                    return False, "Peça não encontrada"
                
                # Verificar estoque se tiver o campo
                if 'estoque' in item_info and item_info['estoque'] < quantidade:
                    return False, f"Estoque insuficiente. Disponível: {item_info['estoque']}"
                
                preco = item_info.get('preco', 0)
                
            elif tipo_item == 'veiculo':
                item_info = VeiculosRepository.buscar_por_id(item_id)
                if not item_info:
                    return False, "Veículo não encontrado"
                
                if item_info.get('status') != 'disponivel':
                    return False, "Veículo não está disponível"
                
                quantidade = 1  # Veículo sempre quantidade 1
                preco = item_info.get('preco', 0)
            
            # Criar modelo do item
            carrinho_item = CarrinhoItemModel(
                user_id=user_id,
                tipo_item=tipo_item,
                item_id=item_id,
                quantidade=quantidade,
                preco_unitario=preco
            )
            
            # Validar modelo
            valido, mensagem = carrinho_item.validar()
            if not valido:
                return False, mensagem
            
            # Adicionar ao carrinho
            sucesso = CarrinhoRepository.adicionar_item(carrinho_item.to_dict())
            
            if sucesso:
                print(f"   ✅ Item adicionado com sucesso!")
                print(f"{'='*60}\n")
                return True, "Item adicionado ao carrinho"
            else:
                return False, "Erro ao adicionar item ao carrinho"
                
        except Exception as e:
            print(f"❌ ERRO ao adicionar item: {str(e)}")
            import traceback
            traceback.print_exc()
            return False, f"Erro interno: {str(e)}"
    
    @staticmethod
    def atualizar_quantidade(item_id, user_id, nova_quantidade):
        """
        Atualiza a quantidade de um item
        
        Args:
            item_id (str): ID do item no carrinho
            user_id (str): ID do usuário (para validação)
            nova_quantidade (int): Nova quantidade
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            if nova_quantidade <= 0:
                return False, "Quantidade deve ser maior que zero"
            
            # Atualizar quantidade
            sucesso = CarrinhoRepository.atualizar_quantidade(item_id, nova_quantidade)
            
            if sucesso:
                return True, "Quantidade atualizada"
            else:
                return False, "Item não encontrado ou erro ao atualizar"
                
        except Exception as e:
            print(f"❌ Erro ao atualizar quantidade: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    @staticmethod
    def remover_item(item_id, user_id):
        """
        Remove um item do carrinho
        
        Args:
            item_id (str): ID do item
            user_id (str): ID do usuário
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            sucesso = CarrinhoRepository.remover_item(item_id, user_id)
            
            if sucesso:
                return True, "Item removido do carrinho"
            else:
                return False, "Item não encontrado ou já removido"
                
        except Exception as e:
            print(f"❌ Erro ao remover item: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    @staticmethod
    def limpar_carrinho(user_id):
        """
        Remove todos os itens do carrinho
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            tuple: (sucesso, mensagem)
        """
        try:
            count = CarrinhoRepository.limpar_carrinho(user_id)
            
            if count > 0:
                return True, f"{count} itens removidos do carrinho"
            else:
                return True, "Carrinho já estava vazio"
                
        except Exception as e:
            print(f"❌ Erro ao limpar carrinho: {str(e)}")
            return False, f"Erro interno: {str(e)}"
    
    @staticmethod
    def verificar_disponibilidade(user_id):
        """
        Verifica se todos os itens ainda estão disponíveis
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            tuple: (todos_disponíveis, lista_indisponíveis)
        """
        try:
            itens = CarrinhoRepository.listar_por_usuario(user_id)
            itens_indisponiveis = []
            
            for item in itens:
                disponivel = True
                motivo = ""
                
                if item['tipo_item'] == 'peca':
                    peca = PecasRepository.buscar_por_id(item['item_id'])
                    if not peca:
                        disponivel = False
                        motivo = "Peça não encontrada"
                    elif peca.get('status') != 'ativo':
                        disponivel = False
                        motivo = "Peça não está mais disponível"
                    elif 'estoque' in peca and peca['estoque'] < item['quantidade']:
                        disponivel = False
                        motivo = f"Estoque insuficiente (disponível: {peca['estoque']})"
                
                elif item['tipo_item'] == 'veiculo':
                    veiculo = VeiculosRepository.buscar_por_id(item['item_id'])
                    if not veiculo:
                        disponivel = False
                        motivo = "Veículo não encontrado"
                    elif veiculo.get('status') != 'disponivel':
                        disponivel = False
                        motivo = "Veículo não está mais disponível"
                
                if not disponivel:
                    itens_indisponiveis.append({
                        "id": item['id'],
                        "tipo_item": item['tipo_item'],
                        "item_id": item['item_id'],
                        "nome": item.get('nome', 'Item'),
                        "motivo": motivo
                    })
            
            todos_disponiveis = len(itens_indisponiveis) == 0
            
            return todos_disponiveis, itens_indisponiveis
            
        except Exception as e:
            print(f"❌ Erro ao verificar disponibilidade: {str(e)}")
            return False, []
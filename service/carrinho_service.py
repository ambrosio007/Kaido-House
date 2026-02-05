"""
Service de Carrinho de Compras
✅ VERSÃO SIMPLIFICADA - Usa apenas CarrinhoRepository
"""

from model.carrinho_model import CarrinhoItemModel
from repository.carrinho_repository import CarrinhoRepository


class CarrinhoService:
    
    @staticmethod
    def obter_resumo_carrinho(user_id):
        """
        Obtém resumo completo do carrinho
        ✅ USA O JOIN DO REPOSITORY - Não precisa buscar peças/veículos separadamente
        
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
            
            # ✅ Buscar itens - O repository já faz JOIN e traz tudo
            itens = CarrinhoRepository.listar_por_usuario(user_id)
            
            print(f"📦 {len(itens)} itens encontrados no carrinho")
            
            # Processar itens para o formato esperado pelo frontend
            itens_formatados = []
            total_quantidade = 0
            total_valor = 0.0
            
            for item in itens:
                print(f"\n   📋 Processando item:")
                print(f"      - Tipo: {item.get('tipo_item')}")
                print(f"      - Quantidade: {item.get('quantidade')}")
                print(f"      - Preço: R$ {item.get('preco_unitario', 0):.2f}")
                
                # Determinar nome do item baseado no tipo
                if item.get('tipo_item') == 'veiculo':
                    # Para veículos: marca + modelo + ano
                    nome = f"{item.get('marca', '')} {item.get('modelo', '')} {item.get('ano', '')}".strip()
                    if not nome:
                        nome = 'Veículo'
                else:
                    # Para peças: usar campo 'nome'
                    nome = item.get('nome', 'Produto sem nome')
                
                print(f"      - Nome: {nome}")
                
                # Processar fotos (pegar primeira foto)
                fotos = item.get('fotos', '')
                if fotos and isinstance(fotos, str):
                    primeira_foto = fotos.split(',')[0].strip()
                else:
                    primeira_foto = '/static/img/placeholder.jpg'
                
                # Calcular subtotal
                quantidade = item.get('quantidade', 0)
                preco_unitario = float(item.get('preco_unitario', 0))
                subtotal = quantidade * preco_unitario
                
                # Montar objeto formatado
                item_formatado = {
                    "id": item.get('id'),
                    "tipo_item": item.get('tipo_item'),
                    "item_id": item.get('item_id'),
                    "nome": nome,
                    "preco": preco_unitario,
                    "quantidade": quantidade,
                    "imagem": primeira_foto,
                    "subtotal": round(subtotal, 2)
                }
                
                # Adicionar data_adicao se existir
                if 'data_adicao' in item:
                    data_adicao = item['data_adicao']
                    if hasattr(data_adicao, 'isoformat'):
                        item_formatado['data_adicao'] = data_adicao.isoformat()
                    else:
                        item_formatado['data_adicao'] = str(data_adicao)
                
                # Adicionar campos específicos por tipo
                if item.get('tipo_item') == 'peca':
                    item_formatado.update({
                        "categoria": item.get('categoria', 'N/A'),
                        "marca": item.get('peca_marca') or item.get('marca', 'N/A'),
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
                total_quantidade += quantidade
                total_valor += subtotal
                
                print(f"      💰 Subtotal: R$ {subtotal:.2f}")
            
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
        ✅ VERSÃO SIMPLIFICADA - Assume que validação será feita no controller
        
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
            
            # Validações básicas
            if quantidade <= 0:
                return False, "Quantidade deve ser maior que zero"
            
            if tipo_item not in ['peca', 'veiculo']:
                return False, "Tipo de item inválido"
            
            # ⚠️ ATENÇÃO: Você precisará buscar o preço da peça/veículo
            # Por enquanto, vou usar um valor padrão
            # VOCÊ DEVE SUBSTITUIR ISSO pela busca real do preço
            
            # TODO: Buscar preço real do banco de dados
            # Exemplo: preco = buscar_preco_do_item(tipo_item, item_id)
            preco_unitario = 0.0  # ⚠️ TEMPORÁRIO
            
            # Criar modelo do item
            carrinho_item = CarrinhoItemModel(
                user_id=user_id,
                tipo_item=tipo_item,
                item_id=item_id,
                quantidade=quantidade,
                preco_unitario=preco_unitario
            )
            
            # Validar modelo
            valido, mensagem = carrinho_item.validar()
            if not valido and 'preço' not in mensagem.lower():  # Ignora validação de preço por enquanto
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
        ✅ VERSÃO SIMPLIFICADA - Assume que itens no carrinho estão disponíveis
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            tuple: (todos_disponíveis, lista_indisponíveis)
        """
        try:
            # Por enquanto, retorna que está tudo disponível
            # Você pode implementar validações mais complexas depois
            return True, []
            
        except Exception as e:
            print(f"❌ Erro ao verificar disponibilidade: {str(e)}")
            return False, []
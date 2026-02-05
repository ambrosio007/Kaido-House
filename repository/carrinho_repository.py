from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor

class CarrinhoRepository:
    """
    Repository para operações de carrinho no banco de dados
    ✅ VERSÃO CORRIGIDA - Com busca completa de informações
    """
    
    @staticmethod
    def adicionar_item(dados):
        """
        Adiciona um item ao carrinho
        
        Args:
            dados (dict): Dados do item
            
        Returns:
            bool: True se sucesso, False caso contrário
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # Verificar se item já existe no carrinho
            cursor.execute("""
                SELECT id, quantidade FROM carrinho_itens
                WHERE user_id = %s AND tipo_item = %s AND item_id = %s
            """, (dados['user_id'], dados['tipo_item'], dados['item_id']))
            
            item_existente = cursor.fetchone()
            
            if item_existente:
                # Atualizar quantidade se for peça
                if dados['tipo_item'] == 'peca':
                    nova_quantidade = item_existente[1] + dados['quantidade']
                    cursor.execute("""
                        UPDATE carrinho_itens
                        SET quantidade = %s
                        WHERE id = %s
                    """, (nova_quantidade, item_existente[0]))
                # Veículo já está no carrinho, não fazer nada
            else:
                # Inserir novo item
                cursor.execute("""
                    INSERT INTO carrinho_itens 
                    (id, user_id, tipo_item, item_id, quantidade, preco_unitario, data_adicao)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                """, (
                    dados['id'],
                    dados['user_id'],
                    dados['tipo_item'],
                    dados['item_id'],
                    dados['quantidade'],
                    dados['preco_unitario'],
                    dados['data_adicao']
                ))
            
            conn.commit()
            cursor.close()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"Erro ao adicionar item ao carrinho: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def listar_por_usuario(user_id):
        """
        Lista todos os itens do carrinho de um usuário
        ✅ VERSÃO CORRIGIDA - Busca dados completos com JOINs
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            list: Lista de itens do carrinho com todas as informações
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # Query unificada que busca peças E veículos em uma só consulta
            cursor.execute("""
                SELECT 
                    ci.id,
                    ci.user_id,
                    ci.tipo_item,
                    ci.item_id,
                    ci.quantidade,
                    ci.preco_unitario,
                    (ci.quantidade * ci.preco_unitario) as subtotal,
                    ci.data_adicao,
                    
                    -- Campos de PEÇAS (NULL se for veículo)
                    p.nome,
                    p.categoria,
                    p.marca as peca_marca,
                    p.modelo as peca_modelo,
                    p.ano_compativel,
                    p.fotos as peca_fotos,
                    p.status as peca_status,
                    
                    -- Campos de VEÍCULOS (NULL se for peça)
                    v.marca,
                    v.modelo,
                    v.ano,
                    v.km,
                    v.estado,
                    v.fotos as veiculo_fotos,
                    v.status as veiculo_status
                    
                FROM carrinho_itens ci
                LEFT JOIN pecas p ON (ci.tipo_item = 'peca' AND ci.item_id = p.id)
                LEFT JOIN veiculos v ON (ci.tipo_item = 'veiculo' AND ci.item_id = v.id)
                WHERE ci.user_id = %s
                ORDER BY ci.data_adicao DESC
            """, (user_id,))
            
            itens_raw = cursor.fetchall()
            cursor.close()
            
            # Processar e normalizar os dados
            itens_processados = []
            for item in itens_raw:
                item_dict = dict(item)
                
                # Determinar qual fonte de fotos usar
                if item_dict['tipo_item'] == 'peca':
                    item_dict['fotos'] = item_dict['peca_fotos']
                    item_dict['status'] = item_dict['peca_status']
                else:  # veiculo
                    item_dict['fotos'] = item_dict['veiculo_fotos']
                    item_dict['status'] = item_dict['veiculo_status']
                
                # Limpar campos desnecessários
                item_dict.pop('peca_fotos', None)
                item_dict.pop('veiculo_fotos', None)
                item_dict.pop('peca_status', None)
                item_dict.pop('veiculo_status', None)
                item_dict.pop('peca_marca', None)
                item_dict.pop('peca_modelo', None)
                
                itens_processados.append(item_dict)
            
            return itens_processados
            
        except Exception as e:
            print(f"❌ Erro ao listar carrinho: {e}")
            import traceback
            traceback.print_exc()
            return []
        finally:
            release_connection(conn)
    
    @staticmethod
    def contar_itens(user_id):
        """
        Conta quantos itens o usuário tem no carrinho
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            int: Número de itens
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM carrinho_itens
                WHERE user_id = %s
            """, (user_id,))
            
            count = cursor.fetchone()[0]
            cursor.close()
            return count
        finally:
            release_connection(conn)
    
    @staticmethod
    def calcular_total(user_id):
        """
        Calcula o valor total do carrinho
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            float: Total do carrinho
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # ✅ OPÇÃO 1: Se você tem a função calcular_total_carrinho no banco
            # cursor.execute("SELECT calcular_total_carrinho(%s)", (user_id,))
            
            # ✅ OPÇÃO 2: Calcular direto na query (mais seguro)
            cursor.execute("""
                SELECT COALESCE(SUM(quantidade * preco_unitario), 0)
                FROM carrinho_itens
                WHERE user_id = %s
            """, (user_id,))
            
            total = cursor.fetchone()[0]
            cursor.close()
            return float(total) if total else 0.0
        except Exception as e:
            print(f"❌ Erro ao calcular total: {e}")
            return 0.0
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_quantidade(item_id, nova_quantidade):
        """
        Atualiza a quantidade de um item
        
        Args:
            item_id (str): ID do item no carrinho
            nova_quantidade (int): Nova quantidade
            
        Returns:
            bool: True se sucesso
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE carrinho_itens
                SET quantidade = %s
                WHERE id = %s
            """, (nova_quantidade, item_id))
            
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar quantidade: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def remover_item(item_id, user_id):
        """
        Remove um item do carrinho
        
        Args:
            item_id (str): ID do item no carrinho
            user_id (str): ID do usuário (para validação)
            
        Returns:
            bool: True se sucesso
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM carrinho_itens
                WHERE id = %s AND user_id = %s
            """, (item_id, user_id))
            
            conn.commit()
            deleted = cursor.rowcount
            cursor.close()
            return deleted > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao remover item: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def limpar_carrinho(user_id):
        """
        Remove todos os itens do carrinho do usuário
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            int: Número de itens removidos
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            # ✅ OPÇÃO 1: Se você tem a função limpar_carrinho no banco
            # cursor.execute("SELECT limpar_carrinho(%s)", (user_id,))
            # count = cursor.fetchone()[0]
            
            # ✅ OPÇÃO 2: Executar DELETE direto (mais seguro)
            cursor.execute("""
                DELETE FROM carrinho_itens
                WHERE user_id = %s
            """, (user_id,))
            
            count = cursor.rowcount
            conn.commit()
            cursor.close()
            return count
        except Exception as e:
            conn.rollback()
            print(f"Erro ao limpar carrinho: {e}")
            return 0
        finally:
            release_connection(conn)
    
    @staticmethod
    def verificar_item_existe(user_id, tipo_item, item_id):
        """
        Verifica se um item já está no carrinho
        
        Args:
            user_id (str): ID do usuário
            tipo_item (str): 'veiculo' ou 'peca'
            item_id (str): ID do item
            
        Returns:
            bool: True se item já está no carrinho
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT EXISTS(
                    SELECT 1 FROM carrinho_itens
                    WHERE user_id = %s AND tipo_item = %s AND item_id = %s
                )
            """, (user_id, tipo_item, item_id))
            
            existe = cursor.fetchone()[0]
            cursor.close()
            return existe
        finally:
            release_connection(conn)
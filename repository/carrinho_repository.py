from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor

class CarrinhoRepository:
    """
    Repository para operações de carrinho no banco de dados
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
        
        Args:
            user_id (str): ID do usuário
            
        Returns:
            list: Lista de itens do carrinho
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("""
                SELECT * FROM vw_carrinho_completo
                WHERE user_id = %s
                ORDER BY data_adicao DESC
            """, (user_id,))
            
            itens = cursor.fetchall()
            cursor.close()
            return [dict(item) for item in itens]
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
            cursor.execute("SELECT calcular_total_carrinho(%s)", (user_id,))
            
            total = cursor.fetchone()[0]
            cursor.close()
            return float(total) if total else 0.0
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
            cursor.execute("SELECT limpar_carrinho(%s)", (user_id,))
            
            count = cursor.fetchone()[0]
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
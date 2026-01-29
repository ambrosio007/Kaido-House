from config.database import get_connection, release_connection
from controller.pecas_controller import estado
from psycopg2.extras import RealDictCursor

class PecaRepository:

    @staticmethod
    def adicionar_peca(dados):
        """Adiciona uma nova peça"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO pecas (id, user_id, nome, categoria, marca, modelo, estado, preco, descricao, fotos, data_cadastro, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados['id'], 
                dados['user_id'], 
                dados['nome'], 
                dados['categoria'], 
                dados['marca'], 
                dados['modelo'],
                dados['estado'], 
                dados['preco'], 
                dados['descricao'], 
                dados.get('fotos', ''),
                dados['data_cadastro'],
                dados['status']
            ))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao adicionar peça: {e}")
            return False
        finally:
            release_connection(conn)

    @staticmethod
    def listar_por_usuario(user_id):
        """Lista peças de um usuário específico"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM pecas WHERE user_id = %s AND status = 'ativo'", 
                (user_id,)
            )
            pecas = cursor.fetchall()
            cursor.close()
            return [dict(p) for p in pecas]
        finally:
            release_connection(conn)
    
    @staticmethod
    def listar_todos(categoria=None, estado=None):
        """Lista todas as peças ativas com filtros opcionais"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            query = "SELECT * FROM pecas WHERE status = 'ativo'"
            params = []
            
            if categoria:
                query += " AND categoria = %s"
                params.append(categoria)
            
            if estado:
                query += " AND estado = %s"
                params.append(estado)
            
            cursor.execute(query, params if params else None)
            pecas = cursor.fetchall()
            cursor.close()
            return [dict(p) for p in pecas]
        finally:
            release_connection(conn)
    
    @staticmethod
    def buscar_por_id(peca_id):
        """Busca peça por ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM pecas WHERE id = %s", (peca_id,))
            peca = cursor.fetchone()
            cursor.close()
            return dict(peca) if peca else None
        finally:
            release_connection(conn)
    
    @staticmethod
    def deletar(peca_id):
        """Deleta (inativa) uma peça"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE pecas SET status = 'inativo' WHERE id = %s", 
                (peca_id,)
            )
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao deletar peça: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_peca(peca_id, dados):
        """Atualiza dados da peça"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE pecas
                SET nome = %s, categoria = %s, marca = %s, modelo = %s,
                    estado = %s, preco = %s, descricao = %s
                WHERE id = %s
            """, (
                dados.get('nome'),
                dados.get('categoria'),
                dados.get('marca'),
                dados.get('modelo'),
                dados.get('estado'),
                dados.get('preco'),
                dados.get('descricao'),
                peca_id
            ))
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar peça: {e}")
            return False
        finally:
            release_connection(conn)

@staticmethod
def listar_aleatorio(limit=5, apenas_novos=True):
    conn = get_connection()
    try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            # SQL base
            query = "SELECT * FROM pecas WHERE 1=1"
            params = []

            # Filtra por estado se for enviado (novo ou usado)
            if estado:
                query += " AND estado = %s"
                params.append(estado)

            # Ordena aleatoriamente e limita a 5
            query += " ORDER BY RANDOM() LIMIT %s"
            params.append(limit)

            cursor.execute(query, params)
            return cursor.fetchall()
    finally:
            release_connection(conn)
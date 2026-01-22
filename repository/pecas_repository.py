import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='kaido-server'
    )

class PecaRepository:

    @staticmethod
    def adicionar_peca(dados):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
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
            return True
        except Exception as e:
            print(f"Erro ao adicionar peça: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_por_usuario(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pecas WHERE user_id = %s AND status = 'ativo'", (user_id,))
            pecas = cursor.fetchall()
            return pecas
        except Exception as e:
            print(f"Erro ao listar peças: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def listar_todos(categoria=None, estado=None):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
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
            return pecas
        except Exception as e:
            print(f"Erro ao listar todas as peças: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def buscar_por_id(peca_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM pecas WHERE id = %s", (peca_id,))
            peca = cursor.fetchone()
            return peca
        except Exception as e:
            print(f"Erro ao buscar peça: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def deletar(peca_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE pecas SET status = 'inativo' WHERE id = %s", (peca_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao deletar peça: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def atualizar_peca(peca_id, dados):
        conn = get_connection()
        cursor = conn.cursor()
        try:
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
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar peça: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
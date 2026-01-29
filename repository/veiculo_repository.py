from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor

class VeiculoRepository:

    @staticmethod
    def adicionar_veiculo(dados):
        """Adiciona um novo veículo"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO veiculos (id, user_id, marca, modelo, ano, km, cor, preco, descricao, fotos, data_cadastro, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados['id'], 
                dados['user_id'], 
                dados['marca'], 
                dados['modelo'], 
                dados['ano'],
                dados['km'], 
                dados['cor'], 
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
            print(f"Erro ao adicionar veículo: {e}")
            return False
        finally:
            release_connection(conn)

    @staticmethod
    def listar_por_usuario(user_id):
        """Lista veículos de um usuário específico"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                "SELECT * FROM veiculos WHERE user_id = %s AND status = 'ativo'", 
                (user_id,)
            )
            veiculos = cursor.fetchall()
            cursor.close()
            return [dict(v) for v in veiculos]
        finally:
            release_connection(conn)
    
    @staticmethod
    def listar_todos():
        """Lista todos os veículos ativos"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM veiculos WHERE status = 'ativo'")
            veiculos = cursor.fetchall()
            cursor.close()
            return [dict(v) for v in veiculos]
        finally:
            release_connection(conn)
    
    @staticmethod
    def buscar_por_id(veiculo_id):
        """Busca veículo por ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM veiculos WHERE id = %s", (veiculo_id,))
            veiculo = cursor.fetchone()
            cursor.close()
            return dict(veiculo) if veiculo else None
        finally:
            release_connection(conn)
    
    @staticmethod
    def deletar(veiculo_id):
        """Deleta (inativa) um veículo"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE veiculos SET status = 'inativo' WHERE id = %s", 
                (veiculo_id,)
            )
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao deletar veículo: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_veiculo(veiculo_id, dados):
        """Atualiza dados do veículo"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE veiculos
                SET marca = %s, modelo = %s, ano = %s, km = %s, 
                    cor = %s, preco = %s, descricao = %s
                WHERE id = %s
            """, (
                dados.get('marca'),
                dados.get('modelo'),
                dados.get('ano'),
                dados.get('km'),
                dados.get('cor'),
                dados.get('preco'),
                dados.get('descricao'),
                veiculo_id
            ))
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar veículo: {e}")
            return False
        finally:
            release_connection(conn)

@staticmethod
def listar_aleatorio(apenas_novos=True, limit=5):
        conn = get_connection()
        try:
            # Usamos RealDictCursor para o JS receber um objeto JSON pronto
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            
            # Se apenas_novos for True, busca KM < 100. Se False, busca KM >= 100.
            if apenas_novos:
                query = "SELECT * FROM veiculos WHERE km < 100 ORDER BY RANDOM() LIMIT %s"
            else:
                query = "SELECT * FROM veiculos WHERE km >= 100 ORDER BY RANDOM() LIMIT %s"
            
            cursor.execute(query, (limit,))
            return cursor.fetchall()
        finally:
            release_connection(conn)
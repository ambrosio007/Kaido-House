import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='kaido-server'
    )

class VeiculoRepository:

    @staticmethod
    def adicionar_veiculo(dados):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
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
            return True
        except Exception as e:
            print(f"Erro ao adicionar veículo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def listar_por_usuario(user_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM veiculos WHERE user_id = %s AND status = 'ativo'", (user_id,))
            veiculos = cursor.fetchall()
            return veiculos
        except Exception as e:
            print(f"Erro ao listar veículos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def listar_todos():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM veiculos WHERE status = 'ativo'")
            veiculos = cursor.fetchall()
            return veiculos
        except Exception as e:
            print(f"Erro ao listar todos os veículos: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def buscar_por_id(veiculo_id):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM veiculos WHERE id = %s", (veiculo_id,))
            veiculo = cursor.fetchone()
            return veiculo
        except Exception as e:
            print(f"Erro ao buscar veículo: {e}")
            return None
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def deletar(veiculo_id):
        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE veiculos SET status = 'inativo' WHERE id = %s", (veiculo_id,))
            conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao deletar veículo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    @staticmethod
    def atualizar_veiculo(veiculo_id, dados):
        conn = get_connection()
        cursor = conn.cursor()
        try:
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
            return cursor.rowcount > 0
        except Exception as e:
            print(f"Erro ao atualizar veículo: {e}")
            return False
        finally:
            cursor.close()
            conn.close()
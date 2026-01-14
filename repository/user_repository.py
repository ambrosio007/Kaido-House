import mysql.connector

def get_connection():
    return mysql.connector.connect(
        host='localhost',
        user='root',
        password='admin',
        database='kaido-server'
    )

class UserRepository:

    @staticmethod
    def lista_users():
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios")
        users = cursor.fetchall()
        cursor.close()
        conn.close()
        return users
    
    @staticmethod
    def adicionar_user(dados):
        conn = get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, email, idade, senha, perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (dados['id'], dados['nome'], dados['cpf'], dados['cep'], dados['email'],
                dados['idade'], dados['senha'], dados['perfil']))
            conn.commit()
            cursor.close()
            conn.close()
            return True
        except:
            return False

    @staticmethod
    def buscar_por_email_e_senha(email, senha):
        conn = get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM usuarios WHERE email = %s AND senha = %s", (email, senha))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        return user
    
    @staticmethod
    def delet(user_id):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
        conn.commit()
        deleted = cursor.rowcount
        cursor.close()
        conn.close()
        return deleted > 0
    
    @staticmethod
    def atualizar_user(user_id, dados):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuarios
            SET nome = %s, cpf = %s, cep = %s, idade = %s, email = %s, senha = %s
            WHERE id = %s
        """, (dados['nome'], dados['cpf'], dados['cep'], dados['idade'],
              dados['email'], dados['senha'], user_id))
        conn.commit()
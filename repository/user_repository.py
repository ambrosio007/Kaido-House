from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor

class UserRepository:

    @staticmethod
    def lista_users():
        """Lista todos os usuários"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM usuarios")
            users = cursor.fetchall()
            cursor.close()
            return [dict(user) for user in users]
        finally:
            release_connection(conn)
    
    @staticmethod
    def adicionar_user(dados):
        """Adiciona um novo usuário"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, cep, email, idade, senha, perfil, foto_perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados['id'], 
                dados['nome'], 
                dados['cpf'], 
                dados['cep'], 
                dados['email'], 
                dados['idade'], 
                dados['senha_hash'],
                dados.get('perfil', 'cliente'),
                dados.get('foto_perfil', None)
            ))
            conn.commit()
            cursor.close()
            return True
        except Exception as e:
            conn.rollback()
            print(f"Erro ao adicionar usuário: {e}")
            return False
        finally:
            release_connection(conn)

    @staticmethod
    def buscar_por_email_e_senha(email, senha):
        """Busca usuário por email"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM usuarios WHERE email = %s", (email,))
            user = cursor.fetchone()
            cursor.close()
            return dict(user) if user else None
        finally:
            release_connection(conn)
    
    @staticmethod
    def buscar_por_id(user_id):
        """Busca usuário por ID"""
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute("SELECT * FROM usuarios WHERE id = %s", (user_id,))
            user = cursor.fetchone()
            cursor.close()
            return dict(user) if user else None
        finally:
            release_connection(conn)
    
    @staticmethod
    def delet(user_id):
        """Deleta um usuário"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM usuarios WHERE id = %s", (user_id,))
            conn.commit()
            deleted = cursor.rowcount
            cursor.close()
            return deleted > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao deletar usuário: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_user(user_id, dados):
        """Atualiza dados do usuário"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET nome = %s, cpf = %s, cep = %s, idade = %s, email = %s
                WHERE id = %s
            """, (
                dados['nome'], 
                dados['cpf'], 
                dados['cep'], 
                dados['idade'],
                dados['email'], 
                user_id
            ))
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar usuário: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_senha(user_id, senha_hash):
        """Atualiza apenas a senha do usuário"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET senha = %s
                WHERE id = %s
            """, (senha_hash, user_id))
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar senha: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def atualizar_foto_perfil(user_id, foto_url):
        """Atualiza a foto de perfil do usuário"""
        conn = get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE usuarios
                SET foto_perfil = %s
                WHERE id = %s
            """, (foto_url, user_id))
            conn.commit()
            updated = cursor.rowcount
            cursor.close()
            return updated > 0
        except Exception as e:
            conn.rollback()
            print(f"Erro ao atualizar foto de perfil: {e}")
            return False
        finally:
            release_connection(conn)
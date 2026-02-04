from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor
import psycopg2

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
        """
        Adiciona um novo usuário
        ✅ VERSÃO FINAL - Commit garantido antes de devolver conexão
        """
        conn = None
        cursor = None
        
        try:
            print(f"\n{'='*60}")
            print(f"📝 INSERINDO USUÁRIO NO BANCO")
            print(f"{'='*60}")
            
            # Obter conexão
            conn = get_connection()
            cursor = conn.cursor()
            
            # Executar INSERT
            print(f"💾 Executando INSERT...")
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
            
            print(f"✅ INSERT executado (rowcount: {cursor.rowcount})")
            
            # ⭐ COMMIT IMEDIATAMENTE
            print(f"💿 Executando COMMIT...")
            conn.commit()
            print(f"✅ COMMIT concluído!")
            
            # Verificar se foi inserido
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE id = %s", (dados['id'],))
            count = cursor.fetchone()[0]
            print(f"🔍 Verificação: {count} registro(s) encontrado(s)")
            
            if count == 0:
                print(f"❌ ERRO: Registro não foi persistido!")
                raise Exception("Falha ao persistir no banco")
            
            print(f"✅ Usuário '{dados['nome']}' inserido com sucesso!")
            print(f"{'='*60}\n")
            
            return True
            
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
            
            erro_str = str(e)
            if 'email' in erro_str.lower():
                raise Exception(f"Email '{dados.get('email')}' já está cadastrado")
            elif 'cpf' in erro_str.lower():
                raise Exception(f"CPF '{dados.get('cpf')}' já está cadastrado")
            else:
                raise Exception(f"Erro de integridade: {erro_str}")
                
        except Exception as e:
            if conn:
                print(f"❌ Erro: {str(e)}")
                conn.rollback()
            raise
            
        finally:
            if cursor:
                cursor.close()
            if conn:
                # ⭐ GARANTIR que não há transação pendente antes de devolver
                try:
                    if conn.info.transaction_status != psycopg2.extensions.TRANSACTION_STATUS_IDLE:
                        print(f"⚠️ Transação ainda ativa, forçando commit...")
                        conn.commit()
                except:
                    pass
                
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
            
            # ⭐ COMMIT IMEDIATAMENTE
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
            
            # ⭐ COMMIT IMEDIATAMENTE
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
            
            # ⭐ COMMIT IMEDIATAMENTE
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
            
            # ⭐ COMMIT IMEDIATAMENTE
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
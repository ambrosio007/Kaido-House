from config.database import get_connection, release_connection
from psycopg2.extras import RealDictCursor
from datetime import datetime, timedelta
import secrets

class PasswordResetRepository:
    
    @staticmethod
    def criar_token_recuperacao(user_id, email):
        """
        Cria um token único para recuperação de senha
        
        Args:
            user_id (str): ID do usuário
            email (str): E-mail do usuário
        
        Returns:
            str: Token gerado ou None se falhar
        """
        conn = get_connection()
        try:
            # Gerar token único e seguro
            token = secrets.token_urlsafe(32)
            
            # Definir expiração (1 hora a partir de agora)
            expira_em = datetime.now() + timedelta(hours=1)
            
            cursor = conn.cursor()
            
            # Primeiro, invalidar tokens antigos deste usuário
            cursor.execute("""
                UPDATE password_reset_tokens
                SET usado = TRUE
                WHERE user_id = %s AND usado = FALSE
            """, (user_id,))
            
            # Inserir novo token
            cursor.execute("""
                INSERT INTO password_reset_tokens (token, user_id, email, expira_em, criado_em, usado)
                VALUES (%s, %s, %s, %s, NOW(), FALSE)
            """, (token, user_id, email, expira_em))
            
            conn.commit()
            cursor.close()
            
            print(f"✅ Token criado para {email}")
            print(f"   Token: {token[:10]}...")
            print(f"   Expira em: {expira_em}")
            
            return token
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao criar token: {e}")
            return None
        finally:
            release_connection(conn)
    
    @staticmethod
    def validar_token(token):
        """
        Valida se o token existe, não foi usado e não expirou
        
        Args:
            token (str): Token a validar
        
        Returns:
            dict: Dados do token se válido, None caso contrário
        """
        conn = get_connection()
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            
            cursor.execute("""
                SELECT * FROM password_reset_tokens
                WHERE token = %s
                AND usado = FALSE
                AND expira_em > NOW()
            """, (token,))
            
            token_data = cursor.fetchone()
            cursor.close()
            
            if token_data:
                print(f"✅ Token válido encontrado para user_id: {token_data['user_id']}")
                return dict(token_data)
            else:
                print(f"❌ Token inválido ou expirado")
                return None
                
        except Exception as e:
            print(f"❌ Erro ao validar token: {e}")
            return None
        finally:
            release_connection(conn)
    
    @staticmethod
    def marcar_token_usado(token):
        """
        Marca um token como usado após a senha ser redefinida
        
        Args:
            token (str): Token a marcar
        
        Returns:
            bool: True se marcado com sucesso
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE password_reset_tokens
                SET usado = TRUE, usado_em = NOW()
                WHERE token = %s
            """, (token,))
            
            conn.commit()
            rows_affected = cursor.rowcount
            cursor.close()
            
            if rows_affected > 0:
                print(f"✅ Token marcado como usado")
                return True
            else:
                print(f"⚠️ Nenhum token encontrado para marcar")
                return False
                
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao marcar token: {e}")
            return False
        finally:
            release_connection(conn)
    
    @staticmethod
    def limpar_tokens_expirados():
        """
        Remove tokens expirados do banco (manutenção)
        
        Returns:
            int: Número de tokens removidos
        """
        conn = get_connection()
        try:
            cursor = conn.cursor()
            
            cursor.execute("""
                DELETE FROM password_reset_tokens
                WHERE expira_em < NOW() - INTERVAL '7 days'
            """)
            
            conn.commit()
            rows_deleted = cursor.rowcount
            cursor.close()
            
            print(f"🧹 {rows_deleted} tokens expirados removidos")
            return rows_deleted
            
        except Exception as e:
            conn.rollback()
            print(f"❌ Erro ao limpar tokens: {e}")
            return 0
        finally:
            release_connection(conn)
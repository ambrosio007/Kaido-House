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
        ✅ VERSÃO CORRIGIDA com logs detalhados e tratamento de erros
        """
        conn = None
        try:
            print(f"\n========== USER REPOSITORY - ADICIONAR ==========")
            print(f"1. Dados recebidos no repository:")
            for key, value in dados.items():
                if key == 'senha_hash':
                    print(f"   {key}: {value[:20]}... (hash)")
                else:
                    print(f"   {key}: {value}")
            
            # Validar campos obrigatórios
            campos_obrigatorios = ['id', 'nome', 'cpf', 'email', 'idade', 'senha_hash']
            for campo in campos_obrigatorios:
                if campo not in dados or dados[campo] is None:
                    raise ValueError(f"Campo obrigatório '{campo}' está faltando ou vazio")
            
            # Validar tipo da idade
            idade = dados.get('idade')
            if not isinstance(idade, int):
                try:
                    idade = int(idade)
                    print(f"⚠️  Idade convertida de {type(dados['idade'])} para int: {idade}")
                except (ValueError, TypeError):
                    raise ValueError(f"Campo 'idade' deve ser um número inteiro, recebido: {type(idade)} = {idade}")
            
            conn = get_connection()
            print(f"\n2. ✅ Conexão obtida com sucesso")
            
            cursor = conn.cursor()
            
            # Log da query SQL
            print(f"\n3. Executando INSERT...")
            print(f"   Tabela: usuarios")
            print(f"   Campos: id, nome, cpf, cep, email, idade, senha, perfil, foto_perfil")
            
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, cep, email, idade, senha, perfil, foto_perfil)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                dados['id'], 
                dados['nome'], 
                dados['cpf'], 
                dados['cep'], 
                dados['email'], 
                idade,  # Usar a variável idade validada
                dados['senha_hash'],
                dados.get('perfil', 'cliente'),
                dados.get('foto_perfil', None)
            ))
            
            print(f"   ✅ Query executada sem erros")
            
            conn.commit()
            print(f"\n4. ✅ COMMIT realizado com sucesso")
            print(f"   Usuário '{dados['nome']}' inserido no banco!")
            
            cursor.close()
            print(f"=================================================\n")
            
            return True
            
        except psycopg2.IntegrityError as e:
            if conn:
                conn.rollback()
                print(f"\n❌ ERRO DE INTEGRIDADE (rollback realizado)")
            
            erro_str = str(e)
            print(f"   Detalhes: {erro_str}")
            
            # Identificar qual constraint foi violada
            if 'usuarios_email_key' in erro_str or 'email' in erro_str.lower():
                raise Exception(f"Email '{dados.get('email')}' já está cadastrado no sistema")
            elif 'usuarios_cpf_key' in erro_str or 'cpf' in erro_str.lower():
                raise Exception(f"CPF '{dados.get('cpf')}' já está cadastrado no sistema")
            else:
                raise Exception(f"Erro de integridade: {erro_str}")
                
        except psycopg2.DataError as e:
            if conn:
                conn.rollback()
            print(f"\n❌ ERRO DE TIPO DE DADOS (rollback realizado)")
            print(f"   Detalhes: {str(e)}")
            raise Exception(f"Dados inválidos: {str(e)}")
            
        except Exception as e:
            if conn:
                conn.rollback()
                print(f"\n❌ ERRO GERAL (rollback realizado)")
            print(f"   Tipo: {type(e).__name__}")
            print(f"   Mensagem: {str(e)}")
            print(f"=================================================\n")
            raise
            
        finally:
            if conn:
                release_connection(conn)
                print(f"5. Conexão devolvida ao pool")

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
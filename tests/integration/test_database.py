"""
Testes de conexão e operações básicas do banco de dados
"""
import pytest
from config.database import get_connection, release_connection, test_connection

class TestDatabase:
    
    def test_database_connection(self):
        """Testa se consegue conectar ao banco de dados"""
        assert test_connection() is True
    
    def test_get_connection(self):
        """Testa obtenção de conexão do pool"""
        conn = get_connection()
        
        assert conn is not None
        assert conn.closed == 0  # Conexão aberta
        
        release_connection(conn)
    
    def test_execute_simple_query(self, db_connection):
        """Testa execução de query simples"""
        cursor = db_connection.cursor()
        cursor.execute("SELECT 1 + 1 as resultado")
        resultado = cursor.fetchone()
        
        assert resultado[0] == 2
        cursor.close()
    
    def test_tables_exist(self, db_connection):
        """Testa se as tabelas necessárias existem"""
        cursor = db_connection.cursor()
        
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """)
        
        tables = [row[0] for row in cursor.fetchall()]
        
        assert 'usuarios' in tables
        assert 'veiculos' in tables
        assert 'pecas' in tables
        
        cursor.close()
    
    def test_usuarios_table_structure(self, db_connection):
        """Testa estrutura da tabela usuarios"""
        cursor = db_connection.cursor()
        
        cursor.execute("""
            SELECT column_name, data_type 
            FROM information_schema.columns 
            WHERE table_name = 'usuarios'
        """)
        
        columns = {row[0]: row[1] for row in cursor.fetchall()}
        
        assert 'id' in columns
        assert 'nome' in columns
        assert 'email' in columns
        assert 'senha' in columns
        assert 'cpf' in columns
        
        cursor.close()
    
    def test_foreign_keys_exist(self, db_connection):
        """Testa se as foreign keys existem"""
        cursor = db_connection.cursor()
        
        cursor.execute("""
            SELECT 
                tc.table_name, 
                kcu.column_name,
                ccu.table_name AS foreign_table_name
            FROM information_schema.table_constraints AS tc 
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
            WHERE tc.constraint_type = 'FOREIGN KEY'
        """)
        
        foreign_keys = cursor.fetchall()
        
        # Deve ter pelo menos 2 FKs (veiculos e pecas apontando para usuarios)
        assert len(foreign_keys) >= 2
        
        cursor.close()
    
    def test_transaction_rollback(self, db_connection):
        """Testa rollback de transação"""
        cursor = db_connection.cursor()
        
        try:
            # Tentar inserir dados inválidos
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, email, senha, perfil, cep, idade)
                VALUES ('invalid', 'Test', '111', 'test@test.com', 'pass', 'cliente', '57000-000', '1990-01-01')
            """)
            
            # Forçar erro com email duplicado
            cursor.execute("""
                INSERT INTO usuarios (id, nome, cpf, email, senha, perfil, cep, idade)
                VALUES ('invalid2', 'Test2', '222', 'test@test.com', 'pass', 'cliente', '57000-000', '1990-01-01')
            """)
            
            db_connection.commit()
        except:
            db_connection.rollback()
            
            # Verificar que nenhum registro foi inserido
            cursor.execute("SELECT COUNT(*) FROM usuarios WHERE email = 'test@test.com'")
            count = cursor.fetchone()[0]
            
            assert count == 0
        
        cursor.close()
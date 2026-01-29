import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv # pip install python-dotenv

# Carrega as variáveis do arquivo .env
load_dotenv()

# Configurações do banco de dados PostgreSQL
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASS', 'postgres'), # Pega do .env ou usa padrão
    'database': os.getenv('DB_NAME', 'server_kaido_house'),
    'port': int(os.getenv('DB_PORT', 5432))
}

# ... resto do código igual ...

# Pool de conexões para melhor performance
connection_pool = None

def init_connection_pool():
    """Inicializa o pool de conexões"""
    global connection_pool
    try:
        connection_pool = psycopg2.pool.SimpleConnectionPool(
            1, 20,  # Min e Max conexões
            **DB_CONFIG
        )
        if connection_pool:
            print("✅ Pool de conexões PostgreSQL criado com sucesso")
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Erro ao criar pool de conexões: {error}")

def get_connection():
    """
    Retorna uma conexão do pool.
    
    Returns:
        connection: Objeto de conexão PostgreSQL
    """
    global connection_pool
    
    if connection_pool is None:
        init_connection_pool()
    
    try:
        connection = connection_pool.getconn()
        return connection
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Erro ao obter conexão: {error}")
        raise

def release_connection(connection):
    """
    Devolve a conexão ao pool.
    
    Args:
        connection: Conexão a ser devolvida
    """
    global connection_pool
    if connection_pool:
        connection_pool.putconn(connection)

def close_all_connections():
    """Fecha todas as conexões do pool"""
    global connection_pool
    if connection_pool:
        connection_pool.closeall()
        print("✅ Todas as conexões fechadas")

def test_connection():
    """Testa a conexão com o banco de dados"""
    try:
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"✅ Conectado ao PostgreSQL")
        print(f"   Versão: {version[0]}")
        cursor.close()
        release_connection(conn)
        return True
    except (Exception, psycopg2.Error) as error:
        print(f"❌ Falha na conexão: {error}")
        print("\n🔧 Verifique:")
        print("1. O PostgreSQL está rodando?")
        print("2. A senha está correta?")
        print("3. O banco 'kaido_house' existe?")
        print("4. O usuário 'postgres' tem permissão?")
        return False

if __name__ == "__main__":
    # Teste a conexão executando este arquivo diretamente
    test_connection()
    close_all_connections()
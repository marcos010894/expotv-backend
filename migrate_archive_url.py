"""
Script de migração para garantir que a coluna archive_url existe nas tabelas
"""
import pymysql
from urllib.parse import quote_plus

# Configuração do banco
usuario = "u441041902_exportv"
senha = "Mito010894@@"
host = "193.203.175.53"
banco = "u441041902_exportv"
porta = 3306

print("🔧 Iniciando verificação/migração do banco de dados...")

try:
    # Conectar ao banco
    connection = pymysql.connect(
        host=host,
        port=porta,
        user=usuario,
        password=senha,
        database=banco,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    print("✅ Conectado ao banco de dados")
    
    # Verificar se a coluna archive_url existe na tabela anuncio
    print("\n📋 Verificando tabela 'anuncio'...")
    cursor.execute("SHOW COLUMNS FROM anuncio LIKE 'archive_url'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Coluna 'archive_url' já existe na tabela 'anuncio'")
    else:
        print("⚠️  Coluna 'archive_url' NÃO existe! Adicionando...")
        cursor.execute("ALTER TABLE anuncio ADD COLUMN archive_url TEXT NULL")
        connection.commit()
        print("✅ Coluna 'archive_url' adicionada à tabela 'anuncio'")
    
    # Verificar se a coluna tempo_exibicao existe
    print("\n📋 Verificando coluna 'tempo_exibicao'...")
    cursor.execute("SHOW COLUMNS FROM anuncio LIKE 'tempo_exibicao'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Coluna 'tempo_exibicao' já existe")
    else:
        print("⚠️  Coluna 'tempo_exibicao' NÃO existe! Adicionando...")
        cursor.execute("ALTER TABLE anuncio ADD COLUMN tempo_exibicao INT DEFAULT 10")
        connection.commit()
        print("✅ Coluna 'tempo_exibicao' adicionada")
    
    # Verificar tabela aviso
    print("\n📋 Verificando tabela 'aviso'...")
    cursor.execute("SHOW COLUMNS FROM aviso LIKE 'archive_url'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Coluna 'archive_url' já existe na tabela 'aviso'")
    else:
        print("⚠️  Coluna 'archive_url' NÃO existe! Adicionando...")
        cursor.execute("ALTER TABLE aviso ADD COLUMN archive_url TEXT NULL")
        connection.commit()
        print("✅ Coluna 'archive_url' adicionada à tabela 'aviso'")
    
    # Mostrar estrutura final
    print("\n📊 Estrutura final da tabela 'anuncio':")
    cursor.execute("DESCRIBE anuncio")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\n📊 Estrutura final da tabela 'aviso':")
    cursor.execute("DESCRIBE aviso")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\n✅ Migração concluída com sucesso!")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")
finally:
    if connection:
        connection.close()
        print("\n🔌 Conexão fechada")

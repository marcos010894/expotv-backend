"""
Migração: Adiciona coluna last_ping na tabela tv
"""
import pymysql

# Configuração do banco
usuario = "u441041902_exportv"
senha = "Mito010894@@"
host = "193.203.175.53"
banco = "u441041902_exportv"
porta = 3306

print("🔧 Adicionando coluna last_ping na tabela tv...")

try:
    connection = pymysql.connect(
        host=host,
        port=porta,
        user=usuario,
        password=senha,
        database=banco,
        charset='utf8mb4'
    )
    
    cursor = connection.cursor()
    
    # Verificar se a coluna já existe
    cursor.execute("SHOW COLUMNS FROM tv LIKE 'last_ping'")
    result = cursor.fetchone()
    
    if result:
        print("✅ Coluna 'last_ping' já existe!")
    else:
        print("➕ Adicionando coluna 'last_ping'...")
        cursor.execute("ALTER TABLE tv ADD COLUMN last_ping DATETIME NULL")
        connection.commit()
        print("✅ Coluna 'last_ping' adicionada com sucesso!")
    
    # Mostrar estrutura da tabela
    print("\n📊 Estrutura da tabela 'tv':")
    cursor.execute("DESCRIBE tv")
    for row in cursor.fetchall():
        print(f"  {row[0]}: {row[1]}")
    
    print("\n✅ Migração concluída!")
    
except Exception as e:
    print(f"❌ Erro: {str(e)}")
finally:
    if connection:
        connection.close()
        print("🔌 Conexão fechada")

#!/usr/bin/env python3
"""
Migração: Adicionar campos reset_token e reset_token_expires na tabela user
"""

from sqlmodel import create_engine, text
import os
from urllib.parse import quote_plus

# Usar a mesma configuração do db.py
usuario = "u441041902_exportv"
senha = quote_plus("Mito010894@@")
host = "193.203.175.53"
banco = "u441041902_exportv"
porta = 3306

DATABASE_URL = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}"

engine = create_engine(DATABASE_URL, echo=True)

def migrate():
    """Adiciona colunas para recuperação de senha"""
    
    print("🔧 Adicionando campos de recuperação de senha na tabela user...")
    
    with engine.connect() as conn:
        # Verificar se as colunas já existem
        result = conn.execute(text("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = 'u441041902_exportv' 
            AND TABLE_NAME = 'user'
            AND COLUMN_NAME IN ('reset_token', 'reset_token_expires')
        """))
        
        existing_columns = [row[0] for row in result]
        
        # Adicionar reset_token se não existir
        if 'reset_token' not in existing_columns:
            print("➕ Adicionando coluna 'reset_token'...")
            conn.execute(text("""
                ALTER TABLE user 
                ADD COLUMN reset_token VARCHAR(255) NULL
            """))
            conn.commit()
            print("✅ Coluna 'reset_token' adicionada!")
        else:
            print("ℹ️  Coluna 'reset_token' já existe")
        
        # Adicionar reset_token_expires se não existir
        if 'reset_token_expires' not in existing_columns:
            print("➕ Adicionando coluna 'reset_token_expires'...")
            conn.execute(text("""
                ALTER TABLE user 
                ADD COLUMN reset_token_expires DATETIME NULL
            """))
            conn.commit()
            print("✅ Coluna 'reset_token_expires' adicionada!")
        else:
            print("ℹ️  Coluna 'reset_token_expires' já existe")
        
        # Mostrar estrutura da tabela
        print("\n📋 Estrutura atual da tabela user:")
        result = conn.execute(text("DESCRIBE user"))
        for row in result:
            print(f"  - {row[0]}: {row[1]}")
    
    print("\n✅ Migração concluída!")

if __name__ == "__main__":
    migrate()

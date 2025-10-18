#!/usr/bin/env python3

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from sqlmodel import SQLModel
from app.db import engine
from app.models import User, Condominio, TV, Anuncio

def create_tables():
    print("🔄 Criando todas as tabelas...")
    SQLModel.metadata.create_all(engine)
    print("✅ Tabelas criadas com sucesso!")
    
    # Verificar se funcionou
    import sqlite3
    conn = sqlite3.connect('database.db')
    cursor = conn.cursor()

    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print('\n📋 Tabelas criadas:')
    for table in tables:
        print(f'  - {table[0]}')

    # Verificar estrutura da tabela user
    if any('user' in table for table in tables):
        cursor.execute('PRAGMA table_info(user);')
        columns = cursor.fetchall()
        print('\n📊 Estrutura da tabela user:')
        for col in columns:
            print(f'  - {col[1]} ({col[2]})')
            
    conn.close()

if __name__ == "__main__":
    create_tables()

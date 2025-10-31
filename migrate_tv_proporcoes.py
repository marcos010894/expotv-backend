#!/usr/bin/env python3
"""
Migração: Adicionar configurações de proporção nas TVs
Data: 31 de outubro de 2025
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

print("🔄 Migração: Configurações de Proporção de Exibição por TV")
print("=" * 70)

# Conectar ao banco
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", "3306"))
)

try:
    with conn.cursor() as cursor:
        print("\n📋 Adicionando colunas de configuração...")
        
        # Verificar se as colunas já existem
        cursor.execute("""
            SELECT COUNT(*) 
            FROM information_schema.COLUMNS 
            WHERE TABLE_SCHEMA = %s 
            AND TABLE_NAME = 'tv' 
            AND COLUMN_NAME = 'proporcao_avisos'
        """, (os.getenv("DB_NAME"),))
        
        if cursor.fetchone()[0] > 0:
            print("⚠️  Colunas já existem! Pulando migração...")
        else:
            # Adicionar coluna proporcao_avisos
            cursor.execute("""
                ALTER TABLE tv 
                ADD COLUMN proporcao_avisos INT NOT NULL DEFAULT 1
            """)
            print("✅ Adicionada coluna 'proporcao_avisos' (padrão: 1)")
            
            # Adicionar coluna proporcao_anuncios
            cursor.execute("""
                ALTER TABLE tv 
                ADD COLUMN proporcao_anuncios INT NOT NULL DEFAULT 5
            """)
            print("✅ Adicionada coluna 'proporcao_anuncios' (padrão: 5)")
            
            # Adicionar coluna proporcao_noticias
            cursor.execute("""
                ALTER TABLE tv 
                ADD COLUMN proporcao_noticias INT NOT NULL DEFAULT 3
            """)
            print("✅ Adicionada coluna 'proporcao_noticias' (padrão: 3)")
            
            conn.commit()
            print("\n✅ Migração concluída com sucesso!")
            
        # Mostrar TVs existentes
        cursor.execute("SELECT id, nome, proporcao_avisos, proporcao_anuncios, proporcao_noticias FROM tv")
        tvs = cursor.fetchall()
        
        if tvs:
            print(f"\n📺 TVs no sistema ({len(tvs)}):")
            print("-" * 70)
            for tv_id, nome, av, an, nt in tvs:
                print(f"  TV #{tv_id}: {nome}")
                print(f"    Proporção: {av} aviso : {an} anúncios : {nt} notícias")
        else:
            print("\n⚠️  Nenhuma TV cadastrada no sistema")

except Exception as e:
    print(f"\n❌ Erro durante migração: {e}")
    conn.rollback()
finally:
    conn.close()

print("\n" + "=" * 70)
print("✅ Script finalizado!")
print("\n💡 Dica: Use o endpoint PUT /tvs/{id}/config para atualizar as proporções")

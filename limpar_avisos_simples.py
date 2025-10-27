#!/usr/bin/env python3
"""
Script simples para deletar avisos inativos
"""
import pymysql
import os
from dotenv import load_dotenv

load_dotenv()

# Conectar ao banco
conn = pymysql.connect(
    host=os.getenv("DB_HOST"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    database=os.getenv("DB_NAME"),
    port=int(os.getenv("DB_PORT", "3306"))
)

print("🗑️ Limpeza Rápida de Avisos")
print("=" * 60)

try:
    with conn.cursor() as cursor:
        # Listar todos os avisos
        cursor.execute("SELECT id, nome, status, condominios_ids FROM aviso")
        avisos = cursor.fetchall()
        
        print(f"\n📊 Total de avisos: {len(avisos)}\n")
        
        ativos = []
        inativos = []
        outros = []
        
        for aviso in avisos:
            aviso_id, nome, status, cond_ids = aviso
            
            if status == "Ativo":
                ativos.append(aviso)
                print(f"✅ #{aviso_id}: {nome} - {status} - Conds: {cond_ids}")
            elif status == "Inativo":
                inativos.append(aviso)
                print(f"❌ #{aviso_id}: {nome} - {status} - Conds: {cond_ids}")
            else:
                outros.append(aviso)
                print(f"⚠️  #{aviso_id}: {nome} - {status} - Conds: {cond_ids}")
        
        print("\n" + "=" * 60)
        print(f"✅ Ativos: {len(ativos)}")
        print(f"❌ Inativos: {len(inativos)}")
        print(f"⚠️  Outros status: {len(outros)}")
        print("=" * 60)
        
        # Deletar inativos
        if inativos:
            print(f"\n⚠️ Deletar {len(inativos)} avisos INATIVOS?")
            print("Avisos a deletar:")
            for aviso in inativos:
                print(f"   - #{aviso[0]}: {aviso[1]}")
            
            confirma = input("\nDigite 'SIM' para confirmar: ").strip()
            
            if confirma == "SIM":
                cursor.execute("DELETE FROM aviso WHERE status = 'Inativo'")
                conn.commit()
                print(f"\n✅ {cursor.rowcount} avisos deletados!")
            else:
                print("\n❌ Cancelado")
        
        # Deletar outros status (ativo, ativoetc)
        if outros:
            print(f"\n⚠️ Encontrados {len(outros)} avisos com status diferente de 'Ativo' ou 'Inativo'")
            print("Avisos:")
            for aviso in outros:
                print(f"   - #{aviso[0]}: {aviso[1]} ({aviso[2]})")
            
            print("\nOpções:")
            print("1. Atualizar para 'Ativo'")
            print("2. Atualizar para 'Inativo'")
            print("3. Deletar")
            print("4. Deixar como está")
            
            opcao = input("\nEscolha (1-4): ").strip()
            
            if opcao == "1":
                ids = [str(a[0]) for a in outros]
                cursor.execute(f"UPDATE aviso SET status = 'Ativo' WHERE id IN ({','.join(ids)})")
                conn.commit()
                print(f"✅ {cursor.rowcount} avisos atualizados para 'Ativo'")
            elif opcao == "2":
                ids = [str(a[0]) for a in outros]
                cursor.execute(f"UPDATE aviso SET status = 'Inativo' WHERE id IN ({','.join(ids)})")
                conn.commit()
                print(f"✅ {cursor.rowcount} avisos atualizados para 'Inativo'")
            elif opcao == "3":
                ids = [str(a[0]) for a in outros]
                cursor.execute(f"DELETE FROM aviso WHERE id IN ({','.join(ids)})")
                conn.commit()
                print(f"✅ {cursor.rowcount} avisos deletados")

finally:
    conn.close()

print("\n" + "=" * 60)
print("✅ Concluído!")

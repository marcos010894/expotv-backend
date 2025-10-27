#!/usr/bin/env python3
"""
Script para limpar avisos do banco de dados
"""
from sqlmodel import Session, select
from app.db import engine
from app.models import Aviso, Condominio, User

print("🗑️ Limpeza de Avisos")
print("=" * 60)

with Session(engine) as session:
    # Buscar todos os avisos
    avisos = session.exec(select(Aviso)).all()
    
    print(f"\n📊 Total de avisos no banco: {len(avisos)}")
    print("\n" + "=" * 60)
    
    # Listar todos os avisos
    for aviso in avisos:
        # Buscar nome do síndico
        condominio_ids = [int(id.strip()) for id in aviso.condominios_ids.split(",") if id.strip()]
        sindico_nome = "Desconhecido"
        
        if condominio_ids:
            cond = session.get(Condominio, condominio_ids[0])
            if cond and cond.sindico_id:
                sindico = session.get(User, cond.sindico_id)
                if sindico:
                    sindico_nome = sindico.nome
        
        status_emoji = "✅" if aviso.status == "Ativo" else "❌"
        print(f"\n{status_emoji} Aviso #{aviso.id}")
        print(f"   Nome: {aviso.nome}")
        print(f"   Status: {aviso.status}")
        print(f"   Condomínios: {aviso.condominios_ids}")
        print(f"   Síndico: {sindico_nome}")
    
    print("\n" + "=" * 60)
    print("\n🤔 O que você quer fazer?")
    print("1. Deletar TODOS os avisos Inativos")
    print("2. Deletar avisos específicos por ID")
    print("3. Deletar TODOS os avisos (CUIDADO!)")
    print("4. Sair sem fazer nada")
    
    escolha = input("\nEscolha uma opção (1-4): ").strip()
    
    if escolha == "1":
        # Deletar avisos inativos
        avisos_inativos = session.exec(
            select(Aviso).where(Aviso.status != "Ativo")
        ).all()
        
        print(f"\n⚠️ Serão deletados {len(avisos_inativos)} avisos inativos:")
        for aviso in avisos_inativos:
            print(f"   - #{aviso.id}: {aviso.nome} ({aviso.status})")
        
        confirma = input("\nConfirmar deleção? (sim/não): ").strip().lower()
        if confirma == "sim":
            for aviso in avisos_inativos:
                session.delete(aviso)
            session.commit()
            print(f"✅ {len(avisos_inativos)} avisos inativos deletados!")
        else:
            print("❌ Operação cancelada")
    
    elif escolha == "2":
        # Deletar por ID
        ids_str = input("\nDigite os IDs separados por vírgula (ex: 1,2,3): ").strip()
        ids = [int(id.strip()) for id in ids_str.split(",") if id.strip().isdigit()]
        
        avisos_para_deletar = []
        for aviso_id in ids:
            aviso = session.get(Aviso, aviso_id)
            if aviso:
                avisos_para_deletar.append(aviso)
                print(f"   ✓ Encontrado: #{aviso.id} - {aviso.nome}")
            else:
                print(f"   ✗ Não encontrado: #{aviso_id}")
        
        if avisos_para_deletar:
            confirma = input(f"\nConfirmar deleção de {len(avisos_para_deletar)} avisos? (sim/não): ").strip().lower()
            if confirma == "sim":
                for aviso in avisos_para_deletar:
                    session.delete(aviso)
                session.commit()
                print(f"✅ {len(avisos_para_deletar)} avisos deletados!")
            else:
                print("❌ Operação cancelada")
    
    elif escolha == "3":
        # DELETAR TUDO
        print("\n⚠️⚠️⚠️ ATENÇÃO! ⚠️⚠️⚠️")
        print(f"Isso vai deletar TODOS os {len(avisos)} avisos do banco!")
        confirma = input("Digite 'DELETAR TUDO' para confirmar: ").strip()
        
        if confirma == "DELETAR TUDO":
            for aviso in avisos:
                session.delete(aviso)
            session.commit()
            print(f"✅ Todos os {len(avisos)} avisos foram deletados!")
        else:
            print("❌ Operação cancelada")
    
    else:
        print("👋 Saindo sem fazer alterações...")

print("\n" + "=" * 60)
print("✅ Script finalizado!")

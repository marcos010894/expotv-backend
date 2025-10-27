#!/usr/bin/env python3
"""
Script para verificar e corrigir todas as senhas dos usuários
"""

from sqlmodel import Session, select
from app.db import engine
from app.models import User
from app.auth import get_password_hash, verify_password

def fix_all_passwords():
    print("🔧 Verificando e corrigindo senhas de todos os usuários...")
    
    with Session(engine) as session:
        # Buscar todos os usuários
        users = session.exec(select(User)).all()
        
        if not users:
            print("❌ Nenhum usuário encontrado!")
            return
        
        print(f"📋 Encontrados {len(users)} usuários:")
        
        for user in users:
            print(f"\n👤 Usuário: {user.nome} ({user.email})")
            print(f"   Senha atual: {user.senha}")
            
            # Verificar se a senha já está hasheada
            if user.senha.startswith('$2b$'):
                print("   ✅ Senha já está hasheada corretamente!")
                continue
            
            # Testar se consegue fazer hash da senha atual
            try:
                # Converter senha para hash
                print(f"   🔄 Convertendo senha '{user.senha}' para hash...")
                hashed_password = get_password_hash(user.senha)
                
                # Testar se o hash funciona
                if verify_password(user.senha, hashed_password):
                    print("   ✅ Hash criado e testado com sucesso!")
                    
                    # Atualizar no banco
                    user.senha = hashed_password
                    session.add(user)
                    print(f"   💾 Senha atualizada no banco")
                else:
                    print("   ❌ Erro ao testar hash!")
                    
            except Exception as e:
                print(f"   ❌ Erro ao processar senha: {str(e)}")
        
        try:
            session.commit()
            print("\n✅ Todas as senhas foram atualizadas com sucesso!")
        except Exception as e:
            print(f"\n❌ Erro ao salvar no banco: {str(e)}")
            session.rollback()

if __name__ == "__main__":
    fix_all_passwords()

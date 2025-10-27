#!/usr/bin/env python3
"""
Script para testar o login
"""

from sqlmodel import Session, select
from app.db import engine
from app.models import User
from app.auth import verify_password, get_password_hash

def test_login():
    print("🧪 Testando sistema de login...")
    
    with Session(engine) as session:
        # Buscar um usuário
        user = session.exec(select(User).where(User.email == "marcosmachadodev@gmail.com")).first()
        
        if not user:
            print("❌ Usuário não encontrado!")
            return
        
        print(f"👤 Testando login para: {user.nome} ({user.email})")
        print(f"   Hash no banco: {user.senha}")
        
        # Testar algumas senhas
        test_passwords = ["Mito010894@@", "123456", "admin123", "Mito0108946@", "senha123"]
        
        for pwd in test_passwords:
            print(f"\n🔑 Testando senha: '{pwd}'")
            try:
                result = verify_password(pwd, user.senha)
                if result:
                    print(f"   ✅ SUCESSO! Senha '{pwd}' está correta!")
                    return pwd
                else:
                    print(f"   ❌ Senha '{pwd}' incorreta")
            except Exception as e:
                print(f"   💥 Erro ao verificar senha '{pwd}': {str(e)}")
        
        print("\n❌ Nenhuma senha funcionou!")
        
        # Criar nova senha de teste
        print("\n🔧 Criando nova senha de teste...")
        new_password = "123456"
        new_hash = get_password_hash(new_password)
        
        print(f"   Nova senha: {new_password}")
        print(f"   Novo hash: {new_hash}")
        
        # Testar novo hash
        if verify_password(new_password, new_hash):
            print("   ✅ Novo hash funciona!")
            
            # Atualizar no banco
            user.senha = new_hash
            session.add(user)
            session.commit()
            print("   💾 Senha atualizada no banco!")
            
        else:
            print("   ❌ Erro ao testar novo hash!")

if __name__ == "__main__":
    test_login()

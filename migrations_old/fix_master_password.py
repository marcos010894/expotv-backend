#!/usr/bin/env python3
"""
Script para corrigir senha do usuário master
Converte senhas em texto simples para hash bcrypt
"""

from sqlmodel import Session, select
from app.db import engine
from app.models import User
from app.auth import get_password_hash

def fix_master_password():
    print("🔧 Corrigindo senha do usuário master...")
    
    with Session(engine) as session:
        # Buscar usuário master
        master = session.exec(select(User).where(User.email == "admin@admin.com")).first()
        
        if not master:
            print("❌ Usuário master não encontrado!")
            return
        
        # Verificar se a senha já está hasheada
        if master.senha.startswith('$2b$'):
            print("✅ Senha já está hasheada corretamente!")
            return
        
        # Converter senha para hash
        print(f"📝 Convertendo senha '{master.senha}' para hash...")
        hashed_password = get_password_hash(master.senha)
        
        # Atualizar no banco
        master.senha = hashed_password
        session.add(master)
        session.commit()
        
        print("✅ Senha do master atualizada com sucesso!")
        print(f"   Email: {master.email}")
        print(f"   Hash: {hashed_password[:50]}...")

if __name__ == "__main__":
    fix_master_password()

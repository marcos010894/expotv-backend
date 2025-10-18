from sqlmodel import Session, select, SQLModel
from app.db import engine
from app.models import User
from app.auth import get_password_hash
from datetime import datetime

def create_master_user():
    # Primeiro criar as tabelas
    SQLModel.metadata.create_all(engine)
    
    with Session(engine) as session:
        # Verificar se já existe um usuário master
        existing_master = session.exec(select(User).where(User.email == "admin@expo-tv.com")).first()
        if existing_master:
            print("Usuário master já existe!")
            return
        
        # Criar usuário master
        master_user = User(
            nome="Administrador Master",
            email="admin@expo-tv.com",
            senha=get_password_hash("master123"),  # Senha: master123
            tipo="ADM",
            data_criacao=datetime.utcnow()
        )
        
        session.add(master_user)
        session.commit()
        session.refresh(master_user)
        
        print("Usuário master criado com sucesso!")
        print(f"Email: admin@expo-tv.com")
        print(f"Senha: master123")
        print(f"Tipo: ADM")

if __name__ == "__main__":
    create_master_user()

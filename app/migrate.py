from sqlmodel import SQLModel
from app.db import engine
# Importar TODOS os modelos para o SQLModel reconhecê-los
from app.models import User, Condominio, TV, Anuncio, Aviso

def create_db_and_tables():
    print("Criando tabelas...")
    SQLModel.metadata.create_all(engine)
    print("Tabelas criadas com sucesso!")

if __name__ == "__main__":
    create_db_and_tables()

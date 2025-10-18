from sqlmodel import SQLModel, create_engine
import pymysql
from urllib.parse import quote_plus

# Configuração do banco de dados MySQL
usuario = "u441041902_exportv"
senha = quote_plus("Mito010894@@")  # Codificar caracteres especiais
host = "193.203.175.53"
banco = "u441041902_exportv"
porta = 3306

DATABASE_URL = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}"

engine = create_engine(DATABASE_URL, echo=True)

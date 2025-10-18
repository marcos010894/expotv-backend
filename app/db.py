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

# Engine com configurações de pool para evitar conexões perdidas
engine = create_engine(
    DATABASE_URL, 
    echo=False,                   # Desabilita logs SQL (melhor performance)
    pool_pre_ping=True,           # Testa conexão antes de usar (previne conexões mortas)
    pool_recycle=3600,            # Recicla conexões a cada 1 hora (previne timeout do MySQL)
    pool_size=10,                 # Máximo de 10 conexões ativas no pool
    max_overflow=20,              # Até 20 conexões extras temporárias
    pool_timeout=30,              # Timeout ao aguardar conexão disponível
    connect_args={
        "connect_timeout": 10,    # Timeout de conexão: 10s
        "read_timeout": 30,       # Timeout de leitura: 30s
        "write_timeout": 30       # Timeout de escrita: 30s
    }
)

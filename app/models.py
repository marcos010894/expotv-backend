from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    tipo: str  # 'ADM' ou 'SINDICO'
    nome: str
    email: str
    senha: str
    token: Optional[str] = None
    data_criacao: datetime = Field(default_factory=datetime.utcnow)
    data_update: Optional[datetime] = None
    telefone: Optional[str] = None
    foto_url: Optional[str] = None
    limite_avisos: int = Field(default=10)  # Quantidade de avisos permitidos para o síndico
    condominios: List["Condominio"] = Relationship(back_populates="sindico")

class Condominio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    sindico_id: int = Field(foreign_key="user.id")
    localizacao: Optional[str] = None
    cep: Optional[str] = None
    data_registro: datetime = Field(default_factory=datetime.utcnow)
    sindico: Optional[User] = Relationship(back_populates="condominios")
    tvs: List["TV"] = Relationship(back_populates="condominio")

class TV(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    condominio_id: int = Field(foreign_key="condominio.id")
    codigo_conexao: str
    status: str  # 'online' ou 'offline'
    template: Optional[str] = None
    data_registro: datetime = Field(default_factory=datetime.utcnow)
    last_ping: Optional[datetime] = None  # Último ping recebido da TV
    condominio: Optional[Condominio] = Relationship(back_populates="tvs")

class Anuncio(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    condominios_ids: str  # Armazenar como string separada por vírgula para SQLite
    numero_anunciante: Optional[str] = None
    nome_anunciante: Optional[str] = None
    status: str
    data_expiracao: Optional[datetime] = None
    archive_url: Optional[str] = None
    tempo_exibicao: int = Field(default=10)  # Tempo em segundos para exibir o anúncio (padrão: 10s)

class Aviso(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nome: str
    condominios_ids: str  # Armazenar como string separada por vírgula
    sindico_ids: Optional[str] = None  # IDs dos síndicos (separados por vírgula)
    numero_anunciante: Optional[str] = None
    nome_anunciante: Optional[str] = None
    status: str
    data_expiracao: Optional[datetime] = None
    archive_url: Optional[str] = None
    mensagem: Optional[str] = None  # Campo adicional para avisos (opcional)

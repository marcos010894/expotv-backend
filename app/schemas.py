from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    tipo: str = "SINDICO"
    nome: str
    email: str
    senha: str
    telefone: Optional[str] = None
    limite_avisos: int = 10  # Limite de avisos permitidos (padrão: 10)

class UserUpdate(BaseModel):
    tipo: Optional[str] = None
    nome: Optional[str] = None
    email: Optional[str] = None
    senha: Optional[str] = None  # Senha é opcional na atualização
    telefone: Optional[str] = None
    limite_avisos: Optional[int] = None

class PasswordChange(BaseModel):
    senha_atual: str
    senha_nova: str

class CondominioCreate(BaseModel):
    nome: str
    sindico_id: int
    localizacao: Optional[str] = None
    cep: Optional[str] = None

class TVCreate(BaseModel):
    nome: str
    condominio_id: int
    template: Optional[str] = None

class AnuncioCreate(BaseModel):
    nome: str
    condominios_ids: str
    numero_anunciante: Optional[str] = None
    nome_anunciante: Optional[str] = None
    status: str
    data_expiracao: Optional[datetime] = None
    tempo_exibicao: int = 10  # Tempo em segundos (padrão: 10s)

class AvisoCreate(BaseModel):
    nome: str
    condominios_ids: str
    sindico_ids: Optional[str] = None  # IDs dos síndicos (separados por vírgula)
    numero_anunciante: Optional[str] = None
    nome_anunciante: Optional[str] = None
    status: str
    data_expiracao: Optional[datetime] = None
    mensagem: str  # Campo adicional para avisos

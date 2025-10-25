from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import engine
from app.models import TV
from app.schemas import TVCreate
from datetime import datetime
import random

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/tvs", summary="Listar TVs", description="Lista todas as TVs do sistema")
def get_all_tvs(session: Session = Depends(get_session)):
    tvs = session.exec(select(TV)).all()
    return tvs

@router.get("/tvs/{tv_id}", summary="Buscar TV", description="Busca uma TV específica por ID")
def get_tv(tv_id: int, session: Session = Depends(get_session)):
    tv = session.get(TV, tv_id)
    if not tv:
        raise HTTPException(status_code=404, detail="TV não encontrada")
    return tv

@router.post("/tvs", summary="Criar TV", description="Cria nova TV e gera código de conexão automaticamente")
def create_tv(tv_data: TVCreate, session: Session = Depends(get_session)):
    tv = TV(
        nome=tv_data.nome,
        condominio_id=tv_data.condominio_id,
        codigo_conexao=str(random.randint(10000, 99999)),
        status="offline",
        template=tv_data.template,
        data_registro=datetime.utcnow()
    )
    session.add(tv)
    session.commit()
    session.refresh(tv)
    return tv

@router.put("/tvs/{tv_id}", summary="Atualizar TV", description="Atualiza dados de uma TV")
def update_tv(tv_id: int, tv_data: TVCreate, session: Session = Depends(get_session)):
    db_tv = session.get(TV, tv_id)
    if not db_tv:
        raise HTTPException(status_code=404, detail="TV não encontrada")
    
    db_tv.nome = tv_data.nome
    db_tv.condominio_id = tv_data.condominio_id
    db_tv.template = tv_data.template
    
    session.add(db_tv)
    session.commit()
    session.refresh(db_tv)
    return db_tv

@router.delete("/tvs/{tv_id}", summary="Deletar TV", description="Remove uma TV do sistema")
def delete_tv(tv_id: int, session: Session = Depends(get_session)):
    db_tv = session.get(TV, tv_id)
    if not db_tv:
        raise HTTPException(status_code=404, detail="TV não encontrada")
    session.delete(db_tv)
    session.commit()
    return {"ok": True}

@router.post("/tvs/{codigo_conexao}/status", summary="Conectar TV", description="Marca TV como online usando código de conexão")
def update_tv_status(codigo_conexao: str, session: Session = Depends(get_session)):
    tv = session.exec(select(TV).where(TV.codigo_conexao == codigo_conexao)).first()
    if not tv:
        raise HTTPException(status_code=404, detail="TV não encontrada")
    tv.status = "online"
    tv.last_ping = datetime.now()  # Atualizar timestamp do último ping
    session.add(tv)
    session.commit()
    session.refresh(tv)
    return tv

@router.post("/tvs/{codigo_conexao}/ping", summary="💓 Heartbeat da TV", description="Endpoint que a TV deve chamar a cada 1-2 minutos para manter status online")
def tv_heartbeat(codigo_conexao: str, session: Session = Depends(get_session)):
    """
    Endpoint de heartbeat/ping para TVs
    
    A TV deve chamar este endpoint a cada 1-2 minutos para:
    - Manter status como 'online'
    - Atualizar timestamp do último ping
    - Evitar ser marcada como offline pelo monitor
    
    Args:
        codigo_conexao: Código único de conexão da TV
    
    Returns:
        Status da TV e timestamp do ping
    """
    tv = session.exec(select(TV).where(TV.codigo_conexao == codigo_conexao)).first()
    if not tv:
        raise HTTPException(status_code=404, detail="TV não encontrada com este código")
    
    # Atualizar status e último ping
    tv.status = "online"
    tv.last_ping = datetime.now()
    session.add(tv)
    session.commit()
    session.refresh(tv)
    
    return {
        "success": True,
        "status": tv.status,
        "last_ping": tv.last_ping,
        "message": "Heartbeat registrado com sucesso"
    }

@router.get("/tvs/{codigo_conexao}/status", summary="Status da TV", description="Verifica status da TV pelo código de conexão")
def get_tv_status(codigo_conexao: str, session: Session = Depends(get_session)):
    tv = session.exec(select(TV).where(TV.codigo_conexao == codigo_conexao)).first()
    if not tv:
        raise HTTPException(status_code=404, detail="TV não encontrada")
    return {
        "status": tv.status,
        "last_ping": tv.last_ping,
        "nome": tv.nome
    }

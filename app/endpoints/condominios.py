from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from app.db import engine
from app.models import Condominio, User, TV, Anuncio
from app.schemas import CondominioCreate
from datetime import datetime

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/condominios/", summary="Listar condomínios", description="Lista todos os condomínios do sistema")
def get_all_condominios(session: Session = Depends(get_session)):
    condominios = session.exec(select(Condominio)).all()
    return condominios

@router.post("/condominios/", summary="Criar condomínio", description="Cria um novo condomínio")
def create_condominio(condominio_data: CondominioCreate, session: Session = Depends(get_session)):
    condominio = Condominio(
        nome=condominio_data.nome,
        sindico_id=condominio_data.sindico_id,
        localizacao=condominio_data.localizacao,
        cep=condominio_data.cep,
        data_registro=datetime.utcnow()
    )
    session.add(condominio)
    session.commit()
    session.refresh(condominio)
    return condominio

@router.put("/condominios/{condominio_id}", summary="Atualizar condomínio", description="Atualiza dados de um condomínio")
def update_condominio(condominio_id: int, condominio_data: CondominioCreate, session: Session = Depends(get_session)):
    db_condominio = session.get(Condominio, condominio_id)
    if not db_condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")
    
    db_condominio.nome = condominio_data.nome
    db_condominio.sindico_id = condominio_data.sindico_id
    db_condominio.localizacao = condominio_data.localizacao
    db_condominio.cep = condominio_data.cep
    
    session.add(db_condominio)
    session.commit()
    session.refresh(db_condominio)
    return db_condominio

@router.delete("/condominios/{condominio_id}", summary="Deletar condomínio", description="Remove um condomínio do sistema")
def delete_condominio(condominio_id: int, session: Session = Depends(get_session)):
    db_condominio = session.get(Condominio, condominio_id)
    if not db_condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")
    session.delete(db_condominio)
    session.commit()
    return {"ok": True}

@router.get("/condominios/{condominio_id}", summary="Detalhes do condomínio", description="Busca condomínio com suas TVs, anúncios e informações do síndico")
def get_condominio_detail(condominio_id: int, session: Session = Depends(get_session)):
    condominio = session.get(Condominio, condominio_id)
    if not condominio:
        raise HTTPException(status_code=404, detail="Condomínio não encontrado")
    
    # Buscar informações do síndico
    sindico = session.get(User, condominio.sindico_id)
    
    # Buscar TVs do condomínio
    tvs = session.exec(select(TV).where(TV.condominio_id == condominio_id)).all()
    
    # Buscar anúncios que contenham este condomínio_id na string condominios_ids
    anuncios = session.exec(select(Anuncio).where(Anuncio.condominios_ids.contains(str(condominio_id)))).all()
    
    return {
        "condominio": condominio, 
        "sindico": sindico,
        "tvs": tvs, 
        "anuncios": anuncios
    }

@router.get("/sindico/{user_id}/condominios", summary="Condomínios do síndico", description="Lista condomínios de um síndico específico")
def get_condominios_by_sindico(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user or user.tipo != "SINDICO":
        raise HTTPException(status_code=404, detail="Sindico não encontrado")
    condominios = session.exec(select(Condominio).where(Condominio.sindico_id == user_id)).all()
    return condominios

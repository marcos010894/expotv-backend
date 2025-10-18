from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from app.db import engine
from app.models import Aviso, Condominio
from app.schemas import AvisoCreate
from app.storage import upload_image_to_r2, delete_image_from_r2
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

# Schema para resposta com síndico
class AvisoWithSindico(BaseModel):
    id: int
    nome: str
    condominios_ids: str
    numero_anunciante: Optional[str]
    nome_anunciante: Optional[str]
    status: str
    data_expiracao: Optional[datetime]
    archive_url: Optional[str]
    mensagem: str
    sindico_ids: List[int]  # IDs dos síndicos responsáveis

@router.get("/avisos/", 
    summary="📋 Listar Avisos", 
    description="Lista todos os avisos cadastrados no sistema com ID do síndico responsável",
    response_description="Lista de avisos com síndicos",
    response_model=List[AvisoWithSindico]
)
def get_all_avisos(session: Session = Depends(get_session)):
    avisos = session.exec(select(Aviso)).all()
    
    # Para cada aviso, buscar os síndicos responsáveis
    avisos_with_sindico = []
    for aviso in avisos:
        # Extrair IDs dos condomínios
        condominio_ids = [int(id.strip()) for id in aviso.condominios_ids.split(",") if id.strip()]
        
        # Buscar síndicos dos condomínios
        sindico_ids = []
        for cond_id in condominio_ids:
            condominio = session.get(Condominio, cond_id)
            if condominio and condominio.sindico_id:
                if condominio.sindico_id not in sindico_ids:
                    sindico_ids.append(condominio.sindico_id)
        
        avisos_with_sindico.append(AvisoWithSindico(
            id=aviso.id,
            nome=aviso.nome,
            condominios_ids=aviso.condominios_ids,
            numero_anunciante=aviso.numero_anunciante,
            nome_anunciante=aviso.nome_anunciante,
            status=aviso.status,
            data_expiracao=aviso.data_expiracao,
            archive_url=aviso.archive_url,
            mensagem=aviso.mensagem,
            sindico_ids=sindico_ids
        ))
    
    return avisos_with_sindico

@router.get("/avisos/{aviso_id}", 
    summary="🔍 Buscar Aviso", 
    description="Busca um aviso específico pelo seu ID com síndico responsável",
    response_description="Dados do aviso com síndico",
    response_model=AvisoWithSindico
)
def get_aviso(aviso_id: int, session: Session = Depends(get_session)):
    aviso = session.get(Aviso, aviso_id)
    if not aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")
    
    # Extrair IDs dos condomínios
    condominio_ids = [int(id.strip()) for id in aviso.condominios_ids.split(",") if id.strip()]
    
    # Buscar síndicos dos condomínios
    sindico_ids = []
    for cond_id in condominio_ids:
        condominio = session.get(Condominio, cond_id)
        if condominio and condominio.sindico_id:
            if condominio.sindico_id not in sindico_ids:
                sindico_ids.append(condominio.sindico_id)
    
    return AvisoWithSindico(
        id=aviso.id,
        nome=aviso.nome,
        condominios_ids=aviso.condominios_ids,
        numero_anunciante=aviso.numero_anunciante,
        nome_anunciante=aviso.nome_anunciante,
        status=aviso.status,
        data_expiracao=aviso.data_expiracao,
        archive_url=aviso.archive_url,
        mensagem=aviso.mensagem,
        sindico_ids=sindico_ids
    )

@router.post("/avisos/", 
    summary="➕ Criar Aviso", 
    description="Cria um novo aviso no sistema",
    response_description="Aviso criado com sucesso"
)
def create_aviso(
    nome: str = Form(..., description="Nome/título do aviso", example="Aviso Importante"),
    condominios_ids: str = Form(..., description="IDs dos condomínios (separados por vírgula)", example="1,2,3"),
    numero_anunciante: Optional[str] = Form(None, description="Número de telefone do anunciante", example="11999887766"),
    nome_anunciante: Optional[str] = Form(None, description="Nome completo do anunciante", example="João Silva"),
    status: str = Form(..., description="Status do aviso", example="Ativo"),
    data_expiracao: Optional[datetime] = Form(None, description="Data de expiração do aviso (formato ISO)", example="2025-12-31T23:59:59"),
    mensagem: str = Form(..., description="Mensagem do aviso", example="Esta é uma mensagem importante para os moradores"),
    imagem: Optional[UploadFile] = File(
        None, 
        description="🖼️ Imagem do aviso (PNG, JPG, JPEG)",
        openapi_extra={
            "example": "imagem_aviso.png"
        }
    ),
    session: Session = Depends(get_session)
):
    """
    Cria um novo aviso no sistema:
    
    - **nome**: Título do aviso
    - **condominios_ids**: Lista de IDs dos condomínios (ex: "1,2,3")
    - **numero_anunciante**: Telefone do responsável (opcional)
    - **nome_anunciante**: Nome do responsável (opcional)
    - **status**: Status do aviso (ex: "Ativo", "Inativo")
    - **data_expiracao**: Data de vencimento (opcional)
    - **mensagem**: Conteúdo da mensagem do aviso
    - **imagem**: Arquivo de imagem (opcional)
    """
    
    archive_url = None
    if imagem:
        try:
            archive_url = upload_image_to_r2(imagem, "avisos")
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Erro ao fazer upload da imagem: {str(e)}")
    
    db_aviso = Aviso(
        nome=nome,
        condominios_ids=condominios_ids,
        numero_anunciante=numero_anunciante,
        nome_anunciante=nome_anunciante,
        status=status,
        data_expiracao=data_expiracao,
        archive_url=archive_url,
        mensagem=mensagem
    )
    
    session.add(db_aviso)
    session.commit()
    session.refresh(db_aviso)
    
    return db_aviso

@router.put("/avisos/{aviso_id}", 
    summary="✏️ Atualizar Aviso", 
    description="Atualiza dados de um aviso existente",
    response_description="Aviso atualizado com sucesso"
)
def update_aviso(
    aviso_id: int,
    nome: Optional[str] = Form(None, description="Nome/título do aviso"),
    condominios_ids: Optional[str] = Form(None, description="IDs dos condomínios (separados por vírgula)"),
    numero_anunciante: Optional[str] = Form(None, description="Número de telefone do anunciante"),
    nome_anunciante: Optional[str] = Form(None, description="Nome completo do anunciante"),
    status: Optional[str] = Form(None, description="Status do aviso"),
    data_expiracao: Optional[datetime] = Form(None, description="Data de expiração do aviso"),
    mensagem: Optional[str] = Form(None, description="Mensagem do aviso"),
    session: Session = Depends(get_session)
):
    """
    Atualiza um aviso existente.
    Apenas os campos enviados serão atualizados.
    """
    
    db_aviso = session.get(Aviso, aviso_id)
    if not db_aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")
    
    # Atualizar apenas os campos fornecidos
    if nome is not None:
        db_aviso.nome = nome
    if condominios_ids is not None:
        db_aviso.condominios_ids = condominios_ids
    if numero_anunciante is not None:
        db_aviso.numero_anunciante = numero_anunciante
    if nome_anunciante is not None:
        db_aviso.nome_anunciante = nome_anunciante
    if status is not None:
        db_aviso.status = status
    if data_expiracao is not None:
        db_aviso.data_expiracao = data_expiracao
    if mensagem is not None:
        db_aviso.mensagem = mensagem
    
    session.add(db_aviso)
    session.commit()
    session.refresh(db_aviso)
    
    return db_aviso

@router.put("/avisos/{aviso_id}/imagem", 
    summary="🖼️ Atualizar Imagem do Aviso", 
    description="Substitui a imagem de um aviso existente",
    response_description="Imagem atualizada com sucesso"
)
def update_aviso_image(
    aviso_id: int,
    imagem: UploadFile = File(
        ..., 
        description="🖼️ Nova imagem do aviso (PNG, JPG, JPEG)",
        openapi_extra={
            "example": "nova_imagem.png"
        }
    ),
    session: Session = Depends(get_session)
):
    db_aviso = session.get(Aviso, aviso_id)
    if not db_aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")
    
    # Deletar imagem antiga se existir
    if db_aviso.archive_url:
        try:
            delete_image_from_r2(db_aviso.archive_url)
        except Exception as e:
            print(f"Erro ao deletar imagem antiga: {e}")
    
    # Fazer upload da nova imagem
    try:
        new_archive_url = upload_image_to_r2(imagem, "avisos")
        db_aviso.archive_url = new_archive_url
        
        session.add(db_aviso)
        session.commit()
        session.refresh(db_aviso)
        
        return {"message": "Imagem atualizada com sucesso", "archive_url": new_archive_url}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Erro ao fazer upload da nova imagem: {str(e)}")

@router.delete("/avisos/{aviso_id}", 
    summary="🗑️ Deletar Aviso", 
    description="Remove um aviso do sistema",
    response_description="Aviso deletado com sucesso"
)
def delete_aviso(aviso_id: int, session: Session = Depends(get_session)):
    """
    Deleta um aviso do sistema e remove sua imagem do armazenamento.
    """
    
    db_aviso = session.get(Aviso, aviso_id)
    if not db_aviso:
        raise HTTPException(status_code=404, detail="Aviso não encontrado")
    
    # Deletar imagem do R2 se existir
    if db_aviso.archive_url:
        try:
            delete_image_from_r2(db_aviso.archive_url)
        except Exception as e:
            print(f"Erro ao deletar imagem do R2: {e}")
    
    # Deletar aviso do banco de dados
    session.delete(db_aviso)
    session.commit()
    
    return {"message": "Aviso deletado com sucesso", "id": aviso_id}

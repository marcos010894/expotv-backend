from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlmodel import Session, select
from app.db import engine
from app.models import Anuncio
from app.schemas import AnuncioCreate
from app.storage import upload_image_to_r2, delete_image_from_r2
from typing import Optional
from datetime import datetime

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/anuncios", 
    summary="📋 Listar Anúncios", 
    description="Lista todos os anúncios cadastrados no sistema",
    response_description="Lista de anúncios"
)
def get_all_anuncios(session: Session = Depends(get_session)):
    anuncios = session.exec(select(Anuncio)).all()
    return anuncios

@router.get("/anuncios/{anuncio_id}", 
    summary="🔍 Buscar Anúncio", 
    description="Busca um anúncio específico pelo seu ID",
    response_description="Dados do anúncio"
)
def get_anuncio(anuncio_id: int, session: Session = Depends(get_session)):
    anuncio = session.get(Anuncio, anuncio_id)
    if not anuncio:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")
    return anuncio

@router.post("/anuncios", 
    summary="📢 Criar Anúncio", 
    description="Cria um novo anúncio/alerta para exibição nas TVs dos condomínios. Você pode incluir uma imagem ou vídeo.",
    response_description="Anúncio criado com sucesso"
)
async def create_anuncio(
    nome: str = Form(..., description="Nome/título do anúncio", example="Promoção Especial"),
    condominios_ids: str = Form(..., description="IDs dos condomínios (separados por vírgula)", example="1,2,3"),
    numero_anunciante: Optional[str] = Form(None, description="Número de telefone do anunciante", example="11999887766"),
    nome_anunciante: Optional[str] = Form(None, description="Nome completo do anunciante", example="João Silva"),
    status: str = Form(..., description="Status do anúncio", example="Ativo"),
    data_expiracao: Optional[datetime] = Form(None, description="Data de expiração do anúncio (formato ISO)", example="2025-12-31T23:59:59"),
    tempo_exibicao: int = Form(10, description="Tempo de exibição em segundos (padrão: 10s)", example=10, ge=1, le=300),
    image: Optional[UploadFile] = File(
        None, 
        description="🖼️ Imagem/Vídeo do anúncio (PNG, JPG, JPEG, WebP, MP4, MOV, AVI, WebM) - Opcional",
        openapi_extra={
            "example": "anuncio.png"
        }
    ),
    session: Session = Depends(get_session)
):
    archive_url = ""
    
    # Se tem imagem/vídeo, fazer upload
    if image and image.filename:
        # Validar tipo de arquivo (imagem ou vídeo)
        allowed_types = [
            'image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif',
            'video/mp4', 
            'video/quicktime', 
            'video/x-msvideo',  # AVI padrão
            'video/msvideo',     # AVI alternativo
            'video/avi',         # AVI alternativo 2
            'application/x-troff-msvideo',  # AVI antigo
            'video/webm', 
            'video/mpeg',
            'video/x-matroska'   # MKV (bonus)
        ]
        
        if image.content_type not in allowed_types:
            raise HTTPException(
                status_code=400, 
                detail=f"Tipo de arquivo não suportado. Envie PNG, JPG, WebP, GIF, MP4, MOV, AVI ou WebM"
            )
        
        try:
            # Upload para R2 (usa a função original que já funciona)
            image_content = await image.read()
            archive_url = upload_image_to_r2(image_content, image.filename, image.content_type)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")
            print(f"❌ Erro no upload: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")
    
    # Criar anúncio
    anuncio = Anuncio(
        nome=nome,
        condominios_ids=condominios_ids,
        numero_anunciante=numero_anunciante,
        nome_anunciante=nome_anunciante,
        status=status,
        data_expiracao=data_expiracao,
        archive_url=archive_url,
        tempo_exibicao=tempo_exibicao
    )
    
    session.add(anuncio)
    session.commit()
    session.refresh(anuncio)
    
    return anuncio

@router.put("/anuncios/{anuncio_id}", 
    summary="✏️ Atualizar Anúncio", 
    description="Atualiza os dados de um anúncio existente (exceto a imagem)",
    response_description="Anúncio atualizado"
)
def update_anuncio(anuncio_id: int, anuncio_data: AnuncioCreate, session: Session = Depends(get_session)):
    db_anuncio = session.get(Anuncio, anuncio_id)
    if not db_anuncio:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")
    
    db_anuncio.nome = anuncio_data.nome
    db_anuncio.condominios_ids = anuncio_data.condominios_ids
    db_anuncio.numero_anunciante = anuncio_data.numero_anunciante
    db_anuncio.nome_anunciante = anuncio_data.nome_anunciante
    db_anuncio.status = anuncio_data.status
    db_anuncio.data_expiracao = anuncio_data.data_expiracao
    db_anuncio.tempo_exibicao = anuncio_data.tempo_exibicao
    # archive_url mantém o valor existente (para não perder a imagem)
    
    session.add(db_anuncio)
    session.commit()
    session.refresh(db_anuncio)
    return db_anuncio

@router.put("/anuncios/{anuncio_id}/image", 
    summary="🖼️ Atualizar Imagem", 
    description="Substitui a imagem de um anúncio existente",
    response_description="Imagem atualizada com sucesso"
)
async def update_anuncio_image(
    anuncio_id: int,
    image: UploadFile = File(
        ..., 
        description="🖼️ Nova imagem do anúncio (PNG, JPG, JPEG)",
        openapi_extra={
            "example": "nova_imagem.png"
        }
    ),
    session: Session = Depends(get_session)
):
    db_anuncio = session.get(Anuncio, anuncio_id)
    if not db_anuncio:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")
    
    # Validar tipo de arquivo
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
    if image.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de arquivo não suportado. Tipos aceitos: PNG, JPG, JPEG, WebP"
        )
    
    # Validar tamanho do arquivo (máximo 5MB)
    if hasattr(image, 'size') and image.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
    
    try:
        # Deletar imagem antiga se existir
        if db_anuncio.archive_url:
            delete_image_from_r2(db_anuncio.archive_url)
        
        # Upload nova imagem
        image_content = await image.read()
        new_image_url = upload_image_to_r2(image_content, image.filename, image.content_type)
        
        # Atualizar URL
        db_anuncio.archive_url = new_image_url
        session.add(db_anuncio)
        session.commit()
        session.refresh(db_anuncio)
        
        return db_anuncio
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload: {str(e)}")

@router.delete("/anuncios/{anuncio_id}", 
    summary="🗑️ Deletar Anúncio", 
    description="Remove um anúncio do sistema e sua imagem associada",
    response_description="Confirmação da exclusão"
)
def delete_anuncio(anuncio_id: int, session: Session = Depends(get_session)):
    db_anuncio = session.get(Anuncio, anuncio_id)
    if not db_anuncio:
        raise HTTPException(status_code=404, detail="Anúncio não encontrado")
    
    # Deletar imagem do R2 se existir
    if db_anuncio.archive_url:
        delete_image_from_r2(db_anuncio.archive_url)
    
    session.delete(db_anuncio)
    session.commit()
    return {"ok": True}

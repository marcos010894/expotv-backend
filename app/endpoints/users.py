from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlmodel import Session, select
from app.db import engine
from app.models import User
from app.schemas import UserCreate, UserUpdate, PasswordChange
from app.storage import upload_image_to_r2, delete_image_from_r2
from app.auth import get_password_hash, verify_password
from datetime import datetime

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

@router.get("/users", summary="Listar usuários", description="Lista todos os usuários do sistema")
def get_all_users(session: Session = Depends(get_session)):
    users = session.exec(select(User)).all()
    return users

@router.get("/users/{user_id}", summary="Buscar usuário", description="Busca um usuário específico por ID")
def get_user(user_id: int, session: Session = Depends(get_session)):
    user = session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return user

@router.post("/users", summary="Criar usuário", description="Cria um novo usuário no sistema")
def create_user(user_data: UserCreate, session: Session = Depends(get_session)):
    # Hash da senha antes de salvar
    hashed_password = get_password_hash(user_data.senha)
    
    user = User(
        tipo=user_data.tipo,
        nome=user_data.nome,
        email=user_data.email,
        senha=hashed_password,  # Usar senha hasheada
        telefone=user_data.telefone,
        limite_avisos=user_data.limite_avisos,  # Adicionar limite de avisos
        data_criacao=datetime.utcnow()
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return user

@router.put("/users/{user_id}", summary="Atualizar usuário", description="Atualiza dados de um usuário existente")
def update_user(user_id: int, user_data: UserUpdate, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar apenas os campos fornecidos
    if user_data.tipo is not None:
        db_user.tipo = user_data.tipo
    if user_data.nome is not None:
        db_user.nome = user_data.nome
    if user_data.email is not None:
        db_user.email = user_data.email
    if user_data.telefone is not None:
        db_user.telefone = user_data.telefone
    if user_data.limite_avisos is not None:
        db_user.limite_avisos = user_data.limite_avisos
    
    db_user.data_update = datetime.utcnow()
    
    # Hash da senha apenas se foi fornecida uma nova senha
    if user_data.senha:
        db_user.senha = get_password_hash(user_data.senha)
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

@router.delete("/users/{user_id}", summary="Deletar usuário", description="Remove um usuário do sistema")
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Deletar foto do R2 se existir
    if db_user.foto_url:
        delete_image_from_r2(db_user.foto_url)
    
    session.delete(db_user)
    session.commit()
    return {"ok": True}

@router.put("/users/{user_id}/foto", 
    summary="📸 Atualizar Foto do Usuário", 
    description="Atualiza a foto de perfil de um usuário",
    response_description="Usuário com foto atualizada"
)
async def update_user_photo(
    user_id: int,
    foto: UploadFile = File(
        ..., 
        description="📸 Foto de perfil do usuário (PNG, JPG, JPEG, WebP)",
        openapi_extra={
            "example": "perfil.jpg"
        }
    ),
    session: Session = Depends(get_session)
):
    """
    Atualiza a foto de perfil de um usuário
    
    - **user_id**: ID do usuário
    - **foto**: Arquivo de imagem (PNG, JPG, JPEG, WebP)
    - **Tamanho máximo**: 5MB
    
    Retorna o usuário com a nova URL da foto
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Validar tipo de arquivo
    allowed_types = ['image/png', 'image/jpeg', 'image/jpg', 'image/webp']
    if foto.content_type not in allowed_types:
        raise HTTPException(
            status_code=400, 
            detail=f"Tipo de arquivo não suportado. Tipos aceitos: PNG, JPG, JPEG, WebP"
        )
    
    # Validar tamanho do arquivo (máximo 5MB)
    if hasattr(foto, 'size') and foto.size > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Arquivo muito grande. Máximo: 5MB")
    
    try:
        # Deletar foto antiga se existir
        if db_user.foto_url:
            delete_image_from_r2(db_user.foto_url)
        
        # Upload nova foto
        foto_content = await foto.read()
        nova_foto_url = upload_image_to_r2(foto_content, f"user_{user_id}_{foto.filename}", foto.content_type)
        
        # Atualizar URL da foto
        db_user.foto_url = nova_foto_url
        db_user.data_update = datetime.utcnow()
        session.add(db_user)
        session.commit()
        session.refresh(db_user)
        
        return db_user
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro no upload da foto: {str(e)}")

@router.delete("/users/{user_id}/foto",
    summary="🗑️ Remover Foto do Usuário",
    description="Remove a foto de perfil de um usuário",
    response_description="Confirmação da remoção"
)
def delete_user_photo(user_id: int, session: Session = Depends(get_session)):
    """
    Remove a foto de perfil de um usuário
    
    - **user_id**: ID do usuário
    
    Remove a foto do storage e limpa a URL no banco
    """
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    if not db_user.foto_url:
        raise HTTPException(status_code=404, detail="Usuário não possui foto")
    
    try:
        # Deletar foto do R2
        delete_image_from_r2(db_user.foto_url)
        
        # Limpar URL no banco
        db_user.foto_url = None
        db_user.data_update = datetime.utcnow()
        session.add(db_user)
        session.commit()
        
        return {"message": "Foto removida com sucesso"}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao remover foto: {str(e)}")

@router.put("/users/{user_id}/limite-avisos", 
    summary="📊 Atualizar Limite de Avisos", 
    description="Atualiza a quantidade de avisos permitidos para um síndico",
    response_description="Limite atualizado com sucesso"
)
def update_limite_avisos(
    user_id: int,
    limite_avisos: int,
    session: Session = Depends(get_session)
):
    """
    Atualiza o limite de avisos permitidos para um síndico
    
    - **user_id**: ID do usuário/síndico
    - **limite_avisos**: Novo limite de avisos (deve ser >= 0)
    """
    
    if limite_avisos < 0:
        raise HTTPException(
            status_code=400, 
            detail="O limite de avisos deve ser maior ou igual a 0"
        )
    
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Atualizar limite
    db_user.limite_avisos = limite_avisos
    db_user.data_update = datetime.utcnow()
    
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {
        "message": "Limite de avisos atualizado com sucesso",
        "user_id": user_id,
        "limite_avisos": limite_avisos
    }

@router.put("/users/{user_id}/senha", 
    summary="🔐 Alterar Senha", 
    description="Permite que o usuário altere sua própria senha",
    response_description="Senha alterada com sucesso"
)
def change_password(
    user_id: int,
    password_data: PasswordChange,
    session: Session = Depends(get_session)
):
    """
    Altera a senha do usuário.
    
    Requer:
    - **senha_atual**: A senha atual do usuário para validação
    - **senha_nova**: A nova senha desejada
    
    ⚠️ A senha atual será validada antes de permitir a alteração
    """
    
    # Buscar usuário
    db_user = session.get(User, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    
    # Verificar se a senha atual está correta
    if not verify_password(password_data.senha_atual, db_user.senha):
        raise HTTPException(
            status_code=401, 
            detail="Senha atual incorreta"
        )
    
    # Validar nova senha (mínimo 6 caracteres)
    if len(password_data.senha_nova) < 6:
        raise HTTPException(
            status_code=400, 
            detail="A nova senha deve ter no mínimo 6 caracteres"
        )
    
    # Atualizar senha
    db_user.senha = get_password_hash(password_data.senha_nova)
    db_user.data_update = datetime.utcnow()
    
    session.add(db_user)
    session.commit()
    
    return {
        "message": "Senha alterada com sucesso",
        "user_id": user_id
    }

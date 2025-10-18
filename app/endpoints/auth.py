from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional, List, Dict, Any
from app.db import engine
from app.models import User, Condominio
from app.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from pydantic import BaseModel
from app.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class LoginRequest(BaseModel):
    email: str
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str
    user_type: str
    url_photo: Optional[str] = None
    condominios_ids: List[int] = []  # IDs dos condomínios do síndico
    condominios: List[dict] = []  # Dados completos dos condomínios

def get_session():
    with Session(engine) as session:
        yield session

def authenticate_user(session: Session, email: str, password: str):
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return False
    if not verify_password(password, user.senha):
        return False
    return user

def get_current_user(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    return user

@router.post("/token", summary="Login do usuário", description="Efetua login e retorna token JWT")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = authenticate_user(session, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    # Atualizar token no banco
    user.token = access_token
    session.add(user)
    session.commit()
    return {"access_token": access_token, "token_type": "bearer", "user": user}

@router.post("/login", summary="🔐 Login Simples", description="Login com email e senha - retorna token JWT", response_model=LoginResponse)
async def login(login_data: LoginRequest, session: Session = Depends(get_session)):
    """
    Faz login com email e senha
    
    - **email**: Email do usuário
    - **senha**: Senha do usuário
    
    Retorna token JWT para autenticação nas outras rotas
    """
    user = authenticate_user(session, login_data.email, login_data.senha)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    # Atualizar token no banco
    user.token = access_token
    session.add(user)
    session.commit()
    
    # Buscar condomínios ligados ao usuário
    condominios_ids = []
    condominios_data = []
    
    # Fazer consulta explícita para buscar condomínios do usuário
    condominios = session.exec(
        select(Condominio).where(Condominio.sindico_id == user.id)
    ).all()
    
    if condominios:
        condominios_ids = [condominio.id for condominio in condominios]
        condominios_data = [
            {
                "id": condominio.id,
                "nome": condominio.nome,
                "localizacao": condominio.localizacao,
                "cep": condominio.cep
            }
            for condominio in condominios
        ]
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        user_id=user.id,
        user_name=user.nome,
        user_type=user.tipo,
        url_photo=user.foto_url,
        condominios_ids=condominios_ids,
        condominios=condominios_data
    )

@router.post("/register", summary="Registrar novo usuário", description="Cria um novo usuário no sistema")
def register_user(nome: str, email: str, senha: str, tipo: str = "SINDICO", session: Session = Depends(get_session)):
    # Verificar se email já existe
    existing_user = session.exec(select(User).where(User.email == email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email já cadastrado")
    
    # Criar novo usuário
    hashed_password = get_password_hash(senha)
    user = User(
        nome=nome,
        email=email,
        senha=hashed_password,
        tipo=tipo
    )
    session.add(user)
    session.commit()
    session.refresh(user)
    return {"message": "Usuário criado com sucesso", "user": user}

@router.get("/me", summary="Dados do usuário logado", description="Retorna informações do usuário autenticado")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user

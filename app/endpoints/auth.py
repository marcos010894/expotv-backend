from fastapi import APIRouter, Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer, HTTPAuthorizationCredentials
from sqlmodel import Session, select
from datetime import timedelta
from typing import Optional, List
from app.db import engine
from app.models import User, Condominio
from app.auth import verify_password, get_password_hash, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES, verify_token
from pydantic import BaseModel, EmailStr

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
security = HTTPBearer()

class LoginRequest(BaseModel):
    email: EmailStr
    senha: str

class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    user_name: str
    user_type: str
    url_photo: Optional[str] = None
    condominios_ids: List[int] = []
    condominios: List[dict] = []
    expires_in: int  # Tempo de expiração em minutos

def get_session():
    with Session(engine) as session:
        yield session

def authenticate_user(session: Session, email: str, password: str) -> Optional[User]:
    """
    Autentica um usuário verificando email e senha
    
    Args:
        session: Sessão do banco de dados
        email: Email do usuário
        password: Senha fornecida
    
    Returns:
        Objeto User se autenticação bem-sucedida, None caso contrário
    """
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        return None
    if not verify_password(password, user.senha):
        return None
    return user

def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
) -> User:
    """
    Obtém o usuário atual a partir do token JWT
    
    Raises:
        HTTPException: Se o token for inválido ou o usuário não for encontrado
    
    Returns:
        Objeto User do usuário autenticado
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciais inválidas ou token expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    token = credentials.credentials
    email = verify_token(token)
    
    if email is None:
        raise credentials_exception
    
    user = session.exec(select(User).where(User.email == email)).first()
    if user is None:
        raise credentials_exception
    
    return user

def get_current_user_optional(
    authorization: Optional[str] = Header(None),
    session: Session = Depends(get_session)
) -> Optional[User]:
    """
    Obtém o usuário atual se um token válido for fornecido (autenticação opcional)
    
    Returns:
        Objeto User se token válido, None caso contrário
    """
    if not authorization:
        return None
    
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
            
        email = verify_token(token)
        if email is None:
            return None
        
        user = session.exec(select(User).where(User.email == email)).first()
        return user
    except:
        return None

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

@router.post("/login", 
    summary="🔐 Login", 
    description="Login com email e senha - retorna token JWT válido por 30 dias", 
    response_model=LoginResponse
)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    """
    Faz login com email e senha
    
    - **username**: Email do usuário (usar 'username' para OAuth2)
    - **password**: Senha do usuário
    
    Retorna:
    - **access_token**: Token JWT para autenticação (válido por 30 dias)
    - **user_id**: ID do usuário
    - **user_name**: Nome completo do usuário
    - **user_type**: Tipo de usuário (ADMIN, SINDICO, etc)
    - **condominios**: Lista de condomínios vinculados ao usuário
    
    ⚠️ Importante: 
    - Guarde o token em localStorage ou cookies seguros
    - Envie o token no header: `Authorization: Bearer {token}`
    - Token expira em 30 dias
    - Use formato: application/x-www-form-urlencoded
    - Campo 'username' deve conter o email
    """
    user = authenticate_user(session, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Criar token com expiração de 30 dias
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "sub": user.email,
            "user_id": user.id,
            "user_type": user.tipo
        },
        expires_delta=access_token_expires
    )
    
    # Atualizar token no banco
    user.token = access_token
    session.add(user)
    session.commit()
    
    # Buscar condomínios ligados ao usuário
    condominios_ids = []
    condominios_data = []
    
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
        condominios=condominios_data,
        expires_in=ACCESS_TOKEN_EXPIRE_MINUTES
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

@router.get("/me", 
    summary="👤 Dados do Usuário Logado", 
    description="Retorna informações do usuário autenticado pelo token"
)
async def read_users_me(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Retorna os dados do usuário autenticado
    
    Requer token JWT válido no header:
    `Authorization: Bearer {token}`
    """
    # Buscar condomínios do usuário
    condominios = session.exec(
        select(Condominio).where(Condominio.sindico_id == current_user.id)
    ).all()
    
    condominios_data = [
        {
            "id": cond.id,
            "nome": cond.nome,
            "localizacao": cond.localizacao,
            "cep": cond.cep
        }
        for cond in condominios
    ]
    
    return {
        "id": current_user.id,
        "nome": current_user.nome,
        "email": current_user.email,
        "tipo": current_user.tipo,
        "telefone": current_user.telefone,
        "foto_url": current_user.foto_url,
        "limite_avisos": current_user.limite_avisos,
        "condominios": condominios_data
    }

@router.post("/verify-token", 
    summary="✅ Verificar Token", 
    description="Verifica se um token JWT é válido"
)
async def verify_token_endpoint(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    session: Session = Depends(get_session)
):
    """
    Verifica se um token é válido e retorna informações básicas do usuário
    
    Retorna 200 se válido, 401 se inválido/expirado
    """
    token = credentials.credentials
    email = verify_token(token)
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado"
        )
    
    user = session.exec(select(User).where(User.email == email)).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado"
        )
    
    return {
        "valid": True,
        "user_id": user.id,
        "email": user.email,
        "name": user.nome,
        "type": user.tipo
    }
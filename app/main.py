from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.endpoints.users import router as users_router
from app.endpoints.condominios import router as condominios_router
from app.endpoints.tvs import router as tvs_router
from app.endpoints.anuncios import router as anuncios_router
from app.endpoints.avisos import router as avisos_router
from app.endpoints.auth import router as auth_router
from app.endpoints.app import router as app_router
from app.endpoints.monitor import router as monitor_router

app = FastAPI(
    title="EXPO-TV API",
    description="Sistema de gerenciamento para TVs em condomínios",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para aceitar requisições de qualquer lugar
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permite todas as origens
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos os métodos (GET, POST, PUT, DELETE, etc.)
    allow_headers=["*"],  # Permite todos os headers
)

app.include_router(auth_router, tags=["Autenticação"])
app.include_router(users_router, tags=["Usuários"])
app.include_router(condominios_router, tags=["Condomínios"])
app.include_router(tvs_router, tags=["TVs"])
app.include_router(anuncios_router, tags=["Anúncios"])
app.include_router(avisos_router, tags=["Avisos"])
app.include_router(app_router, tags=["📱 App Mobile/TV"])
app.include_router(monitor_router, tags=["🔧 Monitores"])

# Iniciar monitores em background
@app.on_event("startup")
async def startup_event():
    """
    Evento executado quando a aplicação inicia
    Inicia os serviços de monitoramento em background
    """
    from app.services.tv_monitor import start_tv_monitor
    from app.services.expiration_monitor import start_expiration_monitor
    
    # Iniciar monitor de TVs (verifica a cada 1 minuto)
    start_tv_monitor()
    
    # Iniciar monitor de expiração (verifica a cada 1 hora)
    start_expiration_monitor()
    
    print("🚀 Monitores em background iniciados com sucesso!")

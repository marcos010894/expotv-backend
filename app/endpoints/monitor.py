from fastapi import APIRouter
from app.services.expiration_monitor import check_expired_content
from app.services.tv_monitor import check_offline_tvs

router = APIRouter()

@router.post("/monitor/check-expiration", 
    summary="🕐 Verificar Expiração", 
    description="Força verificação manual de avisos/anúncios expirados",
    response_description="Resultado da verificação"
)
def force_check_expiration():
    """
    Executa manualmente a verificação de conteúdo expirado
    """
    check_expired_content()
    return {"message": "Verificação de expiração executada com sucesso"}

@router.post("/monitor/check-tvs", 
    summary="📺 Verificar TVs Offline", 
    description="Força verificação manual do status das TVs",
    response_description="Resultado da verificação"
)
def force_check_tvs():
    """
    Executa manualmente a verificação de TVs offline
    """
    check_offline_tvs()
    return {"message": "Verificação de TVs executada com sucesso"}

@router.get("/monitor/status", 
    summary="📊 Status dos Monitores", 
    description="Retorna informações sobre os monitores em execução",
    response_description="Status dos monitores"
)
def get_monitor_status():
    """
    Retorna status dos monitores em background
    """
    return {
        "tv_monitor": {
            "active": True,
            "interval": "1 minuto",
            "description": "Verifica TVs offline (sem ping por 5+ minutos)"
        },
        "expiration_monitor": {
            "active": True,
            "interval": "1 hora",
            "description": "Verifica e inativa avisos/anúncios expirados"
        }
    }

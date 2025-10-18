"""
Serviço de monitoramento de expiração de Avisos e Anúncios
Verifica automaticamente se avisos/anúncios expiraram e os inativa
"""

from datetime import datetime
from sqlmodel import Session, select
from app.db import engine
from app.models import Aviso, Anuncio
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_expired_content():
    """
    Verifica avisos e anúncios expirados e os inativa automaticamente
    """
    with Session(engine) as session:
        try:
            current_time = datetime.now()
            avisos_inativados = 0
            anuncios_inativados = 0
            
            # 1. Verificar Avisos Expirados
            avisos_ativos = session.exec(
                select(Aviso).where(Aviso.status == "Ativo")
            ).all()
            
            for aviso in avisos_ativos:
                if aviso.data_expiracao and aviso.data_expiracao <= current_time:
                    aviso.status = "Inativo"
                    session.add(aviso)
                    avisos_inativados += 1
                    logger.info(f"📋 Aviso ID {aviso.id} ('{aviso.nome}') expirado e inativado")
            
            # 2. Verificar Anúncios Expirados
            anuncios_ativos = session.exec(
                select(Anuncio).where(Anuncio.status == "Ativo")
            ).all()
            
            for anuncio in anuncios_ativos:
                if anuncio.data_expiracao and anuncio.data_expiracao <= current_time:
                    anuncio.status = "Inativo"
                    session.add(anuncio)
                    anuncios_inativados += 1
                    logger.info(f"📢 Anúncio ID {anuncio.id} ('{anuncio.nome}') expirado e inativado")
            
            # 3. Commit das mudanças
            if avisos_inativados > 0 or anuncios_inativados > 0:
                session.commit()
                logger.info(f"✅ Verificação completa: {avisos_inativados} avisos e {anuncios_inativados} anúncios inativados")
            else:
                logger.info("✅ Verificação completa: Nenhum conteúdo expirado encontrado")
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar conteúdo expirado: {e}")
            session.rollback()

def start_expiration_monitor():
    """
    Inicia o monitoramento de expiração em background
    Verifica a cada 1 hora
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Executar a cada 1 hora
    scheduler.add_job(
        check_expired_content,
        'interval',
        hours=1,
        id='expiration_monitor',
        name='Monitor de Expiração de Avisos/Anúncios',
        replace_existing=True
    )
    
    # Executar imediatamente ao iniciar
    check_expired_content()
    
    scheduler.start()
    logger.info("🕐 Monitor de expiração iniciado - Verificando a cada 1 hora")
    
    return scheduler

"""
Serviço de monitoramento de status de TVs
Verifica automaticamente se TVs estão offline (sem heartbeat por 5+ minutos)
"""

from datetime import datetime, timedelta
from sqlmodel import Session, select
from app.db import engine
from app.models import TV
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def check_offline_tvs():
    """
    Verifica TVs que não enviaram heartbeat nos últimos 5 minutos
    e marca como offline
    """
    with Session(engine) as session:
        try:
            # Buscar todas as TVs online
            tvs_online = session.exec(
                select(TV).where(TV.status == "online")
            ).all()
            
            tvs_offline_count = 0
            current_time = datetime.now()
            timeout_threshold = current_time - timedelta(minutes=5)
            
            for tv in tvs_online:
                # Verificar se o último ping foi há mais de 5 minutos
                if tv.last_ping and tv.last_ping < timeout_threshold:
                    tv.status = "offline"
                    session.add(tv)
                    tvs_offline_count += 1
                    
                    tempo_sem_ping = (current_time - tv.last_ping).total_seconds() / 60
                    logger.warning(
                        f"📺 TV '{tv.nome}' (código: {tv.codigo_conexao}) "
                        f"marcada como offline - Sem ping há {tempo_sem_ping:.1f} minutos"
                    )
            
            # Commit das mudanças
            if tvs_offline_count > 0:
                session.commit()
                logger.info(f"✅ {tvs_offline_count} TV(s) marcada(s) como offline")
            else:
                logger.info("✅ Todas as TVs online estão respondendo")
                
        except Exception as e:
            logger.error(f"❌ Erro ao verificar status das TVs: {e}")
            session.rollback()

def start_tv_monitor():
    """
    Inicia o monitoramento de TVs em background
    Verifica a cada 10 minutos
    """
    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Executar a cada 10 minutos
    scheduler.add_job(
        check_offline_tvs,
        'interval',
        minutes=10,
        id='tv_monitor',
        name='Monitor de Status de TVs',
        replace_existing=True
    )
    
    # Executar imediatamente ao iniciar
    check_offline_tvs()
    
    scheduler.start()
    logger.info("📺 Monitor de TVs iniciado - Verificando a cada 10 minutos")
    
    return scheduler

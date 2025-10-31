from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from typing import List, Optional, Union
from app.db import engine
from app.models import Anuncio, Aviso, TV
from pydantic import BaseModel
import requests
import logging

router = APIRouter()

def get_session():
    with Session(engine) as session:
        yield session

class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: str
    source: str

def get_jovempan_news(limit: int = 15) -> List[NewsItem]:
    """
    Busca notícias APENAS da Jovem Pan
    Retorna até 15 notícias por padrão
    """
    try:
        from datetime import datetime
        import re
        
        news_items = []
        
        # Buscar RSS da Jovem Pan
        response = requests.get(
            'https://api.rss2json.com/v1/api.json',
            params={'rss_url': 'https://jovempan.com.br/feed/'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            # A API retorna 10 por padrão, mas vamos pegar quantos vier
            for item in items[:limit]:
                # Limpar HTML da descrição
                description = item.get('description', '')
                description = re.sub('<[^<]+?>', '', description).strip()
                
                if len(description) > 200:
                    description = description[:200] + "..."
                
                # Extrair imagem
                thumbnail = item.get('thumbnail', '')
                if not thumbnail and 'enclosure' in item:
                    thumbnail = item.get('enclosure', {}).get('link', '')
                
                news_item = NewsItem(
                    title=item.get('title', '').strip(),
                    description=description,
                    url=item.get('link', ''),
                    urlToImage=thumbnail,
                    publishedAt=item.get('pubDate', datetime.now().isoformat() + "Z"),
                    source='🎙️ Jovem Pan'
                )
                
                if news_item.title:
                    news_items.append(news_item)
        
        return news_items
        
    except Exception as e:
        logging.error(f"Erro ao buscar notícias da Jovem Pan: {e}")
        return []

class AppContent(BaseModel):
    anuncios: List[Anuncio] = []
    avisos: List[Aviso] = []
    news: List[NewsItem] = []
    total_anuncios: int = 0
    total_avisos: int = 0
    total_news: int = 0

@router.get("/app/content/{condominio_id}", 
    summary="📱 Conteúdo do App", 
    description="Retorna todos os anúncios, avisos e notícias para um condomínio específico",
    response_description="Anúncios, avisos e notícias do condomínio",
    response_model=AppContent
)
def get_app_content(
    condominio_id: int,
    status: Optional[str] = Query("Ativo", description="Status dos conteúdos (padrão: Ativo)"),
    include_news: bool = Query(True, description="Incluir notícias da Jovem Pan"),
    news_limit: int = Query(15, description="Número máximo de notícias (padrão: 15)"),
    session: Session = Depends(get_session)
):
    """
    Retorna conteúdo para o app mobile/TV
    
    - **condominio_id**: ID do condomínio
    - **status**: Status dos conteúdos (padrão: Ativo)
    - **include_news**: Se deve incluir notícias da Jovem Pan 🎙️
    - **news_limit**: Número máximo de notícias (padrão: 15)
    
    Busca anúncios e avisos onde o condomínio está na lista de condomínios_ids
    Também busca notícias da Jovem Pan
    
    ⏱️ Cada anúncio retorna o campo `tempo_exibicao` em segundos para controle de rotação na TV
    """
    
    # Buscar anúncios que incluem este condomínio
    anuncios = session.exec(
        select(Anuncio).where(
            Anuncio.status == status,
            Anuncio.condominios_ids.like(f"%{condominio_id}%")
        )
    ).all()
    
    # Filtrar anúncios que realmente contêm o condomínio (verificação mais precisa)
    anuncios_filtrados = []
    for anuncio in anuncios:
        condominios_list = [int(id.strip()) for id in anuncio.condominios_ids.split(',') if id.strip().isdigit()]
        if condominio_id in condominios_list:
            anuncios_filtrados.append(anuncio)
    
    # Buscar avisos que incluem este condomínio
    avisos = session.exec(
        select(Aviso).where(
            Aviso.status == status,
            Aviso.condominios_ids.like(f"%{condominio_id}%")
        )
    ).all()
    
    # Filtrar avisos que realmente contêm o condomínio (verificação mais precisa)
    avisos_filtrados = []
    for aviso in avisos:
        condominios_list = [int(id.strip()) for id in aviso.condominios_ids.split(',') if id.strip().isdigit()]
        if condominio_id in condominios_list:
            avisos_filtrados.append(aviso)
    
    # Buscar notícias se solicitado (sempre da Jovem Pan)
    news_items = []
    if include_news:
        news_items = get_jovempan_news(limit=news_limit)
    
    return AppContent(
        anuncios=anuncios_filtrados,
        avisos=avisos_filtrados,
        news=news_items,
        total_anuncios=len(anuncios_filtrados),
        total_avisos=len(avisos_filtrados),
        total_news=len(news_items)
    )

@router.get("/app/anuncios/{condominio_id}", 
    summary="📢 Anúncios do Condomínio", 
    description="Retorna apenas anúncios de um condomínio específico com tempo de exibição individual",
    response_description="Lista de anúncios com tempo_exibicao (em segundos)"
)
def get_anuncios_condominio(
    condominio_id: int,
    status: Optional[str] = Query("Ativo", description="Status dos anúncios"),
    session: Session = Depends(get_session)
):
    """
    Retorna anúncios específicos de um condomínio
    
    ⏱️ Cada anúncio inclui o campo `tempo_exibicao` em segundos
    """
    anuncios = session.exec(
        select(Anuncio).where(
            Anuncio.status == status,
            Anuncio.condominios_ids.like(f"%{condominio_id}%")
        )
    ).all()
    
    # Filtrar precisamente
    anuncios_filtrados = []
    for anuncio in anuncios:
        condominios_list = [int(id.strip()) for id in anuncio.condominios_ids.split(',') if id.strip().isdigit()]
        if condominio_id in condominios_list:
            anuncios_filtrados.append(anuncio)
    
    return {"anuncios": anuncios_filtrados, "total": len(anuncios_filtrados)}

@router.get("/app/avisos/{condominio_id}", 
    summary="📋 Avisos do Condomínio", 
    description="Retorna apenas avisos de um condomínio específico",
    response_description="Lista de avisos"
)
def get_avisos_condominio(
    condominio_id: int,
    status: Optional[str] = Query("Ativo", description="Status dos avisos"),
    session: Session = Depends(get_session)
):
    """
    Retorna avisos específicos de um condomínio
    """
    avisos = session.exec(
        select(Aviso).where(
            Aviso.status == status,
            Aviso.condominios_ids.like(f"%{condominio_id}%")
        )
    ).all()
    
    # Filtrar precisamente
    avisos_filtrados = []
    for aviso in avisos:
        condominios_list = [int(id.strip()) for id in aviso.condominios_ids.split(',') if id.strip().isdigit()]
        if condominio_id in condominios_list:
            avisos_filtrados.append(aviso)
    
    return {"avisos": avisos_filtrados, "total": len(avisos_filtrados)}

@router.get("/app/news", 
    summary="📰 Notícias Jovem Pan", 
    description="Retorna notícias da Jovem Pan",
    response_description="Lista de notícias da Jovem Pan"
)
def get_news_endpoint(
    limit: int = Query(10, description="Número máximo de notícias", ge=1, le=50)
):
    """
    Retorna notícias APENAS da Jovem Pan
    """
    news_items = get_jovempan_news(limit=limit)
    return {"news": news_items, "total": len(news_items), "source": "🎙️ Jovem Pan"}

@router.get("/app/status", 
    summary="📊 Status do Sistema", 
    description="Retorna estatísticas gerais do sistema",
    response_description="Estatísticas do sistema"
)
def get_app_status(session: Session = Depends(get_session)):
    """
    Retorna estatísticas do sistema incluindo disponibilidade de notícias
    """
    total_anuncios = len(session.exec(select(Anuncio)).all())
    total_avisos = len(session.exec(select(Aviso)).all())
    anuncios_ativos = len(session.exec(select(Anuncio).where(Anuncio.status == "Ativo")).all())
    avisos_ativos = len(session.exec(select(Aviso).where(Aviso.status == "Ativo")).all())
    
    # Testar disponibilidade de notícias
    news_available = True
    news_count = 0
    try:
        news_items = get_jovempan_news(limit=5)
        news_count = len(news_items)
    except Exception as e:
        news_available = False
        logging.error(f"Erro ao verificar notícias: {e}")
    
    return {
        "anuncios": {
            "total": total_anuncios,
            "ativos": anuncios_ativos,
            "inativos": total_anuncios - anuncios_ativos
        },
        "avisos": {
            "total": total_avisos,
            "ativos": avisos_ativos,
            "inativos": total_avisos - avisos_ativos
        },
        "news": {
            "available": news_available,
            "sample_count": news_count
        }
    }

@router.get("/app/jovempan", 
    summary="🎙️ Notícias Jovem Pan", 
    description="Retorna notícias exclusivas da Jovem Pan",
    response_description="Lista de notícias da Jovem Pan"
)
def get_jovempan_endpoint(
    limit: int = Query(10, description="Número máximo de notícias", ge=1, le=50)
):
    """
    Retorna notícias exclusivas do feed RSS da Jovem Pan
    
    Fonte: https://jovempan.com.br/feed/
    """
    try:
        from datetime import datetime
        import re
        
        news_items = []
        
        # Buscar RSS da Jovem Pan
        response = requests.get(
            'https://api.rss2json.com/v1/api.json',
            params={'rss_url': 'https://jovempan.com.br/feed/'},
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            items = data.get('items', [])
            
            for item in items[:limit]:
                # Limpar HTML da descrição
                description = item.get('description', '')
                description = re.sub('<[^<]+?>', '', description)
                description = description.strip()
                
                if len(description) > 200:
                    description = description[:200] + "..."
                
                # Extrair imagem
                thumbnail = item.get('thumbnail', '')
                if not thumbnail and 'enclosure' in item:
                    thumbnail = item.get('enclosure', {}).get('link', '')
                
                news_item = NewsItem(
                    title=item.get('title', '').strip(),
                    description=description,
                    url=item.get('link', ''),
                    urlToImage=thumbnail,
                    publishedAt=item.get('pubDate', datetime.now().isoformat() + "Z"),
                    source='🎙️ Jovem Pan'
                )
                
                if news_item.title:
                    news_items.append(news_item)
        
        return {
            "news": news_items,
            "total": len(news_items),
            "source": "Jovem Pan",
            "feed_url": "https://jovempan.com.br/"
        }
        
    except Exception as e:
        logging.error(f"Erro ao buscar notícias da Jovem Pan: {e}")
        return {
            "news": [],
            "total": 0,
            "source": "Jovem Pan",
            "error": str(e)
        }

@router.get("/app/tv/{codigo_conexao}/content",
    summary="📺 Conteúdo Intercalado por TV",
    description="Retorna conteúdo (avisos, anúncios, notícias) intercalado de acordo com a proporção configurada da TV"
)
def get_tv_intercalated_content(
    codigo_conexao: str,
    session: Session = Depends(get_session)
):
    """
    Retorna conteúdo intercalado baseado nas configurações da TV
    
    **Como funciona:**
    1. Busca a TV pelo código de conexão
    2. Obtém as configurações de proporção (avisos:anúncios:notícias)
    3. Busca avisos e anúncios do condomínio da TV
    4. Intercala o conteúdo na proporção configurada
    5. Adiciona notícias no final (se configurado)
    
    **Layout 1**: Notícias são exibidas em rodapé/banner
    **Layout 2**: Notícias são exibidas em tela cheia
    
    **Exemplo de proporção 1:5:3:**
    - 1 aviso
    - 5 anúncios
    - 1 aviso
    - 5 anúncios
    - ... (repete)
    - 3 notícias (no final)
    
    **Resposta:**
    ```json
    {
        "content": [...],  // Lista intercalada de avisos, anúncios e notícias
        "config": {
            "proporcao_avisos": 1,
            "proporcao_anuncios": 5,
            "proporcao_noticias": 3
        },
        "stats": {
            "total_items": 15,
            "avisos": 5,
            "anuncios": 7,
            "noticias": 3
        }
    }
    ```
    
    Cada item retornado tem:
    - **type**: "aviso", "anuncio" ou "noticia"
    - **data**: Objeto com os dados do conteúdo
    """
    
    # 1. Buscar TV
    tv = session.exec(select(TV).where(TV.codigo_conexao == codigo_conexao)).first()
    if not tv:
        raise HTTPException(status_code=404, detail="TV não encontrada com este código")
    
    # 2. Buscar avisos do condomínio
    avisos_query = session.exec(
        select(Aviso).where(
            Aviso.status.ilike("Ativo"),
            Aviso.condominios_ids.like(f"%{tv.condominio_id}%")
        )
    ).all()
    
    # Filtrar avisos que realmente contêm o condomínio
    avisos = []
    for aviso in avisos_query:
        cond_ids = [int(id.strip()) for id in aviso.condominios_ids.split(",") if id.strip()]
        if tv.condominio_id in cond_ids:
            avisos.append(aviso)
    
    # 3. Buscar anúncios do condomínio
    anuncios_query = session.exec(
        select(Anuncio).where(
            Anuncio.status == "Ativo",
            Anuncio.condominios_ids.like(f"%{tv.condominio_id}%")
        )
    ).all()
    
    # Filtrar anúncios que realmente contêm o condomínio
    anuncios = []
    for anuncio in anuncios_query:
        cond_ids = [int(id.strip()) for id in anuncio.condominios_ids.split(",") if id.strip()]
        if tv.condominio_id in cond_ids:
            anuncios.append(anuncio)
    
    # 4. Buscar notícias (se proporção configurada)
    # Layout 1: Exibe em rodapé/banner
    # Layout 2: Exibe em tela cheia
    # Usando APENAS notícias da Jovem Pan
    noticias = []
    if tv.proporcao_noticias > 0:
        logging.info(f"TV {tv.nome}: Buscando {tv.proporcao_noticias} notícias da Jovem Pan")
        noticias = get_jovempan_news(limit=tv.proporcao_noticias)
        logging.info(f"TV {tv.nome}: {len(noticias)} notícias encontradas da Jovem Pan")
    else:
        logging.info(f"TV {tv.nome}: proporcao_noticias = 0, pulando busca de notícias")
    
    # 5. Intercalar conteúdo
    content = []
    aviso_index = 0
    anuncio_index = 0
    
    # Calcular quantos ciclos precisamos
    total_cycles = max(
        (len(avisos) // tv.proporcao_avisos) if tv.proporcao_avisos > 0 else 0,
        (len(anuncios) // tv.proporcao_anuncios) if tv.proporcao_anuncios > 0 else 0,
        1  # Pelo menos 1 ciclo
    )
    
    for cycle in range(total_cycles + 1):
        # Adicionar avisos conforme proporção
        for _ in range(tv.proporcao_avisos):
            if aviso_index < len(avisos):
                content.append({
                    "type": "aviso",
                    "data": avisos[aviso_index]
                })
                aviso_index += 1
        
        # Adicionar anúncios conforme proporção
        for _ in range(tv.proporcao_anuncios):
            if anuncio_index < len(anuncios):
                content.append({
                    "type": "anuncio",
                    "data": anuncios[anuncio_index]
                })
                anuncio_index += 1
        
        # Se não tem mais conteúdo, parar
        if aviso_index >= len(avisos) and anuncio_index >= len(anuncios):
            break
    
    # Adicionar notícias no final
    # Layout 1: TV exibe em rodapé/banner
    # Layout 2: TV exibe em tela cheia
    for noticia in noticias:
        content.append({
            "type": "noticia",
            "data": noticia
        })
    
    return {
        "success": True,
        "tv": {
            "id": tv.id,
            "nome": tv.nome,
            "codigo_conexao": tv.codigo_conexao,
            "template": tv.template
        },
        "config": {
            "proporcao_avisos": tv.proporcao_avisos,
            "proporcao_anuncios": tv.proporcao_anuncios,
            "proporcao_noticias": tv.proporcao_noticias,
            "descricao": f"{tv.proporcao_avisos} aviso(s) : {tv.proporcao_anuncios} anúncio(s) : {tv.proporcao_noticias} notícia(s)"
        },
        "content": content,
        "stats": {
            "total_items": len(content),
            "avisos": sum(1 for item in content if item["type"] == "aviso"),
            "anuncios": sum(1 for item in content if item["type"] == "anuncio"),
            "noticias": sum(1 for item in content if item["type"] == "noticia")
        }
    }

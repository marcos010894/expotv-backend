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
                
                # Extrair imagem (está no content como HTML)
                thumbnail = item.get('thumbnail', '')
                
                # Se não tiver thumbnail, buscar no content
                if not thumbnail:
                    content = item.get('content', '')
                    # Buscar tag img src no HTML
                    img_match = re.search(r'<img[^>]+src="([^"]+)"', content)
                    if img_match:
                        thumbnail = img_match.group(1)
                
                # Tentar enclosure se ainda não tiver imagem
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

class ContentItem(BaseModel):
    """Item de conteúdo unificado (pode ser aviso, anúncio ou notícia)"""
    type: str  # "aviso", "anuncio", "noticia"
    data: Union[Aviso, Anuncio, NewsItem]

class AppContent(BaseModel):
    anuncios: List[Anuncio] = []
    avisos: List[Aviso] = []
    news: List[NewsItem] = []
    total_anuncios: int = 0
    total_avisos: int = 0
    total_news: int = 0

class AppContentIntercalado(BaseModel):
    """Conteúdo intercalado respeitando proporções da TV"""
    content: List[dict] = []
    total_items: int = 0
    proporcao_avisos: int = 1
    proporcao_anuncios: int = 5
    proporcao_noticias: int = 3

@router.get("/app/content/{condominio_id}", 
    summary="📱 Conteúdo do App", 
    description="Retorna todos os anúncios, avisos e notícias para um condomínio específico",
    response_description="Anúncios, avisos e notícias do condomínio"
)
def get_app_content(
    condominio_id: int,
    status: Optional[str] = Query("Ativo", description="Status dos conteúdos (padrão: Ativo)"),
    include_news: bool = Query(True, description="Incluir notícias da Jovem Pan"),
    news_limit: int = Query(15, description="Número máximo de notícias (padrão: 15)"),
    intercalado: bool = Query(False, description="Retornar conteúdo intercalado (padrão: False)"),
    proporcao_avisos: int = Query(1, description="Proporção de avisos (padrão: 1)"),
    proporcao_anuncios: int = Query(5, description="Proporção de anúncios (padrão: 5)"),
    proporcao_noticias: int = Query(3, description="Proporção de notícias (padrão: 3)"),
    session: Session = Depends(get_session)
):
    """
    Retorna conteúdo para o app mobile/TV
    
    - **condominio_id**: ID do condomínio
    - **status**: Status dos conteúdos (padrão: Ativo)
    - **include_news**: Se deve incluir notícias da Jovem Pan 🎙️
    - **news_limit**: Número máximo de notícias (padrão: 15)
    - **intercalado**: Se True, retorna conteúdo intercalado respeitando proporções (padrão: False)
    - **proporcao_avisos**: Proporção de avisos no intercalamento (padrão: 1)
    - **proporcao_anuncios**: Proporção de anúncios no intercalamento (padrão: 5)
    - **proporcao_noticias**: Proporção de notícias no intercalamento (padrão: 3)
    
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
    
    # Se intercalado=True, retornar conteúdo misturado em ROUND-ROBIN
    if intercalado:
        content_intercalado = []
        
        # Índices para controlar posição em cada lista
        idx_avisos = 0
        idx_anuncios = 0
        idx_noticias = 0
        
        # ROUND-ROBIN: Continuar enquanto houver conteúdo em qualquer lista
        while idx_avisos < len(avisos_filtrados) or idx_anuncios < len(anuncios_filtrados) or idx_noticias < len(news_items):
            # 1. Adicionar X avisos SEGUIDOS (conforme proporção)
            for _ in range(proporcao_avisos):
                if idx_avisos < len(avisos_filtrados):
                    aviso = avisos_filtrados[idx_avisos]
                    content_intercalado.append({
                        "type": "aviso",
                        "id": aviso.id,
                        "nome": aviso.nome,
                        "descricao": aviso.descricao,
                        "imagem_url": aviso.imagem_url,
                        "video_url": aviso.video_url,
                        "data_criacao": aviso.data_criacao.isoformat() if aviso.data_criacao else None,
                        "data_expiracao": aviso.data_expiracao.isoformat() if aviso.data_expiracao else None,
                        "status": aviso.status
                    })
                    idx_avisos += 1
                else:
                    break  # Para de tentar adicionar avisos se acabaram
            
            # 2. Adicionar X anúncios SEGUIDOS (conforme proporção)
            for _ in range(proporcao_anuncios):
                if idx_anuncios < len(anuncios_filtrados):
                    anuncio = anuncios_filtrados[idx_anuncios]
                    content_intercalado.append({
                        "type": "anuncio",
                        "id": anuncio.id,
                        "nome": anuncio.nome,
                        "descricao": anuncio.descricao,
                        "imagem_url": anuncio.imagem_url,
                        "video_url": anuncio.video_url,
                        "tempo_exibicao": anuncio.tempo_exibicao,
                        "data_criacao": anuncio.data_criacao.isoformat() if anuncio.data_criacao else None,
                        "data_expiracao": anuncio.data_expiracao.isoformat() if anuncio.data_expiracao else None,
                        "status": anuncio.status
                    })
                    idx_anuncios += 1
                else:
                    break  # Para de tentar adicionar anúncios se acabaram
            
            # 3. Adicionar X notícias SEGUIDAS (conforme proporção)
            for _ in range(proporcao_noticias):
                if idx_noticias < len(news_items):
                    noticia = news_items[idx_noticias]
                    content_intercalado.append({
                        "type": "noticia",
                        "title": noticia.title,
                        "description": noticia.description,
                        "url": noticia.url,
                        "urlToImage": noticia.urlToImage,
                        "publishedAt": noticia.publishedAt,
                        "source": noticia.source
                    })
                    idx_noticias += 1
                else:
                    break  # Para de tentar adicionar notícias se acabaram
            
            # Volta pro início do ciclo (próxima rodada)
        
        return {
            "content": content_intercalado,
            "total_items": len(content_intercalado),
            "proporcao_avisos": proporcao_avisos,
            "proporcao_anuncios": proporcao_anuncios,
            "proporcao_noticias": proporcao_noticias,
            "total_avisos": len(avisos_filtrados),
            "total_anuncios": len(anuncios_filtrados),
            "total_news": len(news_items)
        }
    
    # Retorno padrão (separado por tipo)
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

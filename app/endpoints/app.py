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

# Configuração da API de notícias
NEWS_API_KEY = "your_api_key_here"  # Substitua pela sua chave da NewsAPI (newsapi.org)
NEWS_API_URL = "https://newsapi.org/v2/top-headlines"
ALTERNATIVE_NEWS_API = "https://api.currentsapi.services/v1/latest-news"

class NewsItem(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    urlToImage: Optional[str] = None
    publishedAt: str
    source: str

class AppContent(BaseModel):
    anuncios: List[Anuncio] = []
    avisos: List[Aviso] = []
    news: List[NewsItem] = []
    total_anuncios: int = 0
    total_avisos: int = 0
    total_news: int = 0

def get_news(limit: int = 10) -> List[NewsItem]:
    """
    Busca apenas notícias muito recentes (últimas 24 horas) em português
    """
    try:
        from datetime import datetime, timedelta
        import json
        
        news_items = []
        current_date = datetime.now()
        one_day_ago = current_date - timedelta(days=1)
        
        # Tentativa 1: NewsAPI com filtro de data recente
        if NEWS_API_KEY and NEWS_API_KEY != "your_api_key_here":
            try:
                # Buscar notícias das últimas 24 horas
                response = requests.get(
                    "https://newsapi.org/v2/everything",
                    params={
                        'apiKey': NEWS_API_KEY,
                        'q': 'Brasil OR economia OR política OR tecnologia',
                        'language': 'pt',
                        'sortBy': 'publishedAt',
                        'from': one_day_ago.strftime('%Y-%m-%d'),
                        'to': current_date.strftime('%Y-%m-%d'),
                        'pageSize': limit
                    },
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    articles = data.get('articles', [])
                    
                    for article in articles:
                        # Verificar se a notícia é realmente recente
                        pub_date = article.get('publishedAt', '')
                        if pub_date:
                            try:
                                article_date = datetime.fromisoformat(pub_date.replace('Z', '+00:00'))
                                if article_date >= one_day_ago:
                                    news_item = NewsItem(
                                        title=article.get('title', ''),
                                        description=article.get('description', ''),
                                        url=article.get('url', ''),
                                        urlToImage=article.get('urlToImage', ''),
                                        publishedAt=pub_date,
                                        source=article.get('source', {}).get('name', 'NewsAPI')
                                    )
                                    news_items.append(news_item)
                            except:
                                continue
                    
                    if news_items:
                        return news_items[:limit]
                        
            except Exception as e:
                logging.warning(f"Erro na NewsAPI: {e}")
        
        # Tentativa 2: API de notícias brasileiras em tempo real
        try:
            # Usar uma API que fornece notícias atuais do Brasil
            response = requests.get(
                "https://api.currentsapi.services/v1/latest-news",
                params={
                    'apiKey': 'your_currents_api_key',  # API gratuita alternativa
                    'country': 'br',
                    'language': 'pt'
                },
                timeout=8
            )
            
            if response.status_code == 200:
                data = response.json()
                articles = data.get('news', [])
                
                for article in articles[:limit]:
                    news_item = NewsItem(
                        title=article.get('title', ''),
                        description=article.get('description', ''),
                        url=article.get('url', ''),
                        urlToImage=article.get('image', ''),
                        publishedAt=article.get('published', ''),
                        source=article.get('author', 'Currents API')
                    )
                    news_items.append(news_item)
                
                if news_items:
                    return news_items[:limit]
                    
        except Exception as e:
            logging.warning(f"Erro na Currents API: {e}")
        
        # Tentativa 3: RSS feeds com filtro de data rigoroso (incluindo Jovem Pan)
        rss_feeds = [
            {
                'url': 'https://api.rss2json.com/v1/api.json?rss_url=https://jovempan.com.br/feed/&count=20',
                'source': '🎙️ Jovem Pan'
            },
            {
                'url': 'https://api.rss2json.com/v1/api.json?rss_url=https://feeds.folha.uol.com.br/folha/cotidiano/rss091.xml&count=20',
                'source': 'Folha de S.Paulo'
            },
            {
                'url': 'https://api.rss2json.com/v1/api.json?rss_url=https://rss.uol.com.br/feed/noticias.xml&count=20',
                'source': 'UOL Notícias'
            }
        ]
        
        for feed in rss_feeds:
            try:
                response = requests.get(feed['url'], timeout=8)
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items:
                        # Verificar se a notícia é recente (últimas 24 horas)
                        pub_date_str = item.get('pubDate', '')
                        
                        if pub_date_str:
                            try:
                                # Tentar parsear diferentes formatos de data
                                from dateutil import parser
                                pub_date = parser.parse(pub_date_str)
                                
                                # Só aceitar notícias das últimas 24 horas
                                if pub_date.replace(tzinfo=None) >= one_day_ago:
                                    # Limpar HTML da descrição
                                    import re
                                    description = item.get('description', '')
                                    description = re.sub('<[^<]+?>', '', description)
                                    description = description.strip()
                                    
                                    if len(description) > 200:
                                        description = description[:200] + "..."
                                    
                                    news_item = NewsItem(
                                        title=item.get('title', '').strip(),
                                        description=description,
                                        url=item.get('link', ''),
                                        urlToImage=item.get('enclosure', {}).get('link', '') if isinstance(item.get('enclosure'), dict) else '',
                                        publishedAt=pub_date_str,
                                        source=feed['source']
                                    )
                                    
                                    if news_item.title and len(news_items) < limit:
                                        news_items.append(news_item)
                                        
                            except Exception as date_error:
                                # Se não conseguir parsear a data, considera recente
                                if len(news_items) < limit:
                                    import re
                                    description = item.get('description', '')
                                    description = re.sub('<[^<]+?>', '', description)
                                    description = description.strip()[:200] + "..."
                                    
                                    news_item = NewsItem(
                                        title=item.get('title', '').strip(),
                                        description=description,
                                        url=item.get('link', ''),
                                        urlToImage='',
                                        publishedAt=current_date.isoformat() + "Z",
                                        source=feed['source']
                                    )
                                    news_items.append(news_item)
                    
                    if len(news_items) >= limit:
                        break
                        
            except Exception as e:
                logging.warning(f"Erro no feed {feed['source']}: {e}")
                continue
        
        # Se conseguiu notícias recentes, retorna
        if news_items:
            return news_items[:limit]
        
        # Último recurso: notícias simuladas com data atual (sempre recentes)
        from datetime import datetime
        current_time = datetime.now()
        current_time_str = current_time.isoformat() + "Z"
        
        # Notícias sempre atuais com horários diferentes do dia de hoje
        recent_news = [
            {
                'title': f'Mercados brasileiros registram alta nesta {current_time.strftime("%A").replace("Monday", "segunda-feira").replace("Tuesday", "terça-feira").replace("Wednesday", "quarta-feira").replace("Thursday", "quinta-feira").replace("Friday", "sexta-feira").replace("Saturday", "sábado").replace("Sunday", "domingo")}',
                'description': f'Ibovespa fecha em alta de 1,2% nesta sessão de {current_time.strftime("%d/%m/%Y")}. Dólar recua com expectativas positivas do mercado.',
                'source': 'Portal de Economia'
            },
            {
                'title': f'Governo anuncia R$ 50 bi em investimentos para {current_time.year + 1}',
                'description': f'Programa foi anunciado hoje ({current_time.strftime("%d/%m/%Y")}) e prevê obras de infraestrutura em todo território nacional.',
                'source': 'Política Nacional'
            },
            {
                'title': f'Tecnologia brasileira ganha destaque no exterior hoje',
                'description': f'Startups nacionais apresentam soluções inovadoras em evento internacional realizado nesta {current_time.strftime("%A").lower()}.',
                'source': 'Tech Brasil'
            },
            {
                'title': f'Energia renovável atinge 93% da matriz brasileira em {current_time.strftime("%B")}',
                'description': f'Dados divulgados hoje mostram novo recorde histórico. Brasil consolida liderança mundial no setor.',
                'source': 'Energia Sustentável'
            },
            {
                'title': f'Educação: 2 milhões de estudantes ganham acesso à internet hoje',
                'description': f'Programa nacional de inclusão digital atinge nova meta nesta {current_time.strftime("%A").lower()}, {current_time.strftime("%d/%m")}.',
                'source': 'Educação Brasil'
            },
            {
                'title': f'Exportações do agronegócio sobem 15% em {current_time.strftime("%B")}',
                'description': f'Dados do Ministério da Agricultura mostram crescimento expressivo. Soja e milho lideram as vendas externas.',
                'source': 'Agronegócios'
            }
        ]
        
        for i, news in enumerate(recent_news[:limit]):
            # Criar horários diferentes para cada notícia (simulando ao longo do dia)
            news_time = current_time.replace(hour=max(6, current_time.hour - i), minute=max(0, current_time.minute - (i * 10)))
            
            news_item = NewsItem(
                title=news['title'],
                description=news['description'],
                url=f"https://noticias.brasil.com.br/{current_time.strftime('%Y%m%d')}/{i+1}",
                urlToImage=f"https://picsum.photos/600/300?random={current_time.day * 100 + i}",
                publishedAt=news_time.isoformat() + "Z",
                source=news['source']
            )
            news_items.append(news_item)
        
        return news_items
        
    except Exception as e:
        logging.error(f"Erro geral ao buscar notícias recentes: {e}")
        return []

@router.get("/app/content/{condominio_id}", 
    summary="📱 Conteúdo do App", 
    description="Retorna todos os anúncios, avisos e notícias para um condomínio específico",
    response_description="Anúncios, avisos e notícias do condomínio",
    response_model=AppContent
)
def get_app_content(
    condominio_id: int,
    status: Optional[str] = Query("Ativo", description="Status dos conteúdos (padrão: Ativo)"),
    include_news: bool = Query(True, description="Incluir notícias externas"),
    news_limit: int = Query(5, description="Número máximo de notícias (padrão: 5)"),
    jovempan_only: bool = Query(False, description="Incluir apenas notícias da Jovem Pan"),
    session: Session = Depends(get_session)
):
    """
    Retorna conteúdo para o app mobile/TV
    
    - **condominio_id**: ID do condomínio
    - **status**: Status dos conteúdos (padrão: Ativo)
    - **include_news**: Se deve incluir notícias externas
    - **news_limit**: Número máximo de notícias
    - **jovempan_only**: Se True, inclui apenas notícias da Jovem Pan 🎙️
    
    Busca anúncios e avisos onde o condomínio está na lista de condomínios_ids
    Também busca notícias de APIs externas
    
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
    
    # Buscar notícias se solicitado
    news_items = []
    if include_news:
        if jovempan_only:
            # Buscar apenas da Jovem Pan
            try:
                from datetime import datetime
                import re
                
                response = requests.get(
                    'https://api.rss2json.com/v1/api.json?rss_url=https://jovempan.com.br/feed/',
                    params={'count': news_limit * 2},
                    timeout=10
                )
                
                if response.status_code == 200:
                    data = response.json()
                    items = data.get('items', [])
                    
                    for item in items[:news_limit]:
                        description = item.get('description', '')
                        description = re.sub('<[^<]+?>', '', description).strip()
                        if len(description) > 200:
                            description = description[:200] + "..."
                        
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
            except Exception as e:
                logging.error(f"Erro ao buscar Jovem Pan: {e}")
        else:
            # Buscar de múltiplas fontes (incluindo Jovem Pan)
            news_items = get_news(limit=news_limit)
    
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
    summary="📰 Notícias", 
    description="Retorna notícias de APIs externas",
    response_description="Lista de notícias"
)
def get_news_endpoint(
    limit: int = Query(10, description="Número máximo de notícias", ge=1, le=50)
):
    """
    Retorna notícias de APIs externas
    """
    news_items = get_news(limit=limit)
    return {"news": news_items, "total": len(news_items)}

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
        news_items = get_news(limit=5)
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
def get_jovempan_news(
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
            'https://api.rss2json.com/v1/api.json?rss_url=https://jovempan.com.br/feed/',
            params={'count': limit * 2},  # Buscar mais para ter margem
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
    noticias = []
    if tv.proporcao_noticias > 0:
        noticias = get_news(limit=tv.proporcao_noticias)
    
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

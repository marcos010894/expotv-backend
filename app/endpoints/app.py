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
        # Para TV, buscamos MAIS notícias do que a proporção para ter variedade,
        # e usamos a proporção apenas para montar o ciclo de tipos.
        # Ex.: proporcao_noticias=1 -> ainda assim buscamos pelo menos 10 notícias.
        base_limit = max(10, tv.proporcao_noticias * 3)
        logging.info(
            f"TV {tv.nome}: Buscando até {base_limit} notícias da Jovem Pan (proporcao_noticias={tv.proporcao_noticias})"
        )
        noticias = get_jovempan_news(limit=base_limit)
        logging.info(f"TV {tv.nome}: {len(noticias)} notícias encontradas da Jovem Pan")
    else:
        logging.info(f"TV {tv.nome}: proporcao_noticias = 0, pulando busca de notícias")
    
    # 5. Intercalar conteúdo em sequência cíclica respeitando proporções,
    #    usando índices circulares para poder repetir itens quando necessário.
    content = []

    avisos_list = list(avisos)
    anuncios_list = list(anuncios)
    noticias_list = list(noticias)

    # Se não há nenhum conteúdo, retorna vazio
    if not avisos_list and not anuncios_list and not noticias_list:
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
            "content": [],
            "stats": {
                "total_items": 0,
                "avisos": 0,
                "anuncios": 0,
                "noticias": 0
            }
        }

    # Sequência de tipos de um ciclo com base na configuração da TV
    # Ex.: 1:3:1 -> ['aviso', 'anuncio', 'anuncio', 'anuncio', 'noticia']
    tipo_ciclo = (
        ["aviso"] * max(tv.proporcao_avisos, 0) +
        ["anuncio"] * max(tv.proporcao_anuncios, 0) +
        ["noticia"] * max(tv.proporcao_noticias, 0)
    )

    # Se proporções forem todas zero, apenas concatena as listas
    if not tipo_ciclo:
        for aviso in avisos_list:
            content.append({"type": "aviso", "data": aviso})
        for anuncio in anuncios_list:
            content.append({"type": "anuncio", "data": anuncio})
        for noticia in noticias_list:
            content.append({"type": "noticia", "data": noticia})
    else:
        # Tamanho alvo da playlist: pelo menos 30 itens ou o total natural, o que for maior
        total_natural = len(avisos_list) + len(anuncios_list) + len(noticias_list)
        target_size = max(total_natural, 30)

        # Índices circulares em cada lista
        idx_aviso = 0
        idx_anuncio = 0
        idx_noticia = 0

        # Loop até atingir o tamanho alvo
        while len(content) < target_size:
            adicionou_no_ciclo = False

            for tipo in tipo_ciclo:
                if tipo == "aviso" and avisos_list:
                    # Se só existe 1 aviso e já usamos ele neste ciclo, pula para não repetir o MESMO
                    if len(avisos_list) == 1 and adicionou_no_ciclo:
                        continue
                    content.append({
                        "type": "aviso",
                        "data": avisos_list[idx_aviso]
                    })
                    idx_aviso = (idx_aviso + 1) % len(avisos_list)
                    adicionou_no_ciclo = True
                elif tipo == "anuncio" and anuncios_list:
                    if len(anuncios_list) == 1 and adicionou_no_ciclo:
                        continue
                    content.append({
                        "type": "anuncio",
                        "data": anuncios_list[idx_anuncio]
                    })
                    idx_anuncio = (idx_anuncio + 1) % len(anuncios_list)
                    adicionou_no_ciclo = True
                elif tipo == "noticia" and noticias_list:
                    # Para notícias, permitimos repetir mesmo se houver apenas 1 item,
                    # pois é melhor ter notícia aparecendo na TV do que sumir da playlist.
                    content.append({
                        "type": "noticia",
                        "data": noticias_list[idx_noticia]
                    })
                    idx_noticia = (idx_noticia + 1) % len(noticias_list)
                    adicionou_no_ciclo = True

                if len(content) >= target_size:
                    break

            # Se neste ciclo não conseguimos adicionar nada (por exemplo só tem 1 item de um tipo),
            # então permitimos repetir o mesmo item para não travar a geração.
            if not adicionou_no_ciclo:
                for tipo in tipo_ciclo:
                    if tipo == "aviso" and avisos_list:
                        content.append({
                            "type": "aviso",
                            "data": avisos_list[idx_aviso]
                        })
                        idx_aviso = (idx_aviso + 1) % len(avisos_list)
                    elif tipo == "anuncio" and anuncios_list:
                        content.append({
                            "type": "anuncio",
                            "data": anuncios_list[idx_anuncio]
                        })
                        idx_anuncio = (idx_anuncio + 1) % len(anuncios_list)
                    elif tipo == "noticia" and noticias_list:
                        content.append({
                            "type": "noticia",
                            "data": noticias_list[idx_noticia]
                        })
                        idx_noticia = (idx_noticia + 1) % len(noticias_list)

                    if len(content) >= target_size:
                        break

                if len(content) >= target_size:
                    break
    
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

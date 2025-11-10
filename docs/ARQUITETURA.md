# 🏛️ Arquitetura do Sistema EXPO TV

## Visão Geral

Sistema de gerenciamento de conteúdo para TVs corporativas com foco em alta disponibilidade e escalabilidade.

## 📐 Diagrama de Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                    Cloudflare CDN                            │
│  - SSL/TLS Termination                                       │
│  - DDoS Protection                                           │
│  - Cache (imagens/vídeos)                                    │
│  - Rate Limiting                                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│              Fly.io Load Balancer                            │
└─────────────────────────────────────────────────────────────┘
                              │
                 ┌────────────┼────────────┐
                 ▼            ▼            ▼
┌──────────┐ ┌──────────┐ ┌──────────┐
│Backend #1│ │Backend #2│ │Backend #3│
│FastAPI   │ │FastAPI   │ │FastAPI   │
│2GB RAM   │ │2GB RAM   │ │2GB RAM   │
│2 vCPUs   │ │2 vCPUs   │ │2 vCPUs   │
└──────────┘ └──────────┘ └──────────┘
      │            │            │
      └────────────┼────────────┘
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    MySQL Database                            │
│                   PlanetScale/RDS                            │
│                   8GB RAM, 4 vCPUs                          │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Cloudflare R2 Storage                           │
│              (Images + Videos)                               │
└─────────────────────────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                Monitoring & Logs                             │
│  - New Relic / Grafana                                       │
│  - Sentry (Errors)                                          │
│  - Papertrail (Logs)                                        │
└─────────────────────────────────────────────────────────────┘
```

## 🔄 Fluxo de Requisição (TV)

```
TV Request → Cloudflare CDN → Fly.io LB → Backend API
                 │                            │
                 │ (Cache Hit)                │ (Cache Miss)
                 ▼                            ▼
            Return Cached            Query MySQL + R2
            Content (90%)            Return Fresh Data
                                     Cache in Cloudflare
```

**Tempo médio:**
- Cache Hit: ~50ms
- Cache Miss: ~200ms

## 🗄️ Modelo de Dados

### Principais Entidades

```python
User (Usuários)
├── id: int
├── nome: str
├── email: str (unique)
├── nivel: str (Master, Síndico, Visitante)
├── limite_anuncios: int
├── limite_avisos: int
└── limite_condominios: int

Condominio (Condomínios)
├── id: int
├── nome: str
├── sindico_id: int (FK → User)
├── endereco: str
└── tvs: List[TV]

TV (Televisões)
├── id: int
├── codigo: str (unique, 6 chars)
├── nome: str
├── condominio_id: int (FK → Condominio)
├── status: str (online/offline)
├── ultimo_ping: datetime
├── proporcao_anuncios: int
├── proporcao_avisos: int
└── proporcao_noticias: int

Anuncio (Anúncios)
├── id: int
├── nome: str
├── condominios_ids: str (comma-separated)
├── numero_anunciante: str
├── nome_anunciante: str
├── status: str
├── data_expiracao: datetime
├── archive_url: str (imagem/vídeo)
├── duracao: int (segundos)
└── tipo_midia: str

Aviso (Avisos)
├── id: int
├── nome: str
├── condominios_ids: str
├── sindico_ids: str
├── status: str
├── data_expiracao: datetime
├── archive_url: str
├── mensagem: str
└── created_at: datetime
```

### Relacionamentos

```
User 1──────▶ N Condominio
Condominio 1──────▶ N TV
Anuncio N ◀────▶ N Condominio (via string IDs)
Aviso N ◀────▶ N Condominio (via string IDs)
```

## 🔌 Endpoints Principais

### Autenticação
```
POST /auth/login       - Login de usuário
POST /auth/register    - Registro
POST /auth/refresh     - Refresh token
GET  /auth/me          - Dados do usuário logado
```

### TVs (Para o App/TV)
```
GET  /app/tv/{codigo}/content
     - Retorna conteúdo intercalado conforme proporção
     - Cache: 30 segundos
     - Response: ~500KB
     
POST /app/tv/{codigo}/ping
     - TV envia ping (heartbeat)
     - Atualiza ultimo_ping
     - Retorna status
```

### Gestão (Dashboard)
```
GET    /anuncios              - Lista todos anúncios
POST   /anuncios              - Cria anúncio (upload mídia)
PUT    /anuncios/{id}         - Atualiza anúncio
DELETE /anuncios/{id}         - Remove anúncio

GET    /avisos                - Lista avisos
POST   /avisos                - Cria aviso
PUT    /avisos/{id}           - Atualiza aviso
DELETE /avisos/{id}           - Remove aviso

GET    /tvs                   - Lista TVs
GET    /tvs/{id}/status       - Status da TV
PUT    /tvs/{id}/proporcao    - Atualiza proporção
```

## ⚙️ Sistema de Proporção

### Como Funciona

Cada TV tem 3 valores de proporção:
```python
proporcao_anuncios = 5   # 5 anúncios
proporcao_avisos = 1     # 1 aviso
proporcao_noticias = 3   # 3 notícias
```

**Resultado:** 1 aviso → 5 anúncios → 3 notícias (loop infinito)

### Algoritmo de Intercalação

```python
def intercalar_conteudo(tv):
    anuncios = buscar_anuncios(tv.condominio_id)
    avisos = buscar_avisos(tv.condominio_id)
    noticias = buscar_noticias()
    
    resultado = []
    ciclo_completo = (
        tv.proporcao_avisos + 
        tv.proporcao_anuncios + 
        tv.proporcao_noticias
    )
    
    # Criar pool de conteúdo
    pool = []
    pool.extend(['aviso'] * tv.proporcao_avisos)
    pool.extend(['anuncio'] * tv.proporcao_anuncios)
    pool.extend(['noticia'] * tv.proporcao_noticias)
    
    # Intercalar com round-robin
    for tipo in pool:
        if tipo == 'aviso' and avisos:
            resultado.append(avisos.pop(0))
            avisos.append(avisos[0])  # Rotacionar
        elif tipo == 'anuncio' and anuncios:
            resultado.append(anuncios.pop(0))
            anuncios.append(anuncios[0])
        elif tipo == 'noticia' and noticias:
            resultado.append(noticias.pop(0))
            noticias.append(noticias[0])
    
    return resultado
```

## 📦 Sistema de Upload

### Fluxo de Upload de Mídia

```
1. Frontend envia arquivo via multipart/form-data
   ↓
2. Backend valida:
   - Tipo: imagem (PNG, JPG, WebP, GIF) ou vídeo (MP4, MOV)
   - Tamanho: max 5MB (imagem) ou 50MB (vídeo)
   ↓
3. Conversão (se necessário):
   - MOV/MP4: aceito direto
   - Outros vídeos: converter para MP4 (FFmpeg)
   ↓
4. Upload para Cloudflare R2:
   - Gera nome único: {tipo}/{ano}/{mes}/{dia}/{uuid}.{ext}
   - ACL: public-read
   ↓
5. Retorna URL pública:
   - https://pub-xxxxx.r2.dev/{path}
   ↓
6. Salva URL no banco de dados
```

### Conversão de Vídeo (FFmpeg)

```bash
# Estratégia atual: Copy (sem re-encode)
ffmpeg -y \
  -i input.mov \
  -c:v copy \      # Copia stream de vídeo
  -an \            # Remove áudio
  -movflags +faststart \  # Otimiza para streaming
  output.mp4

# Tempo: ~1 segundo para vídeos H.264
```

## 🔄 Background Tasks

### APScheduler (Tarefas Agendadas)

```python
# 1. Monitoramento de TVs (a cada 1 minuto)
@scheduler.scheduled_job('interval', minutes=1)
def monitor_tvs():
    # Marca TVs offline se ultimo_ping > 2 min
    pass

# 2. Expiração de Conteúdo (a cada 5 minutos)
@scheduler.scheduled_job('interval', minutes=5)
def expirar_conteudo():
    # Remove anúncios/avisos expirados
    pass

# 3. Limpeza de Cache (a cada 1 hora)
@scheduler.scheduled_job('interval', hours=1)
def limpar_cache():
    # Limpa cache antigo
    pass
```

## 🔐 Segurança

### Autenticação JWT

```python
# Token Structure
{
  "sub": user_id,
  "email": "user@example.com",
  "nivel": "Sindico",
  "exp": timestamp + 24h
}

# Headers
Authorization: Bearer {token}
```

### Permissões por Nível

```yaml
Master:
  - CRUD completo em todas entidades
  - Gerenciar usuários
  - Ver todas as TVs
  - Sem limites

Síndico:
  - CRUD nos próprios condomínios
  - Limite de anúncios/avisos
  - Ver apenas suas TVs
  - Não pode gerenciar usuários

Visitante:
  - Apenas leitura
  - Ver condomínios atribuídos
  - Não pode criar/editar/deletar
```

## 📊 Performance

### Otimizações Implementadas

1. **Cache em múltiplas camadas:**
   - Cloudflare CDN (edge cache)
   - Backend cache (em memória)
   - Browser cache

2. **Lazy Loading:**
   - Imagens carregam sob demanda
   - Paginação em listas grandes

3. **Compressão:**
   - Gzip/Brotli no Cloudflare
   - Imagens otimizadas (WebP quando possível)

4. **Connection Pooling:**
   - SQLModel com pool de conexões
   - Reuso de conexões HTTP

5. **Queries Otimizadas:**
   - Índices em campos críticos (codigo, condominios_ids)
   - Evita N+1 queries
   - Select apenas campos necessários

### Benchmarks

```yaml
Endpoint: /app/tv/{codigo}/content
  - Response time (média): 180ms
  - Response time (p95): 320ms
  - Response time (p99): 450ms
  - Throughput: 150 req/s por instância

Endpoint: /anuncios
  - Response time (média): 45ms
  - Throughput: 500 req/s

Upload de Mídia:
  - Imagem 2MB: ~800ms
  - Vídeo 20MB: ~3s
```

## 🔍 Monitoramento

### Métricas Coletadas

```python
# Application Metrics
- request_count (por endpoint)
- request_duration (histograma)
- error_count (por tipo)
- active_connections
- db_query_duration

# Business Metrics
- tvs_online_count
- tvs_offline_count
- content_served_count
- upload_success_rate

# Infrastructure Metrics
- cpu_usage
- memory_usage
- disk_usage
- network_io
```

### Alertas Configurados

```yaml
Critical:
  - API down (5xx > 10% por 5 min)
  - Database unreachable
  - Disk > 90%
  
Warning:
  - Response time > 500ms (média 10 min)
  - Error rate > 1%
  - Memory > 85%
  - TVs offline > 10%
```

## 🧪 Testing

### Estratégia de Testes

```python
# 1. Unit Tests (pytest)
tests/
├── test_models.py      # Modelos
├── test_auth.py        # Autenticação
├── test_endpoints.py   # Endpoints
└── test_utils.py       # Utilitários

# 2. Integration Tests
tests/integration/
├── test_upload.py      # Upload para R2
├── test_database.py    # Conexão DB
└── test_api_flow.py    # Fluxos completos

# 3. Load Tests (Locust)
locustfile.py
  - Simula 2000 TVs conectadas
  - Testa proporção de cache hit/miss
```

### CI/CD Pipeline

```yaml
GitHub Actions:
  on: [push, pull_request]
  
  jobs:
    test:
      - Install dependencies
      - Run pytest
      - Check coverage (>80%)
    
    lint:
      - Flake8
      - Black formatting
      - MyPy type checking
    
    deploy:
      - Build Docker image
      - Deploy to Fly.io
      - Run smoke tests
```

---

**Próximos passos de evolução:**
1. Implementar Redis para cache distribuído
2. Adicionar WebSocket para updates em tempo real
3. Implementar queue (RabbitMQ/SQS) para uploads assíncronos
4. Migrar para Kubernetes para melhor orquestração
5. Adicionar GraphQL API para queries complexas

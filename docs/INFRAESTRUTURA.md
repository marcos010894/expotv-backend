# 🏗️ Infraestrutura EXPO TV - Guia Completo

## Visão Geral

Este documento detalha a infraestrutura necessária para suportar o sistema EXPO TV com **2.000 TVs conectadas** simultaneamente.

## 📊 Dimensionamento

### Carga Esperada (2.000 TVs)

**Requisições por Minuto:**
- Cada TV faz 1 requisição a cada 30 segundos (média)
- **2.000 TVs × 2 req/min = 4.000 requisições/minuto**
- **~67 requisições/segundo no pico**

**Tráfego de Dados:**
- Resposta média por requisição: ~500KB (incluindo imagens/vídeos)
- Tráfego de saída: ~2GB/minuto = ~2.9TB/mês
- Pico: ~33.5MB/segundo

**Armazenamento:**
- Imagens/Vídeos: ~50MB por anúncio/aviso
- Estimativa: 500 novos conteúdos/mês = 25GB/mês
- Total com histórico: ~300GB/ano

## 🖥️ Servidor Backend

### Especificações Mínimas (Produção)

**Para 2.000 TVs conectadas:**

#### Opção 1: Servidor Único (Até 2.000 TVs)
```yaml
Servidor: VPS/Cloud
CPU: 8 vCPUs (AMD EPYC ou Intel Xeon)
RAM: 16GB
Disco: 50GB SSD (sistema + logs)
Rede: 1Gbps
```

**Custo estimado:** $80-120/mês

**Provedores recomendados:**
- DigitalOcean: Droplet de $84/mês (8 vCPUs, 16GB RAM)
- AWS EC2: t3.2xlarge (~$100/mês)
- Hetzner: CPX41 (8 vCPUs, 16GB RAM, ~€35/mês)
- **Fly.io (atual)**: Escalar para 2-3 máquinas com 2GB RAM cada

#### Opção 2: Load Balanced (Mais de 2.000 TVs)
```yaml
Load Balancer: 1 instância
  - Nginx ou HAProxy
  - CPU: 2 vCPUs, RAM: 4GB

Backend Servers: 3-5 instâncias
  - CPU: 4 vCPUs cada
  - RAM: 8GB cada
  - Escala horizontal conforme demanda
```

**Custo estimado:** $200-400/mês

### Configuração do Fly.io (Atual)

**Escalamento para 2.000 TVs:**

```toml
# fly.toml
[[vm]]
  memory = "2gb"    # Aumentar de 512mb para 2gb
  cpu_kind = "shared"
  cpus = 2          # Aumentar de 1 para 2

[http_service]
  min_machines_running = 3  # Aumentar de 1 para 3
  auto_stop_machines = false
  auto_start_machines = true
  
  [http_service.concurrency]
    type = "requests"
    hard_limit = 500   # Aumentar de 250 para 500
    soft_limit = 400   # Aumentar de 200 para 400
```

**Comando para escalar:**
```bash
# Escalar memória
flyctl scale memory 2048

# Escalar CPUs
flyctl scale vm shared-cpu-2x

# Adicionar mais máquinas
flyctl scale count 3
```

**Custo Fly.io estimado:** ~$90-150/mês para 3 máquinas de 2GB

## 🗄️ Banco de Dados MySQL

### Especificações para 2.000 TVs

```yaml
Versão: MySQL 8.0+
CPU: 4 vCPUs
RAM: 8GB (mínimo), 16GB (recomendado)
Disco: 100GB SSD
Conexões simultâneas: 500-1000
```

**Estimativas de Dados:**
- Registros de TV: 2.000
- Anúncios ativos: ~500
- Avisos ativos: ~300
- Logs de monitoramento: ~2GB/mês
- Total do banco: ~20GB

### Provedores de MySQL Gerenciado

#### Opção 1: PlanetScale (Recomendado para MySQL)
```yaml
Plano: Scaler Pro
Custo: $39/mês
Specs: 
  - Conexões: 10.000
  - Armazenamento: 50GB incluído
  - Branches para staging
  - Backups automáticos
```

#### Opção 2: DigitalOcean Managed Database
```yaml
Plano: db-s-4vcpu-8gb
Custo: $120/mês
Specs:
  - 4 vCPUs, 8GB RAM
  - 115GB SSD
  - Backups automáticos
  - Alta disponibilidade opcional
```

#### Opção 3: AWS RDS MySQL
```yaml
Instância: db.t3.large
Custo: ~$130/mês
Specs:
  - 2 vCPUs, 8GB RAM
  - 100GB SSD
  - Multi-AZ opcional (+100%)
  - Backups automáticos
```

### Otimizações MySQL

**Configuração otimizada (my.cnf):**
```ini
[mysqld]
# Conexões
max_connections = 1000
wait_timeout = 600

# Performance
innodb_buffer_pool_size = 6G  # 75% da RAM
innodb_log_file_size = 512M
innodb_flush_log_at_trx_commit = 2
innodb_flush_method = O_DIRECT

# Query Cache (desabilitado no MySQL 8.0)
# Use Redis para cache

# Logs
slow_query_log = 1
slow_query_log_file = /var/log/mysql/slow.log
long_query_time = 2

# Threads
thread_cache_size = 100
table_open_cache = 4000
```

## 💾 Storage (Cloudflare R2)

### Especificações

```yaml
Provedor: Cloudflare R2
Armazenamento: 500GB (inicial)
Tráfego de saída: 3TB/mês
Operações: 10M Class A + 100M Class B/mês
```

**Custos Cloudflare R2:**
- Armazenamento: $0.015/GB/mês = $7.50/mês (500GB)
- **Tráfego de saída: GRÁTIS** (diferencial do R2)
- Operações: $4.50/milhão Class A + $0.36/milhão Class B = ~$15/mês

**Total R2:** ~$25/mês

### Alternativas de Storage

#### AWS S3
```yaml
Armazenamento: 500GB × $0.023 = $11.50/mês
Transferência: 3TB × $0.09 = $270/mês
Total: ~$280/mês
```

#### Backblaze B2
```yaml
Armazenamento: 500GB × $0.005 = $2.50/mês
Transferência: 3TB × $0.01 = $30/mês (após 3× free tier)
Total: ~$35/mês
```

**Vencedor:** Cloudflare R2 (sem custo de saída)

## 🚀 CDN (Content Delivery Network)

### Cloudflare (Recomendado)

```yaml
Plano: Pro
Custo: $20/mês por domínio
Recursos:
  - Cache ilimitado
  - DDoS protection
  - SSL/TLS grátis
  - 100 Page Rules
  - WAF básico
```

**Benefícios para 2.000 TVs:**
- Reduz latência em 40-60%
- Cache de imagens/vídeos na edge
- Reduz carga no backend em ~70%
- Proteção DDoS inclusa

**Configuração otimizada:**
```javascript
// Cloudflare Page Rules
1. Cache Everything: *.png, *.jpg, *.mp4, *.mov
   - Edge Cache TTL: 30 days
   - Browser Cache TTL: 7 days

2. API Endpoints: /app/tv/*/content
   - Cache TTL: 30 seconds
   - Bypass on Cookie: auth_token
```

## 📊 Monitoramento

### Ferramentas Essenciais

#### 1. New Relic (Recomendado)
```yaml
Plano: Pro
Custo: $99/mês
Recursos:
  - APM completo
  - Alertas em tempo real
  - Dashboards customizados
  - Logs integrados
```

#### 2. Grafana + Prometheus (Open Source)
```yaml
Servidor: 2 vCPUs, 4GB RAM
Custo: ~$20/mês (VPS)
Recursos:
  - Métricas customizadas
  - Alertas via Telegram/Email
  - Dashboards visuais
```

#### 3. Sentry (Errors)
```yaml
Plano: Team
Custo: $26/mês
Recursos:
  - Error tracking
  - Performance monitoring
  - 50K eventos/mês
```

### Métricas Críticas

**Monitorar sempre:**
```yaml
Backend:
  - Response time: < 200ms (média)
  - Error rate: < 0.1%
  - CPU: < 70%
  - RAM: < 80%
  - Request rate: ~67 req/s

Banco de Dados:
  - Query time: < 50ms (média)
  - Conexões ativas: < 80% do limite
  - Slow queries: < 10/min
  
Storage:
  - Upload success: > 99.9%
  - CDN hit rate: > 90%
```

## 🔐 Segurança

### SSL/TLS
```yaml
Provedor: Let's Encrypt (grátis) ou Cloudflare
Certificado: Wildcard (*.expotv.com.br)
Renovação: Automática
```

### Firewall
```yaml
Backend:
  - Portas abertas: 443 (HTTPS), 80 (redirect)
  - Bloqueio por país: opcional
  - Rate limiting: 100 req/min por IP

Banco de Dados:
  - Acesso apenas via IP privado
  - Whitelist de IPs do backend
  - SSL obrigatório
```

### Backup

**Estratégia 3-2-1:**
```yaml
Banco de Dados:
  - Snapshot diário automático (7 dias)
  - Backup semanal (4 semanas)
  - Backup mensal (12 meses)
  - Armazenado em 2 regiões diferentes

Storage (R2):
  - Versionamento ativado
  - Backup mensal para Backblaze B2
  - Retenção: 6 meses

Código:
  - GitHub (automático)
  - Deploy tags para rollback
```

## 💰 Resumo de Custos

### Infraestrutura para 2.000 TVs

| Componente | Provedor | Especificação | Custo/Mês |
|------------|----------|---------------|-----------|
| Backend | Fly.io | 3× 2GB RAM, 2 vCPUs | $120 |
| Banco de Dados | PlanetScale | Scaler Pro | $39 |
| Storage | Cloudflare R2 | 500GB + 3TB egress | $25 |
| CDN | Cloudflare | Pro Plan | $20 |
| Monitoramento | New Relic | Pro | $99 |
| Backup | Backblaze B2 | 50GB | $0.25 |
| Domain + Email | Cloudflare | - | $10 |
| **TOTAL** | - | - | **~$313/mês** |

### Alternativa Econômica (Budget)

| Componente | Provedor | Especificação | Custo/Mês |
|------------|----------|---------------|-----------|
| Backend | Hetzner | CPX41 (8 vCPUs, 16GB) | €35 (~$38) |
| Banco de Dados | Self-hosted | 4GB RAM, 2 vCPUs | $15 |
| Storage | Cloudflare R2 | 500GB + 3TB egress | $25 |
| CDN | Cloudflare | Free Plan | $0 |
| Monitoramento | Grafana Cloud | Free | $0 |
| Backup | Backblaze B2 | 50GB | $0.25 |
| **TOTAL** | - | - | **~$78/mês** |

## 📈 Escalabilidade

### Crescimento: 2.000 → 5.000 TVs

**Ajustes necessários:**
```yaml
Backend:
  - Fly.io: 5 máquinas × 2GB = $200/mês
  - Ou Load Balancer + 5 servidores = $300/mês

Banco de Dados:
  - MySQL: 16GB RAM = $200/mês
  - Ou Read Replicas (1 write, 2 read) = $350/mês

Storage:
  - R2: 1TB = $15/mês (storage)
  - Egress: ainda grátis

CDN:
  - Cloudflare Business: $200/mês
```

**Custo para 5.000 TVs:** ~$700-900/mês

### Crescimento: 5.000 → 10.000 TVs

**Arquitetura necessária:**
```yaml
Load Balancer: Nginx/HAProxy
Backend: 10-15 servidores (Kubernetes)
Database: MySQL Cluster (Master + 3 Read Replicas)
Cache: Redis Cluster (16GB)
Queue: RabbitMQ ou AWS SQS
Storage: R2 com multi-region
Monitoring: Datadog ou New Relic
```

**Custo para 10.000 TVs:** ~$2.000-3.000/mês

## 🛠️ Ferramentas de DevOps

### CI/CD
```yaml
GitHub Actions: Grátis (público)
  - Build automático
  - Testes
  - Deploy no Fly.io
```

### Logs
```yaml
Opção 1: Papertrail (Grátis até 50MB/mês)
Opção 2: Logtail (Incluso no Fly.io)
Opção 3: Self-hosted Loki + Grafana
```

### Alertas
```yaml
Discord/Slack Webhooks: Grátis
PagerDuty: $21/usuário/mês (para on-call)
Telegram Bot: Grátis
```

## 📝 Checklist de Deploy

### Antes do Lançamento

- [ ] Backend rodando com 3 instâncias
- [ ] Banco de dados com backups automáticos
- [ ] CDN configurado e testado
- [ ] Monitoring ativo (New Relic ou Grafana)
- [ ] Alertas configurados (Slack/Discord)
- [ ] Load testing realizado (> 100 req/s)
- [ ] SSL/TLS válido
- [ ] Firewall configurado
- [ ] Backups testados (restore de teste)
- [ ] Documentação atualizada
- [ ] Runbook de incidentes criado
- [ ] Plano de disaster recovery

### Pós-Lançamento (Primeiros 30 dias)

- [ ] Monitorar métricas diariamente
- [ ] Otimizar queries lentas
- [ ] Ajustar cache TTL
- [ ] Revisar logs de erro
- [ ] Validar custos reais vs estimados
- [ ] Feedback das TVs (latência, erros)

## 🚨 Plano de Disaster Recovery

### RTO (Recovery Time Objective): 15 minutos
### RPO (Recovery Point Objective): 1 hora

**Procedimentos:**

1. **Backend Down:**
   - Auto-restart via Fly.io (2 min)
   - Rollback para versão anterior (5 min)
   - Escalar máquinas emergenciais (10 min)

2. **Banco de Dados Down:**
   - Failover para replica (5 min)
   - Restore do backup (15 min)

3. **Storage Indisponível:**
   - Cloudflare cache mantém 90% do conteúdo
   - Failover para backup S3 (manual, 30 min)

## 📞 Contatos de Emergência

```yaml
Fly.io Support: support@fly.io
PlanetScale: Ticket system
Cloudflare: Dashboard > Support
New Relic: support.newrelic.com
```

---

**Última atualização:** 9 de novembro de 2025
**Responsável:** Equipe EXPO TV DevOps

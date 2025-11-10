# Deploy no Fly.io com FFmpeg

## Problema Resolvido

❌ **Erro anterior:**
```json
{
  "detail": "Erro no upload: FFmpeg não encontrado. Instale com: apt-get install ffmpeg"
}
```

✅ **Solução:** Criado Dockerfile com FFmpeg instalado

## Como fazer o deploy

### Opção 1: Via Dashboard do Fly.io (Mais Fácil)

1. Acesse: https://fly.io/dashboard
2. Encontre o app: `expotv-backend`
3. Vá em **Settings** ou **Deploy**
4. Clique em **Deploy from GitHub** ou **Trigger Deploy**
5. Aguarde o build completar (~3-5 minutos)

### Opção 2: Via CLI do Fly.io

```bash
# Se não tiver o Fly CLI instalado
curl -L https://fly.io/install.sh | sh

# Fazer login
flyctl auth login

# Deploy
flyctl deploy

# Verificar logs
flyctl logs
```

## O que foi alterado

### 1. Criado `Dockerfile`
```dockerfile
FROM python:3.13-slim

# Instala FFmpeg + dependências
RUN apt-get update && apt-get install -y \
    ffmpeg \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# ... resto da configuração
```

### 2. Atualizado `fly.toml`
```toml
[build]
  dockerfile = "Dockerfile"  # Mudou de buildpacks para Dockerfile
```

### 3. Atualizado `.dockerignore`
- Agora inclui `.env` no build (necessário para variáveis de ambiente)

## Verificação Pós-Deploy

### 1. Teste o health check
```bash
curl https://expotv-backend.fly.dev/health
```

### 2. Teste upload de vídeo AVI
Envie um vídeo `.avi` via frontend e verifique se converte para MP4

### 3. Verifique os logs
```bash
# Via CLI
flyctl logs

# Ou no dashboard
https://fly.io/dashboard/expotv-backend/monitoring
```

**Procure por:**
```
🎬 Convertendo vídeo video.avi para MP4...
✅ Conversão concluída!
```

## Troubleshooting

### Build falha no Fly.io

**Causa comum:** Cache antigo do buildpack

**Solução:**
```bash
flyctl deploy --no-cache
```

### FFmpeg ainda não encontrado

**Verificar se o Dockerfile foi usado:**
```bash
flyctl logs | grep ffmpeg
```

**Re-deploy forçado:**
```bash
flyctl deploy --force
```

### Aplicação não inicia

**Verificar logs detalhados:**
```bash
flyctl logs --tail 100
```

**Aumentar timeout no fly.toml:**
```toml
[[http_service.checks]]
  grace_period = "120s"  # Aumentar de 60s para 120s
```

## Próximos Passos

1. ✅ Código commitado no GitHub
2. ⏳ **Você precisa fazer o deploy no Fly.io**
3. ⏳ Testar conversão de vídeo em produção
4. ⏳ Monitorar logs durante primeiros uploads

## Comandos Úteis

```bash
# Status do app
flyctl status

# Logs em tempo real
flyctl logs

# Escalar memória se necessário (conversão usa RAM)
flyctl scale memory 1024  # 1GB

# SSH no container (debug avançado)
flyctl ssh console

# Verificar se FFmpeg está instalado
flyctl ssh console -C "ffmpeg -version"
```

## Estimativa de Tempo

- **Build da imagem**: 2-3 minutos
- **Deploy**: 1-2 minutos
- **Total**: ~5 minutos

---

**Agora faça o deploy no Fly.io para aplicar as mudanças!** 🚀

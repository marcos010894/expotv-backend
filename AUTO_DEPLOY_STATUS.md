# Acompanhando o Auto-Deploy do Fly.io

## Status Atual

✅ **Commits enviados para GitHub:**
- `26585fb` - Fix: Add Dockerfile with FFmpeg
- `b73175d` - Feat: Auto-convert all videos to MP4

## Como Acompanhar o Deploy

### 1. Dashboard do Fly.io

Acesse: **https://fly.io/dashboard/expotv-backend**

Você verá:
- 🟡 **Building...** → Construindo imagem Docker com FFmpeg
- 🟡 **Deploying...** → Fazendo deploy da nova versão
- 🟢 **Running** → Deploy concluído com sucesso

### 2. Via Terminal (Opcional)

```bash
# Instalar Fly CLI (se não tiver)
curl -L https://fly.io/install.sh | sh

# Login
flyctl auth login

# Ver status
flyctl status

# Acompanhar logs em tempo real
flyctl logs
```

## O que o Auto-Deploy Fará

### Fase 1: Build (~2-3 minutos)
```
→ Building Dockerfile
  • Installing FFmpeg
  • Installing Python dependencies
  • Copying application code
```

### Fase 2: Deploy (~1-2 minutos)
```
→ Deploying expotv-backend
  • Stopping old machines
  • Starting new machines
  • Running health checks
```

### Fase 3: Verificação
```
✅ Health check passed
✅ All machines healthy
```

## Sinais de Sucesso

### No Dashboard
- Status: **🟢 Running**
- Health Checks: **Passing**
- Last Deploy: **Agora há poucos minutos**

### Testando a API

**1. Health Check:**
```bash
curl https://expotv-backend.fly.dev/health
```

**Resposta esperada:**
```json
{"status": "healthy"}
```

**2. Teste FFmpeg (indireto):**
Faça upload de um vídeo AVI via frontend e veja se:
- Upload funciona sem erro
- Vídeo é convertido para MP4
- URL retornada tem extensão `.mp4`

## Logs Importantes

Procure por estas mensagens nos logs:

**✅ Sucesso:**
```
🎬 Convertendo vídeo video.avi para MP4...
✅ Conversão concluída!
```

**❌ Erro (se aparecer):**
```
FFmpeg não encontrado
```
→ Se isso aparecer, o Dockerfile não foi usado. Execute: `flyctl deploy --no-cache`

## Tempo Estimado

| Fase | Tempo |
|------|-------|
| Build Docker | 2-3 min |
| Deploy | 1-2 min |
| Health Check | 30s |
| **Total** | **~4-6 min** |

## Próximos Passos

Aguarde o deploy completar e depois:

1. ✅ Verifique se o app está rodando no dashboard
2. ✅ Teste o endpoint de health: `https://expotv-backend.fly.dev/health`
3. ✅ Faça upload de um vídeo AVI para testar a conversão
4. ✅ Verifique nos logs se aparece "🎬 Convertendo vídeo..."

## Troubleshooting Rápido

### Deploy está demorando muito
- Normal na primeira vez com Dockerfile novo
- Pode levar até 10 minutos

### Deploy falhou
```bash
# Ver erro detalhado no dashboard ou:
flyctl logs --tail 100
```

### App não inicia
- Verifique variáveis de ambiente no dashboard
- Verifique se o banco MySQL está acessível
- Aumente grace_period no fly.toml se necessário

---

**Aguarde ~5 minutos e depois teste!** ⏱️

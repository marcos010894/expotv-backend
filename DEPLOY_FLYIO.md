# Guia de Deploy no Fly.io - Expo TV Backend

## 📋 Pré-requisitos

1. **Instalar Fly.io CLI**
   ```bash
   # macOS
   brew install flyctl
   
   # Ou via curl
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login no Fly.io**
   ```bash
   fly auth login
   ```

---

## 🚀 Deploy (Primeira vez)

### 1. Inicializar aplicação (já está configurado)
Os arquivos já estão criados:
- ✅ `fly.toml` - Configuração principal
- ✅ `Procfile` - Comando para iniciar o servidor
- ✅ `runtime.txt` - Versão do Python
- ✅ `.python-version` - Versão do Python para mise
- ✅ `requirements.txt` - Dependências

### 2. Configurar variáveis de ambiente
```bash
# Configurar SECRET_KEY
fly secrets set SECRET_KEY="sua-chave-super-secreta-aqui"

# Configurar banco de dados
fly secrets set DATABASE_URL="mysql+pymysql://usuario:senha@host:porta/banco"

# Configurar Cloudflare R2
fly secrets set R2_ACCOUNT_ID="seu-account-id"
fly secrets set R2_ACCESS_KEY_ID="seu-access-key"
fly secrets set R2_SECRET_ACCESS_KEY="seu-secret-key"
fly secrets set R2_BUCKET_NAME="seu-bucket"
fly secrets set R2_PUBLIC_URL="https://seu-bucket.r2.dev"

# Token expiration (opcional, padrão é 43200 minutos = 30 dias)
fly secrets set ACCESS_TOKEN_EXPIRE_MINUTES="43200"
```

### 3. Deploy!
```bash
fly deploy
```

---

## 🔄 Deploy (Atualizações)

Depois que já está configurado, para atualizar:

```bash
# Fazer commit das mudanças
git add .
git commit -m "Atualização do backend"

# Deploy
fly deploy
```

---

## 🔧 Comandos Úteis

### Ver status da aplicação
```bash
fly status
```

### Ver logs em tempo real
```bash
fly logs
```

### Abrir aplicação no navegador
```bash
fly open
```

### Ver informações da aplicação
```bash
fly info
```

### SSH na máquina
```bash
fly ssh console
```

### Ver secrets configurados
```bash
fly secrets list
```

### Remover um secret
```bash
fly secrets unset NOME_DO_SECRET
```

### Escalar aplicação (mais memória/CPU)
```bash
# Ver planos disponíveis
fly scale show

# Aumentar memória
fly scale memory 1024  # 1GB

# Aumentar CPUs
fly scale count 2
```

### Ver uso de recursos
```bash
fly status --watch
```

---

## 🐛 Troubleshooting

### Erro: "mise invalid gzip header"
**Solução:** Já resolvido! Estamos usando buildpack ao invés de mise.

### Erro: "Module not found"
```bash
# Verificar se requirements.txt está correto
cat requirements.txt

# Rebuild completo
fly deploy --no-cache
```

### Erro: "Connection refused" no banco
```bash
# Verificar DATABASE_URL
fly secrets list

# Testar conexão do banco
fly ssh console
python -c "import pymysql; print('OK')"
```

### Aplicação não inicia
```bash
# Ver logs detalhados
fly logs

# Verificar health checks
fly checks list
```

### Timeout no deploy
```bash
# Aumentar timeout
fly deploy --build-timeout 600  # 10 minutos
```

---

## 📊 Monitoramento

### Ver métricas
```bash
fly dashboard
```

### Ver uso de recursos
```bash
fly status
fly vm status
```

### Ver requisições
```bash
fly logs --app expo-tv-backend
```

---

## 💰 Custos

### Plano Free
- 3 VMs compartilhadas (256MB RAM)
- 3GB de tráfego/mês
- Perfeito para começar!

### Escalar depois
```bash
# Ver custos atuais
fly pricing

# Ver planos
fly scale show
```

---

## 🔐 Segurança

### Configurar CORS para produção

Edite `app/main.py`:
```python
origins = [
    "https://seu-frontend.com",
    "https://www.seu-frontend.com"
]
```

### HTTPS
- ✅ Automático no Fly.io!
- ✅ Certificado SSL gratuito

---

## 📝 Checklist de Deploy

- [ ] `fly auth login` feito
- [ ] Secrets configurados (`fly secrets set ...`)
- [ ] Banco de dados acessível
- [ ] R2 configurado
- [ ] CORS configurado para domínio de produção
- [ ] `fly deploy` executado
- [ ] Aplicação funcionando (`fly open`)
- [ ] Logs sem erros (`fly logs`)
- [ ] Endpoints testados (Postman/Insomnia)

---

## 🌍 URL da Aplicação

Após o deploy:
```
https://expo-tv-backend.fly.dev
```

Documentação automática:
```
https://expo-tv-backend.fly.dev/docs
```

---

## 📱 Conectar Frontend

No seu frontend, use:
```javascript
const API_URL = 'https://expo-tv-backend.fly.dev';
```

---

## 🔄 CI/CD (Opcional)

### GitHub Actions

Crie `.github/workflows/deploy.yml`:
```yaml
name: Deploy to Fly.io

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: superfly/flyctl-actions/setup-flyctl@master
      - run: flyctl deploy --remote-only
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
```

---

## 📞 Suporte

- Documentação: https://fly.io/docs
- Comunidade: https://community.fly.io
- Status: https://status.fly.io

---

**Pronto para deploy!** 🚀

```bash
fly deploy
```

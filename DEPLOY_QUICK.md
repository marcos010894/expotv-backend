# 🚀 Deploy Rápido - Fly.io

## Comandos Essenciais

```bash
# 1. Instalar Fly CLI (se ainda não tem)
brew install flyctl

# 2. Login
fly auth login

# 3. Configurar secrets (OBRIGATÓRIO antes do primeiro deploy)
fly secrets set SECRET_KEY="sua-chave-super-secreta-aqui"
fly secrets set DATABASE_URL="mysql+pymysql://u441041902_exportv:Mito010894%40%40@193.203.175.53:3306/u441041902_exportv"
fly secrets set R2_ACCOUNT_ID="seu-account-id"
fly secrets set R2_ACCESS_KEY_ID="seu-access-key"
fly secrets set R2_SECRET_ACCESS_KEY="seu-secret-key"
fly secrets set R2_BUCKET_NAME="seu-bucket"
fly secrets set R2_PUBLIC_URL="https://seu-bucket.r2.dev"

# 4. Deploy (usar script ou comando direto)
./deploy.sh
# OU
fly deploy

# 5. Ver logs
fly logs

# 6. Abrir no navegador
fly open
```

---

## ⚠️ IMPORTANTE - Primeira vez

**NÃO use `mise`!** O erro que você teve foi porque o Fly tentou usar mise.

**Solução:** Os arquivos já estão configurados para usar **buildpack** ao invés de mise/Docker:
- ✅ `fly.toml` - Usa `paketobuildpacks/builder:base`
- ✅ `Procfile` - Define comando de start
- ✅ `runtime.txt` - Python 3.13.7
- ✅ `.python-version` - Versão do Python

---

## 📋 Checklist

- [ ] Fly CLI instalado (`brew install flyctl`)
- [ ] Logado (`fly auth login`)
- [ ] Secrets configurados (ver comando acima)
- [ ] Executar: `fly deploy`
- [ ] Verificar logs: `fly logs`
- [ ] Testar: `fly open /docs`

---

## 🐛 Se der erro

```bash
# Ver logs detalhados
fly logs

# Rebuild sem cache
fly deploy --no-cache

# Ver status
fly status

# SSH na máquina (debug avançado)
fly ssh console
```

---

## 🔄 Atualizar depois

```bash
# Só fazer commit e deploy
git add .
git commit -m "Atualização"
fly deploy
```

---

## 💡 Dica

Use o script facilitador:
```bash
./deploy.sh
```

Ele checa tudo automaticamente! 🎯

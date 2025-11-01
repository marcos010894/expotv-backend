# ✅ Configuração Concluída - EXPO TV Backend

## 📋 Arquivos Criados

### 1. `.env` (Arquivo de Produção)
**Localização:** `/Users/marcospaulomachadoazevedo/Documents/EXPO-TV/BACKEND/.env`

**✅ Configurações incluídas:**

#### 🗄️ Banco de Dados
- **Host:** 193.203.175.53:3306
- **Database:** u441041902_exportv
- **Usuário:** u441041902_exportv
- **Senha:** Mito010894@@

#### 📧 Email SMTP (Gmail)
- **Host:** smtp.gmail.com:587
- **Email:** dev@salexpress.com.br
- **Senha de App:** hypu vaxf cpym dsfs
- **Nome Remetente:** EXPO TV - Sal Express

#### 🌐 Aplicação
- **Frontend URL:** https://expotv.com.br
- **Ambiente:** production

**⚠️ IMPORTANTE:**
- ✅ Arquivo `.env` já está no `.gitignore`
- ✅ Não será commitado no Git
- ✅ Senha de app do Gmail configurada
- ✅ Pronto para uso em produção

---

### 2. `.env.example` (Documentação)

Arquivo de exemplo com instruções.

---

### 3. `test_email.py` (Script de Teste)
Script para testar envio de emails.

**Como usar:**
```bash
python tests/test_email.py
```

Solicita um email de destino e envia 2 emails de teste:
1. Email de recuperação de senha
2. Email de confirmação de alteração

---

## 🔧 Serviços Atualizados

### `app/email_service.py`
**Atualizado para:**
- ✅ Carregar variáveis do `.env` automaticamente
- ✅ Usar credenciais do email dev@salexpress.com.br
- ✅ Funcionar em desenvolvimento E produção

**Configurações padrão (fallback):**
```python
SMTP_USER = "dev@salexpress.com.br"
SMTP_PASSWORD = "hypu vaxf cpym dsfs"
FROM_NAME = "EXPO TV - Sal Express"
```

---

## 🚀 Como Usar

### 1. Desenvolvimento Local

```bash
# 1. Ativar ambiente virtual
source .venv/bin/activate

# 2. O .env será carregado automaticamente
uvicorn app.main:app --reload

# 3. Testar email
python test_email.py
```

### 2. Deploy no Fly.io

```bash
# Configurar secrets (substituir credenciais do .env)
fly secrets set SMTP_HOST=smtp.gmail.com
fly secrets set SMTP_PORT=587
fly secrets set SMTP_USER=dev@salexpress.com.br
fly secrets set SMTP_PASSWORD="hypu vaxf cpym dsfs"
fly secrets set FROM_EMAIL=dev@salexpress.com.br
fly secrets set FROM_NAME="EXPO TV - Sal Express"
fly secrets set FRONTEND_URL=https://expotv.com.br
fly secrets set ENV=production

# Deploy
fly deploy
```

---

## 📧 Configurações do Email

### Credenciais Configuradas

**Email de Envio:**
```
Email: dev@salexpress.com.br
Nome: EXPO TV - Sal Express
```

**Configuração SMTP:**
```
Host: smtp.gmail.com
Porta: 587 (STARTTLS)
Senha de App: hypu vaxf cpym dsfs
```

### Funcionalidades Disponíveis

1. **Recuperação de Senha**
   - Endpoint: `POST /forgot-password`
   - Envia email com token de reset
   - Template HTML profissional

2. **Confirmação de Alteração**
   - Disparado ao resetar senha
   - Notifica usuário sobre mudança

### Templates de Email

Os emails incluem:
- ✅ Design HTML responsivo
- ✅ Versão texto (fallback)
- ✅ Logo/branding "EXPO TV"
- ✅ Links clicáveis para reset
- ✅ Instruções claras

---

## 🧪 Testar Envio de Email

### Opção 1: Script de Teste

```bash
python test_email.py
```

**O que faz:**
1. Mostra configurações SMTP
2. Pede email de destino
3. Envia 2 emails de teste
4. Mostra resultado

**Exemplo de uso:**
```bash
$ python test_email.py
📧 Teste de Envio de Email - EXPO TV
🔧 Configurações SMTP:
  Host: smtp.gmail.com
  Port: 587
  User: dev@salexpress.com.br
  From: dev@salexpress.com.br
  Nome: EXPO TV - Sal Express

📨 Digite o email de destino para teste: seu-email@gmail.com

✅ Email de recuperação enviado com sucesso!
✅ Email de confirmação enviado com sucesso!
```

### Opção 2: Via API

```bash
# Testar forgot-password
curl -X POST http://localhost:8000/forgot-password \
  -H "Content-Type: application/json" \
  -d '{"email": "seu-email@example.com"}'
```

---

## 📊 Variáveis de Ambiente

### Arquivo `.env` Atual

```bash
# Banco de Dados
DB_USER=u441041902_exportv
DB_PASSWORD=Mito010894@@
DB_HOST=193.203.175.53
DB_PORT=3306
DB_NAME=u441041902_exportv

# Email SMTP
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@salexpress.com.br
SMTP_PASSWORD=hypu vaxf cpym dsfs
FROM_EMAIL=dev@salexpress.com.br
FROM_NAME=EXPO TV - Sal Express

# Aplicação
FRONTEND_URL=https://expotv.com.br
ENV=production
```

### Como Atualizar

1. **Desenvolvimento:** Edite `.env` diretamente
2. **Produção (Fly.io):** Use `fly secrets set`

---

## ✅ Checklist de Configuração

- [x] `.env` criado com credenciais reais
- [x] `.env` está no `.gitignore`
- [x] Email SMTP configurado (Gmail)
- [x] Senha de app do Gmail configurada
- [x] `app/email_service.py` atualizado
- [x] `python-dotenv` instalado
- [x] `requirements.txt` atualizado
- [x] Script de teste criado (`test_email.py`)
- [x] `.env.example` documentado

---

## 🆘 Troubleshooting

### Email não está sendo enviado

**1. Verificar configurações:**
```bash
cat .env | grep SMTP
```

**2. Testar script:**
```bash
python test_email.py
```

**3. Verificar logs do servidor:**
```bash
# Deve mostrar:
✅ Email enviado para usuario@example.com
# Ou:
⚠️ SMTP não configurado. Email não será enviado.
```

### Erro: "SMTP authentication failed"

**Possíveis causas:**
- Senha de app incorreta
- Verificação em 2 etapas não ativada
- Email bloqueado pelo Gmail

**Solução:**
1. Verificar senha em `.env`
2. Criar nova senha de app: https://myaccount.google.com/apppasswords
3. Atualizar `.env` com nova senha

### Email vai para SPAM

**Solução:**
- Configure SPF, DKIM, DMARC no domínio salexpress.com.br
- Use email verificado pelo Gmail
- Adicione remetente aos contatos

---

## 📞 Suporte

- **Configuração:** `.env`
- **Serviço de Email:** `app/email_service.py`
- **Teste:** `test_email.py`
- **Documentação:** `PASSWORD_RESET_GUIDE.md`

**Status:** ✅ Configurado e Pronto para Uso  
**Email Configurado:** dev@salexpress.com.br  
**Data:** 27/10/2025

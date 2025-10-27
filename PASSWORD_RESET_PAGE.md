# 🔐 Página de Redefinição de Senha

## 📋 Visão Geral

O sistema agora possui uma página HTML completa hospedada no próprio backend para redefinir senhas. O usuário recebe um email com link direto para a página.

---

## 🔄 Fluxo Completo

### 1. Usuário Esquece a Senha
```
Usuário → Frontend → POST /forgot-password
```

### 2. Sistema Envia Email
```
Backend → Gmail SMTP → Email do Usuário
```

**Email contém:**
- Link: `https://expotv-backend.fly.dev/reset-password-page?token={TOKEN}`
- Token único válido por 1 hora
- Design profissional com botão de ação

### 3. Usuário Clica no Link
```
https://expotv-backend.fly.dev/reset-password-page?token=abc123xyz
```

**O que acontece:**
- Abre página HTML bonita no servidor
- Token é extraído da URL automaticamente
- Formulário de nova senha é exibido

### 4. Usuário Define Nova Senha
```
Formulário → POST /reset-password → Senha Atualizada
```

**Validações em tempo real:**
- ✓ Mínimo 6 caracteres
- ✓ Senhas devem ser iguais
- ✓ Token válido e não expirado

### 5. Sucesso!
```
✓ Senha atualizada
✓ Token invalidado
✓ Email de confirmação enviado
✓ Redirecionamento para o site (3 segundos)
```

---

## 🎨 Página de Reset

### URL de Acesso
```
https://expotv-backend.fly.dev/reset-password-page?token={TOKEN}
```

### Características
- **Design Moderno:** Gradiente roxo/azul, responsivo
- **Validação em Tempo Real:** Feedback visual imediato
- **Segurança:** Token na URL, validação no backend
- **UX Profissional:** Loading states, mensagens de sucesso/erro
- **Mobile-First:** Funciona perfeitamente em celulares

### Elementos da Página

#### 1. Header
```
📺 EXPO TV
Sal Express
```

#### 2. Formulário
```
┌─────────────────────────────────┐
│ Nova Senha                      │
│ ┌─────────────────────────────┐ │
│ │ ●●●●●●●●                    │ │
│ └─────────────────────────────┘ │
│                                 │
│ Confirmar Senha                 │
│ ┌─────────────────────────────┐ │
│ │ ●●●●●●●●                    │ │
│ └─────────────────────────────┘ │
└─────────────────────────────────┘
```

#### 3. Validação Visual
```
A senha deve conter:
✓ Mínimo de 6 caracteres
✓ As senhas devem ser iguais
```

#### 4. Botão de Ação
```
┌─────────────────────────────────┐
│     Redefinir Senha             │
└─────────────────────────────────┘
```

---

## 🔧 Configuração

### Variáveis de Ambiente

**.env**
```bash
# URL do backend (para a página de reset)
BACKEND_URL=https://expotv-backend.fly.dev

# URL do frontend (para redirecionamento após sucesso)
FRONTEND_URL=https://expotv.com.br

# Email SMTP (para enviar o link)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=dev@salexpress.com.br
SMTP_PASSWORD=hypu vaxf cpym dsfs
FROM_EMAIL=dev@salexpress.com.br
FROM_NAME=EXPO TV - Sal Express
```

### Desenvolvimento Local

```bash
# .env local
BACKEND_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000
```

**Testar localmente:**
```
http://localhost:8000/reset-password-page?token=test123
```

---

## 📁 Arquivos Envolvidos

### 1. Página HTML
```
📁 static/reset-password.html
```
- Interface completa
- JavaScript para validação
- CSS responsivo
- Integração com API

### 2. Endpoint HTML
```python
# app/main.py

@app.get("/reset-password-page")
async def reset_password_page():
    """Serve a página HTML de reset"""
    # Retorna static/reset-password.html
```

### 3. Email Service
```python
# app/email_service.py

def send_password_reset_email():
    # Link: {BACKEND_URL}/reset-password-page?token={token}
```

### 4. API de Reset
```python
# app/endpoints/auth.py

@router.post("/reset-password")
async def reset_password():
    # Valida token e atualiza senha
```

---

## 🧪 Teste Manual

### 1. Solicitar Reset
```bash
curl -X POST "https://expotv-backend.fly.dev/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{"email": "seu-email@gmail.com"}'
```

### 2. Verificar Email
- Abrir email recebido
- Clicar no botão "Redefinir Senha"

### 3. Preencher Formulário
- Digite nova senha (mínimo 6 caracteres)
- Confirme a senha
- Clique em "Redefinir Senha"

### 4. Verificar Sucesso
- ✓ aparece na tela
- Mensagem de sucesso
- Redirecionamento automático em 3 segundos

### 5. Testar Login
```bash
curl -X POST "https://expotv-backend.fly.dev/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=seu-email@gmail.com&password=nova-senha"
```

---

## 🔒 Segurança

### Token Único
- Gerado com `secrets.token_urlsafe(32)`
- 43 caracteres aleatórios
- Criptograficamente seguro

### Expiração
- Válido por **1 hora** apenas
- Verificado no backend
- Invalidado após uso

### Proteção
- ✓ Token não pode ser reutilizado
- ✓ Senha hasheada com bcrypt
- ✓ Email de confirmação enviado
- ✓ HTTPS obrigatório em produção

---

## 🎯 Endpoints Relacionados

### POST /forgot-password
**Solicita reset de senha**
```json
{
  "email": "usuario@email.com"
}
```
**Resposta:** Sempre sucesso (segurança)

### GET /reset-password-page
**Serve página HTML**
```
URL: /reset-password-page?token={TOKEN}
```
**Resposta:** HTML completo

### POST /reset-password
**Atualiza a senha**
```json
{
  "token": "abc123xyz...",
  "new_password": "nova-senha-segura"
}
```
**Resposta:** Sucesso ou erro

---

## 📱 Responsividade

### Desktop (> 768px)
```
┌────────────────────────────────────────┐
│                                        │
│         📺 EXPO TV                     │
│         Sal Express                    │
│                                        │
│    ┌─────────────────────────┐        │
│    │  Redefinir Senha        │        │
│    │  Digite sua nova senha  │        │
│    │                         │        │
│    │  [Nova Senha]           │        │
│    │  [Confirmar Senha]      │        │
│    │                         │        │
│    │  [Redefinir Senha]      │        │
│    └─────────────────────────┘        │
│                                        │
└────────────────────────────────────────┘
```

### Mobile (< 768px)
```
┌──────────────────────┐
│                      │
│   📺 EXPO TV         │
│   Sal Express        │
│                      │
│ ┌──────────────────┐ │
│ │ Redefinir Senha  │ │
│ │                  │ │
│ │ [Nova Senha]     │ │
│ │ [Confirmar]      │ │
│ │                  │ │
│ │ [Redefinir]      │ │
│ └──────────────────┘ │
│                      │
└──────────────────────┘
```

---

## 🚀 Deploy

### Fly.io (Produção)
```bash
# 1. Deploy do código
fly deploy

# 2. Configurar variáveis
fly secrets set BACKEND_URL=https://expotv-backend.fly.dev
fly secrets set FRONTEND_URL=https://expotv.com.br

# 3. Testar
curl https://expotv-backend.fly.dev/reset-password-page?token=test
```

### Verificar
```bash
# Health check
curl https://expotv-backend.fly.dev/health

# Teste da página (deve retornar HTML)
curl https://expotv-backend.fly.dev/reset-password-page
```

---

## 📊 Estatísticas de Uso

Para monitorar o uso do sistema de reset:

```sql
-- Tokens gerados nas últimas 24h
SELECT COUNT(*) 
FROM user 
WHERE reset_token IS NOT NULL 
  AND reset_token_expires > NOW();

-- Tokens expirados (limpeza)
UPDATE user 
SET reset_token = NULL, reset_token_expires = NULL 
WHERE reset_token_expires < NOW();
```

---

## 🎨 Personalização

### Alterar Cores
Edite `static/reset-password.html`:
```css
/* Gradiente do fundo */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);

/* Cor primária dos botões */
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```

### Alterar Logo
```html
<div class="logo">
    <h1>📺 EXPO TV</h1>
    <p>Sal Express</p>
</div>
```

### Alterar URL de Redirecionamento
```javascript
setTimeout(() => {
    window.location.href = 'https://expotv.com.br';
}, 3000);
```

---

## ✅ Checklist de Implementação

- [x] Criar página HTML em `/static/reset-password.html`
- [x] Adicionar endpoint `GET /reset-password-page` no main.py
- [x] Atualizar email_service.py com novo link
- [x] Adicionar BACKEND_URL no .env.example
- [x] Testar validação de senha
- [x] Testar integração com API
- [x] Testar responsividade mobile
- [x] Documentar sistema completo

---

## 🔗 Links Úteis

- **Página de Reset:** https://expotv-backend.fly.dev/reset-password-page
- **API Docs:** https://expotv-backend.fly.dev/docs
- **Health Check:** https://expotv-backend.fly.dev/health
- **Frontend:** https://expotv.com.br

---

## 💡 Dicas

1. **Desenvolvimento Local:** Use `http://localhost:8000/reset-password-page?token=test`
2. **Email de Teste:** Configure SMTP_USER e SMTP_PASSWORD no .env
3. **Validação:** A página valida em tempo real (6+ caracteres, senhas iguais)
4. **Expiração:** Tokens expiram em 1 hora automaticamente
5. **Segurança:** Sempre use HTTPS em produção

---

**Criado em:** 27 de outubro de 2025  
**Sistema:** EXPO TV - Recuperação de Senha  
**Versão:** 1.0.0

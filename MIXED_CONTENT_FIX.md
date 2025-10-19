# ⚠️ MIXED CONTENT - Solução

## 🔍 Problema

**Erro:** "bloqueado: mixed-content"

**Causa:** Frontend em HTTPS tentando chamar API em HTTP

## ✅ Solução

### No Frontend

Use **HTTPS** na URL da API:

```javascript
// ❌ ERRADO - HTTP
const API_URL = 'http://expotv-backend.fly.dev';

// ✅ CERTO - HTTPS
const API_URL = 'https://expotv-backend.fly.dev';
```

---

## 📱 Configuração por Ambiente

### React / Next.js

```javascript
// .env.production
NEXT_PUBLIC_API_URL=https://expotv-backend.fly.dev

// .env.development
NEXT_PUBLIC_API_URL=http://localhost:8000
```

```javascript
// config.js
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
```

### Vue.js

```javascript
// .env.production
VUE_APP_API_URL=https://expotv-backend.fly.dev

// .env.development
VUE_APP_API_URL=http://localhost:8000
```

```javascript
// config.js
export const API_URL = process.env.VUE_APP_API_URL || 'http://localhost:8000';
```

### JavaScript Puro

```javascript
// config.js
const isDevelopment = window.location.hostname === 'localhost';

export const API_URL = isDevelopment 
  ? 'http://localhost:8000'
  : 'https://expotv-backend.fly.dev';
```

---

## 🔧 Verificar se HTTPS está funcionando

### 1. Testar no navegador
```
https://expotv-backend.fly.dev/health
```

Deve retornar:
```json
{
  "status": "healthy",
  "service": "EXPO-TV API",
  "version": "1.0.0"
}
```

### 2. Testar com curl
```bash
curl https://expotv-backend.fly.dev/health
```

### 3. Ver certificado SSL
```bash
curl -vI https://expotv-backend.fly.dev/health 2>&1 | grep "SSL certificate"
```

---

## 🌐 URLs Corretas da API

### Produção (Fly.io)
```
Base URL: https://expotv-backend.fly.dev
Docs: https://expotv-backend.fly.dev/docs
Health: https://expotv-backend.fly.dev/health
Login: https://expotv-backend.fly.dev/login
```

### Desenvolvimento (Local)
```
Base URL: http://localhost:8000
Docs: http://localhost:8000/docs
Health: http://localhost:8000/health
Login: http://localhost:8000/login
```

---

## 🔒 CORS - Se ainda der erro

Se mesmo com HTTPS der erro de CORS, adicione o domínio do frontend no backend:

```python
# app/main.py

origins = [
    "https://seu-frontend.vercel.app",
    "https://seu-frontend.com",
    "http://localhost:3000",  # Desenvolvimento
    "http://localhost:5173",  # Vite
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Mude de ["*"] para lista específica
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## 📋 Checklist

- [ ] Frontend usa `https://` na URL da API
- [ ] API responde em `https://expotv-backend.fly.dev`
- [ ] Certificado SSL válido (automático no Fly.io)
- [ ] CORS configurado corretamente
- [ ] Testar em produção (não localhost)

---

## 🐛 Debug

### Ver requisições no DevTools

1. Abrir DevTools (F12)
2. Aba **Network**
3. Fazer requisição
4. Ver se está usando HTTP ou HTTPS
5. Ver mensagem de erro completa

### Console do navegador

```javascript
console.log('API URL:', API_URL);
```

Deve mostrar `https://...` em produção!

---

## 💡 Dica Rápida

**Ambiente automático:**

```javascript
// Detecta automaticamente
const API_URL = window.location.protocol === 'https:' 
  ? 'https://expotv-backend.fly.dev'
  : 'http://localhost:8000';
```

**Ou usando hostname:**

```javascript
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'
  : 'https://expotv-backend.fly.dev';
```

---

## ✅ Resumo

1. ✅ Backend já está configurado para HTTPS (Fly.io automático)
2. ✅ `force_https = true` no `fly.toml`
3. ⚠️ Frontend precisa usar `https://` na URL da API
4. ⚠️ Não usar `http://` em produção

**A solução é trocar HTTP por HTTPS no frontend!** 🎯

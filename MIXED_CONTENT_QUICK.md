# 🚨 SOLUÇÃO RÁPIDA - Mixed Content

## O Problema

**Erro:** "bloqueado: mixed-content"

**Causa:** Frontend em HTTPS tentando chamar API em HTTP

## A Solução (3 passos)

### 1️⃣ No Frontend - Trocar HTTP por HTTPS

```javascript
// ❌ ERRADO
const API_URL = 'http://expotv-backend.fly.dev';

// ✅ CERTO
const API_URL = 'https://expotv-backend.fly.dev';
```

### 2️⃣ Detecção Automática (Recomendado)

```javascript
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'           // Local
  : 'https://expotv-backend.fly.dev';  // Produção
```

### 3️⃣ Testar

```bash
# 1. Abrir DevTools (F12)
# 2. Aba Console
# 3. Verificar
console.log('API URL:', API_URL);

# Deve mostrar: https://expotv-backend.fly.dev
```

---

## 📋 URLs Corretas

| Ambiente | URL |
|----------|-----|
| **Produção** | `https://expotv-backend.fly.dev` |
| **Docs** | `https://expotv-backend.fly.dev/docs` |
| **Health** | `https://expotv-backend.fly.dev/health` |
| **Local** | `http://localhost:8000` |

---

## ✅ Checklist

- [ ] Frontend usa `https://` (não `http://`)
- [ ] Testar em: `https://expotv-backend.fly.dev/health`
- [ ] DevTools não mostra erro de mixed-content
- [ ] Requisições funcionam em produção

---

## 📁 Arquivos de Ajuda

- `MIXED_CONTENT_FIX.md` - Explicação completa
- `frontend-config-example.js` - Código pronto para copiar
- `GUIA_API.md` - URLs atualizadas

---

**Pronto! O backend já está em HTTPS. Só falta atualizar o frontend!** 🎯

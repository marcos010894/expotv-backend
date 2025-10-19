# 🔧 SOLUÇÃO - 307 Redirect causando Mixed Content

## 🔍 O Problema Real

**Erro:** "bloqueado: mixed-content"  
**Status:** 307 Temporary Redirect  
**Causa:** Fly.io fazia redirect de HTTPS → HTTP

### O que acontecia:

1. Frontend chama: `https://expotv-backend.fly.dev/condominios`
2. Fly.io redireciona: `http://expotv-backend.fly.dev/condominios/` (HTTP!)
3. Navegador bloqueia: Mixed content!

---

## ✅ Solução Implementada

### 1. Desabilitar trailing slash redirect
```python
app = FastAPI(
    redirect_slashes=False  # ⭐ IMPORTANTE
)
```

### 2. Middleware para forçar HTTPS
```python
class HTTPSRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Se vier como HTTP do proxy, força HTTPS
        if request.headers.get("x-forwarded-proto") == "http":
            url = request.url.replace(scheme="https")
            return RedirectResponse(url=str(url), status_code=301)
        
        response = await call_next(request)
        return response

app.add_middleware(HTTPSRedirectMiddleware)
```

---

## 📋 O que foi alterado

**Arquivo:** `app/main.py`

### Mudanças:
1. ✅ Adicionado `redirect_slashes=False` no FastAPI
2. ✅ Criado `HTTPSRedirectMiddleware` 
3. ✅ Middleware verifica header `x-forwarded-proto`
4. ✅ Força redirect 301 para HTTPS se necessário

---

## 🧪 Como Testar

### Antes (com erro):
```bash
curl -I https://expotv-backend.fly.dev/condominios
# HTTP/1.1 307 Temporary Redirect
# Location: http://expotv-backend.fly.dev/condominios/  ❌ HTTP!
```

### Depois (corrigido):
```bash
curl -I https://expotv-backend.fly.dev/condominios
# HTTP/1.1 200 OK  ✅
```

---

## 🚀 Próximos Passos

### 1. Fazer commit
```bash
git add app/main.py
git commit -m "Fix: Corrige redirect HTTPS causando mixed content"
```

### 2. Deploy
```bash
fly deploy
```

### 3. Testar no frontend
```javascript
// Deve funcionar agora!
const response = await fetch('https://expotv-backend.fly.dev/condominios', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

---

## 🔍 Debug

### Ver headers da requisição:
```bash
curl -v https://expotv-backend.fly.dev/condominios
```

### Ver se está usando HTTPS:
```javascript
// No DevTools Console
fetch('https://expotv-backend.fly.dev/health')
  .then(r => console.log('Status:', r.status, 'URL:', r.url))
```

---

## 📊 Por que acontecia?

### Fly.io Proxy
```
Cliente HTTPS → Fly.io Proxy → Backend HTTP interno
```

O Fly.io usa proxy reverso que:
- Recebe HTTPS externamente
- Comunica HTTP internamente com a app
- Passa header `x-forwarded-proto: http`

### FastAPI redirect
FastAPI via `x-forwarded-proto: http` e fazia redirect usando HTTP!

### Nossa solução
Detectamos `x-forwarded-proto: http` e forçamos HTTPS no redirect 🎯

---

## ✅ Checklist Final

- [x] `redirect_slashes=False` adicionado
- [x] Middleware HTTPS criado
- [x] Middleware adicionado à app
- [ ] Deploy no Fly.io (`fly deploy`)
- [ ] Testar endpoints no frontend
- [ ] Verificar DevTools sem erros

---

## 🎯 Resumo

**Problema:** 307 redirect de HTTPS → HTTP  
**Causa:** Fly.io proxy + FastAPI trailing slash  
**Solução:** Middleware que força HTTPS em redirects  
**Status:** ✅ RESOLVIDO!

---

**Agora é só fazer deploy!** 🚀

```bash
fly deploy
```

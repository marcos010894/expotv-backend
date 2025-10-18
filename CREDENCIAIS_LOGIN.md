# 🔐 CREDENCIAIS DE LOGIN - EXPO-TV

## ✅ **PROBLEMA RESOLVIDO!**

O sistema de login está funcionando corretamente. O problema era que as senhas não estavam hasheadas corretamente.

## 📋 **Credenciais dos Usuários**

### 👑 **Administrador Master**
- **Email**: `admin@expo-tv.com`
- **Senha**: `admin123` (padrão)
- **Tipo**: ADM

### 👤 **Marcos Machado**
- **Email**: `marcosmachadodev@gmail.com`
- **Senha**: `Mito010894@@`
- **Tipo**: SINDICO

### 👤 **Kelli Vitoria**
- **Email**: `contato@eaglesoftware.com`
- **Senha**: `123456` (padrão)
- **Tipo**: SINDICO

## 🧪 **Como Testar o Login**

### 1. **Via Swagger UI** (Recomendado)
- Acesse: http://localhost:8000/docs
- Vá na seção "Autenticação"
- Use o endpoint **POST /login**

### 2. **Exemplo JSON para teste:**
```json
{
    "email": "marcosmachadodev@gmail.com",
    "senha": "Mito010894@@"
}
```

### 3. **Resposta esperada:**
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 2,
    "user_name": "Marcos machado",
    "user_type": "SINDICO"
}
```

## 🔧 **Comandos Úteis**

### Iniciar servidor:
```bash
cd /Users/marcospaulomachadoazevedo/Documents/EXPO-TV/BACKEND
.venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Testar login via cURL:
```bash
curl -X POST "http://localhost:8000/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "marcosmachadodev@gmail.com", "senha": "Mito010894@@"}'
```

## ✅ **Status do Sistema**

- ✅ Senhas hasheadas corretamente
- ✅ Login funcionando
- ✅ Tokens JWT sendo gerados
- ✅ Autenticação protegendo rotas
- ✅ CORS configurado
- ✅ Upload de imagens funcionando
- ✅ CRUD completo para todos os módulos

## 🎯 **Próximos Passos**

1. **Testar no frontend** com as credenciais corretas
2. **Criar mais usuários** se necessário via endpoint `/register`
3. **Configurar env variables** para produção
4. **Deploy** quando estiver pronto

---

**🚀 Sistema pronto para uso!**

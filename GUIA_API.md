# Guia de Consumo da API - Expo TV

## 🔐 Autenticação

### Como funciona
1. Faça login uma vez e receba um token
2. Guarde o token no frontend (localStorage/sessionStorage)
3. Envie o token em todas as requisições protegidas
4. Token válido por **30 dias**

### Endpoint de Login
```
POST /login
Content-Type: application/x-www-form-urlencoded

username=usuario@email.com&password=senha123
```

**Resposta:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 43200,
  "user": {
    "id": 1,
    "nome": "Nome do Usuário",
    "email": "usuario@email.com",
    "user_type": "sindico"
  },
  "condominios": [...]
}
```

### Como usar o token nas requisições
Adicione o header em **todas as requisições protegidas**:
```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

---

## 📡 Endpoints Principais

### Autenticação

#### Verificar Token
```
POST /verify-token
Authorization: Bearer {token}
```

#### Dados do Usuário Logado
```
GET /me
Authorization: Bearer {token}
```

---

### Avisos

#### Listar Avisos
```
GET /avisos
GET /avisos?condominio_id=1
Authorization: Bearer {token}
```

#### Buscar Aviso por ID
```
GET /avisos/{id}
Authorization: Bearer {token}
```

#### Criar Aviso
```
POST /avisos
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- titulo (obrigatório)
- condominio_id (obrigatório)
- mensagem (opcional)
- imagem (opcional, arquivo)
```

#### Atualizar Aviso
```
PUT /avisos/{id}
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- titulo (opcional)
- mensagem (opcional)
- imagem (opcional, arquivo)
```

#### Deletar Aviso
```
DELETE /avisos/{id}
Authorization: Bearer {token}
```

---

### Anúncios

#### Listar Anúncios
```
GET /anuncios
GET /anuncios?condominio_id=1
Authorization: Bearer {token}
```

#### Criar Anúncio
```
POST /anuncios
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- titulo (obrigatório)
- descricao (obrigatório)
- condominio_id (obrigatório)
- imagem (opcional, arquivo)
```

#### Atualizar Anúncio
```
PUT /anuncios/{id}
Content-Type: multipart/form-data
Authorization: Bearer {token}

Form Data:
- titulo (opcional)
- descricao (opcional)
- imagem (opcional, arquivo)
```

#### Deletar Anúncio
```
DELETE /anuncios/{id}
Authorization: Bearer {token}
```

---

### Condominios

#### Listar Condominios
```
GET /condominios
Authorization: Bearer {token}
```

#### Buscar Condominio por ID
```
GET /condominios/{id}
Authorization: Bearer {token}
```

#### Criar Condominio
```
POST /condominios
Content-Type: application/json
Authorization: Bearer {token}

{
  "nome": "Nome do Condomínio",
  "endereco": "Rua Exemplo, 123",
  "sindico_id": 1
}
```

#### Atualizar Condominio
```
PUT /condominios/{id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "nome": "Novo Nome",
  "endereco": "Novo Endereço"
}
```

---

### TVs

#### Listar TVs
```
GET /tvs
GET /tvs?condominio_id=1
Authorization: Bearer {token}
```

#### Criar TV
```
POST /tvs
Content-Type: application/json
Authorization: Bearer {token}

{
  "nome": "TV Portaria",
  "condominio_id": 1,
  "localizacao": "Portaria Principal"
}
```

#### Atualizar TV
```
PUT /tvs/{id}
Content-Type: application/json
Authorization: Bearer {token}

{
  "nome": "Novo Nome",
  "localizacao": "Nova Localização"
}
```

---

## 🔄 Fluxo de Trabalho

### 1. Autenticação Inicial
```
POST /login → Recebe access_token → Armazena no frontend
```

### 2. Requisições Protegidas
```
Adiciona header: Authorization: Bearer {access_token}
```

### 3. Tratamento de Erro 401
```
Se receber 401 → Token expirado → Redirecionar para login
```

### 4. Logout
```
Remove token do armazenamento local
```

---

## 📋 Estrutura de Dados

### Aviso
```json
{
  "id": 1,
  "titulo": "Título do Aviso",
  "mensagem": "Mensagem opcional",
  "imagem_url": "https://...",
  "condominio_id": 1,
  "data_criacao": "2025-10-18T10:30:00",
  "data_atualizacao": "2025-10-18T10:30:00"
}
```

### Anúncio
```json
{
  "id": 1,
  "titulo": "Título do Anúncio",
  "descricao": "Descrição do anúncio",
  "imagem_url": "https://...",
  "condominio_id": 1,
  "data_criacao": "2025-10-18T10:30:00"
}
```

### Condominio
```json
{
  "id": 1,
  "nome": "Condomínio Exemplo",
  "endereco": "Rua Exemplo, 123",
  "sindico_id": 1,
  "data_criacao": "2025-10-18T10:30:00"
}
```

### TV
```json
{
  "id": 1,
  "nome": "TV Portaria",
  "condominio_id": 1,
  "localizacao": "Portaria Principal",
  "ativa": true
}
```

---

## ⚠️ Tratamento de Erros

### Códigos de Status HTTP

| Código | Significado | Ação |
|--------|-------------|------|
| 200 | Sucesso | - |
| 201 | Criado | - |
| 400 | Requisição inválida | Verificar dados enviados |
| 401 | Não autenticado | Fazer login novamente |
| 403 | Sem permissão | Verificar permissões do usuário |
| 404 | Não encontrado | Verificar ID do recurso |
| 422 | Validação falhou | Verificar campos obrigatórios |
| 500 | Erro interno | Contatar suporte |

### Formato de Erro
```json
{
  "detail": "Mensagem de erro descritiva"
}
```

---

## 🔑 Pontos Importantes

### ✅ Fazer
- Armazenar token após login
- Enviar token em requisições protegidas
- Tratar erro 401 (token expirado)
- Usar HTTPS em produção
- Validar campos antes de enviar

### ❌ Não Fazer
- Enviar credenciais em toda requisição
- Armazenar senha no frontend
- Compartilhar token entre dispositivos
- Ignorar erros 401
- Usar HTTP em produção

---

## 🚀 Exemplo de Fluxo Completo

### 1. Login
```
POST /login
→ Recebe: { "access_token": "...", "user": {...} }
→ Armazena token
```

### 2. Criar Aviso
```
POST /avisos
Headers: Authorization: Bearer {token}
Body: FormData com titulo, condominio_id, mensagem?, imagem?
→ Recebe: { "id": 1, "titulo": "...", ... }
```

### 3. Listar Avisos
```
GET /avisos?condominio_id=1
Headers: Authorization: Bearer {token}
→ Recebe: [{ "id": 1, ... }, { "id": 2, ... }]
```

### 4. Atualizar Aviso
```
PUT /avisos/1
Headers: Authorization: Bearer {token}
Body: FormData com campos a atualizar
→ Recebe: { "id": 1, "titulo": "Atualizado", ... }
```

### 5. Deletar Aviso
```
DELETE /avisos/1
Headers: Authorization: Bearer {token}
→ Recebe: { "message": "Aviso deletado com sucesso" }
```

---

## 📞 URLs da API

### 🌐 Produção (Fly.io)
**Base URL:** `https://expotv-backend.fly.dev`

**Documentação Interativa:**
- Swagger UI: `https://expotv-backend.fly.dev/docs`
- ReDoc: `https://expotv-backend.fly.dev/redoc`
- Health Check: `https://expotv-backend.fly.dev/health`

### 💻 Desenvolvimento (Local)
**Base URL:** `http://localhost:8000`

**Documentação Interativa:**
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`
- Health Check: `http://localhost:8000/health`

### ⚠️ IMPORTANTE - Mixed Content
**SEMPRE use HTTPS em produção!**
- ✅ `https://expotv-backend.fly.dev`
- ❌ `http://expotv-backend.fly.dev` (será bloqueado pelo navegador)

**Token:** Válido por 30 dias (43200 minutos)

---

## 🔐 Configuração de Segurança

Para produção, configure as variáveis de ambiente:

```env
SECRET_KEY=sua-chave-secreta-super-segura
ACCESS_TOKEN_EXPIRE_MINUTES=43200
DATABASE_URL=mysql+pymysql://user:pass@host/db
```

Veja `.env.example` para mais detalhes.

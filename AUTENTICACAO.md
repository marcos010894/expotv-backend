# 🔐 Guia de Autenticação - EXPO TV Backend

## 📝 Visão Geral

O sistema usa **JWT (JSON Web Tokens)** para autenticação. Os tokens têm validade de **30 dias** e devem ser enviados no header de todas as requisições protegidas.

## 🚀 Como Fazer Login

### Endpoint: `POST /login`

**Request:**
```json
{
  "email": "usuario@exemplo.com",
  "senha": "senha123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "user_name": "João Silva",
  "user_type": "SINDICO",
  "url_photo": "https://...",
  "condominios_ids": [1, 2, 3],
  "condominios": [
    {
      "id": 1,
      "nome": "Condomínio ABC",
      "localizacao": "São Paulo",
      "cep": "01234-567"
    }
  ],
  "expires_in": 43200
}
```

## 🔑 Como Usar o Token

### 1. **Armazenar o Token**

```javascript
// No localStorage (navegador)
localStorage.setItem('access_token', response.access_token);

// Ou em cookies seguros
document.cookie = `token=${response.access_token}; secure; max-age=2592000`;
```

### 2. **Enviar em Requisições**

Todas as requisições protegidas devem incluir o token no header:

```
Authorization: Bearer {seu_token_aqui}
```

**Exemplo com Fetch:**
```javascript
const token = localStorage.getItem('access_token');

fetch('http://localhost:8000/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
})
.then(response => response.json())
.then(data => console.log(data));
```

**Exemplo com Axios:**
```javascript
import axios from 'axios';

const token = localStorage.getItem('access_token');

axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

// Ou em uma requisição específica:
axios.get('http://localhost:8000/me', {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

## 🛡️ Endpoints de Autenticação

### 1. **Login**
```
POST /login
```
Faz login e retorna o token JWT

### 2. **Verificar Token**
```
POST /verify-token
```
Verifica se um token ainda é válido

### 3. **Dados do Usuário**
```
GET /me
```
Retorna dados do usuário autenticado (requer token)

## 📋 Exemplo Completo de Uso

```javascript
// 1. Fazer Login
async function login(email, senha) {
  const response = await fetch('http://localhost:8000/login', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({ email, senha })
  });
  
  if (!response.ok) {
    throw new Error('Login falhou');
  }
  
  const data = await response.json();
  
  // Salvar token
  localStorage.setItem('access_token', data.access_token);
  localStorage.setItem('user_id', data.user_id);
  localStorage.setItem('user_name', data.user_name);
  
  return data;
}

// 2. Criar função auxiliar para requisições autenticadas
async function fetchWithAuth(url, options = {}) {
  const token = localStorage.getItem('access_token');
  
  if (!token) {
    throw new Error('Usuário não autenticado');
  }
  
  const response = await fetch(url, {
    ...options,
    headers: {
      ...options.headers,
      'Authorization': `Bearer ${token}`
    }
  });
  
  if (response.status === 401) {
    // Token expirado, redirecionar para login
    localStorage.removeItem('access_token');
    window.location.href = '/login';
    throw new Error('Token expirado');
  }
  
  return response;
}

// 3. Usar em requisições
async function getMeusDados() {
  const response = await fetchWithAuth('http://localhost:8000/me');
  return await response.json();
}

async function criarAviso(dados) {
  const formData = new FormData();
  formData.append('nome', dados.nome);
  formData.append('condominios_ids', dados.condominios_ids);
  // ... outros campos
  
  const response = await fetchWithAuth('http://localhost:8000/avisos/', {
    method: 'POST',
    body: formData
  });
  
  return await response.json();
}
```

## 🔒 Rotas Protegidas

As seguintes rotas **REQUEREM** autenticação (token JWT):

- `GET /me` - Dados do usuário
- `POST /avisos/` - Criar aviso
- `PUT /avisos/{id}` - Atualizar aviso
- `DELETE /avisos/{id}` - Deletar aviso
- `POST /anuncios/` - Criar anúncio
- `PUT /users/{id}` - Atualizar usuário
- E outras rotas de modificação de dados

## ⚠️ Tratamento de Erros

### Token Inválido ou Expirado
**Status:** 401 Unauthorized

```json
{
  "detail": "Credenciais inválidas ou token expirado"
}
```

**Ação:** Redirecionar usuário para tela de login

### Token Não Fornecido
**Status:** 403 Forbidden

```json
{
  "detail": "Not authenticated"
}
```

**Ação:** Redirecionar usuário para tela de login

## 🔐 Segurança

### Boas Práticas:

1. ✅ **Nunca** exponha o token em URLs ou logs
2. ✅ Use HTTPS em produção
3. ✅ Armazene tokens em localStorage ou httpOnly cookies
4. ✅ Implemente logout limpando o token do storage
5. ✅ Verifique a validade do token antes de requisições importantes
6. ✅ Implemente refresh automático quando o token expirar

### Logout:

```javascript
function logout() {
  localStorage.removeItem('access_token');
  localStorage.removeItem('user_id');
  localStorage.removeItem('user_name');
  window.location.href = '/login';
}
```

## 🧪 Testando no Postman/Insomnia

1. Faça login no endpoint `/login`
2. Copie o `access_token` da resposta
3. Em outras requisições, adicione no header:
   - **Key:** `Authorization`
   - **Value:** `Bearer {token_copiado}`

## 📞 Suporte

Para dúvidas sobre autenticação, consulte a documentação interativa em:
`http://localhost:8000/docs`

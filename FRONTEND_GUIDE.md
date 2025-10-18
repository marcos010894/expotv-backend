# Guia de Implementação Frontend - Autenticação

## 🎯 Conceito Importante

**NÃO PRECISA ENVIAR O TOKEN CONSTANTEMENTE!**

- Você faz login **1 vez**
- Armazena o token recebido
- Usa esse token em **todas as requisições** que precisam de autenticação
- Token válido por **30 dias**
- Só precisa fazer login novamente quando o token expirar

---

## 📦 1. Estrutura Recomendada

### Criar um serviço de autenticação (`auth.service.js`)

```javascript
// auth.service.js
class AuthService {
  constructor() {
    this.API_URL = 'http://localhost:8000'; // URL da sua API
    this.TOKEN_KEY = 'expo_tv_token';
    this.USER_KEY = 'expo_tv_user';
  }

  // Fazer login e armazenar token
  async login(email, password) {
    try {
      const formData = new URLSearchParams();
      formData.append('username', email); // OAuth2 usa 'username', não 'email'
      formData.append('password', password);

      const response = await fetch(`${this.API_URL}/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro ao fazer login');
      }

      const data = await response.json();
      
      // Armazenar token e dados do usuário
      this.setToken(data.access_token);
      this.setUser(data.user);
      
      return data;
    } catch (error) {
      console.error('Erro no login:', error);
      throw error;
    }
  }

  // Fazer logout
  logout() {
    localStorage.removeItem(this.TOKEN_KEY);
    localStorage.removeItem(this.USER_KEY);
  }

  // Armazenar token
  setToken(token) {
    localStorage.setItem(this.TOKEN_KEY, token);
  }

  // Recuperar token
  getToken() {
    return localStorage.getItem(this.TOKEN_KEY);
  }

  // Armazenar usuário
  setUser(user) {
    localStorage.setItem(this.USER_KEY, JSON.stringify(user));
  }

  // Recuperar usuário
  getUser() {
    const user = localStorage.getItem(this.USER_KEY);
    return user ? JSON.parse(user) : null;
  }

  // Verificar se está autenticado
  isAuthenticated() {
    return !!this.getToken();
  }

  // Verificar se o token ainda é válido
  async verifyToken() {
    const token = this.getToken();
    if (!token) return false;

    try {
      const response = await fetch(`${this.API_URL}/verify-token`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        this.logout(); // Token inválido, fazer logout
        return false;
      }

      return true;
    } catch (error) {
      console.error('Erro ao verificar token:', error);
      this.logout();
      return false;
    }
  }

  // Obter dados do usuário autenticado
  async getCurrentUser() {
    const token = this.getToken();
    if (!token) throw new Error('Não autenticado');

    try {
      const response = await fetch(`${this.API_URL}/me`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Erro ao buscar dados do usuário');
      }

      const data = await response.json();
      this.setUser(data.user); // Atualizar dados locais
      return data;
    } catch (error) {
      console.error('Erro ao buscar usuário:', error);
      throw error;
    }
  }
}

// Exportar instância única (Singleton)
const authService = new AuthService();
export default authService;
```

---

## 📡 2. Criar um Cliente API com Interceptor

### Cliente API (`api.service.js`)

```javascript
// api.service.js
import authService from './auth.service.js';

class ApiService {
  constructor() {
    this.API_URL = 'http://localhost:8000';
  }

  // Método genérico para fazer requisições
  async request(endpoint, options = {}) {
    const token = authService.getToken();
    
    // Adicionar token automaticamente se estiver autenticado
    const headers = {
      ...options.headers,
    };

    if (token) {
      headers['Authorization'] = `Bearer ${token}`;
    }

    try {
      const response = await fetch(`${this.API_URL}${endpoint}`, {
        ...options,
        headers
      });

      // Se retornar 401, token expirou
      if (response.status === 401) {
        authService.logout();
        window.location.href = '/login'; // Redirecionar para login
        throw new Error('Sessão expirada');
      }

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.detail || 'Erro na requisição');
      }

      return await response.json();
    } catch (error) {
      console.error('Erro na API:', error);
      throw error;
    }
  }

  // Métodos específicos
  async get(endpoint) {
    return this.request(endpoint, { method: 'GET' });
  }

  async post(endpoint, data) {
    return this.request(endpoint, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  async put(endpoint, data) {
    return this.request(endpoint, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data)
    });
  }

  async delete(endpoint) {
    return this.request(endpoint, { method: 'DELETE' });
  }

  // Para upload de arquivos (multipart/form-data)
  async upload(endpoint, formData) {
    return this.request(endpoint, {
      method: 'POST',
      body: formData // Não define Content-Type, deixa o browser definir
    });
  }
}

const apiService = new ApiService();
export default apiService;
```

---

## 🖥️ 3. Exemplos de Uso no Frontend

### Tela de Login (`login.html` + `login.js`)

```html
<!-- login.html -->
<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Login - Expo TV</title>
</head>
<body>
  <div class="login-container">
    <h1>Login</h1>
    <form id="loginForm">
      <input type="email" id="email" placeholder="Email" required>
      <input type="password" id="password" placeholder="Senha" required>
      <button type="submit">Entrar</button>
      <div id="error" class="error"></div>
    </form>
  </div>

  <script type="module" src="login.js"></script>
</body>
</html>
```

```javascript
// login.js
import authService from './services/auth.service.js';

document.getElementById('loginForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const email = document.getElementById('email').value;
  const password = document.getElementById('password').value;
  const errorDiv = document.getElementById('error');

  try {
    const data = await authService.login(email, password);
    
    console.log('Login bem-sucedido!', data);
    console.log('Token válido por 30 dias');
    
    // Redirecionar para dashboard
    window.location.href = '/dashboard.html';
  } catch (error) {
    errorDiv.textContent = error.message;
  }
});
```

### Dashboard - Buscar Avisos Protegidos

```javascript
// dashboard.js
import authService from './services/auth.service.js';
import apiService from './services/api.service.js';

// Verificar autenticação ao carregar a página
async function init() {
  if (!authService.isAuthenticated()) {
    window.location.href = '/login.html';
    return;
  }

  // Opcional: Verificar se token ainda é válido
  const isValid = await authService.verifyToken();
  if (!isValid) {
    window.location.href = '/login.html';
    return;
  }

  loadDashboard();
}

async function loadDashboard() {
  try {
    // Buscar dados do usuário
    const userData = await authService.getCurrentUser();
    console.log('Usuário:', userData);

    // Buscar avisos (automáticamente com token)
    const avisos = await apiService.get('/avisos');
    console.log('Avisos:', avisos);

    renderAvisos(avisos);
  } catch (error) {
    console.error('Erro ao carregar dashboard:', error);
  }
}

function renderAvisos(avisos) {
  const container = document.getElementById('avisos-container');
  container.innerHTML = avisos.map(aviso => `
    <div class="aviso">
      <h3>${aviso.titulo}</h3>
      <p>${aviso.mensagem || 'Sem mensagem'}</p>
    </div>
  `).join('');
}

// Logout
document.getElementById('logoutBtn').addEventListener('click', () => {
  authService.logout();
  window.location.href = '/login.html';
});

init();
```

### Criar Aviso com Imagem

```javascript
// criar-aviso.js
import apiService from './services/api.service.js';

document.getElementById('avisoForm').addEventListener('submit', async (e) => {
  e.preventDefault();

  const formData = new FormData();
  formData.append('titulo', document.getElementById('titulo').value);
  formData.append('condominio_id', document.getElementById('condominio').value);
  
  const mensagem = document.getElementById('mensagem').value;
  if (mensagem) {
    formData.append('mensagem', mensagem); // Opcional!
  }

  const imagemFile = document.getElementById('imagem').files[0];
  if (imagemFile) {
    formData.append('imagem', imagemFile);
  }

  try {
    // Token é enviado automaticamente pelo apiService
    const result = await apiService.upload('/avisos', formData);
    console.log('Aviso criado:', result);
    alert('Aviso criado com sucesso!');
  } catch (error) {
    console.error('Erro ao criar aviso:', error);
    alert('Erro: ' + error.message);
  }
});
```

---

## 🔐 4. Proteção de Rotas (React/Vue/Angular)

### React Example

```javascript
// ProtectedRoute.jsx
import { Navigate } from 'react-router-dom';
import authService from './services/auth.service';

function ProtectedRoute({ children }) {
  if (!authService.isAuthenticated()) {
    return <Navigate to="/login" replace />;
  }

  return children;
}

// App.jsx
import { BrowserRouter, Routes, Route } from 'react-router-dom';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login" element={<Login />} />
        <Route 
          path="/dashboard" 
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          } 
        />
      </Routes>
    </BrowserRouter>
  );
}
```

### Vue 3 Example

```javascript
// router/index.js
import { createRouter, createWebHistory } from 'vue-router';
import authService from '@/services/auth.service';

const router = createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/login', component: Login },
    { 
      path: '/dashboard', 
      component: Dashboard,
      meta: { requiresAuth: true }
    }
  ]
});

// Guard global
router.beforeEach((to, from, next) => {
  if (to.meta.requiresAuth && !authService.isAuthenticated()) {
    next('/login');
  } else {
    next();
  }
});

export default router;
```

---

## ⚡ 5. Axios (Alternativa ao Fetch)

Se preferir usar Axios:

```javascript
// api.service.js com Axios
import axios from 'axios';
import authService from './auth.service';

const api = axios.create({
  baseURL: 'http://localhost:8000'
});

// Interceptor para adicionar token automaticamente
api.interceptors.request.use(
  (config) => {
    const token = authService.getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      authService.logout();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;

// Uso:
import api from './api.service';

// GET
const avisos = await api.get('/avisos');

// POST
const result = await api.post('/avisos', formData);

// PUT
await api.put(`/avisos/${id}`, updateData);

// DELETE
await api.delete(`/avisos/${id}`);
```

---

## 🔄 6. Quando Renovar o Token?

Com token de 30 dias, você tem 3 opções:

### Opção 1: Não fazer nada (Recomendado)
- Token válido por 30 dias
- Usuário faz login novamente quando expirar
- Simples e seguro

### Opção 2: Verificar periodicamente
```javascript
// Verificar a cada 1 hora se o token ainda é válido
setInterval(async () => {
  const isValid = await authService.verifyToken();
  if (!isValid) {
    alert('Sua sessão expirou. Faça login novamente.');
    window.location.href = '/login';
  }
}, 3600000); // 1 hora
```

### Opção 3: Implementar Refresh Token (Futuro)
- Requer mudanças no backend
- Token de acesso curto (15min)
- Refresh token longo (30 dias)
- Renovação automática

---

## 📋 Checklist de Implementação

- [ ] Criar `auth.service.js` com métodos de login/logout
- [ ] Criar `api.service.js` com interceptor de token
- [ ] Implementar tela de login
- [ ] Armazenar token no localStorage após login
- [ ] Adicionar token em todas as requisições protegidas
- [ ] Implementar proteção de rotas
- [ ] Tratar erro 401 (logout automático)
- [ ] Adicionar botão de logout
- [ ] Testar fluxo completo

---

## 🎯 Resumo - Fluxo Completo

1. **Usuário faz login** → Recebe token válido por 30 dias
2. **Token armazenado** no localStorage
3. **Todas as requisições** enviam `Authorization: Bearer {token}`
4. **Se 401** → Token expirado → Logout automático → Redirect para login
5. **Após 30 dias** → Token expira → Usuário faz login novamente

**NÃO PRECISA:**
- ❌ Enviar credenciais em toda requisição
- ❌ Fazer login constantemente
- ❌ Verificar token a cada segundo

**PRECISA:**
- ✅ Fazer login 1 vez
- ✅ Enviar token em requisições protegidas
- ✅ Tratar erro 401 (token expirado)
- ✅ Fazer logout ao sair

---

## 🔒 Segurança

1. **HTTPS em produção** (obrigatório)
2. **Não compartilhar token** entre dispositivos
3. **Logout ao sair** (limpar localStorage)
4. **HttpOnly cookies** (alternativa mais segura, requer backend change)
5. **CORS configurado** corretamente no backend

---

**Qualquer dúvida sobre a implementação, é só perguntar!** 🚀

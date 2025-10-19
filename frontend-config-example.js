// =====================================================
// CONFIGURAÇÃO DA API - FRONTEND
// =====================================================

// OPÇÃO 1: Detecção Automática por Hostname
// Recomendado para a maioria dos casos
const API_URL = window.location.hostname === 'localhost'
  ? 'http://localhost:8000'      // Desenvolvimento
  : 'https://expotv-backend.fly.dev';  // Produção

// OPÇÃO 2: Detecção por Protocolo
const API_URL_V2 = window.location.protocol === 'https:'
  ? 'https://expotv-backend.fly.dev'
  : 'http://localhost:8000';

// OPÇÃO 3: Variável de Ambiente (React/Next.js)
// .env.production
// NEXT_PUBLIC_API_URL=https://expotv-backend.fly.dev

// .env.development
// NEXT_PUBLIC_API_URL=http://localhost:8000

const API_URL_V3 = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// OPÇÃO 4: Variável de Ambiente (Vue.js)
// .env.production
// VUE_APP_API_URL=https://expotv-backend.fly.dev

// .env.development
// VUE_APP_API_URL=http://localhost:8000

const API_URL_V4 = process.env.VUE_APP_API_URL || 'http://localhost:8000';

// =====================================================
// EXPORTAR CONFIGURAÇÃO
// =====================================================

export default {
  API_URL: API_URL,  // Use a opção escolhida
  
  // Endpoints principais
  LOGIN: `${API_URL}/login`,
  VERIFY_TOKEN: `${API_URL}/verify-token`,
  ME: `${API_URL}/me`,
  
  // Avisos
  AVISOS: `${API_URL}/avisos`,
  AVISOS_BY_ID: (id) => `${API_URL}/avisos/${id}`,
  
  // Anúncios
  ANUNCIOS: `${API_URL}/anuncios`,
  ANUNCIOS_BY_ID: (id) => `${API_URL}/anuncios/${id}`,
  
  // Condominios
  CONDOMINIOS: `${API_URL}/condominios`,
  CONDOMINIOS_BY_ID: (id) => `${API_URL}/condominios/${id}`,
  
  // TVs
  TVS: `${API_URL}/tvs`,
  TVS_BY_ID: (id) => `${API_URL}/tvs/${id}`,
  
  // Users
  USERS: `${API_URL}/users`,
  USERS_BY_ID: (id) => `${API_URL}/users/${id}`,
};

// =====================================================
// USO NO CÓDIGO
// =====================================================

// Exemplo 1: Login
/*
import config from './config';

const response = await fetch(config.LOGIN, {
  method: 'POST',
  headers: {
    'Content-Type': 'application/x-www-form-urlencoded',
  },
  body: new URLSearchParams({
    username: 'user@email.com',
    password: 'senha123'
  })
});

const data = await response.json();
*/

// Exemplo 2: Buscar avisos (protegido)
/*
import config from './config';

const token = localStorage.getItem('token');

const response = await fetch(config.AVISOS, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});

const avisos = await response.json();
*/

// Exemplo 3: Criar aviso com imagem
/*
import config from './config';

const formData = new FormData();
formData.append('titulo', 'Título do Aviso');
formData.append('condominio_id', '1');
formData.append('mensagem', 'Mensagem opcional');
formData.append('imagem', fileInput.files[0]);

const token = localStorage.getItem('token');

const response = await fetch(config.AVISOS, {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`
  },
  body: formData
});

const result = await response.json();
*/

// =====================================================
// DEBUG
// =====================================================

// Ver qual URL está sendo usada
console.log('🌐 API URL:', API_URL);
console.log('🏠 Hostname:', window.location.hostname);
console.log('🔒 Protocol:', window.location.protocol);

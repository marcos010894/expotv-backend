# EXPO-TV Backend API

Sistema de gerenciamento para TVs em condomínios usando FastAPI e SQLModel.

## Funcionalidades

- **Autenticação JWT**: Login seguro com tokens
- **Gestão de Usuários**: ADM e SINDICO
- **Gestão de Condomínios**: CRUD completo
- **Gestão de TVs**: CRUD + status online/offline
- **Gestão de Anúncios**: CRUD para anúncios/alertas

## Instalação e Configuração

### 1. Instalar dependências
```bash
cd /Users/marcospaulomachadoazevedo/Documents/EXPO-TV/BACKEND
source .venv/bin/activate
```

### 2. Executar migrações
```bash
python -m app.migrate
```

### 3. Criar usuário master (já foi criado)
```bash
python -m create_master
```
**Credenciais do Master:**
- Email: `admin@expo-tv.com`
- Senha: `master123`
- Tipo: `ADM`

### 4. Iniciar servidor
```bash
uvicorn app.main:app --reload
```

## Endpoints Principais

### Autenticação
- `POST /token` - Login (retorna JWT token)
- `POST /register` - Registrar novo usuário
- `GET /me` - Informações do usuário autenticado

### Usuários
- `GET /users/` - Listar todos os usuários
- `GET /users/{user_id}` - Buscar usuário específico
- `POST /users/` - Criar usuário
- `PUT /users/{user_id}` - Atualizar usuário
- `DELETE /users/{user_id}` - Deletar usuário

### Condomínios
- `GET /condominios/` - Listar todos os condomínios
- `GET /condominios/{condominio_id}` - Buscar condomínio com TVs e anúncios
- `GET /sindico/{user_id}/condominios` - Condomínios de um síndico
- `POST /condominios/` - Criar condomínio
- `PUT /condominios/{condominio_id}` - Atualizar condomínio
- `DELETE /condominios/{condominio_id}` - Deletar condomínio

### TVs
- `GET /tvs/` - Listar todas as TVs
- `GET /tvs/{tv_id}` - Buscar TV específica
- `GET /tvs/{codigo_conexao}/status` - Verificar status da TV
- `POST /tvs/` - Criar TV (gera código automaticamente)
- `POST /tvs/{codigo_conexao}/status` - Marcar TV como online
- `PUT /tvs/{tv_id}` - Atualizar TV
- `DELETE /tvs/{tv_id}` - Deletar TV

### Anúncios
- `GET /anuncios/` - Listar todos os anúncios
- `GET /anuncios/{anuncio_id}` - Buscar anúncio específico
- `POST /anuncios/` - Criar anúncio
- `PUT /anuncios/{anuncio_id}` - Atualizar anúncio
- `DELETE /anuncios/{anuncio_id}` - Deletar anúncio

## Como Usar

### 1. Login
```bash
curl -X POST "http://localhost:8000/token" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@expo-tv.com&password=master123"
```

### 2. Usar Token nos Requests
Adicione o header: `Authorization: Bearer {seu_token}`

### 3. Documentação Interativa
Acesse: `http://localhost:8000/docs`

## Fluxo de TV

1. **Criar TV**: O sistema gera código de 5 dígitos automaticamente
2. **Conectar TV**: A TV chama `POST /tvs/{codigo_conexao}/status`
3. **Verificar Status**: Use `GET /tvs/{codigo_conexao}/status`

## Tipos de Usuário

- **ADM**: Acesso total ao sistema
- **SINDICO**: Acesso apenas aos seus condomínios

## Banco de Dados

SQLite para desenvolvimento (arquivo: `expo_tv.db`)

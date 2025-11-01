# EXPO TV - Backend API

Sistema de gerenciamento de conteúdo para TVs corporativas com suporte a avisos, anúncios e notícias.

## Tecnologias

- **Python 3.13**
- **FastAPI** - Framework web moderno e rápido
- **SQLModel** - ORM baseado em Pydantic e SQLAlchemy
- **MySQL** - Banco de dados relacional
- **Cloudflare R2** - Storage de arquivos
- **APScheduler** - Tarefas agendadas (monitoramento)
- **JWT** - Autenticação de usuários

## Pré-requisitos

- Python 3.13 ou superior
- MySQL 8.0 ou superior
- Git

## Instalação

### 1. Clone o repositório

```bash
git clone .EsteREPO
cd expotv-backend
```

### 2. Crie e ative o ambiente virtual

**macOS/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

**Windows:**
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
```

### 4. Configure as variáveis de ambiente

Copie o arquivo de exemplo e configure suas credenciais:

```bash
cp .env.example .env
```

Edite o arquivo `.env` com suas configurações:

```env
# Banco de Dados MySQL
DB_USER=seu_usuario
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=3306
DB_NAME=expotv

# Email SMTP (Gmail)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu_email@gmail.com
SMTP_PASSWORD=sua_senha_app
FROM_EMAIL=seu_email@gmail.com
FROM_NAME=EXPO TV

# Aplicação
FRONTEND_URL=http://localhost:3000
BACKEND_URL=http://localhost:8000
ENV=development
SECRET_KEY=gere_uma_chave_secreta_aqui

# Cloudflare R2
R2_ACCOUNT_ID=seu_account_id
R2_ACCESS_KEY_ID=sua_access_key
R2_SECRET_ACCESS_KEY=sua_secret_key
R2_BUCKET_NAME=seu_bucket
R2_PUBLIC_URL=https://seu-bucket.r2.dev
```

**Gerar SECRET_KEY:**
```bash
python -c "from secrets import token_urlsafe; print(token_urlsafe(32))"
```

### 5. Configure o banco de dados

Crie o banco de dados MySQL:

```sql
CREATE DATABASE expotv CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

As tabelas serão criadas automaticamente na primeira execução.

### 6. Crie o usuário master (opcional)

```bash
python create_master.py
```

Este script cria um usuário administrador com as credenciais:
- Email: master@expotv.com
- Senha: Master@2024

## Execução

### Desenvolvimento

Execute o servidor com reload automático:

```bash
uvicorn app.main:app --reload --port 8000
```

A API estará disponível em: `http://localhost:8000`

### Produção

Execute o servidor em modo produção:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## Documentação da API

Após iniciar o servidor, acesse:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Estrutura do Projeto

```
expotv-backend/
├── app/
│   ├── endpoints/          # Rotas da API
│   │   ├── anuncios.py    # CRUD de anúncios
│   │   ├── app.py         # Endpoints do app mobile/TV
│   │   ├── auth.py        # Autenticação
│   │   ├── avisos.py      # CRUD de avisos
│   │   ├── condominios.py # CRUD de condomínios
│   │   ├── tvs.py         # CRUD de TVs
│   │   └── users.py       # CRUD de usuários
│   ├── services/          # Serviços de background
│   │   ├── tv_monitor.py  # Monitor de status das TVs
│   │   └── expiration_monitor.py  # Monitor de expiração
│   ├── db.py              # Configuração do banco
│   ├── email_service.py   # Serviço de email
│   ├── main.py            # Ponto de entrada
│   ├── models.py          # Modelos do banco de dados
│   └── storage.py         # Integração com Cloudflare R2
├── static/                # Arquivos estáticos
├── tests/                 # Testes automatizados
├── .env                   # Variáveis de ambiente (não versionado)
├── .env.example           # Exemplo de variáveis
├── requirements.txt       # Dependências Python
└── README.md             # Este arquivo
```

## Principais Endpoints

### Autenticação
- `POST /login` - Login de usuário
- `POST /reset-password-request` - Solicitar reset de senha
- `POST /reset-password` - Resetar senha com token

### Usuários
- `GET /users` - Listar usuários
- `POST /users` - Criar usuário
- `PUT /users/{id}` - Atualizar usuário
- `DELETE /users/{id}` - Deletar usuário

### Condomínios
- `GET /condominios` - Listar condomínios
- `POST /condominios` - Criar condomínio
- `PUT /condominios/{id}` - Atualizar condomínio
- `DELETE /condominios/{id}` - Deletar condomínio

### TVs
- `GET /tvs` - Listar TVs
- `POST /tvs` - Criar TV
- `PUT /tvs/{id}` - Atualizar TV
- `DELETE /tvs/{id}` - Deletar TV
- `PUT /tvs/{id}/config` - Configurar proporção de conteúdo
- `GET /tvs/{id}/config` - Obter configuração

### Avisos
- `GET /avisos` - Listar avisos
- `POST /avisos` - Criar aviso
- `PUT /avisos/{id}` - Atualizar aviso
- `DELETE /avisos/{id}` - Deletar aviso
- `PUT /avisos/{id}/marcar-lido` - Marcar como lido

### Anúncios
- `GET /anuncios` - Listar anúncios
- `POST /anuncios` - Criar anúncio
- `PUT /anuncios/{id}` - Atualizar anúncio
- `DELETE /anuncios/{id}` - Deletar anúncio

### App (Mobile/TV)
- `GET /app/content/{condominio_id}` - Conteúdo completo do app
- `GET /app/tv/{codigo}/content` - Conteúdo intercalado por TV
- `GET /app/news` - Notícias da Jovem Pan
- `GET /app/jovempan` - Notícias exclusivas Jovem Pan
- `POST /app/tv/ping` - Heartbeat da TV

## Sistema de Proporções

Cada TV pode ser configurada individualmente para controlar a proporção de exibição:

- **proporcao_avisos**: Quantidade de avisos por ciclo (padrão: 1)
- **proporcao_anuncios**: Quantidade de anúncios por ciclo (padrão: 5)
- **proporcao_noticias**: Quantidade de notícias (padrão: 3)

Exemplo: Proporção 1:5:3 significa 1 aviso, 5 anúncios, 3 notícias.

## Monitoramento

O sistema inclui dois monitores em background:

1. **Monitor de Status das TVs** - Verifica a cada 1 minuto se as TVs estão online
2. **Monitor de Expiração** - Verifica a cada 1 hora se há conteúdo expirado

## Testes

Execute os testes:

```bash
pytest
```

Com cobertura:

```bash
pytest --cov=app tests/
```

## Deploy

### Fly.io

1. Instale o Fly CLI:
```bash
curl -L https://fly.io/install.sh | sh
```

2. Faça login:
```bash
fly auth login
```

3. Configure os secrets:
```bash
fly secrets set DB_USER=seu_usuario
fly secrets set DB_PASSWORD=sua_senha
fly secrets set SMTP_USER=seu_email
fly secrets set SMTP_PASSWORD=sua_senha
fly secrets set SECRET_KEY=sua_chave
fly secrets set R2_ACCOUNT_ID=seu_account
fly secrets set R2_ACCESS_KEY_ID=sua_key
fly secrets set R2_SECRET_ACCESS_KEY=sua_secret
```

4. Deploy:
```bash
fly deploy
```

## Comandos Úteis

### Parar servidor na porta 8000
```bash
lsof -ti:8000 | xargs kill -9
```

### Ver logs do servidor
```bash
tail -f logs/app.log
```

### Verificar versão do Python
```bash
python --version
```

### Atualizar dependências
```bash
pip install --upgrade -r requirements.txt
```

## Solução de Problemas

### Erro de conexão com MySQL
- Verifique se o MySQL está rodando: `mysql -u root -p`
- Confirme as credenciais no arquivo `.env`
- Verifique se o banco de dados existe

### Erro de permissão no email
- Use uma senha de aplicativo do Gmail (não a senha normal)
- Ative a autenticação de 2 fatores no Gmail
- Gere uma senha de app em: https://myaccount.google.com/apppasswords

### Erro de upload de arquivos
- Verifique as credenciais do Cloudflare R2
- Confirme se o bucket existe e está acessível
- Teste a URL pública do R2

### Servidor não inicia
- Verifique se a porta 8000 está livre
- Confirme se todas as dependências estão instaladas
- Revise o arquivo `.env`

## Suporte

Para dúvidas e suporte:
- Email: dev@salexpress.com.br
- Documentação: http://localhost:8000/docs

## Licença

Propriedade de Sal Express - Todos os direitos reservados.

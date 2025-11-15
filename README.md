# EXPO TV - Backend API

Sistema de gerenciamento de conteúdo para TVs corporativas com suporte a avisos, anúncios e notícias.

## 📚 Documentação

**[Acesse a documentação completa aqui →](docs/INDEX.md)**

### Links Rápidos
- 📖 [Guia de Instalação](docs/guias/INSTALL.md)
- 🔌 [Documentação da API](docs/api/GUIA_API.md)
- 🚀 [Guia de Deploy](docs/deploy/DEPLOY_FLYIO_FFMPEG.md)
- 🎬 [Conversão de Vídeos](docs/guias/CONVERSAO_VIDEO.md)
- ⚙️ [Configuração de Ambiente](docs/guias/ENV_SETUP.md)

## 🚀 Quick Start

```bash
# 1. Clone o repositório
git clone https://github.com/marcos010894/expotv-backend.git
cd expotv-backend

# 2. Instale FFmpeg
./scripts/install-ffmpeg.sh

# 3. Configure ambiente
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
cp .env.example .env
# Edite o .env com suas configurações

# 5. Execute
uvicorn app.main:app --reload
```

Acesse: http://localhost:8000/docs

## 🛠️ Tecnologias

- **Python 3.13**
- **FastAPI** - Framework web moderno e rápido
- **SQLModel** - ORM baseado em Pydantic e SQLAlchemy
- **MySQL** - Banco de dados relacional
- **Cloudflare R2** - Storage de arquivos (S3-compatible)
- **APScheduler** - Tarefas agendadas (monitoramento)
- **JWT** - Autenticação de usuários
- **FFmpeg** - Conversão automática de vídeos

## 📁 Estrutura do Projeto

```
BACKEND/
├── app/                    # Código fonte
│   ├── endpoints/          # Rotas da API
│   ├── models.py           # Modelos do banco
│   └── main.py            # Aplicação FastAPI
├── docs/                   # 📚 Documentação completa
│   ├── api/               # Docs da API
│   ├── deploy/            # Guias de deploy
│   └── guias/             # Tutoriais
├── scripts/               # Scripts utilitários
├── examples/              # Exemplos de código
├── tests/                 # Testes
├── Dockerfile             # Imagem Docker
├── fly.toml              # Config Fly.io
└── requirements.txt      # Dependências
```

## 🔥 Funcionalidades

- ✅ CRUD completo de Anúncios, Avisos e TVs
- ✅ Sistema de proporção inteligente (ex: 1 aviso : 5 anúncios : 3 notícias)
- ✅ Upload de imagens e vídeos com conversão automática para MP4
- ✅ Integração com Jovem Pan (notícias)
- ✅ Monitoramento automático de TVs online/offline
- ✅ Expiração automática de conteúdo
- ✅ Autenticação JWT
- ✅ Sistema de níveis de usuário (Master, Síndico, Visitante)
- ✅ Cloudflare R2 para storage
- ✅ Health checks automáticos

## 🌐 API Endpoints

Documentação interativa disponível em: **http://localhost:8000/docs**

Principais endpoints:
- `/auth/*` - Autenticação e usuários
- `/anuncios/*` - Gerenciamento de anúncios  
- `/avisos/*` - Gerenciamento de avisos
- `/condominios/*` - Gerenciamento de condomínios
- `/tvs/*` - Gerenciamento de TVs
- `/app/*` - Endpoints para o app mobile/TV

## 🚀 Deploy

### Produção (Fly.io)

```bash
# Deploy automático via GitHub
git push origin main

# Ou via CLI
flyctl deploy
```

[Ver guia completo de deploy →](docs/deploy/DEPLOY_FLYIO_FFMPEG.md)

## 🧪 Testes

```bash
pytest tests/
```

## 📜 Scripts Úteis

Localizados em `/scripts/`:

```bash
# Criar usuário master
python scripts/create_master.py

# Criar tabelas
python scripts/create_tables.py

# Limpar avisos expirados
python scripts/limpar_avisos.py

# Migrar proporções das TVs
python scripts/migrate_tv_proporcoes.py
```

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/NovaFuncionalidade`)
3. Commit suas mudanças (`git commit -m 'Add: Nova funcionalidade'`)
4. Push para a branch (`git push origin feature/NovaFuncionalidade`)
5. Abra um Pull Request

## 📄 Licença

Todos os direitos reservados © 2025 EXPO TV

## 📞 Suporte

- 📚 [Documentação Completa](docs/INDEX.md)
- 🐛 [Reportar Bug](https://github.com/marcos010894/expotv-backend/issues)
- 💬 Dúvidas: Entre em contato com a equipe

---

**Desenvolvido com ❤️ para EXPO TV**
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

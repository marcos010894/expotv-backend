# 🚀 Guia de Instalação - EXPO TV Backend

## 📋 Pré-requisitos

- Python 3.10 ou superior
- MySQL/MariaDB 5.7 ou superior
- Git
- pip (gerenciador de pacotes Python)

---

## 📦 Instalação em Banco de Dados Novo

### 1️⃣ Clonar o Repositório

```bash
git clone https://github.com/marcos010894/expotv-backend.git
cd expotv-backend
```

### 2️⃣ Criar Ambiente Virtual

```bash
# Criar venv
python -m venv .venv

# Ativar venv
# No Mac/Linux:
source .venv/bin/activate

# No Windows:
.venv\Scripts\activate
```

### 3️⃣ Instalar Dependências

```bash
pip install -r requirements.txt
```

### 4️⃣ Configurar Banco de Dados

Edite o arquivo `app/db.py` com suas credenciais:

```python
usuario = "seu_usuario"
senha = quote_plus("sua_senha")
host = "localhost"  # ou IP do servidor
banco = "expotv"
porta = 3306
```

**OU** use variáveis de ambiente (recomendado):

```bash
# Criar arquivo .env
export DB_USER="seu_usuario"
export DB_PASSWORD="sua_senha"
export DB_HOST="localhost"
export DB_NAME="expotv"
export DB_PORT="3306"
```

### 5️⃣ Executar Setup do Banco

**Este é o passo mais importante!**

```bash
python migrations_old/setup_database.py
```

Este script irá:
- ✅ Criar todas as tabelas necessárias
- ✅ Executar todas as migrações
- ✅ Criar usuário administrador padrão
- ✅ Validar a estrutura do banco

**Credenciais do Admin criadas:**
- Email: `admin@expotv.com.br`
- Senha: `admin123`
- ⚠️ **IMPORTANTE: Altere a senha após primeiro login!**

### 6️⃣ Configurar Email (Opcional)

Para recuperação de senha, configure o SMTP:

```bash
# Copiar exemplo
cp .env.email.example .env

# Editar .env com suas credenciais
nano .env
```

Exemplo para Gmail:
```bash
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-de-app
FROM_EMAIL=seu-email@gmail.com
FROM_NAME=EXPO TV
FRONTEND_URL=https://seu-frontend.com.br
ENV=production
```

📚 **Como criar senha de app Gmail:** https://myaccount.google.com/apppasswords

### 7️⃣ Iniciar o Servidor

```bash
uvicorn app.main:app --reload
```

O servidor estará rodando em: http://localhost:8000

### 8️⃣ Testar a API

Acesse a documentação interativa:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

**Fazer login:**
```bash
curl -X POST http://localhost:8000/login \
  -F "username=admin@expotv.com.br" \
  -F "password=admin123"
```

---

## 🔄 Instalação em Banco de Dados Existente

Se você já tem um banco EXPO TV e quer **apenas atualizar** para a versão mais recente:

### Opção 1: Usar o setup_database.py (Recomendado)

```bash
python setup_database.py
```

Este script é **inteligente** e irá:
- ✅ Detectar tabelas existentes (não duplica)
- ✅ Adicionar apenas colunas novas
- ✅ Preservar todos os dados existentes
- ✅ Não criar admin se já existir

### Opção 2: Executar migrações manualmente

```bash
# Migração 1: Campo last_ping (TV heartbeat)
python migrate_last_ping.py

# Migração 2: Campos de recuperação de senha
python migrate_password_reset.py
```

---

## 📁 Estrutura de Arquivos

```
expotv-backend/
├── app/
│   ├── main.py              # Aplicação principal
│   ├── db.py                # Configuração do banco
│   ├── models.py            # Modelos SQLModel
│   ├── auth.py              # Funções de autenticação
│   ├── storage.py           # Upload para Cloudflare R2
│   ├── email_service.py     # Envio de emails
│   ├── endpoints/           # Endpoints da API
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── condominios.py
│   │   ├── tvs.py
│   │   ├── anuncios.py
│   │   └── avisos.py
│   └── services/            # Serviços background
│       ├── tv_monitor.py
│       └── expiration_monitor.py
├── setup_database.py        # ⭐ Script de instalação completa
├── migrate_last_ping.py     # Migração específica
├── migrate_password_reset.py # Migração específica
├── requirements.txt         # Dependências Python
├── fly.toml                 # Configuração Fly.io
├── Procfile                 # Comando de inicialização
└── runtime.txt              # Versão do Python
```

---

## 🗃️ Estrutura do Banco de Dados

### Tabelas Criadas

| Tabela | Descrição | Campos Principais |
|--------|-----------|-------------------|
| `user` | Usuários (admins e síndicos) | id, email, senha, tipo, limite_avisos, reset_token |
| `condominio` | Condomínios gerenciados | id, nome, sindico_id, localizacao, cep |
| `tv` | TVs dos condomínios | id, nome, condominio_id, codigo_conexao, status, last_ping |
| `anuncio` | Anúncios para exibição | id, nome, condominios_ids, archive_url, tempo_exibicao |
| `aviso` | Avisos de síndicos | id, nome, condominios_ids, sindico_ids, mensagem, archive_url |

### Diagrama de Relacionamentos

```
User (Síndico)
  └─1:N─> Condominio
            └─1:N─> TV
```

---

## 🔧 Solução de Problemas

### Erro: "Can't connect to MySQL server"

**Problema:** Não consegue conectar ao banco de dados

**Soluções:**
1. Verificar se MySQL está rodando: `systemctl status mysql`
2. Verificar credenciais em `app/db.py`
3. Verificar firewall (porta 3306)
4. Testar conexão: `mysql -h HOST -u USER -p`

### Erro: "Table already exists"

**Problema:** Tabelas já existem no banco

**Solução:** Use `setup_database.py` - ele detecta e não duplica

### Erro: "Column already exists"

**Problema:** Migração já foi executada

**Solução:** Normal! O script detecta e pula colunas existentes

### Admin não foi criado

**Problema:** Já existia um admin

**Solução:**
```bash
# Verificar admins existentes
mysql -u USER -p -e "SELECT id, email, tipo FROM expotv.user WHERE tipo='ADM'"
```

### Erro ao enviar email

**Problema:** SMTP não configurado ou credenciais incorretas

**Solução:**
1. Verificar arquivo `.env`
2. Gmail: usar senha de app (não senha normal)
3. Verificar se 2FA está ativo no Gmail
4. Testar manualmente o SMTP

---

## 🚀 Deploy em Produção

### Fly.io (Recomendado)

```bash
# 1. Instalar Fly CLI
curl -L https://fly.io/install.sh | sh

# 2. Login
fly auth login

# 3. Deploy
fly deploy

# 4. Configurar secrets
fly secrets set SMTP_USER=seu-email@gmail.com
fly secrets set SMTP_PASSWORD=sua-senha-app
fly secrets set FRONTEND_URL=https://seu-frontend.com

# 5. Executar setup do banco (uma única vez)
fly ssh console
python setup_database.py
exit
```

### Outras Plataformas

- **Heroku:** Usar Procfile incluído
- **Railway:** Detecta automaticamente
- **VPS:** Usar systemd ou supervisor

---

## 📚 Documentação Adicional

Após a instalação, consulte:

- **Autenticação:** `AUTENTICACAO.md`
- **Recuperação de Senha:** `PASSWORD_RESET_GUIDE.md`
- **TV Heartbeat:** `TV_HEARTBEAT_GUIDE.md`
- **API Completa:** http://localhost:8000/docs

---

## ✅ Checklist de Instalação

- [ ] Python 3.10+ instalado
- [ ] MySQL/MariaDB criado
- [ ] Repositório clonado
- [ ] Ambiente virtual criado
- [ ] Dependências instaladas
- [ ] Credenciais do banco configuradas
- [ ] `setup_database.py` executado com sucesso
- [ ] Admin criado (admin@expotv.com.br)
- [ ] Servidor iniciado
- [ ] API testada em /docs
- [ ] SMTP configurado (opcional)
- [ ] Senha do admin alterada

---

## 🆘 Suporte

- **Documentação:** Ver arquivos .md no repositório
- **Issues:** https://github.com/marcos010894/expotv-backend/issues
- **Email:** admin@expotv.com.br

---

**Versão:** 1.0.0  
**Última atualização:** 27/10/2025

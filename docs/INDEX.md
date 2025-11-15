# 📚 Documentação EXPO TV Backend

## Estrutura da Documentação

### 🏗️ Infraestrutura & Arquitetura
- [Infraestrutura](INFRAESTRUTURA.md) - **Dimensionamento para 2.000 TVs**
- [Arquitetura](ARQUITETURA.md) - Visão técnica do sistema

### 📖 Guias
- [Instalação](guias/INSTALL.md) - Como instalar o sistema do zero
- [Configuração de Ambiente](guias/ENV_SETUP.md) - Variáveis de ambiente
- [Conversão de Vídeos](guias/CONVERSAO_VIDEO.md) - Sistema de conversão automática para MP4
- [Sistema de Proporção TV](guias/TV_PROPORCAO_GUIDE.md) - Como funciona o intercalamento de conteúdo
- [Sistema de Proporção (Texto)](guias/SISTEMA_PROPORCAO_TV.txt) - Versão texto
- [Limpeza de Migrations](guias/MIGRATIONS_CLEANUP.md) - Como limpar migrations antigas
- [Reset de Senha](guias/PASSWORD_RESET_PAGE.md) - Página de reset de senha

### 🚀 Deploy
- [Deploy no Fly.io com FFmpeg](deploy/DEPLOY_FLYIO_FFMPEG.md) - Como fazer deploy com suporte a vídeo
- [Status do Auto-Deploy](deploy/AUTO_DEPLOY_STATUS.md) - Acompanhamento do deploy automático

### 🔌 API
- [Guia da API](api/GUIA_API.md) - Documentação completa dos endpoints
- [Integração App/TV](api/INTEGRACAO_APP_TV.txt) - Como integrar o app mobile e as TVs

### 📜 Scripts
Localizados em `/scripts/`:
- `create_master.py` - Cria usuário master
- `create_tables.py` - Cria tabelas do banco
- `limpar_avisos.py` - Limpa avisos expirados
- `limpar_avisos_simples.py` - Versão simples da limpeza
- `migrate_tv_proporcoes.py` - Migra proporções das TVs
- `test_reset_endpoint.py` - Testa endpoint de reset
- `install-ffmpeg.sh` - Instala FFmpeg no sistema
- `deploy.sh` - Script de deploy

### 💡 Exemplos
Localizados em `/examples/`:
- `frontend-config-example.js` - Exemplo de configuração do frontend

## 🗂️ Estrutura do Projeto

```
BACKEND/
├── app/                    # Código fonte da aplicação
│   ├── endpoints/          # Endpoints da API
│   ├── models.py           # Modelos do banco
│   ├── schemas.py          # Schemas Pydantic
│   ├── db.py              # Configuração do banco
│   ├── storage.py         # Upload para R2
│   └── main.py            # Aplicação FastAPI
├── docs/                   # 📚 Documentação
│   ├── api/               # Docs da API
│   ├── deploy/            # Docs de deploy
│   └── guias/             # Guias e tutoriais
├── scripts/               # 📜 Scripts utilitários
├── examples/              # 💡 Exemplos de código
├── static/                # Arquivos estáticos
├── tests/                 # Testes
├── Dockerfile             # Imagem Docker
├── fly.toml              # Configuração Fly.io
├── requirements.txt      # Dependências Python
└── README.md             # Leia-me principal

```

## 🚀 Links Rápidos

- **README Principal**: [`../README.md`](../README.md)
- **Documentação da API**: http://localhost:8000/docs (quando rodando localmente)
- **Repositório**: https://github.com/marcos010894/expotv-backend
- **Deploy Produção**: https://expotv-backend.fly.dev

## 📝 Ordem de Leitura Recomendada

1. **Começando**: [`../README.md`](../README.md)
2. **Instalação**: [`guias/INSTALL.md`](guias/INSTALL.md)
3. **Configuração**: [`guias/ENV_SETUP.md`](guias/ENV_SETUP.md)
4. **API**: [`api/GUIA_API.md`](api/GUIA_API.md)
5. **Deploy**: [`deploy/DEPLOY_FLYIO_FFMPEG.md`](deploy/DEPLOY_FLYIO_FFMPEG.md)

## 🔧 Contribuindo

Para adicionar nova documentação:
1. Coloque arquivos de API em `docs/api/`
2. Coloque guias em `docs/guias/`
3. Coloque documentos de deploy em `docs/deploy/`
4. Atualize este índice

## 📞 Suporte

- Dúvidas sobre API: Veja [`api/GUIA_API.md`](api/GUIA_API.md)
- Problemas de deploy: Veja [`deploy/DEPLOY_FLYIO_FFMPEG.md`](deploy/DEPLOY_FLYIO_FFMPEG.md)
- Bugs: Abra uma issue no GitHub

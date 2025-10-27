# 📁 Migrações Antigas (Arquivadas)

## ℹ️ Sobre esta Pasta

Esta pasta contém **migrações antigas** que foram **substituídas** pelo script `setup_database.py`.

Estes arquivos são mantidos apenas para **referência histórica** e **não devem ser executados**.

---

## 📜 Histórico de Migrações

### 1. migrate_last_ping.py
**Data:** 25/10/2025  
**Objetivo:** Adicionar campo `last_ping` na tabela `tv`  
**Status:** ✅ Obsoleto - Incluído no `setup_database.py`

**O que fazia:**
```sql
ALTER TABLE tv ADD COLUMN last_ping DATETIME NULL;
```

**Motivo da criação:**
- Sistema de heartbeat para monitorar status das TVs (online/offline)
- Resolver erro: "'TV' object has no attribute 'last_ping'"

---

### 2. migrate_password_reset.py
**Data:** 27/10/2025  
**Objetivo:** Adicionar campos de recuperação de senha na tabela `user`  
**Status:** ✅ Obsoleto - Incluído no `setup_database.py`

**O que fazia:**
```sql
ALTER TABLE user ADD COLUMN reset_token VARCHAR(255) NULL;
ALTER TABLE user ADD COLUMN reset_token_expires DATETIME NULL;
```

**Motivo da criação:**
- Sistema de recuperação de senha (forgot password)
- Endpoints: `/forgot-password` e `/reset-password`

---

## 🚀 Como Usar (Novo Método)

**❌ NÃO USE ESTES ARQUIVOS!**

Em vez disso, use o script unificado:

```bash
# Script principal que faz TUDO
python setup_database.py
```

Este script:
- ✅ Cria todas as tabelas do zero
- ✅ Executa todas as migrações automaticamente
- ✅ Cria usuário admin
- ✅ É idempotente (seguro rodar múltiplas vezes)
- ✅ Funciona em banco novo OU existente

---

## 📚 Documentação

Para informações sobre migrações e instalação, veja:

- `../INSTALL.md` - Guia de instalação completo
- `../MIGRATIONS_GUIDE.md` - Guia sobre migrações
- `../setup_database.py` - Script principal de setup

---

## 🗑️ Posso Deletar Esta Pasta?

**Sim**, mas não é recomendado porque:

- Serve como documentação histórica
- Útil para entender evolução do schema
- Referência para rollback manual se necessário
- Não ocupa espaço significativo

**Se você realmente quiser deletar:**
```bash
rm -rf migrations_old/
```

---

**Última atualização:** 27/10/2025  
**Status:** Arquivado - Apenas para referência histórica

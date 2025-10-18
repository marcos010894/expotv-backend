# Configuração do Banco de Dados - Resolução de Problemas

## 🔧 Problema Resolvido

### Sintoma
```
INFO:sqlalchemy.engine.Engine:ROLLBACK
```

Esse erro aparecia aleatoriamente durante as requisições, causado por:
- Conexões perdidas com o banco de dados
- Timeout de conexão
- Conexões não recicladas (idle timeout do MySQL)

---

## ✅ Solução Implementada

### Configurações adicionadas em `app/db.py`:

```python
engine = create_engine(
    DATABASE_URL, 
    echo=False,                   # Desabilita logs SQL verbosos
    pool_pre_ping=True,           # ⭐ IMPORTANTE: Testa conexão antes de usar
    pool_recycle=3600,            # Recicla conexões a cada 1 hora
    pool_size=10,                 # Pool de 10 conexões
    max_overflow=20,              # Até 20 conexões extras
    pool_timeout=30,              # Timeout ao aguardar conexão
    connect_args={
        "connect_timeout": 10,    # Timeout de conexão
        "read_timeout": 30,       # Timeout de leitura
        "write_timeout": 30       # Timeout de escrita
    }
)
```

---

## 📋 O que cada parâmetro faz:

### `pool_pre_ping=True` ⭐ MAIS IMPORTANTE
- **O que faz:** Testa a conexão antes de usá-la
- **Por quê:** MySQL fecha conexões idle após 8 horas (wait_timeout)
- **Resultado:** Se a conexão estiver morta, cria uma nova automaticamente

### `pool_recycle=3600`
- **O que faz:** Recicla conexões a cada 1 hora (3600 segundos)
- **Por quê:** Previne que conexões fiquem obsoletas
- **Resultado:** Conexões sempre frescas, evita timeout

### `pool_size=10`
- **O que faz:** Mantém 10 conexões persistentes no pool
- **Por quê:** Reusa conexões, melhor performance
- **Resultado:** Não precisa criar conexão a cada requisição

### `max_overflow=20`
- **O que faz:** Permite até 20 conexões extras temporárias
- **Por quê:** Picos de tráfego não causam erro
- **Resultado:** Total de até 30 conexões simultâneas (10 + 20)

### `pool_timeout=30`
- **O que faz:** Aguarda 30 segundos por uma conexão disponível
- **Por quê:** Em vez de falhar imediatamente, aguarda
- **Resultado:** Requisições não falham em picos de tráfego

### `echo=False`
- **O que faz:** Desabilita logs SQL no console
- **Por quê:** Logs verbosos poluem o terminal
- **Resultado:** Console mais limpo, melhor performance

### `connect_args`
- **connect_timeout:** Tempo para estabelecer conexão (10s)
- **read_timeout:** Tempo máximo para ler dados (30s)
- **write_timeout:** Tempo máximo para escrever dados (30s)

---

## 🚀 Benefícios

### Antes
- ❌ Conexões perdidas causavam ROLLBACK
- ❌ Erros aleatórios em produção
- ❌ Logs poluídos com SQL
- ❌ Performance inconsistente

### Depois
- ✅ Conexões sempre testadas antes do uso
- ✅ Reconexão automática se conexão morta
- ✅ Pool de conexões para melhor performance
- ✅ Logs limpos e organizados
- ✅ Tratamento robusto de picos de tráfego

---

## 📊 Monitoramento

Para verificar o estado do pool de conexões:

```python
from app.db import engine

# Status do pool
print(f"Pool size: {engine.pool.size()}")
print(f"Checked out: {engine.pool.checkedout()}")
print(f"Overflow: {engine.pool.overflow()}")
print(f"Checked in: {engine.pool.checkedin()}")
```

---

## 🔍 Troubleshooting

### Se ainda aparecer ROLLBACK:

1. **Verificar timeout do MySQL**
   ```sql
   SHOW VARIABLES LIKE 'wait_timeout';
   SHOW VARIABLES LIKE 'interactive_timeout';
   ```

2. **Aumentar pool_recycle se necessário**
   ```python
   pool_recycle=1800  # 30 minutos
   ```

3. **Ativar logs temporariamente**
   ```python
   echo=True  # Para debug
   ```

4. **Verificar número de conexões**
   ```sql
   SHOW PROCESSLIST;
   SHOW STATUS LIKE 'Threads_connected';
   ```

---

## 🛡️ Boas Práticas

### ✅ Fazer
- Usar `pool_pre_ping=True` sempre
- Reciclar conexões antes do MySQL timeout
- Definir timeouts adequados
- Usar pool de conexões em produção

### ❌ Evitar
- `echo=True` em produção (performance)
- `pool_size` muito grande (desperdício de recursos)
- Não definir timeouts (conexões travadas)
- Criar engine por requisição (lento)

---

## 📝 Configuração Atual

**Ambiente:** Produção  
**Database:** MySQL/MariaDB  
**Host:** 193.203.175.53  
**Pool:** 10 conexões + 20 overflow  
**Recycle:** 1 hora  
**Timeouts:** 10s (connect), 30s (read/write)  

---

## 🔗 Referências

- [SQLAlchemy Engine Configuration](https://docs.sqlalchemy.org/en/20/core/engines.html)
- [Pool Configuration](https://docs.sqlalchemy.org/en/20/core/pooling.html)
- [MySQL Connection Pooling](https://dev.mysql.com/doc/refman/8.0/en/connection-pooling.html)

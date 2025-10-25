# 📺 Sistema de Heartbeat/Ping para TVs

## 🎯 Resumo

A TV deve enviar um **ping/heartbeat** a cada **1-2 minutos** para manter o status **online**.

Se a TV **não enviar ping por 5+ minutos**, será automaticamente marcada como **offline** pelo monitor.

---

## 🔌 Endpoint de Heartbeat

### POST `/tvs/{codigo_conexao}/ping`

**Descrição:** Endpoint que a TV deve chamar periodicamente

**Parâmetros:**
- `codigo_conexao` (path): Código único da TV

**Headers:** Nenhum necessário (endpoint público para TVs)

**Resposta:**
```json
{
  "success": true,
  "status": "online",
  "last_ping": "2025-10-25T19:15:30.123456",
  "message": "Heartbeat registrado com sucesso"
}
```

---

## 💻 Implementação no Frontend da TV

### JavaScript/TypeScript

```javascript
// Configuração
const TV_CODE = "ABC123";  // Código único da TV
const API_URL = "https://expotv-backend.fly.dev";
const PING_INTERVAL = 60000;  // 1 minuto (60 segundos)

// Função de ping
async function sendHeartbeat() {
  try {
    const response = await fetch(`${API_URL}/tvs/${TV_CODE}/ping`, {
      method: 'POST'
    });
    
    if (response.ok) {
      const data = await response.json();
      console.log('✅ Heartbeat enviado:', data.last_ping);
    } else {
      console.error('❌ Erro no heartbeat:', response.status);
    }
  } catch (error) {
    console.error('❌ Erro ao enviar heartbeat:', error);
  }
}

// Iniciar heartbeat automático
function startHeartbeat() {
  // Enviar imediatamente
  sendHeartbeat();
  
  // Enviar a cada 1 minuto
  setInterval(sendHeartbeat, PING_INTERVAL);
  
  console.log('📺 Heartbeat iniciado - Enviando a cada', PING_INTERVAL / 1000, 'segundos');
}

// Iniciar quando a TV ligar
window.addEventListener('load', () => {
  startHeartbeat();
});
```

### Python (Raspberry Pi / Android TV)

```python
import requests
import time
import threading

TV_CODE = "ABC123"
API_URL = "https://expotv-backend.fly.dev"
PING_INTERVAL = 60  # 1 minuto

def send_heartbeat():
    """Envia ping para o servidor"""
    try:
        response = requests.post(f"{API_URL}/tvs/{TV_CODE}/ping", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Heartbeat enviado: {data['last_ping']}")
        else:
            print(f"❌ Erro no heartbeat: {response.status_code}")
    except Exception as e:
        print(f"❌ Erro ao enviar heartbeat: {e}")

def heartbeat_loop():
    """Loop infinito de heartbeat"""
    while True:
        send_heartbeat()
        time.sleep(PING_INTERVAL)

def start_heartbeat():
    """Inicia heartbeat em background"""
    thread = threading.Thread(target=heartbeat_loop, daemon=True)
    thread.start()
    print(f"📺 Heartbeat iniciado - Enviando a cada {PING_INTERVAL}s")

# Iniciar
if __name__ == "__main__":
    start_heartbeat()
    # Manter o programa rodando
    while True:
        time.sleep(1)
```

### React / Next.js

```typescript
// hooks/useHeartbeat.ts
import { useEffect, useRef } from 'react';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'https://expotv-backend.fly.dev';
const PING_INTERVAL = 60000; // 1 minuto

export function useHeartbeat(tvCode: string) {
  const intervalRef = useRef<NodeJS.Timeout>();

  const sendHeartbeat = async () => {
    try {
      const response = await fetch(`${API_URL}/tvs/${tvCode}/ping`, {
        method: 'POST'
      });
      
      if (response.ok) {
        const data = await response.json();
        console.log('✅ Heartbeat:', data.last_ping);
      }
    } catch (error) {
      console.error('❌ Heartbeat error:', error);
    }
  };

  useEffect(() => {
    // Enviar imediatamente
    sendHeartbeat();

    // Enviar periodicamente
    intervalRef.current = setInterval(sendHeartbeat, PING_INTERVAL);

    // Cleanup
    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [tvCode]);
}

// Uso no componente
function TVApp() {
  const tvCode = 'ABC123';
  useHeartbeat(tvCode);
  
  return <div>TV Online</div>;
}
```

---

## 🔄 Fluxo Completo

### 1. TV Liga
```
TV → POST /tvs/{codigo}/status (conectar)
TV → POST /tvs/{codigo}/ping (primeiro heartbeat)
```

### 2. TV Operando
```
A cada 1 minuto:
  TV → POST /tvs/{codigo}/ping
  Backend atualiza: status = "online", last_ping = agora
```

### 3. Monitor do Backend (automático)
```
A cada 1 minuto:
  Backend verifica todas as TVs online
  Se last_ping > 5 minutos atrás → status = "offline"
```

### 4. TV Desliga
```
TV para de enviar ping
Após 5 minutos → Backend marca como "offline"
```

---

## 📊 Endpoints Relacionados

### Conectar TV (ao ligar)
```bash
POST /tvs/{codigo_conexao}/status
```

### Heartbeat (periódico)
```bash
POST /tvs/{codigo_conexao}/ping
```

### Verificar Status
```bash
GET /tvs/{codigo_conexao}/status

Response:
{
  "status": "online",
  "last_ping": "2025-10-25T19:15:30",
  "nome": "TV Portaria"
}
```

---

## ⚙️ Configurações

### Intervalos Recomendados

| Cenário | Intervalo de Ping | Timeout Offline |
|---------|-------------------|-----------------|
| **Produção** | 1 minuto | 5 minutos |
| **Desenvolvimento** | 30 segundos | 2 minutos |
| **Rede Instável** | 30 segundos | 3 minutos |

### Ajustar no Backend

Editar `app/services/tv_monitor.py`:
```python
# Linha 28
timeout_threshold = current_time - timedelta(minutes=5)  # Alterar aqui
```

### Ajustar no Frontend da TV

```javascript
const PING_INTERVAL = 60000;  // Alterar aqui (em milissegundos)
```

---

## 🐛 Troubleshooting

### TV fica offline mesmo enviando ping

**Problema:** Ping não está sendo recebido

**Solução:**
1. Verificar se está usando o código correto da TV
2. Testar manualmente:
```bash
curl -X POST https://expotv-backend.fly.dev/tvs/SEU_CODIGO/ping
```

### TV demora muito para ficar offline

**Problema:** Timeout muito longo

**Solução:** Diminuir o timeout em `tv_monitor.py`

### Erro 404 no ping

**Problema:** Código de conexão inválido

**Solução:** Verificar o código no banco de dados

---

## 📝 Estrutura do Banco

### Tabela `tv`

```sql
- id: INT (Primary Key)
- nome: VARCHAR(255)
- condominio_id: INT (Foreign Key)
- codigo_conexao: VARCHAR(255) UNIQUE
- status: VARCHAR(255) -- 'online' ou 'offline'
- template: VARCHAR(255)
- data_registro: DATETIME
- last_ping: DATETIME -- ⭐ NOVO!
```

---

## ✅ Checklist de Implementação

### Backend
- [x] Campo `last_ping` adicionado ao modelo TV
- [x] Migração do banco executada
- [x] Endpoint `/tvs/{codigo}/ping` criado
- [x] Endpoint `/tvs/{codigo}/status` atualizado
- [x] Monitor verifica `last_ping` a cada 1 minuto

### Frontend da TV
- [ ] Implementar função de heartbeat
- [ ] Enviar ping a cada 1-2 minutos
- [ ] Tratar erros de conexão
- [ ] Enviar ping ao iniciar
- [ ] Testar em produção

---

## 🚀 Teste Rápido

```bash
# 1. Enviar ping manualmente
curl -X POST https://expotv-backend.fly.dev/tvs/ABC123/ping

# 2. Verificar status
curl https://expotv-backend.fly.dev/tvs/ABC123/status

# 3. Aguardar 6 minutos sem enviar ping

# 4. Verificar novamente - deve estar offline
curl https://expotv-backend.fly.dev/tvs/ABC123/status
```

---

## 📞 Suporte

- Backend: `app/endpoints/tvs.py`
- Monitor: `app/services/tv_monitor.py`
- Modelo: `app/models.py`

**Status do sistema:** ✅ Funcionando
**Última atualização:** 25/10/2025

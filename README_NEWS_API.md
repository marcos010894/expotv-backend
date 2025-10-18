# Configuração da API de Notícias

## Como obter notícias reais e atuais

### Opção 1: NewsAPI (Recomendada)

1. Acesse: https://newsapi.org/
2. Crie uma conta gratuita
3. Obtenha sua API Key
4. No arquivo `app/endpoints/app.py`, substitua:
   ```python
   NEWS_API_KEY = "your_api_key_here"
   ```
   Por:
   ```python
   NEWS_API_KEY = "sua_chave_aqui"
   ```

**Vantagens:**
- Notícias reais e atualizadas
- Fontes brasileiras (G1, Folha, UOL, etc.)
- Até 1000 requests/dia grátis
- API confiável e rápida

### Opção 2: Configurar variável de ambiente

Para maior segurança, crie um arquivo `.env`:

```bash
NEWS_API_KEY=sua_chave_aqui
```

E modifique o código para usar:
```python
import os
from dotenv import load_dotenv

load_dotenv()
NEWS_API_KEY = os.getenv("NEWS_API_KEY", "your_api_key_here")
```

### Fontes de notícias disponíveis

Com a NewsAPI, você terá acesso a:
- G1 (globo.com)
- Folha de S.Paulo
- UOL
- Terra
- Exame
- InfoMoney
- E muitas outras fontes brasileiras

### Fallback atual

Se não configurar a NewsAPI, o sistema tentará:
1. RSS feeds públicos brasileiros
2. APIs alternativas gratuitas
3. Sistema de fallback com notícia de manutenção

### Como testar

Após configurar a chave:

1. Inicie o servidor: `uvicorn app.main:app --reload`
2. Acesse: `http://localhost:8000/app/news`
3. Ou: `http://localhost:8000/app/content/1?include_news=true`

As notícias serão reais, atuais e em português!

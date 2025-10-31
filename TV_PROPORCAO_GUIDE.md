# 📺 Sistema de Proporção de Conteúdo por TV

## 🎯 Objetivo

Permitir que o **administrador configure individualmente cada TV** para definir:
1. **Proporção Avisos:Anúncios** - Ex: 1:5 (1 aviso a cada 5 anúncios)
2. **Quantidade de Notícias** - Para TVs com layout 2 (tela cheia)

---

## ⚙️ Configuração Padrão

Todas as TVs começam com:
- **1 aviso** : **5 anúncios** : **3 notícias**

---

## 🔧 Endpoints da API

### 1. Atualizar Configuração da TV
```http
PUT /tvs/{tv_id}/config
Content-Type: application/json

{
  "proporcao_avisos": 2,
  "proporcao_anuncios": 10,
  "proporcao_noticias": 5
}
```

**Resposta:**
```json
{
  "success": true,
  "tv_id": 8,
  "nome": "TV Portaria",
  "config": {
    "proporcao_avisos": 2,
    "proporcao_anuncios": 10,
    "proporcao_noticias": 5,
    "descricao": "2 aviso(s) : 10 anúncio(s) : 5 notícia(s)"
  }
}
```

### 2. Obter Configuração Atual
```http
GET /tvs/{tv_id}/config
```

**Resposta:**
```json
{
  "tv_id": 8,
  "nome": "TV Portaria",
  "codigo_conexao": "12345",
  "config": {
    "proporcao_avisos": 1,
    "proporcao_anuncios": 5,
    "proporcao_noticias": 3,
    "descricao": "1 aviso(s) : 5 anúncio(s) : 3 notícia(s)"
  }
}
```

### 3. Obter Conteúdo Intercalado (TV App)
```http
GET /app/tv/{codigo_conexao}/content
```

**Resposta:**
```json
{
  "success": true,
  "tv": {
    "id": 8,
    "nome": "TV Portaria",
    "codigo_conexao": "12345",
    "template": "layout1"
  },
  "config": {
    "proporcao_avisos": 1,
    "proporcao_anuncios": 5,
    "proporcao_noticias": 3,
    "descricao": "1 aviso(s) : 5 anúncio(s)"
  },
  "content": [
    {
      "type": "aviso",
      "data": {
        "id": 1,
        "nome": "Aviso importante",
        "mensagem": "Reunião amanhã",
        "archive_url": "https://...",
        ...
      }
    },
    {
      "type": "anuncio",
      "data": {
        "id": 5,
        "nome": "Promoção",
        "archive_url": "https://...",
        "tempo_exibicao": 10,
        ...
      }
    },
    {
      "type": "anuncio",
      "data": { ... }
    },
    ...
  ],
  "stats": {
    "total_items": 15,
    "avisos": 3,
    "anuncios": 12,
    "noticias": 0
  }
}
```

---

## 📊 Como Funciona a Intercalação

### Exemplo: Proporção 1:5 (1 aviso : 5 anúncios)

**Conteúdo disponível:**
- 3 avisos
- 15 anúncios

**Ordem de exibição:**
```
1. Aviso #1
2. Anúncio #1
3. Anúncio #2
4. Anúncio #3
5. Anúncio #4
6. Anúncio #5
7. Aviso #2
8. Anúncio #6
9. Anúncio #7
10. Anúncio #8
11. Anúncio #9
12. Anúncio #10
13. Aviso #3
14. Anúncio #11
15. Anúncio #12
16. Anúncio #13
17. Anúncio #14
18. Anúncio #15
```

### Exemplo: Proporção 2:3 (2 avisos : 3 anúncios)

**Ordem de exibição:**
```
1. Aviso #1
2. Aviso #2
3. Anúncio #1
4. Anúncio #2
5. Anúncio #3
6. Aviso #3
7. Aviso #4
8. Anúncio #4
9. Anúncio #5
10. Anúncio #6
...
```

---

## 🎨 Layout 2 - Notícias em Tela Cheia

Para TVs com **template = "layout2"**:

- Notícias são adicionadas **no final** da sequência
- Quantidade controlada por `proporcao_noticias`
- Exemplo com `proporcao_noticias = 3`:

```
1. Aviso #1
2. Anúncio #1
3. Anúncio #2
...
10. Anúncio #10
11. Notícia #1 (tela cheia)
12. Notícia #2 (tela cheia)
13. Notícia #3 (tela cheia)
```

---

## 🖥️ Implementação no Frontend (Admin)

### Interface Sugerida

```jsx
<Card title="Configuração de Exibição">
  <Form>
    <FormItem label="Proporção Avisos:Anúncios">
      <Row gutter={8}>
        <Col span={10}>
          <InputNumber 
            min={0}
            value={proporcaoAvisos}
            onChange={(val) => setProporcaoAvisos(val)}
            addonBefore="Avisos"
          />
        </Col>
        <Col span={4} style={{textAlign: 'center', paddingTop: 4}}>
          :
        </Col>
        <Col span={10}>
          <InputNumber 
            min={0}
            value={proporcaoAnuncios}
            onChange={(val) => setProporcaoAnuncios(val)}
            addonBefore="Anúncios"
          />
        </Col>
      </Row>
      <Alert 
        type="info" 
        message={`Proporção atual: ${proporcaoAvisos}:${proporcaoAnuncios}`}
        description="A cada ciclo, a TV exibirá essa quantidade de avisos seguidos de anúncios"
      />
    </FormItem>
    
    {template === 'layout2' && (
      <FormItem label="Notícias (Tela Cheia)">
        <InputNumber 
          min={0}
          value={proporcaoNoticias}
          onChange={(val) => setProporcaoNoticias(val)}
        />
        <Alert 
          type="info" 
          message="Notícias serão exibidas em tela cheia no final do ciclo"
        />
      </FormItem>
    )}
    
    <Button type="primary" onClick={salvarConfig}>
      Salvar Configuração
    </Button>
  </Form>
</Card>
```

### Código JavaScript

```javascript
// Atualizar configuração
async function salvarConfigTV(tvId) {
  const response = await fetch(`/tvs/${tvId}/config`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      proporcao_avisos: proporcaoAvisos,
      proporcao_anuncios: proporcaoAnuncios,
      proporcao_noticias: proporcaoNoticias
    })
  });
  
  const data = await response.json();
  console.log('Configuração salva:', data);
}

// Buscar configuração atual
async function buscarConfigTV(tvId) {
  const response = await fetch(`/tvs/${tvId}/config`, {
    headers: {
      'Authorization': `Bearer ${token}`
    }
  });
  
  const data = await response.json();
  setProporcaoAvisos(data.config.proporcao_avisos);
  setProporcaoAnuncios(data.config.proporcao_anuncios);
  setProporcaoNoticias(data.config.proporcao_noticias);
}
```

---

## 📱 Implementação no App da TV

### React Native / Electron

```javascript
// Buscar conteúdo intercalado
async function buscarConteudoTV() {
  const codigoConexao = await AsyncStorage.getItem('codigo_conexao');
  
  const response = await fetch(
    `https://api.expotv.com/app/tv/${codigoConexao}/content`
  );
  
  const data = await response.json();
  
  console.log('Configuração:', data.config);
  console.log('Total de itens:', data.stats.total_items);
  
  // Processar conteúdo
  data.content.forEach(item => {
    switch(item.type) {
      case 'aviso':
        exibirAviso(item.data);
        break;
      case 'anuncio':
        exibirAnuncio(item.data);
        break;
      case 'noticia':
        exibirNoticia(item.data);
        break;
    }
  });
}

// Exibir conteúdo em loop
function iniciarExibicao(content) {
  let index = 0;
  
  function proximo() {
    if (index >= content.length) {
      index = 0; // Reiniciar loop
    }
    
    const item = content[index];
    const duracao = item.type === 'anuncio' 
      ? item.data.tempo_exibicao * 1000 
      : 5000; // 5 segundos para avisos/notícias
    
    exibirItem(item);
    
    setTimeout(proximo, duracao);
    index++;
  }
  
  proximo();
}
```

---

## 🎯 Casos de Uso

### 1. Shopping/Mall
```json
{
  "proporcao_avisos": 1,
  "proporcao_anuncios": 10,
  "proporcao_noticias": 2
}
```
- Foco em anúncios (vendas)
- Poucos avisos
- Poucas notícias

### 2. Condomínio Residencial
```json
{
  "proporcao_avisos": 3,
  "proporcao_anuncios": 5,
  "proporcao_noticias": 5
}
```
- Equilíbrio entre avisos e anúncios
- Mais notícias para entreter

### 3. Academia/Clube
```json
{
  "proporcao_avisos": 2,
  "proporcao_anuncios": 8,
  "proporcao_noticias": 3
}
```
- Muitos anúncios de parceiros
- Avisos de horários/eventos
- Notícias esportivas

---

## 📝 Validações

- ✅ Proporção mínima: 0 (pode desabilitar avisos, anúncios ou notícias)
- ✅ Proporção máxima: Ilimitada
- ✅ Valores devem ser inteiros positivos
- ✅ Layout 2: Notícias só aparecem se `template = "layout2"`
- ✅ Se não houver conteúdo suficiente, ciclo termina antes

---

## 🔄 Migração Executada

```sql
ALTER TABLE tv ADD COLUMN proporcao_avisos INT NOT NULL DEFAULT 1;
ALTER TABLE tv ADD COLUMN proporcao_anuncios INT NOT NULL DEFAULT 5;
ALTER TABLE tv ADD COLUMN proporcao_noticias INT NOT NULL DEFAULT 3;
```

**Status:** ✅ Executada com sucesso

---

## 📊 Modelo de Dados

### Tabela `tv`
| Campo | Tipo | Padrão | Descrição |
|-------|------|--------|-----------|
| proporcao_avisos | INT | 1 | Nº de avisos por ciclo |
| proporcao_anuncios | INT | 5 | Nº de anúncios por ciclo |
| proporcao_noticias | INT | 3 | Nº de notícias (layout 2) |

---

## 🚀 Próximos Passos

1. ✅ Backend implementado
2. ⏳ Criar interface no admin
3. ⏳ Atualizar app da TV para usar novo endpoint
4. ⏳ Testar em produção

---

## 💡 Dicas

- **Proporção 0:X** = Sem avisos, só anúncios
- **Proporção X:0** = Sem anúncios, só avisos
- **Proporção 0:0** = Sem conteúdo intercalado (só notícias se layout 2)
- **Layout 1** = Ignora `proporcao_noticias`
- **Layout 2** = Notícias aparecem no final do ciclo

---

**Documentação criada em:** 31 de outubro de 2025  
**Versão:** 1.0.0

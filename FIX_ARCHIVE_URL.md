# 🔧 FIX - Archive URL não estava sendo salvo

## 🔍 O Problema

Depois de adicionar suporte a vídeos, o campo `archive_url` não estava sendo salvo no banco de dados.

## 🕵️ Investigação

1. ✅ Código da aplicação estava correto
2. ✅ Modelo tinha o campo `archive_url`
3. ⚠️ **Coluna do banco estava como VARCHAR(255)**
4. ⚠️ URLs longas (especialmente de vídeos com caminhos completos) eram truncadas

## ✅ Solução

Alterado tipo da coluna no banco de dados:
- **Antes:** `VARCHAR(255)` - máximo 255 caracteres
- **Depois:** `TEXT` - máximo 65.535 caracteres

### Comando executado:
```sql
ALTER TABLE anuncio MODIFY COLUMN archive_url TEXT NULL;
ALTER TABLE aviso MODIFY COLUMN archive_url TEXT NULL;
```

## 📝 Mudanças Adicionais

### Logs de debug adicionados:
```python
# Em anuncios.py
print(f"✅ Upload bem-sucedido! URL: {archive_url}")
print(f"📝 Criando anúncio com archive_url: {archive_url}")
print(f"✅ Anúncio salvo! ID: {anuncio.id}, archive_url: {anuncio.archive_url}")

# Em get_all_anuncios
for a in anuncios:
    print(f"Anúncio #{a.id}: nome={a.nome}, archive_url={a.archive_url}")
```

Esses logs ajudam a debugar problemas de upload.

## 🧪 Como Testar

### 1. Criar anúncio com vídeo
```bash
curl -X POST https://expotv-backend.fly.dev/anuncios \
  -H "Authorization: Bearer {token}" \
  -F "nome=Teste Vídeo" \
  -F "condominios_ids=1" \
  -F "status=Ativo" \
  -F "media=@video.mp4"
```

### 2. Verificar se URL foi salva
```bash
curl https://expotv-backend.fly.dev/anuncios \
  -H "Authorization: Bearer {token}"
```

Deve retornar:
```json
[
  {
    "id": 1,
    "nome": "Teste Vídeo",
    "archive_url": "https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev/anuncios/2025/10/25/uuid.mp4",
    ...
  }
]
```

## 📊 Estrutura Final do Banco

### Tabela `anuncio`:
- `id`: INT (Primary Key)
- `nome`: VARCHAR(255)
- `condominios_ids`: VARCHAR(255)
- `numero_anunciante`: VARCHAR(255)
- `nome_anunciante`: VARCHAR(255)
- `status`: VARCHAR(255)
- `data_expiracao`: DATETIME
- `archive_url`: **TEXT** ✅ (alterado)
- `tempo_exibicao`: INT

### Tabela `aviso`:
- `id`: INT (Primary Key)
- `nome`: VARCHAR(255)
- `condominios_ids`: VARCHAR(255)
- `numero_anunciante`: VARCHAR(255)
- `nome_anunciante`: VARCHAR(255)
- `status`: VARCHAR(255)
- `data_expiracao`: DATETIME
- `archive_url`: **TEXT** ✅ (alterado)
- `mensagem`: TEXT
- `sindico_ids`: VARCHAR(255)

## ✅ Status

- ✅ Tipo de coluna corrigido (VARCHAR → TEXT)
- ✅ Logs de debug adicionados
- ✅ Suporte a vídeos funcionando
- ✅ URLs longas não são mais truncadas

## 🚀 Deploy

```bash
git add -A
git commit -m "Fix: Corrige salvamento de archive_url e adiciona logs de debug"
git push
fly deploy
```

## 💡 Lição Aprendida

**VARCHAR(255) não é suficiente para URLs longas!**

URLs do R2 com estrutura:
```
https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev/anuncios/2025/10/25/uuid-longo.extensao
```

Podem facilmente ultrapassar 255 caracteres, especialmente com:
- UUIDs longos
- Caminhos de data completos
- Extensões de arquivo
- Parâmetros de query (futuramente)

**Sempre use TEXT para URLs!** 📝

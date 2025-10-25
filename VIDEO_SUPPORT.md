# 🎬 Suporte a Vídeos - Anúncios e Avisos

## ✅ Implementado

Agora a API aceita **vídeos** além de imagens nos endpoints de **Anúncios** e **Avisos**!

---

## 📋 O que mudou

### 1. Storage (`app/storage.py`)

#### Nova função: `upload_media_to_r2()`
```python
def upload_media_to_r2(file_content: bytes, filename: str, content_type: str, media_type: str = "anuncios") -> str:
    """
    Faz upload de mídia (imagem ou vídeo) para o Cloudflare R2
    """
```

**Recursos:**
- Aceita imagens E vídeos
- Organiza por tipo (anuncios/avisos)
- Gera nome único com UUID
- Retorna URL pública HTTPS

### 2. Anúncios (`app/endpoints/anuncios.py`)

#### Antes:
```python
image: Optional[UploadFile] = File(None, description="🖼️ Imagem...")
```

#### Depois:
```python
media: Optional[UploadFile] = File(None, description="🎬 Mídia (Imagem ou Vídeo)...")
```

**Formatos aceitos:**
- **Imagens:** PNG, JPG, JPEG, WebP, GIF (máx **5MB**)
- **Vídeos:** MP4, MOV, AVI, WebM, MPEG (máx **50MB**)

### 3. Avisos (`app/endpoints/avisos.py`)

#### Mesmas mudanças:
- Campo `image` → `media`
- Aceita imagens e vídeos
- Validação de tamanho automática

---

## 🎯 Como usar

### 📤 Criar Anúncio com Vídeo

```bash
curl -X POST "https://expotv-backend.fly.dev/anuncios" \
  -H "Authorization: Bearer {token}" \
  -F "nome=Promoção Especial" \
  -F "condominios_ids=1,2,3" \
  -F "status=Ativo" \
  -F "tempo_exibicao=15" \
  -F "media=@video_promocao.mp4"
```

### 📤 Criar Aviso com Vídeo

```bash
curl -X POST "https://expotv-backend.fly.dev/avisos" \
  -H "Authorization: Bearer {token}" \
  -F "nome=Aviso Importante" \
  -F "condominios_ids=1" \
  -F "status=Ativo" \
  -F "mensagem=Reunião amanhã às 19h" \
  -F "media=@video_aviso.mp4"
```

### 🖼️ Ainda funciona com imagens:

```bash
curl -X POST "https://expotv-backend.fly.dev/anuncios" \
  -H "Authorization: Bearer {token}" \
  -F "nome=Promoção" \
  -F "condominios_ids=1" \
  -F "status=Ativo" \
  -F "media=@imagem.png"
```

---

## 📊 Validações Automáticas

### Tipo de Arquivo

**Aceitos:**
```
✅ Imagens: image/png, image/jpeg, image/jpg, image/webp, image/gif
✅ Vídeos: video/mp4, video/quicktime, video/x-msvideo, video/webm, video/mpeg
```

**Rejeitados:**
```
❌ Outros formatos: PDF, TXT, ZIP, etc.
```

### Tamanho do Arquivo

| Tipo | Máximo | Razão |
|------|--------|-------|
| **Imagem** | 5 MB | Carregamento rápido |
| **Vídeo** | 50 MB | Qualidade vs. desempenho |

**Erro se exceder:**
```json
{
  "detail": "Arquivo muito grande. Máximo: 50MB"
}
```

---

## 🔄 Compatibilidade

### ✅ Backend compatível com:
- Uploads antigos (campo `image`)
- Uploads novos (campo `media`)
- Imagens e vídeos

### ⚠️ Frontend precisa:
- Trocar campo `image` para `media`
- Aceitar tipos de arquivo: `image/*,video/*`
- Mostrar preview de vídeo (se aplicável)

---

## 🎨 Frontend - Exemplo HTML

```html
<form id="anuncioForm" enctype="multipart/form-data">
  <input type="text" name="nome" placeholder="Título" required>
  <input type="text" name="condominios_ids" placeholder="IDs (1,2,3)" required>
  
  <!-- Campo de mídia (imagem OU vídeo) -->
  <input 
    type="file" 
    name="media" 
    accept="image/*,video/*"
    onchange="previewMedia(event)"
  >
  
  <!-- Preview -->
  <div id="preview"></div>
  
  <button type="submit">Criar Anúncio</button>
</form>

<script>
function previewMedia(event) {
  const file = event.target.files[0];
  const preview = document.getElementById('preview');
  
  if (file.type.startsWith('image/')) {
    preview.innerHTML = `<img src="${URL.createObjectURL(file)}" width="200">`;
  } else if (file.type.startsWith('video/')) {
    preview.innerHTML = `<video src="${URL.createObjectURL(file)}" width="200" controls></video>`;
  }
}

document.getElementById('anuncioForm').addEventListener('submit', async (e) => {
  e.preventDefault();
  
  const formData = new FormData(e.target);
  
  const response = await fetch('https://expotv-backend.fly.dev/anuncios', {
    method: 'POST',
    headers: {
      'Authorization': `Bearer ${token}`
    },
    body: formData
  });
  
  const result = await response.json();
  console.log('Anúncio criado:', result);
});
</script>
```

---

## 🎥 Frontend - React/Vue

### React

```jsx
import { useState } from 'react';

function AnuncioForm() {
  const [media, setMedia] = useState(null);
  const [preview, setPreview] = useState(null);
  
  const handleMediaChange = (e) => {
    const file = e.target.files[0];
    setMedia(file);
    
    if (file) {
      setPreview(URL.createObjectURL(file));
    }
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    const formData = new FormData(e.target);
    
    const response = await fetch('https://expotv-backend.fly.dev/anuncios', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      },
      body: formData
    });
    
    const result = await response.json();
    console.log('Criado:', result);
  };
  
  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="nome" placeholder="Título" required />
      <input type="text" name="condominios_ids" placeholder="IDs" required />
      
      <input 
        type="file" 
        name="media" 
        accept="image/*,video/*"
        onChange={handleMediaChange}
      />
      
      {preview && media?.type.startsWith('image/') && (
        <img src={preview} width="200" />
      )}
      
      {preview && media?.type.startsWith('video/') && (
        <video src={preview} width="200" controls />
      )}
      
      <button type="submit">Criar</button>
    </form>
  );
}
```

---

## 📝 Resposta da API

### Com vídeo:

```json
{
  "id": 123,
  "nome": "Promoção Especial",
  "archive_url": "https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev/anuncios/2025/10/18/uuid-12345.mp4",
  "status": "Ativo",
  "tempo_exibicao": 15,
  ...
}
```

### Com imagem:

```json
{
  "id": 124,
  "nome": "Aviso Importante",
  "archive_url": "https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev/avisos/2025/10/18/uuid-67890.png",
  "status": "Ativo",
  ...
}
```

---

## 🔍 Como identificar se é imagem ou vídeo

### Opção 1: Pela extensão
```javascript
const isVideo = url.match(/\.(mp4|mov|avi|webm|mpeg)$/i);
const isImage = url.match(/\.(png|jpg|jpeg|webp|gif)$/i);
```

### Opção 2: Pela resposta HTTP (HEAD request)
```javascript
const response = await fetch(url, { method: 'HEAD' });
const contentType = response.headers.get('content-type');

if (contentType.startsWith('video/')) {
  // É vídeo
} else if (contentType.startsWith('image/')) {
  // É imagem
}
```

### Opção 3: Renderização automática
```jsx
function MediaPlayer({ url }) {
  const isVideo = /\.(mp4|mov|avi|webm|mpeg)$/i.test(url);
  
  return isVideo 
    ? <video src={url} controls />
    : <img src={url} />;
}
```

---

## ✅ Checklist

- [x] Função `upload_media_to_r2()` criada
- [x] Endpoint `/anuncios` aceita vídeos
- [x] Endpoint `/avisos` aceita vídeos
- [x] Validação de tipo de arquivo
- [x] Validação de tamanho (5MB img / 50MB video)
- [x] Erro descritivo se inválido
- [x] Documentação atualizada
- [ ] Frontend atualizado para usar campo `media`
- [ ] Frontend com preview de vídeo
- [ ] Deploy e teste em produção

---

## 🚀 Deploy

```bash
git add .
git commit -m "Feature: Adiciona suporte a vídeos em anúncios e avisos"
git push
fly deploy
```

---

## 🎯 Resumo

**ANTES:** ❌ Só aceitava imagens  
**DEPOIS:** ✅ Aceita imagens E vídeos!

**Formatos:**
- 🖼️ PNG, JPG, JPEG, WebP, GIF (5MB)
- 🎥 MP4, MOV, AVI, WebM, MPEG (50MB)

**URLs geradas:** `https://pub-...r2.dev/anuncios/2025/10/18/uuid.mp4`

**Pronto para usar!** 🎉

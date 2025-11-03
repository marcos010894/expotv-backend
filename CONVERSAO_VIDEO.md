# Conversão Automática de Vídeos para MP4

## Visão Geral

O sistema EXPO TV agora **converte automaticamente** todos os vídeos para MP4 antes de salvar no Cloudflare R2.

## Por que MP4?

- ✅ **Compatibilidade universal**: Funciona em todos os navegadores e dispositivos
- ✅ **Otimização web**: Codec H.264 com fast start para streaming
- ✅ **Menor tamanho**: Compressão eficiente mantendo qualidade
- ✅ **Padronização**: Todos os vídeos no mesmo formato

## Formatos Aceitos

O sistema aceita os seguintes formatos de entrada (todos convertidos para MP4):

### Vídeos
- **AVI** (`.avi`) - Múltiplos MIME types suportados
- **MOV** (`.mov`) - QuickTime
- **MPEG** (`.mpg`, `.mpeg`)
- **WebM** (`.webm`)
- **MKV** (`.mkv`) - Matroska
- **MP4** (`.mp4`) - Mantido sem conversão

### Imagens (sem conversão)
- **PNG** (`.png`)
- **JPG/JPEG** (`.jpg`, `.jpeg`)
- **WebP** (`.webp`)
- **GIF** (`.gif`)

## Como Funciona

### Fluxo de Upload

```
1. Frontend envia vídeo AVI
   ↓
2. Backend detecta: "não é MP4"
   ↓
3. FFmpeg converte para MP4
   - Codec: H.264 (libx264)
   - Áudio: AAC 128k
   - Qualidade: CRF 23
   - Otimização: faststart
   ↓
4. Upload do MP4 para R2
   ↓
5. Retorna URL do vídeo MP4
```

### Parâmetros de Conversão

```bash
ffmpeg -i input.avi \
  -c:v libx264      # Codec de vídeo H.264
  -preset fast      # Velocidade média (fast/medium/slow)
  -crf 23          # Qualidade (18=alta, 28=baixa)
  -c:a aac         # Codec de áudio AAC
  -b:a 128k        # Bitrate áudio 128kbps
  -movflags +faststart  # Otimizar para web streaming
  output.mp4
```

## Limites

- **Tamanho máximo**: 50MB para vídeos
- **Timeout**: 5 minutos de conversão
- **Armazenamento temporário**: Usa `/tmp` do sistema

## Logs

Durante a conversão, você verá no console:

```
🎬 Convertendo vídeo video.avi para MP4...
✅ Conversão concluída!
```

## Requisitos Técnicos

### Desenvolvimento Local

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Ou use o script
./install-ffmpeg.sh
```

### Produção (Fly.io)

Adicione ao `Dockerfile` ou `.fly/scripts/install.sh`:

```dockerfile
RUN apt-get update && apt-get install -y ffmpeg
```

## Troubleshooting

### Erro: "FFmpeg não encontrado"

**Solução**: Instale o FFmpeg no sistema operacional

```bash
# Verificar se está instalado
ffmpeg -version

# Se não estiver, instalar
./install-ffmpeg.sh
```

### Erro: "Conversão excedeu tempo limite"

**Causa**: Vídeo muito grande ou complexo

**Soluções**:
1. Reduza o tamanho do vídeo antes de enviar
2. Aumente o timeout em `storage.py` (linha do subprocess.run)
3. Use formato mais simples (MP4 direto)

### Erro: "Arquivo muito grande"

**Causa**: Vídeo excede 50MB

**Solução**: Comprima o vídeo antes do upload ou aumente o limite em:
- `app/endpoints/avisos.py` (linha do max_size)
- `app/endpoints/anuncios.py` (linha do max_size)

## Desempenho

### Tempos Médios de Conversão

| Tamanho | Duração | Tempo Conversão |
|---------|---------|-----------------|
| 5MB     | 30s     | ~5-10s         |
| 10MB    | 1min    | ~10-20s        |
| 25MB    | 2min    | ~20-40s        |
| 50MB    | 5min    | ~40-90s        |

*Tempos variam conforme CPU do servidor*

## Endpoints Afetados

### Avisos
- `POST /avisos` - Cria aviso com conversão automática
- `PUT /avisos/{id}/imagem` - Atualiza mídia do aviso

### Anúncios
- `POST /anuncios` - Cria anúncio com conversão automática
- `PUT /anuncios/{id}/imagem` - Atualiza mídia do anúncio

## Código Relevante

- **Função de conversão**: `app/storage.py` → `convert_video_to_mp4()`
- **Upload com conversão**: `app/storage.py` → `upload_image_to_r2()`
- **Tipos aceitos avisos**: `app/endpoints/avisos.py` (linha ~222)
- **Tipos aceitos anúncios**: `app/endpoints/anuncios.py` (linha ~62)

## Próximos Passos

1. ✅ Conversão automática implementada
2. ⏳ Monitorar performance em produção
3. ⏳ Adicionar preview de vídeo antes do upload
4. ⏳ Implementar fila de conversão para múltiplos uploads
5. ⏳ Adicionar suporte a thumbnails automáticos

#!/bin/bash

# Script para instalar FFmpeg no servidor

echo "🎬 Instalando FFmpeg..."

# Detectar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v apt-get &> /dev/null; then
        # Debian/Ubuntu
        sudo apt-get update
        sudo apt-get install -y ffmpeg
    elif command -v yum &> /dev/null; then
        # RedHat/CentOS
        sudo yum install -y ffmpeg
    fi
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Homebrew não encontrado. Instale com:"
        echo "/bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
fi

# Verificar instalação
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg instalado com sucesso!"
    ffmpeg -version | head -n 1
else
    echo "❌ Erro ao instalar FFmpeg"
    exit 1
fi

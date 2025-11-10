#!/bin/bash

# Script de Deploy para Fly.io - Expo TV Backend

echo "🚀 Deploy Expo TV Backend para Fly.io"
echo "======================================"
echo ""

# Verificar se flyctl está instalado
if ! command -v fly &> /dev/null; then
    echo "❌ Fly CLI não está instalado!"
    echo ""
    echo "Instale com:"
    echo "  brew install flyctl"
    echo "ou"
    echo "  curl -L https://fly.io/install.sh | sh"
    exit 1
fi

# Verificar se está logado
if ! fly auth whoami &> /dev/null; then
    echo "❌ Você não está logado no Fly.io"
    echo ""
    echo "Execute: fly auth login"
    exit 1
fi

echo "✅ Fly CLI instalado e autenticado"
echo ""

# Verificar se app existe
if ! fly status &> /dev/null; then
    echo "⚠️  App não existe ainda. Criando..."
    echo ""
    
    # Perguntar região
    echo "Escolha a região mais próxima:"
    echo "  gru - São Paulo, Brasil"
    echo "  gig - Rio de Janeiro, Brasil"
    echo "  iad - Virginia, EUA"
    echo ""
    read -p "Região (padrão: gru): " region
    region=${region:-gru}
    
    # Criar app
    fly apps create expo-tv-backend --org personal --region $region
    
    echo ""
    echo "📋 Configure os secrets antes do deploy:"
    echo ""
    echo "fly secrets set SECRET_KEY=\"sua-chave-secreta\""
    echo "fly secrets set DATABASE_URL=\"mysql+pymysql://user:pass@host:port/db\""
    echo "fly secrets set R2_ACCOUNT_ID=\"...\""
    echo "fly secrets set R2_ACCESS_KEY_ID=\"...\""
    echo "fly secrets set R2_SECRET_ACCESS_KEY=\"...\""
    echo "fly secrets set R2_BUCKET_NAME=\"...\""
    echo "fly secrets set R2_PUBLIC_URL=\"https://...\""
    echo ""
    read -p "Secrets configurados? (s/N): " configured
    
    if [[ ! $configured =~ ^[Ss]$ ]]; then
        echo "❌ Configure os secrets primeiro!"
        exit 1
    fi
fi

echo ""
echo "📦 Iniciando deploy..."
echo ""

# Deploy
fly deploy --ha=false

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Deploy concluído com sucesso!"
    echo ""
    echo "🌍 URL da aplicação:"
    fly status | grep "Hostname"
    echo ""
    echo "📊 Ver logs:"
    echo "  fly logs"
    echo ""
    echo "🔍 Abrir no navegador:"
    echo "  fly open"
    echo ""
    echo "📚 Documentação da API:"
    echo "  fly open /docs"
else
    echo ""
    echo "❌ Deploy falhou!"
    echo ""
    echo "Ver logs para debug:"
    echo "  fly logs"
fi

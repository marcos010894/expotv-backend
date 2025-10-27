#!/usr/bin/env python3
"""
Teste para verificar se as variáveis de ambiente estão sendo carregadas corretamente
"""

import os
import sys

# Carregar .env
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ python-dotenv carregado")
except ImportError:
    print("❌ python-dotenv não instalado")
    sys.exit(1)

print("\n" + "=" * 70)
print("🔍 Verificação de Variáveis de Ambiente")
print("=" * 70)

# Função auxiliar para mostrar variável (ocultar senhas)
def show_var(name, hide_value=False):
    value = os.getenv(name)
    if value:
        if hide_value and len(value) > 8:
            display = value[:4] + "..." + value[-4:]
        else:
            display = value
        print(f"  ✅ {name}: {display}")
        return True
    else:
        print(f"  ❌ {name}: NÃO CONFIGURADO")
        return False

# Banco de Dados
print("\n🗄️  BANCO DE DADOS:")
show_var("DB_USER")
show_var("DB_PASSWORD", hide_value=True)
show_var("DB_HOST")
show_var("DB_PORT")
show_var("DB_NAME")

# Email
print("\n📧 EMAIL (SMTP):")
show_var("SMTP_HOST")
show_var("SMTP_PORT")
show_var("SMTP_USER")
show_var("SMTP_PASSWORD", hide_value=True)
show_var("FROM_EMAIL")
show_var("FROM_NAME")

# Aplicação
print("\n🌐 APLICAÇÃO:")
show_var("FRONTEND_URL")
show_var("ENV")
show_var("SECRET_KEY", hide_value=True)

# Cloudflare R2
print("\n☁️  CLOUDFLARE R2:")
show_var("R2_ENDPOINT")
show_var("R2_ACCESS_KEY_ID", hide_value=True)
show_var("R2_SECRET_ACCESS_KEY", hide_value=True)
show_var("R2_BUCKET_NAME")
show_var("R2_PUBLIC_URL")

# Servidor
print("\n🚀 SERVIDOR:")
show_var("PORT")
show_var("HOST")

# Testar importação dos módulos
print("\n" + "=" * 70)
print("📦 Testando Importação dos Módulos")
print("=" * 70)

errors = []

try:
    from app.db import engine, DATABASE_URL
    print("  ✅ app.db importado com sucesso")
    print(f"     DATABASE_URL: {DATABASE_URL[:20]}...{DATABASE_URL[-15:]}")
except Exception as e:
    print(f"  ❌ Erro ao importar app.db: {e}")
    errors.append("app.db")

try:
    from app.auth import SECRET_KEY, ACCESS_TOKEN_EXPIRE_MINUTES
    print("  ✅ app.auth importado com sucesso")
    print(f"     SECRET_KEY: {SECRET_KEY[:8]}...{SECRET_KEY[-8:]}")
    print(f"     Token expira em: {ACCESS_TOKEN_EXPIRE_MINUTES} minutos")
except Exception as e:
    print(f"  ❌ Erro ao importar app.auth: {e}")
    errors.append("app.auth")

try:
    from app.storage import R2_ENDPOINT, R2_BUCKET, R2_ACCESS_KEY
    print("  ✅ app.storage importado com sucesso")
    print(f"     R2_BUCKET: {R2_BUCKET}")
    print(f"     R2_ACCESS_KEY: {R2_ACCESS_KEY[:8]}...{R2_ACCESS_KEY[-8:]}")
except Exception as e:
    print(f"  ❌ Erro ao importar app.storage: {e}")
    errors.append("app.storage")

try:
    from app.email_service import SMTP_HOST, SMTP_USER, FROM_NAME
    print("  ✅ app.email_service importado com sucesso")
    print(f"     SMTP: {SMTP_USER} via {SMTP_HOST}")
    print(f"     From Name: {FROM_NAME}")
except Exception as e:
    print(f"  ❌ Erro ao importar app.email_service: {e}")
    errors.append("app.email_service")

# Resultado final
print("\n" + "=" * 70)
if errors:
    print(f"❌ Erros encontrados em: {', '.join(errors)}")
    print("\n🔧 Possíveis soluções:")
    print("  1. Verifique se o arquivo .env existe")
    print("  2. Verifique se todas as variáveis estão preenchidas")
    print("  3. Certifique-se de que python-dotenv está instalado")
    print("  4. Reinicie o servidor se estiver rodando")
    sys.exit(1)
else:
    print("✅ Todas as variáveis de ambiente estão configuradas corretamente!")
    print("✅ Todos os módulos foram importados com sucesso!")
    print("\n🚀 O sistema está pronto para uso!")
    print("\n💡 Próximos passos:")
    print("  1. Iniciar servidor: uvicorn app.main:app --reload")
    print("  2. Testar email: python test_email.py")
    print("  3. Acessar docs: http://localhost:8000/docs")
    sys.exit(0)

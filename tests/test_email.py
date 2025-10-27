#!/usr/bin/env python3
"""
Teste de envio de email usando as configurações do .env
"""

import sys
import os

# Carregar variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("⚠️ python-dotenv não instalado. Usando variáveis de ambiente do sistema.")

from app.email_service import send_password_reset_email, send_password_changed_notification

print("=" * 70)
print("📧 Teste de Envio de Email - EXPO TV")
print("=" * 70)

# Mostrar configurações
print("\n🔧 Configurações SMTP:")
print(f"  Host: {os.getenv('SMTP_HOST', 'smtp.gmail.com')}")
print(f"  Port: {os.getenv('SMTP_PORT', '587')}")
print(f"  User: {os.getenv('SMTP_USER', 'Não configurado')}")
print(f"  From: {os.getenv('FROM_EMAIL', 'Não configurado')}")
print(f"  Nome: {os.getenv('FROM_NAME', 'EXPO TV')}")

# Pedir email de destino
print("\n" + "=" * 70)
email_destino = input("📨 Digite o email de destino para teste: ").strip()

if not email_destino:
    print("❌ Email não fornecido. Abortando.")
    sys.exit(1)

# Validar email básico
if "@" not in email_destino or "." not in email_destino:
    print("❌ Email inválido. Abortando.")
    sys.exit(1)

print("\n" + "=" * 70)
print("📤 Enviando email de teste...")
print("=" * 70)

# Teste 1: Email de reset de senha
print("\n1️⃣ Teste: Email de Recuperação de Senha")
print("-" * 70)

token_fake = "TOKEN_FAKE_PARA_TESTE_123456"
nome_usuario = "Usuário Teste"

print(f"  Para: {email_destino}")
print(f"  Tipo: Recuperação de senha")
print(f"  Token: {token_fake}")

sucesso = send_password_reset_email(
    to_email=email_destino,
    reset_token=token_fake,
    user_name=nome_usuario
)

if sucesso:
    print("\n✅ Email de recuperação enviado com sucesso!")
    print(f"   Verifique a caixa de entrada de: {email_destino}")
else:
    print("\n❌ Falha ao enviar email de recuperação!")
    print("   Verifique as configurações SMTP no .env")

# Teste 2: Email de confirmação
print("\n" + "=" * 70)
print("2️⃣ Teste: Email de Confirmação de Senha Alterada")
print("-" * 70)

print(f"  Para: {email_destino}")
print(f"  Tipo: Confirmação de alteração")

sucesso2 = send_password_changed_notification(
    to_email=email_destino,
    user_name=nome_usuario
)

if sucesso2:
    print("\n✅ Email de confirmação enviado com sucesso!")
    print(f"   Verifique a caixa de entrada de: {email_destino}")
else:
    print("\n❌ Falha ao enviar email de confirmação!")
    print("   Verifique as configurações SMTP no .env")

# Resultado final
print("\n" + "=" * 70)
if sucesso or sucesso2:
    print("✅ Pelo menos um email foi enviado com sucesso!")
    print("\n📬 Verificações:")
    print("  1. Verifique a caixa de entrada")
    print("  2. Verifique a pasta de SPAM/Lixo Eletrônico")
    print("  3. Se não receber, verifique as configurações em .env")
else:
    print("❌ Nenhum email foi enviado!")
    print("\n🔧 Possíveis problemas:")
    print("  1. SMTP_USER ou SMTP_PASSWORD incorretos em .env")
    print("  2. Senha de app do Gmail incorreta")
    print("  3. Firewall bloqueando porta 587")
    print("  4. Email remetente bloqueado pelo Gmail")
    print("\n💡 Solução:")
    print("  1. Verifique se .env tem as credenciais corretas")
    print("  2. Use 'senha de app' do Gmail (não a senha normal)")
    print("  3. Ative verificação em 2 etapas no Gmail")
    print("  4. Crie senha de app em: https://myaccount.google.com/apppasswords")

print("=" * 70)

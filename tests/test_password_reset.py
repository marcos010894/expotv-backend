#!/usr/bin/env python3
"""
Teste do sistema de recuperação de senha
"""

import requests
import json

API_URL = "http://localhost:8000"

print("🧪 Testando Sistema de Recuperação de Senha\n")

# 1. Teste: Forgot Password
print("=" * 60)
print("1️⃣ Teste: POST /forgot-password")
print("=" * 60)

# Buscar um usuário existente primeiro
users_response = requests.get(f"{API_URL}/users")
if users_response.status_code == 200:
    users = users_response.json()
    if users:
        test_email = users[0]['email']
        print(f"📧 Usando email de teste: {test_email}")
    else:
        print("⚠️ Nenhum usuário encontrado. Usando email fake para teste.")
        test_email = "teste@example.com"
else:
    test_email = "teste@example.com"

forgot_data = {
    "email": test_email
}

print(f"\n📤 Enviando: {json.dumps(forgot_data, indent=2)}")

response = requests.post(
    f"{API_URL}/forgot-password",
    json=forgot_data
)

print(f"\n📊 Status: {response.status_code}")
print(f"📋 Resposta:")
print(json.dumps(response.json(), indent=2))

if response.status_code == 200:
    print("\n✅ Teste 1 passou!")
    
    # Em modo desenvolvimento, pegar token da resposta
    response_data = response.json()
    if 'dev_token' in response_data:
        token = response_data['dev_token']
        print(f"\n🔑 Token de desenvolvimento: {token}")
        
        # 2. Teste: Reset Password
        print("\n" + "=" * 60)
        print("2️⃣ Teste: POST /reset-password")
        print("=" * 60)
        
        reset_data = {
            "token": token,
            "new_password": "NovaSenha123"
        }
        
        print(f"\n📤 Enviando: {json.dumps(reset_data, indent=2)}")
        
        reset_response = requests.post(
            f"{API_URL}/reset-password",
            json=reset_data
        )
        
        print(f"\n📊 Status: {reset_response.status_code}")
        print(f"📋 Resposta:")
        print(json.dumps(reset_response.json(), indent=2))
        
        if reset_response.status_code == 200:
            print("\n✅ Teste 2 passou!")
        else:
            print("\n❌ Teste 2 falhou!")
    else:
        print("\n⚠️ Token não retornado (modo produção). Configure ENV=development para testar.")
else:
    print("\n❌ Teste 1 falhou!")

# 3. Teste: Forgot Password com email inexistente (deve retornar sucesso por segurança)
print("\n" + "=" * 60)
print("3️⃣ Teste: POST /forgot-password (email inexistente)")
print("=" * 60)

fake_data = {
    "email": "email-que-nao-existe@fake.com"
}

print(f"\n📤 Enviando: {json.dumps(fake_data, indent=2)}")

fake_response = requests.post(
    f"{API_URL}/forgot-password",
    json=fake_data
)

print(f"\n📊 Status: {fake_response.status_code}")
print(f"📋 Resposta:")
print(json.dumps(fake_response.json(), indent=2))

if fake_response.status_code == 200 and fake_response.json().get('success'):
    print("\n✅ Teste 3 passou! (Sempre retorna sucesso por segurança)")
else:
    print("\n❌ Teste 3 falhou!")

# 4. Teste: Reset com token inválido
print("\n" + "=" * 60)
print("4️⃣ Teste: POST /reset-password (token inválido)")
print("=" * 60)

invalid_data = {
    "token": "token-invalido-fake-123",
    "new_password": "NovaSenha123"
}

print(f"\n📤 Enviando: {json.dumps(invalid_data, indent=2)}")

invalid_response = requests.post(
    f"{API_URL}/reset-password",
    json=invalid_data
)

print(f"\n📊 Status: {invalid_response.status_code}")
print(f"📋 Resposta:")
print(json.dumps(invalid_response.json(), indent=2))

if invalid_response.status_code == 400:
    print("\n✅ Teste 4 passou! (Rejeita token inválido)")
else:
    print("\n❌ Teste 4 falhou!")

# 5. Teste: Reset com senha muito curta
print("\n" + "=" * 60)
print("5️⃣ Teste: POST /reset-password (senha muito curta)")
print("=" * 60)

short_password_data = {
    "token": "token-fake",
    "new_password": "123"  # Menos de 6 caracteres
}

print(f"\n📤 Enviando: {json.dumps(short_password_data, indent=2)}")

short_response = requests.post(
    f"{API_URL}/reset-password",
    json=short_password_data
)

print(f"\n📊 Status: {short_response.status_code}")
print(f"📋 Resposta:")
print(json.dumps(short_response.json(), indent=2))

if short_response.status_code == 400:
    print("\n✅ Teste 5 passou! (Valida tamanho mínimo de senha)")
else:
    print("\n❌ Teste 5 falhou!")

print("\n" + "=" * 60)
print("🏁 Testes concluídos!")
print("=" * 60)
print("\n💡 Dica: Para testar completamente, configure o SMTP no .env")
print("   e verifique se os emails estão sendo enviados.\n")

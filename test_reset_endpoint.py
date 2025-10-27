#!/usr/bin/env python3
"""
Teste simples do endpoint de reset de senha
"""
import requests
import json

# URL do servidor
BASE_URL = "http://localhost:8000"

print("🧪 Teste do Endpoint de Reset de Senha")
print("=" * 60)

# 1. Primeiro, criar um token de teste diretamente no banco
print("\n1️⃣ Solicitando reset de senha...")
response = requests.post(
    f"{BASE_URL}/forgot-password",
    json={"email": "admin@expotv.com.br"},
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")

# 2. Testar com um token fake (deve dar erro)
print("\n2️⃣ Testando com token inválido...")
test_data = {
    "token": "token-fake-123",
    "new_password": "senha123"
}

print(f"Enviando: {json.dumps(test_data, indent=2)}")

response = requests.post(
    f"{BASE_URL}/reset-password",
    json=test_data,
    headers={"Content-Type": "application/json"}
)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.text}")

# 3. Testar formato do JSON
print("\n3️⃣ Verificando formato JSON...")
json_string = json.dumps(test_data)
print(f"JSON válido: {json_string}")
print(f"Sem caracteres de controle: {repr(json_string)}")

print("\n✅ Teste concluído!")
print("\n📋 Para testar com token real:")
print("   1. Acesse o banco de dados")
print("   2. Execute: SELECT reset_token FROM user WHERE email='admin@expotv.com.br'")
print("   3. Use o token retornado no teste")

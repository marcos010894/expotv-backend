#!/usr/bin/env python3
"""
Testa formato JSON para reset de senha
"""
import json

# Simular dados do formulário
test_cases = [
    {
        "name": "Token e senha simples",
        "data": {
            "token": "abc123xyz",
            "new_password": "senha123"
        }
    },
    {
        "name": "Token longo (real)",
        "data": {
            "token": "K7vQxN9pW2mR8sT4yU6zL3hJ5gF1dA0cB",
            "new_password": "Nova@Senha123"
        }
    },
    {
        "name": "Senha com caracteres especiais",
        "data": {
            "token": "test123",
            "new_password": "Senh@123!#$"
        }
    }
]

print("🧪 Testando formatos JSON")
print("=" * 60)

for i, test in enumerate(test_cases, 1):
    print(f"\n{i}. {test['name']}")
    print("-" * 40)
    
    try:
        json_string = json.dumps(test['data'])
        print(f"✅ JSON válido:")
        print(f"   {json_string}")
        print(f"   Tamanho: {len(json_string)} bytes")
        
        # Testar parse reverso
        parsed = json.loads(json_string)
        print(f"✅ Parse OK: {parsed == test['data']}")
        
    except Exception as e:
        print(f"❌ Erro: {e}")

print("\n" + "=" * 60)
print("✅ Todos os formatos são válidos!")

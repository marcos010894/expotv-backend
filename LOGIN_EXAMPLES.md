# Exemplo de uso da função de login

## 1. Login Simples (Novo endpoint criado)

POST http://localhost:8000/login
Content-Type: application/json

{
    "email": "admin@admin.com",
    "senha": "admin123"
}

### Resposta esperada:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user_id": 1,
    "user_name": "Administrador",
    "user_type": "ADM"
}
```

## 2. Login OAuth2 (Para compatibilidade com Swagger)

POST http://localhost:8000/token
Content-Type: application/x-www-form-urlencoded

username=admin@admin.com&password=admin123

### Resposta esperada:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
    "token_type": "bearer",
    "user": {
        "id": 1,
        "nome": "Administrador",
        "email": "admin@admin.com",
        "tipo": "ADM"
    }
}
```

## 3. Usar o token em outras requisições

Para acessar rotas protegidas, inclua o token no header:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## 4. Verificar usuário logado

GET http://localhost:8000/me
Authorization: Bearer {seu_token}

### Resposta:
```json
{
    "id": 1,
    "nome": "Administrador",
    "email": "admin@admin.com",
    "tipo": "ADM"
}
```

## 5. Registrar novo usuário

POST http://localhost:8000/register
Content-Type: application/x-www-form-urlencoded

nome=João Silva&email=joao@email.com&senha=123456&tipo=SINDICO

### Resposta:
```json
{
    "message": "Usuário criado com sucesso",
    "user": {
        "id": 2,
        "nome": "João Silva",
        "email": "joao@email.com",
        "tipo": "SINDICO"
    }
}
```

## Endpoints de autenticação disponíveis:

- **POST /login** - Login simples com JSON
- **POST /token** - Login OAuth2 (para Swagger)
- **POST /register** - Registrar novo usuário
- **GET /me** - Dados do usuário logado (requer token)

## Teste no Swagger:
Acesse http://localhost:8000/docs e teste os endpoints de autenticação!

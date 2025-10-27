#!/usr/bin/env python3
"""
Script de instalação/setup completo do banco de dados EXPO TV

Este script:
1. Cria todas as tabelas do zero (se não existirem)
2. Adiciona campos novos em tabelas existentes (migrações)
3. Insere dados iniciais (usuário admin)
4. Valida a estrutura do banco

Use este script para:
- Instalação inicial em banco novo
- Atualização de banco existente
"""

from sqlmodel import SQLModel, create_engine, Session, select, text
from urllib.parse import quote_plus
import sys
from datetime import datetime

# Importar todos os modelos
from app.models import User, Condominio, TV, Anuncio, Aviso
from app.auth import get_password_hash

# Configuração do banco
usuario = "u441041902_exportv"
senha = quote_plus("Mito010894@@")
host = "193.203.175.53"
banco = "u441041902_exportv"
porta = 3306

DATABASE_URL = f"mysql+pymysql://{usuario}:{senha}@{host}:{porta}/{banco}"

print("=" * 70)
print("🚀 EXPO TV - Setup do Banco de Dados")
print("=" * 70)
print(f"\n📊 Conectando em: {host}:{porta}/{banco}")

engine = create_engine(DATABASE_URL, echo=False)


def check_column_exists(table_name: str, column_name: str) -> bool:
    """Verifica se uma coluna existe em uma tabela"""
    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{banco}' 
            AND TABLE_NAME = '{table_name}'
            AND COLUMN_NAME = '{column_name}'
        """))
        return len(list(result)) > 0


def add_column_if_not_exists(table_name: str, column_name: str, column_definition: str):
    """Adiciona uma coluna se ela não existir"""
    if not check_column_exists(table_name, column_name):
        print(f"  ➕ Adicionando coluna '{column_name}' na tabela '{table_name}'...")
        with engine.connect() as conn:
            conn.execute(text(f"""
                ALTER TABLE {table_name} 
                ADD COLUMN {column_name} {column_definition}
            """))
            conn.commit()
        print(f"  ✅ Coluna '{column_name}' adicionada!")
    else:
        print(f"  ℹ️  Coluna '{column_name}' já existe em '{table_name}'")


def create_tables():
    """Cria todas as tabelas do sistema"""
    print("\n📦 Criando/Verificando tabelas...")
    
    try:
        # Criar todas as tabelas definidas nos modelos
        SQLModel.metadata.create_all(engine)
        print("✅ Tabelas criadas/verificadas com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao criar tabelas: {e}")
        return False


def run_migrations():
    """Executa migrações para campos adicionados após criação inicial"""
    print("\n🔄 Executando migrações...")
    
    # Migração 1: Campo last_ping na tabela TV
    print("\n  🔧 Migração 1: Campo last_ping (TV heartbeat)")
    add_column_if_not_exists('tv', 'last_ping', 'DATETIME NULL')
    
    # Migração 2: Campos de reset de senha na tabela User
    print("\n  🔧 Migração 2: Campos de recuperação de senha")
    add_column_if_not_exists('user', 'reset_token', 'VARCHAR(255) NULL')
    add_column_if_not_exists('user', 'reset_token_expires', 'DATETIME NULL')
    
    # Migração 3: Expandir archive_url para TEXT (se ainda for VARCHAR)
    print("\n  🔧 Migração 3: Expandir archive_url para TEXT")
    with engine.connect() as conn:
        # Verificar tipo atual de archive_url em anuncio
        result = conn.execute(text(f"""
            SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{banco}' 
            AND TABLE_NAME = 'anuncio'
            AND COLUMN_NAME = 'archive_url'
        """))
        row = result.fetchone()
        
        if row and row[0] == 'varchar':
            print(f"  ➕ Alterando archive_url de VARCHAR({row[1]}) para TEXT em anuncio...")
            conn.execute(text("ALTER TABLE anuncio MODIFY COLUMN archive_url TEXT NULL"))
            conn.commit()
            print("  ✅ archive_url alterado em anuncio!")
        else:
            print("  ℹ️  archive_url já é TEXT em anuncio")
        
        # Verificar em aviso
        result = conn.execute(text(f"""
            SELECT DATA_TYPE, CHARACTER_MAXIMUM_LENGTH
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = '{banco}' 
            AND TABLE_NAME = 'aviso'
            AND COLUMN_NAME = 'archive_url'
        """))
        row = result.fetchone()
        
        if row and row[0] == 'varchar':
            print(f"  ➕ Alterando archive_url de VARCHAR({row[1]}) para TEXT em aviso...")
            conn.execute(text("ALTER TABLE aviso MODIFY COLUMN archive_url TEXT NULL"))
            conn.commit()
            print("  ✅ archive_url alterado em aviso!")
        else:
            print("  ℹ️  archive_url já é TEXT em aviso")
    
    print("\n✅ Migrações concluídas!")


def create_admin_user():
    """Cria usuário administrador padrão se não existir"""
    print("\n👤 Verificando usuário administrador...")
    
    with Session(engine) as session:
        # Verificar se já existe algum admin
        admin = session.exec(
            select(User).where(User.tipo == 'ADM')
        ).first()
        
        if admin:
            print(f"  ℹ️  Usuário admin já existe: {admin.email}")
            return
        
        # Criar admin padrão
        print("  ➕ Criando usuário administrador padrão...")
        
        admin_user = User(
            tipo='ADM',
            nome='Administrador',
            email='admin@expotv.com.br',
            senha=get_password_hash('admin123'),  # Senha padrão: admin123
            telefone=None,
            foto_url=None,
            limite_avisos=999,  # Admin sem limite
            data_criacao=datetime.utcnow()
        )
        
        session.add(admin_user)
        session.commit()
        
        print("  ✅ Administrador criado com sucesso!")
        print("  📧 Email: admin@expotv.com.br")
        print("  🔑 Senha: admin123")
        print("  ⚠️  IMPORTANTE: Altere a senha após o primeiro login!")


def show_database_info():
    """Mostra informações sobre o banco de dados"""
    print("\n📊 Informações do Banco de Dados:")
    print("=" * 70)
    
    with engine.connect() as conn:
        # Listar todas as tabelas
        result = conn.execute(text(f"""
            SELECT TABLE_NAME, TABLE_ROWS 
            FROM INFORMATION_SCHEMA.TABLES 
            WHERE TABLE_SCHEMA = '{banco}'
            AND TABLE_TYPE = 'BASE TABLE'
            ORDER BY TABLE_NAME
        """))
        
        print("\n📋 Tabelas criadas:")
        for row in result:
            print(f"  - {row[0]}: {row[1] or 0} registros")
        
        # Contar usuários
        result = conn.execute(text("SELECT COUNT(*) FROM user"))
        total_users = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(*) FROM user WHERE tipo = 'ADM'"))
        total_admins = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(*) FROM user WHERE tipo = 'SINDICO'"))
        total_sindicos = result.fetchone()[0]
        
        print(f"\n👥 Usuários:")
        print(f"  - Total: {total_users}")
        print(f"  - Admins: {total_admins}")
        print(f"  - Síndicos: {total_sindicos}")
        
        # Contar outros dados
        result = conn.execute(text("SELECT COUNT(*) FROM condominio"))
        total_condominios = result.fetchone()[0]
        print(f"\n🏢 Condomínios: {total_condominios}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM tv"))
        total_tvs = result.fetchone()[0]
        
        result = conn.execute(text("SELECT COUNT(*) FROM tv WHERE status = 'online'"))
        tvs_online = result.fetchone()[0]
        
        print(f"\n📺 TVs:")
        print(f"  - Total: {total_tvs}")
        print(f"  - Online: {tvs_online}")
        print(f"  - Offline: {total_tvs - tvs_online}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM anuncio"))
        total_anuncios = result.fetchone()[0]
        print(f"\n📢 Anúncios: {total_anuncios}")
        
        result = conn.execute(text("SELECT COUNT(*) FROM aviso"))
        total_avisos = result.fetchone()[0]
        print(f"\n📋 Avisos: {total_avisos}")


def main():
    """Função principal de setup"""
    try:
        # 1. Criar tabelas
        if not create_tables():
            print("\n❌ Falha ao criar tabelas. Abortando...")
            sys.exit(1)
        
        # 2. Executar migrações
        run_migrations()
        
        # 3. Criar admin se necessário
        create_admin_user()
        
        # 4. Mostrar informações
        show_database_info()
        
        print("\n" + "=" * 70)
        print("✅ Setup do banco de dados concluído com sucesso!")
        print("=" * 70)
        
        print("\n🚀 Próximos passos:")
        print("  1. Configure o arquivo .env com as credenciais do banco")
        print("  2. Configure o SMTP para envio de emails (opcional)")
        print("  3. Inicie o servidor: uvicorn app.main:app --reload")
        print("  4. Acesse a documentação: http://localhost:8000/docs")
        print("  5. Faça login com admin@expotv.com.br / admin123")
        print("  6. ⚠️  IMPORTANTE: Altere a senha do admin!")
        
        print("\n📚 Documentação:")
        print("  - Sistema completo: README.md")
        print("  - Autenticação: AUTENTICACAO.md")
        print("  - Recuperação de senha: PASSWORD_RESET_GUIDE.md")
        print("  - TV Heartbeat: TV_HEARTBEAT_GUIDE.md")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Erro durante o setup: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)

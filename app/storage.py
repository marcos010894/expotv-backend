import boto3
from botocore.config import Config
import os
from datetime import datetime
import uuid

# Configurações do Cloudflare R2
R2_ENDPOINT = "https://6d3e10284be29ce7a44f10d4dc047ad4.r2.cloudflarestorage.com"
R2_BUCKET = "ged"
R2_PUBLIC_URL = "https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev"  # URL pública personalizada
R2_ACCESS_KEY = "77a2210f3311c69b54b2663a3dfe9b4b"
R2_SECRET_KEY = "8c5968c864386322f9afc7f5b6c99ef6e3c91a078c0987a9fd4db1c033fce22d"

# Cliente S3 compatível para R2
s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def upload_image_to_r2(file_content: bytes, filename: str, content_type: str) -> str:
    """
    Faz upload de uma imagem para o Cloudflare R2
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome original do arquivo
        content_type: Tipo MIME do arquivo
    
    Returns:
        URL pública da imagem
    """
    try:
        # Gerar nome único para o arquivo
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"anuncios/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}.{file_extension}"
        
        # Upload para R2
        s3_client.put_object(
            Bucket=R2_BUCKET,
            Key=unique_filename,
            Body=file_content,
            ContentType=content_type,
            ACL='public-read'  # Tornar público
        )
        
        # Retornar URL pública personalizada
        public_url = f"{R2_PUBLIC_URL}/{unique_filename}"
        return public_url
        
    except Exception as e:
        raise Exception(f"Erro no upload: {str(e)}")

def delete_image_from_r2(image_url: str) -> bool:
    """
    Remove uma imagem do R2
    
    Args:
        image_url: URL da imagem a ser removida
    
    Returns:
        True se removido com sucesso
    """
    try:
        # Extrair key da URL pública personalizada
        key = image_url.replace(f"{R2_PUBLIC_URL}/", "")
        
        s3_client.delete_object(
            Bucket=R2_BUCKET,
            Key=key
        )
        
        return True
        
    except Exception as e:
        print(f"Erro ao deletar imagem: {str(e)}")
        return False

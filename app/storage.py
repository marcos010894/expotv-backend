import boto3
from botocore.config import Config
import os
from datetime import datetime
import uuid
import subprocess
import tempfile
from pathlib import Path

# Carregar variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Em produção, variáveis já estarão no ambiente

# Configurações do Cloudflare R2 a partir de variáveis de ambiente
R2_ENDPOINT = os.getenv(
    "R2_ENDPOINT", 
    "https://6d3e10284be29ce7a44f10d4dc047ad4.r2.cloudflarestorage.com"
)
R2_BUCKET = os.getenv("R2_BUCKET_NAME", "ged")
R2_PUBLIC_URL = os.getenv(
    "R2_PUBLIC_URL", 
    "https://pub-44038362d56e40da83d1c72eaec658c5.r2.dev"
)
R2_ACCESS_KEY = os.getenv("R2_ACCESS_KEY_ID", "77a2210f3311c69b54b2663a3dfe9b4b")
R2_SECRET_KEY = os.getenv(
    "R2_SECRET_ACCESS_KEY", 
    "8c5968c864386322f9afc7f5b6c99ef6e3c91a078c0987a9fd4db1c033fce22d"
)

# Cliente S3 compatível para R2
s3_client = boto3.client(
    's3',
    endpoint_url=R2_ENDPOINT,
    aws_access_key_id=R2_ACCESS_KEY,
    aws_secret_access_key=R2_SECRET_KEY,
    config=Config(signature_version='s3v4'),
    region_name='auto'
)

def convert_video_to_mp4(input_content: bytes, input_filename: str) -> tuple[bytes, str]:
    """
    Converte qualquer vídeo para MP4 usando FFmpeg
    
    Args:
        input_content: Conteúdo do vídeo em bytes
        input_filename: Nome original do arquivo
    
    Returns:
        Tuple com (conteúdo MP4 em bytes, content_type)
    """
    temp_input = None
    temp_output = None
    
    try:
        # Criar arquivos temporários
        input_ext = Path(input_filename).suffix
        with tempfile.NamedTemporaryFile(delete=False, suffix=input_ext) as temp_input:
            temp_input.write(input_content)
            temp_input_path = temp_input.name
        
        temp_output_path = temp_input_path.replace(input_ext, '.mp4')
        
        # Converter usando FFmpeg com configurações otimizadas e simples
        # -y: sobrescrever sem perguntar
        # -i: arquivo de entrada
        # -c:v libx264: codec de vídeo H.264
        # -preset fast: velocidade de conversão
        # -crf 23: qualidade (18-28, menor = melhor)
        # -pix_fmt yuv420p: compatibilidade máxima
        # -an: sem áudio (simplifica e evita erros)
        # -movflags +faststart: otimizar para streaming web
        command = [
            'ffmpeg',
            '-y',
            '-i', temp_input_path,
            '-c:v', 'libx264',
            '-preset', 'fast',
            '-crf', '23',
            '-pix_fmt', 'yuv420p',
            '-an',  # Remover áudio - vídeos para TV geralmente não precisam
            '-movflags', '+faststart',
            temp_output_path
        ]
        
        # Executar conversão
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutos de timeout
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg erro: {result.stderr}")
        
        # Ler arquivo convertido
        with open(temp_output_path, 'rb') as f:
            converted_content = f.read()
        
        return converted_content, 'video/mp4'
        
    except subprocess.TimeoutExpired:
        raise Exception("Conversão de vídeo excedeu tempo limite de 5 minutos")
    except FileNotFoundError:
        raise Exception("FFmpeg não encontrado. Instale com: apt-get install ffmpeg")
    except Exception as e:
        raise Exception(f"Erro na conversão de vídeo: {str(e)}")
    finally:
        # Limpar arquivos temporários
        try:
            if temp_input_path and os.path.exists(temp_input_path):
                os.unlink(temp_input_path)
            if temp_output_path and os.path.exists(temp_output_path):
                os.unlink(temp_output_path)
        except:
            pass

def upload_image_to_r2(file_content: bytes, filename: str, content_type: str) -> str:
    """
    Faz upload de uma imagem ou vídeo para o Cloudflare R2
    Converte automaticamente vídeos para MP4
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome original do arquivo
        content_type: Tipo MIME do arquivo
    
    Returns:
        URL pública da mídia
    """
    try:
        # Se for vídeo e NÃO for MP4, converter
        is_video = content_type.startswith('video/')
        is_compatible = content_type in ['video/mp4', 'video/quicktime']
        
        if is_video and not is_compatible:
            print(f"🎬 Convertendo vídeo {filename} para MP4...")
            file_content, content_type = convert_video_to_mp4(file_content, filename)
            # Trocar extensão para .mp4
            filename = filename.rsplit('.', 1)[0] + '.mp4'
            print(f"✅ Conversão concluída!")
        
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

def upload_media_to_r2(file_content: bytes, filename: str, content_type: str, media_type: str = "anuncios") -> str:
    """
    Faz upload de mídia (imagem ou vídeo) para o Cloudflare R2
    Converte automaticamente vídeos para MP4
    
    Args:
        file_content: Conteúdo do arquivo em bytes
        filename: Nome original do arquivo
        content_type: Tipo MIME do arquivo
        media_type: Tipo de pasta (anuncios, avisos, etc)
    
    Returns:
        URL pública da mídia
    """
    try:
        # Se for vídeo e NÃO for MP4, converter
        is_video = content_type.startswith('video/')
        is_compatible = content_type in ['video/mp4', 'video/quicktime']
        
        if is_video and not is_compatible:
            print(f"🎬 Convertendo vídeo {filename} para MP4...")
            file_content, content_type = convert_video_to_mp4(file_content, filename)
            # Trocar extensão para .mp4
            filename = filename.rsplit('.', 1)[0] + '.mp4'
            print(f"✅ Conversão concluída!")
        
        # Gerar nome único para o arquivo
        file_extension = filename.split('.')[-1] if '.' in filename else 'jpg'
        unique_filename = f"{media_type}/{datetime.now().strftime('%Y/%m/%d')}/{uuid.uuid4()}.{file_extension}"
        
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
    Remove uma imagem ou vídeo do R2
    
    Args:
        image_url: URL da mídia a ser removida
    
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
        print(f"Erro ao deletar mídia: {str(e)}")
        return False

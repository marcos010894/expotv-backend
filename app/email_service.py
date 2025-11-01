"""
Serviço de envio de emails para recuperação de senha
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from typing import Optional

# Carregar variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # Em produção, variáveis já estarão no ambiente

# Configurações de email (usar variáveis de ambiente)
SMTP_HOST = os.getenv("SMTP_HOST", "")
SMTP_PORT = int(os.getenv("SMTP_PORT", ""))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
FROM_EMAIL = os.getenv("FROM_EMAIL", SMTP_USER)
FROM_NAME = os.getenv("FROM_NAME", "EXPO TV")

# URL do frontend para reset de senha
FRONTEND_URL = os.getenv("FRONTEND_URL", "https://expotv.com.br")
# URL do backend para a página de reset
BACKEND_URL = os.getenv("BACKEND_URL", "https://expotv-backend.fly.dev")


def send_password_reset_email(to_email: str, reset_token: str, user_name: str) -> bool:
    """
    Envia email com link para resetar senha
    
    Args:
        to_email: Email do destinatário
        reset_token: Token único para reset
        user_name: Nome do usuário
        
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    
    # Link de reset - aponta para a página HTML no backend
    reset_link = f"{BACKEND_URL}/reset-password-page?token={reset_token}"
    
    # HTML do email
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #213547;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .button {{
                display: inline-block;
                padding: 12px 30px;
                background-color: #213547;
                color: white;
                text-decoration: none;
                border-radius: 5px;
                margin: 20px 0;
            }}
            .button:hover {{
                background-color: #2d4a63;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
            .warning {{
                background-color: #fff3cd;
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔒 Recuperação de Senha</h1>
            </div>
            <div class="content">
                <p>Olá <strong>{user_name}</strong>,</p>
                
                <p>Recebemos uma solicitação para redefinir a senha da sua conta no <strong>EXPO TV</strong>.</p>
                
                <p>Para criar uma nova senha, clique no botão abaixo:</p>
                
                <center>
                    <a href="{reset_link}" class="button">Redefinir Senha</a>
                </center>
                
                <p>Ou copie e cole este link no seu navegador:</p>
                <p style="background-color: #f5f5f5; padding: 10px; border-radius: 5px; word-break: break-all;">
                    {reset_link}
                </p>
                
                <div class="warning">
                    <strong>⚠️ Importante:</strong>
                    <ul>
                        <li>Este link é válido por <strong>1 hora</strong></li>
                        <li>Se você não solicitou esta alteração, ignore este email</li>
                        <li>Sua senha atual permanecerá ativa até você criar uma nova</li>
                    </ul>
                </div>
                
                <p>Se tiver alguma dúvida, entre em contato com nosso suporte.</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe EXPO TV</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EXPO TV - Sistema de Gestão para Condomínios</p>
                <p>Este é um email automático, por favor não responda.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Texto alternativo (para clientes que não suportam HTML)
    text_content = f"""
    Recuperação de Senha - EXPO TV
    
    Olá {user_name},
    
    Recebemos uma solicitação para redefinir a senha da sua conta.
    
    Para criar uma nova senha, acesse o link abaixo:
    {reset_link}
    
    Este link é válido por 1 hora.
    
    Se você não solicitou esta alteração, ignore este email.
    
    Atenciosamente,
    Equipe EXPO TV
    """
    
    try:
        # Criar mensagem
        message = MIMEMultipart("alternative")
        message["Subject"] = "🔒 Recuperação de Senha - EXPO TV"
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        # Adicionar ambas as versões
        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        
        message.attach(part1)
        message.attach(part2)
        
        # Conectar e enviar
        if not SMTP_USER or not SMTP_PASSWORD:
            print("⚠️ SMTP não configurado. Email não será enviado.")
            print(f"Link de reset (modo dev): {reset_link}")
            return False
            
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Email enviado para {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar email: {str(e)}")
        print(f"Link de reset (modo dev): {reset_link}")
        return False


def send_password_changed_notification(to_email: str, user_name: str) -> bool:
    """
    Envia notificação de que a senha foi alterada com sucesso
    
    Args:
        to_email: Email do destinatário
        user_name: Nome do usuário
        
    Returns:
        True se enviado com sucesso, False caso contrário
    """
    
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                color: #333;
            }}
            .container {{
                max-width: 600px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f9f9f9;
            }}
            .header {{
                background-color: #213547;
                color: white;
                padding: 20px;
                text-align: center;
                border-radius: 5px 5px 0 0;
            }}
            .content {{
                background-color: white;
                padding: 30px;
                border-radius: 0 0 5px 5px;
            }}
            .success {{
                background-color: #d4edda;
                border: 1px solid #213547;
                padding: 15px;
                border-radius: 5px;
                margin: 15px 0;
            }}
            .footer {{
                text-align: center;
                margin-top: 20px;
                font-size: 12px;
                color: #666;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ Senha Alterada</h1>
            </div>
            <div class="content">
                <p>Olá <strong>{user_name}</strong>,</p>
                
                <div class="success">
                    <strong>✅ Sucesso!</strong><br>
                    Sua senha foi alterada com sucesso.
                </div>
                
                <p>Se você não realizou esta alteração, entre em contato com nosso suporte imediatamente.</p>
                
                <p>Atenciosamente,<br>
                <strong>Equipe EXPO TV</strong></p>
            </div>
            <div class="footer">
                <p>© 2025 EXPO TV - Sistema de Gestão para Condomínios</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    text_content = f"""
    Senha Alterada - EXPO TV
    
    Olá {user_name},
    
    Sua senha foi alterada com sucesso.
    
    Se você não realizou esta alteração, entre em contato com nosso suporte.
    
    Atenciosamente,
    Equipe EXPO TV
    """
    
    try:
        message = MIMEMultipart("alternative")
        message["Subject"] = "✅ Senha Alterada - EXPO TV"
        message["From"] = f"{FROM_NAME} <{FROM_EMAIL}>"
        message["To"] = to_email
        
        part1 = MIMEText(text_content, "plain", "utf-8")
        part2 = MIMEText(html_content, "html", "utf-8")
        
        message.attach(part1)
        message.attach(part2)
        
        if not SMTP_USER or not SMTP_PASSWORD:
            print("⚠️ SMTP não configurado. Notificação não será enviada.")
            return False
            
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        
        print(f"✅ Notificação enviada para {to_email}")
        return True
        
    except Exception as e:
        print(f"❌ Erro ao enviar notificação: {str(e)}")
        return False

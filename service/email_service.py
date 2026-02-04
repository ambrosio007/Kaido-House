import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    
    @staticmethod
    def enviar_email_recuperacao(destinatario, token, nome_usuario):
        """
        Envia e-mail com link de recuperação de senha
        
        Args:
            destinatario (str): E-mail do usuário
            token (str): Token único para recuperação
            nome_usuario (str): Nome do usuário
        
        Returns:
            bool: True se enviado com sucesso, False caso contrário
        """
        try:
            # Configurações do servidor SMTP
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')  # Seu e-mail
            smtp_password = os.getenv('SMTP_PASSWORD')  # Senha de app do Gmail
            
            # URL base da sua aplicação
            base_url = os.getenv('BASE_URL', 'http://localhost:5000')
            link_recuperacao = f"{base_url}/redefinir_senha?token={token}"
            
            # Criar mensagem
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Recuperação de Senha - Kaido-House'
            msg['From'] = f"Kaido-House <{smtp_user}>"
            msg['To'] = destinatario
            
            # Corpo do e-mail em texto simples
            texto_simples = f"""
Olá {nome_usuario},

Recebemos uma solicitação de recuperação de senha para sua conta na Kaido-House.

Para redefinir sua senha, clique no link abaixo:
{link_recuperacao}

Este link é válido por 1 hora.

Se você não solicitou esta recuperação, ignore este e-mail.

Atenciosamente,
Equipe Kaido-House
"""
            
            # Corpo do e-mail em HTML
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background-color: #f4f4f4;
            border-radius: 10px;
            padding: 30px;
        }}
        .header {{
            background-color: #e63946;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .button {{
            display: inline-block;
            background-color: #e63946;
            color: white;
            padding: 15px 30px;
            text-decoration: none;
            border-radius: 5px;
            margin: 20px 0;
            font-weight: bold;
        }}
        .button:hover {{
            background-color: #d62828;
        }}
        .footer {{
            text-align: center;
            margin-top: 20px;
            font-size: 12px;
            color: #666;
        }}
        .warning {{
            background-color: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔐 Recuperação de Senha</h1>
        </div>
        <div class="content">
            <p>Olá <strong>{nome_usuario}</strong>,</p>
            
            <p>Recebemos uma solicitação de recuperação de senha para sua conta na <strong>Kaido-House</strong>.</p>
            
            <p>Para redefinir sua senha, clique no botão abaixo:</p>
            
            <div style="text-align: center;">
                <a href="{link_recuperacao}" class="button">REDEFINIR SENHA</a>
            </div>
            
            <p>Ou copie e cole este link no seu navegador:</p>
            <p style="word-break: break-all; background-color: #f8f9fa; padding: 10px; border-radius: 5px;">
                {link_recuperacao}
            </p>
            
            <div class="warning">
                <strong>⏰ Importante:</strong> Este link é válido por apenas <strong>1 hora</strong>.
            </div>
            
            <p>Se você <strong>não solicitou</strong> esta recuperação, ignore este e-mail. Sua senha permanecerá inalterada.</p>
            
            <p>Atenciosamente,<br>
            <strong>Equipe Kaido-House</strong></p>
        </div>
        <div class="footer">
            <p>&copy; 2026 Kaido-House - Joinville, SC</p>
            <p>Este é um e-mail automático. Por favor, não responda.</p>
        </div>
    </div>
</body>
</html>
"""
            
            # Anexar ambas as versões
            part1 = MIMEText(texto_simples, 'plain', 'utf-8')
            part2 = MIMEText(html, 'html', 'utf-8')
            
            msg.attach(part1)
            msg.attach(part2)
            
            # Enviar e-mail
            print(f"📧 Tentando enviar e-mail para {destinatario}...")
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()  # Segurança TLS
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ E-mail enviado com sucesso para {destinatario}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail: {str(e)}")
            return False
    
    @staticmethod
    def enviar_confirmacao_troca_senha(destinatario, nome_usuario):
        """
        Envia e-mail de confirmação após troca de senha bem-sucedida
        """
        try:
            smtp_server = os.getenv('SMTP_SERVER', 'smtp.gmail.com')
            smtp_port = int(os.getenv('SMTP_PORT', '587'))
            smtp_user = os.getenv('SMTP_USER')
            smtp_password = os.getenv('SMTP_PASSWORD')
            
            msg = MIMEMultipart('alternative')
            msg['Subject'] = 'Senha Alterada com Sucesso - Kaido-House'
            msg['From'] = f"Kaido-House <{smtp_user}>"
            msg['To'] = destinatario
            
            html = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{
            font-family: Arial, sans-serif;
            line-height: 1.6;
            color: #333;
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
        }}
        .container {{
            background-color: #f4f4f4;
            border-radius: 10px;
            padding: 30px;
        }}
        .header {{
            background-color: #28a745;
            color: white;
            padding: 20px;
            text-align: center;
            border-radius: 10px 10px 0 0;
        }}
        .content {{
            background-color: white;
            padding: 30px;
            border-radius: 0 0 10px 10px;
        }}
        .success-icon {{
            font-size: 48px;
            text-align: center;
            margin: 20px 0;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>✅ Senha Alterada</h1>
        </div>
        <div class="content">
            <div class="success-icon">🔒</div>
            
            <p>Olá <strong>{nome_usuario}</strong>,</p>
            
            <p>Sua senha foi <strong>alterada com sucesso</strong>!</p>
            
            <p>Se você não realizou esta alteração, entre em contato conosco imediatamente.</p>
            
            <p>Atenciosamente,<br>
            <strong>Equipe Kaido-House</strong></p>
        </div>
    </div>
</body>
</html>
"""
            
            part = MIMEText(html, 'html', 'utf-8')
            msg.attach(part)
            
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(smtp_user, smtp_password)
                server.send_message(msg)
            
            print(f"✅ E-mail de confirmação enviado para {destinatario}")
            return True
            
        except Exception as e:
            print(f"❌ Erro ao enviar e-mail de confirmação: {str(e)}")
            return False
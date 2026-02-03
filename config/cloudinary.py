import cloudinary
import cloudinary.uploader
import cloudinary.api
import os
from dotenv import load_dotenv

load_dotenv()

# Configuração do Cloudinary
cloudinary.config(
    cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
    api_key=os.getenv('CLOUDINARY_API_KEY'),
    api_secret=os.getenv('CLOUDINARY_API_SECRET'),
    secure=True
)

def upload_image(file, folder='kaido-house'):
    """
    Faz upload de uma imagem para o Cloudinary
    
    Args:
        file: Arquivo de imagem (FileStorage do Flask)
        folder: Pasta no Cloudinary onde a imagem será salva
    
    Returns:
        dict com 'url' e 'public_id' ou None em caso de erro
    """
    try:
        result = cloudinary.uploader.upload(
            file,
            folder=folder,
            resource_type='auto',
            transformation=[
                {'width': 1200, 'height': 900, 'crop': 'limit'},
                {'quality': 'auto:good'}
            ]
        )
        
        return {
            'url': result.get('secure_url'),
            'public_id': result.get('public_id')
        }
    except Exception as e:
        print(f"Erro ao fazer upload para Cloudinary: {e}")
        return None

def delete_image(public_id):
    """
    Deleta uma imagem do Cloudinary
    
    Args:
        public_id: ID público da imagem no Cloudinary
    
    Returns:
        bool: True se deletou com sucesso, False caso contrário
    """
    try:
        result = cloudinary.uploader.destroy(public_id)
        return result.get('result') == 'ok'
    except Exception as e:
        print(f"Erro ao deletar imagem do Cloudinary: {e}")
        return False
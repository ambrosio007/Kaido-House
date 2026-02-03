from model.pecas_model import PecaModel
from repository.pecas_repository import PecaRepository
from config.cloudinary import upload_image, delete_image

class PecaService:

    @staticmethod
    def cadastrar_peca(dados, fotos=None):
        """
        ✅ ATUALIZADO: Cadastra peça com upload no Cloudinary
        """
        try:
            peca = PecaModel(**dados)
            
            # Processar upload de fotos no Cloudinary
            urls_fotos = []
            public_ids = []
            
            if fotos:
                for foto in fotos:
                    if foto and foto.filename:
                        # Upload para Cloudinary
                        result = upload_image(foto, folder='kaido-house/pecas')
                        
                        if result:
                            urls_fotos.append(result['url'])
                            public_ids.append(result['public_id'])
            
            peca_dict = peca.to_dict()
            # Salvar URLs separadas por vírgula
            peca_dict['fotos'] = ','.join(urls_fotos) if urls_fotos else ''
            # Salvar public_ids para poder deletar depois
            peca_dict['public_ids'] = ','.join(public_ids) if public_ids else ''
            
            status = PecaRepository.adicionar_peca(peca_dict)
            
            if status:
                return True, "Peça cadastrada com sucesso!"
            else:
                # Se falhou, deletar imagens do Cloudinary
                for public_id in public_ids:
                    delete_image(public_id)
                return False, "Erro ao cadastrar peça no banco de dados"
                
        except Exception as e:
            print(f"Erro em PecaService.cadastrar_peca: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def listar_por_usuario(user_id):
        try:
            return PecaRepository.listar_por_usuario(user_id)
        except Exception as e:
            print(f"Erro ao listar peças: {e}")
            return []
    
    @staticmethod
    def listar_todos(categoria=None, estado=None):
        try:
            return PecaRepository.listar_todos(categoria, estado)
        except Exception as e:
            print(f"Erro ao listar todas as peças: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(peca_id):
        try:
            return PecaRepository.buscar_por_id(peca_id)
        except Exception as e:
            print(f"Erro ao buscar peça: {e}")
            return None
    
    @staticmethod
    def deletar_peca(peca_id):
        """
        ✅ ATUALIZADO: Deleta peça e suas imagens do Cloudinary
        """
        try:
            # Buscar a peça para pegar os public_ids
            peca = PecaRepository.buscar_por_id(peca_id)
            
            if peca and peca.get('public_ids'):
                # Deletar imagens do Cloudinary
                public_ids = peca['public_ids'].split(',')
                for public_id in public_ids:
                    if public_id.strip():
                        delete_image(public_id.strip())
            
            # Deletar do banco
            return PecaRepository.deletar(peca_id)
        except Exception as e:
            print(f"Erro ao deletar peça: {e}")
            return False
    
    @staticmethod
    def atualizar_peca(peca_id, dados):
        try:
            return PecaRepository.atualizar_peca(peca_id, dados)
        except Exception as e:
            print(f"Erro ao atualizar peça: {e}")
            return False

    @staticmethod
    def buscar_vitrine(estado=None, limit=5):
        """
        ✅ CORRIGIDO: Busca peças para a vitrine da Home de forma aleatória.
        Args:
            estado: 'novo' ou 'usado' para filtrar
            limit: quantidade de peças a retornar
        """
        try:
            return PecaRepository.listar_aleatorio(estado=estado, limit=limit)
        except Exception as e:
            print(f"Erro ao buscar vitrine de peças: {e}")
            return []
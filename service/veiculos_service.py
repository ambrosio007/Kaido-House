from model.veiculos_model import VeiculoModel
from repository.veiculo_repository import VeiculoRepository
from config_cloudinary import upload_image, delete_image

class VeiculoService:

    @staticmethod
    def cadastrar_veiculo(dados, fotos=None):
        """
        ✅ ATUALIZADO: Cadastra veículo com upload no Cloudinary
        """
        try:
            veiculo = VeiculoModel(**dados)
            
            # Processar upload de fotos no Cloudinary
            urls_fotos = []
            public_ids = []
            
            if fotos:
                for foto in fotos:
                    if foto and foto.filename:
                        # Upload para Cloudinary
                        result = upload_image(foto, folder='kaido-house/veiculos')
                        
                        if result:
                            urls_fotos.append(result['url'])
                            public_ids.append(result['public_id'])
            
            veiculo_dict = veiculo.to_dict()
            # Salvar URLs separadas por vírgula
            veiculo_dict['fotos'] = ','.join(urls_fotos) if urls_fotos else ''
            # Salvar public_ids para poder deletar depois
            veiculo_dict['public_ids'] = ','.join(public_ids) if public_ids else ''
            
            status = VeiculoRepository.adicionar_veiculo(veiculo_dict)
            
            if status:
                return True, "Veículo cadastrado com sucesso!"
            else:
                # Se falhou, deletar imagens do Cloudinary
                for public_id in public_ids:
                    delete_image(public_id)
                return False, "Erro ao cadastrar veículo no banco de dados"
                
        except Exception as e:
            print(f"Erro em VeiculoService.cadastrar_veiculo: {e}")
            return False, f"Erro: {str(e)}"
    
    @staticmethod
    def listar_por_usuario(user_id):
        try:
            return VeiculoRepository.listar_por_usuario(user_id)
        except Exception as e:
            print(f"Erro ao listar veículos: {e}")
            return []
    
    @staticmethod
    def listar_todos():
        try:
            return VeiculoRepository.listar_todos()
        except Exception as e:
            print(f"Erro ao listar todos os veículos: {e}")
            return []
    
    @staticmethod
    def buscar_por_id(veiculo_id):
        try:
            return VeiculoRepository.buscar_por_id(veiculo_id)
        except Exception as e:
            print(f"Erro ao buscar veículo: {e}")
            return None
    
    @staticmethod
    def deletar_veiculo(veiculo_id):
        """
        ✅ ATUALIZADO: Deleta veículo e suas imagens do Cloudinary
        """
        try:
            # Buscar o veículo para pegar os public_ids
            veiculo = VeiculoRepository.buscar_por_id(veiculo_id)
            
            if veiculo and veiculo.get('public_ids'):
                # Deletar imagens do Cloudinary
                public_ids = veiculo['public_ids'].split(',')
                for public_id in public_ids:
                    if public_id.strip():
                        delete_image(public_id.strip())
            
            # Deletar do banco
            return VeiculoRepository.deletar(veiculo_id)
        except Exception as e:
            print(f"Erro ao deletar veículo: {e}")
            return False
    
    @staticmethod
    def atualizar_veiculo(veiculo_id, dados):
        try:
            return VeiculoRepository.atualizar_veiculo(veiculo_id, dados)
        except Exception as e:
            print(f"Erro ao atualizar veículo: {e}")
            return False
        
    @staticmethod
    def buscar_vitrine(apenas_novos=True, limit=5):
        """
        ✅ CORRIGIDO: Busca veículos para a vitrine filtrando por novos ou usados.
        Consideramos 'novos' veículos com KM próximo a zero (ex: < 100km).
        """
        try:
            return VeiculoRepository.listar_aleatorio(apenas_novos=apenas_novos, limit=limit)
        except Exception as e:
            print(f"Erro ao buscar vitrine de veículos: {e}")
            return []